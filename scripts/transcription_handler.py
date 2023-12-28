import re

import torch
import mutagen
import stable_whisper
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT, SYLT, Encoding

from lyrics_handler import LyricsHandler
from media_handler import MediaInfoHandler


class TranscriptionHandler:
    def __init__(self, model_name='large', download_root='./models'):
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
        synced_lyrics, cleaned_lyrics = LyricsHandler.fetch_lyrics(track_name, artist_name)

        if cleaned_lyrics:
            self._align_and_transcribe(file_path, cleaned_lyrics)
        else:
            self._transcribe(file_path)

        # Check if the file is an MP3 (after potential FLAC conversion)
        if file_path.lower().endswith('.mp3'):
            enhanced_lrc_path = 'audio.enhanced.lrc'
            self.embed_lyrics(file_path, enhanced_lrc_path, cleaned_lyrics)
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

    def _align_and_transcribe(self, file_path, lyrics):
        print("Lyrics found. Starting alignment with audio...")
        result = self.model.align(file_path, lyrics, language='en')
        print("Alignment completed. Saving result as JSON...")
        
        # Manually specify the path if save_as_json doesn't return it
        json_path = 'audio.json'
        result.save_as_json(json_path)
        result.to_srt_vtt('audio.srt', segment_level=False)
        result.to_srt_vtt('audio.vtt', segment_level=False)
        
        srt_path = 'audio.srt'
        self._convert_srt_to_lrc(srt_path, 'audio.lrc')
        self._convert_srt_to_enhanced_lrc(srt_path, 'audio.enhanced.lrc')

    def _transcribe(self, file_path):
        print("Lyrics not found. Starting transcription without alignment...")
        result = self.model.transcribe(file_path)
        print("Transcription completed. Saving result as JSON...")
        
        # Manually specify the path if save_as_json doesn't return it
        json_path = 'audio.json'
        result.save_as_json(json_path)
        result.to_srt_vtt('audio.srt', segment_level=False)
        result.to_srt_vtt('audio.vtt', segment_level=False)
        
        srt_path = 'audio.srt'
        self._convert_srt_to_lrc(srt_path, 'audio.lrc')
        self._convert_srt_to_enhanced_lrc(srt_path, 'audio.enhanced.lrc')
    
    def _clean_lyrics(self, line):
        # Remove HTML tags and additional timestamps
        line = re.sub(r'<[^>]+>', '', line)
        line = re.sub(r'\[\d{2}:\d{2}\.\d{2}\]', '', line)
        return line.strip()

    def _convert_srt_to_lrc(self, srt_path, lrc_path):
        with open(srt_path, 'r', encoding='utf-8') as srt_file:
            srt_lines = srt_file.readlines()

        with open(lrc_path, 'w', encoding='utf-8') as lrc_file:
            for line in srt_lines:
                if '-->' in line:
                    start_time = line.split('-->')[0].strip()
                    # Convert time format from 'HH:MM:SS,MS' to 'MM:SS.xx'
                    h, m, s_ms = start_time.split(':')
                    s, ms = s_ms.split(',')
                    lrc_time = f"[{int(m):02d}:{int(s):02d}.{int(ms)//10:02d}]"
                elif line.strip() and not line.strip().isdigit():
                    clean_line = self._clean_lyrics(line)
                    if clean_line:  # Ensure the line is not empty and cleaned
                        lrc_file.write(f"{lrc_time} {clean_line}\n")

    def _convert_srt_to_enhanced_lrc(self, srt_path, lrc_path):
        with open(srt_path, 'r', encoding='utf-8') as srt_file:
            srt_lines = srt_file.readlines()

        lrc_start_time, lrc_end_time = "", ""
        current_lyric_lines = []
        with open(lrc_path, 'w', encoding='utf-8') as lrc_file:
            for line in srt_lines:
                if '-->' in line:
                    # Write previous lyrics if any
                    self._write_lyrics(lrc_file, current_lyric_lines, lrc_start_time, lrc_end_time)
                    current_lyric_lines = []

                    lrc_start_time, lrc_end_time = self._parse_srt_times(line)
                elif line.strip() and not line.strip().isdigit():
                    clean_line = self._clean_lyrics(line)
                    if clean_line:
                        current_lyric_lines.append(clean_line)

            # Write any remaining lyrics after the loop ends
            self._write_lyrics(lrc_file, current_lyric_lines, lrc_start_time, lrc_end_time)

    def _parse_srt_times(self, line):
        times = line.split('-->')
        start_time = times[0].strip()
        end_time = times[1].strip()

        lrc_start_time = self._convert_time_to_lrc_format(start_time)
        lrc_end_time = self._convert_time_to_lrc_format(end_time)

        return lrc_start_time, lrc_end_time

    def _convert_time_to_lrc_format(self, time_str):
        h, m, s_ms = time_str.split(':')
        s, ms = s_ms.split(',')
        return f"[{int(m):02d}:{int(s):02d}.{int(ms)//10:02d}]"

    def _write_lyrics(self, lrc_file, lyric_lines, start_time, end_time):
        for lyric_line in lyric_lines:
            lrc_file.write(f"{start_time}{lyric_line}{end_time}\n")

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
        
        print(sylt_lyrics)
        audio.tags.delall('SYLT')
        audio.tags.add(SYLT(encoding=Encoding.UTF8, lang='eng', format=2, type=1, desc='enhanced', text=sylt_lyrics))

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
            lyrics = re.sub(r'\[.*?\]', '', lyrics)

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
