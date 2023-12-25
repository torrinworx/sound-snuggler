import subprocess

from PIL import Image
from io import BytesIO
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.id3 import ID3

class MediaInfoHandler:
    @staticmethod
    def get_track_info(file_path):
        if file_path.lower().endswith('.mp3'):
            return MediaInfoHandler.process_mp3_file(file_path)
        elif file_path.lower().endswith('.flac'):
            return MediaInfoHandler.process_flac_file(file_path)
        else:
            return "Unknown", "Unknown", None

    @staticmethod
    def process_mp3_file(file_path):
        audio = MP3(file_path, ID3=ID3)
        song_name = audio['TIT2'].text[0] if 'TIT2' in audio else "Unknown"
        artist_name = audio['TPE1'].text[0] if 'TPE1' in audio else "Unknown"
        album_art_image = MediaInfoHandler.get_album_art_mp3(audio)
        return song_name, artist_name, album_art_image

    @staticmethod
    def process_flac_file(file_path):
        audio = FLAC(file_path)
        song_name = audio['title'][0] if audio.get('title') else "Unknown"
        artist_name = audio['artist'][0] if audio.get('artist') else "Unknown"
        album_art_image = MediaInfoHandler.get_album_art_flac(audio)
        return song_name, artist_name, album_art_image

    @staticmethod
    def get_album_art_mp3(audio):
        if 'APIC:' in audio:
            return Image.open(BytesIO(audio['APIC:'].data))
        return None

    @staticmethod
    def get_album_art_flac(audio):
        if audio.pictures:
            return Image.open(BytesIO(audio.pictures[0].data))
        return None
    
    @staticmethod
    def extract_synchronized_lyrics(file_path):
        if file_path.lower().endswith('.mp3'):
            audio = MP3(file_path, ID3=ID3)
            if 'SYLT::' in audio:
                return MediaInfoHandler.parse_sylt_frame(audio['SYLT::'])
        return []

    @staticmethod
    def parse_sylt_frame(sylt_frame):
        # Parse the SYLT frame to extract synchronized lyrics
        # This is a simplistic parser; adjust based on the actual format
        lyrics = []
        for line in sylt_frame.text.split('\n'):
            parts = line.split(' ', 1)
            if len(parts) == 2:
                time, text = parts
                lyrics.append((int(time), text))
        return lyrics
    
    @staticmethod
    def convert_flac_to_mp3(source_file_path, target_file_path, bitrate='320k'):
        """
        Convert a FLAC file to MP3 format.

        Args:
        source_file_path (str): Path to the source FLAC file.
        target_file_path (str): Path where the converted MP3 file will be saved.
        bitrate (str): Bitrate for the output MP3 file, default is 320k.

        Returns:
        bool: True if conversion was successful, False otherwise.
        """
        try:
            print(f"Converting {source_file_path} to MP3...")
            subprocess.run(
                ['ffmpeg', '-y', '-i', source_file_path, '-ab', bitrate, target_file_path], # -y flag allows for overwriting existing files if found without y/N intervention
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("Conversion completed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print("An error occurred during conversion.")
            print(f"Error message: {e.stderr}")
            return False
