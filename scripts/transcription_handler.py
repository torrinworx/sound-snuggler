import json
import torch
import stable_whisper
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
    
    def convert_and_transcribe(self, file_path):
        print("Starting conversion and transcription process...")

        # Convert FLAC to MP3 if necessary
        file_path = self._convert_if_flac(file_path)
        if not file_path:
            return

        print("Extracting track name and artist name...")
        track_name, artist_name, _ = MediaInfoHandler.get_track_info(file_path)

        print(f"Fetching lyrics for {track_name} by {artist_name}...")
        lyrics = LyricsHandler.fetch_lyrics(track_name, artist_name)

        if lyrics:
            return self._align_and_transcribe(file_path, lyrics)
        else:
            return self._transcribe(file_path)

    def _convert_if_flac(self, file_path):
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

        # Load the JSON data
        with open(json_path, 'r') as file:
            json_data = json.load(file)

        # Format the lyrics for LRC
        formatted_lyrics = LyricsHandler.format_lyrics_for_lrc(json_data)

        # Embed the lyrics into the MP3 file
        LyricsHandler.embed_lyrics_to_mp3(file_path, formatted_lyrics)

        return json_path

    def _transcribe(self, file_path):
        print("Lyrics not found. Starting transcription without alignment...")
        result = self.model.transcribe(file_path)
        print("Transcription completed. Saving result as JSON...")
        
        # Manually specify the path if save_as_json doesn't return it
        json_path = 'audio.json'
        result.save_as_json(json_path)

        # Load the JSON data
        with open(json_path, 'r') as file:
            json_data = json.load(file)

        # Format the lyrics for LRC
        formatted_lyrics = LyricsHandler.format_lyrics_for_lrc(json_data)

        # Embed the lyrics into the MP3 file
        LyricsHandler.embed_lyrics_to_mp3(file_path, formatted_lyrics)

        return json_path

# Example usage
flac_file_path = "C:\\Users\\torri\\Downloads\\_American Idiot (2004)\\Green Day - American Idiot - 10 - Letterbomb.flac"
transcription_handler = TranscriptionHandler()
transcription_handler.convert_and_transcribe(flac_file_path)
