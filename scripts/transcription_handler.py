import re
import random

import torch
import stable_whisper
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT, SYLT, Encoding

from lyrics_handler import LyricsHandler
from media_handler import MediaInfoHandler

random.seed(0)


class TranscriptionHandler:
    def __init__(self, model_name='large-v3', download_root='./models'):
        # Check if CUDA is available, otherwise use CPU
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Initializing with device: {device}")

        # Indicate the start of model loading
        print(f"Loading model '{model_name}' from {download_root}. This may take a few moments...")

        # Load the model with the selected device
        self.model = stable_whisper.load_model(name=model_name, download_root=download_root, device=device)

        # Confirm model loading and mounting on the device
        print(f"Model '{model_name}' successfully loaded and mounted on {device}.")

        # NOTE: When implementing multi track/multi album transcripting, only load the model once.
    
    def __call__(self, file_path):
        print("Starting conversion and transcription process...")

        # Convert FLAC to MP3 if necessary
        file_path = self._convert_if_flac(file_path)
        if not file_path:
            return

        print("Extracting track name and artist name...")
        track_name, artist_name, _ = MediaInfoHandler.get_track_info(file_path)

        print(f"Fetching lyrics for {track_name} by {artist_name}...")
        lyrics = LyricsHandler.search_lyrics_online(track_name, artist_name)
        processed_lyrics = lyrics["processed_lyrics"]

        # Extract base file name without extension
        base_file_name = file_path.rsplit('.', 1)[0]  # Extract base file name

        if processed_lyrics:
            self._align_and_transcribe(file_path, processed_lyrics, base_file_name)
        else:
            self._transcribe(file_path, base_file_name)

        # Check if the file is an MP3 (after potential FLAC conversion)
        if file_path.lower().endswith('.mp3'):
            enhanced_lrc_path = f'{base_file_name}.enhanced.lrc'  # Use base file name for naming
            self.embed_lyrics(file_path, enhanced_lrc_path, processed_lyrics)
        else:
            print("Embedding lyrics is only supported for MP3 files.")

    def _convert_if_flac(self, file_path):
        # Flac files do not support embeded lyrics to my knowledge.
        if file_path.lower().endswith('.flac'):
            print("FLAC file detected. Starting conversion to MP3...")
            mp3_path = file_path.rsplit('.', 1)[0] + '.mp3'
            if MediaInfoHandler.convert_flac_to_mp3(file_path, mp3_path):
                print("FLAC file successfully converted to MP3.")
                return mp3_path
            else:
                print("Error converting FLAC to MP3.")
                return None
        return file_path

    def _align_and_transcribe(self, file_path, lyrics, base_file_name):
        # Remove line breaks, tabs, and other non-standard characters
        cleaned_lyrics = re.sub(r'[\r\n\t]+', ' ', lyrics)  # Replace line breaks and tabs with a space
        cleaned_lyrics = re.sub(r'[^\w\s]', '', cleaned_lyrics)  # Remove any non-alphanumeric characters except spaces

        print("Lyrics found. Starting alignment with audio...")
        result = self.model.align(
            audio=file_path,
            text=lyrics,
            language='en',
            vad=True,
            demucs=True,
            demucs_options=dict(shifts=5),
            original_split=False,
            regroup=True
        )

        print("Alignment completed. Saving result...")
        
        result.save_as_json('audio.json')
    
        # Saving the LRC and enhanced LRC content
        words = self._extract_words(result)

        with open(f'{base_file_name}.lrc', 'w') as lrc_file:
            lrc_file.write(self._create_lrc(words))

        with open(f'{base_file_name}.enhanced.lrc', 'w') as enhanced_lrc_file:
            enhanced_lrc_file.write(self._create_enhanced_lrc(words))

    
    def _transcribe(self, file_path, base_file_name):
        print("Lyrics not found. Starting transcription without alignment...")
        result = self.model.transcribe(file_path)
        print("Transcription completed. Saving result...")
                
        # Manually specify the path if save_as_json doesn't return it
        result.save_as_json('audio.json')
        
        # Saving the LRC and enhanced LRC content
        words = self._extract_words(result)

        with open(f'{base_file_name}.lrc', 'w') as lrc_file:
            lrc_file.write(self._create_lrc(words))

        with open(f'{base_file_name}.enhanced.lrc', 'w') as enhanced_lrc_file:
            enhanced_lrc_file.write(self._create_enhanced_lrc(words))


    def _extract_words(self, result):
        words = []
        for segment in result.segments:
            words.extend(segment.words)
        return words

    def _create_lrc(self, words):
        lrc_content = ""
        for word_info in words:
            start_time = self._format_time(word_info.start)
            word = word_info.word.strip()
            lrc_content += f"{start_time} {word}\n"
        return lrc_content

    def _create_enhanced_lrc(self, words):
        enhanced_lrc_content = ""
        for word_info in words:
            start_time = self._format_time(word_info.start)
            end_time = self._format_time(word_info.end)
            word = word_info.word.strip()
            enhanced_lrc_content += f"{start_time} {end_time} {word}\n"
        return enhanced_lrc_content

    def _format_time(self, time_in_seconds):
        minutes = int(time_in_seconds // 60)
        seconds = int(time_in_seconds % 60)
        milliseconds = int((time_in_seconds - int(time_in_seconds)) * 100)
        return f"[{minutes:02d}:{seconds:02d}.{milliseconds:02d}]"

    def embed_lyrics(self, mp3_path, enhanced_lrc_path, cleaned_lyrics):
        print(f"Embedding lyrics into {mp3_path}...")

        # Load the MP3 file
        audio = MP3(mp3_path, ID3=ID3)

        # Load existing ID3 tags or create new ones if they don't exist
        if audio.tags is None:
            audio.add_tags()

        # Read the enhanced LRC file
        with open(enhanced_lrc_path, 'r', encoding='utf-8') as lrc_file:
            enhanced_lrc = lrc_file.read()

        # Add or update the USLT tag (Unsynchronized lyrics)
        audio.tags.delall('USLT')
        audio.tags.add(USLT(encoding=Encoding.UTF8, lang='eng', desc='enhanced', text=cleaned_lyrics))

        # Add or update the SYLT tag (Synchronized lyrics)
        sylt_lyrics = self._convert_lrc_to_sylt_format(enhanced_lrc)
        
        audio.tags.delall('SYLT')
        audio.tags.add(SYLT(encoding=Encoding.UTF8, lang='eng', format=2, type=1, desc='enhanced', text=sylt_lyrics))  # NOTE: Might want to look into removing the "lang" and "desc" tags because that might be messing with Navidrome finding the USLT/SYLT tags idk

        # Save the tags
        audio.save()
        print(f"Lyrics embedded into {mp3_path} successfully.")

    def _convert_lrc_to_sylt_format(self, lrc_content):
        sylt_data = []
        for line in lrc_content.splitlines():
            parts = line.split(']', 1)
            if len(parts) < 2:
                continue

            timestamp, lyrics = parts
            timestamp = timestamp.strip('[')
            lyrics = lyrics.strip()

            # Remove any bracketed timing information from the lyrics
            lyrics = re.sub(r'\[[^\]]*\]', '', lyrics)

            # Convert timestamp to milliseconds
            minutes, seconds = map(float, timestamp.split(':'))
            total_milliseconds = int((minutes * 60 + seconds) * 1000)

            # Add each word with its timestamp
            words = lyrics.split()
            for word in words:
                # Each word followed by its timestamp
                sylt_data.append((word, total_milliseconds))

        return sylt_data

# Example usage
flac_file_path = "./Green Day - American Idiot - 10 - Letterbomb.flac"
transcription_handler = TranscriptionHandler()
transcription_handler(flac_file_path)
