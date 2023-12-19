# media_info_handler.py

from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.id3 import ID3
from PIL import Image
from io import BytesIO

class MediaInfoHandler:
    @staticmethod
    def get_song_info(file_path):
        if file_path.lower().endswith('.mp3'):
            return MediaInfoHandler.process_mp3_file(file_path)
        elif file_path.lower().endswith('.flac'):
            return MediaInfoHandler.process_flac_file(file_path)
        else:
            return "Unknown", None

    @staticmethod
    def process_mp3_file(file_path):
        audio = MP3(file_path, ID3=ID3)
        song_name = audio['TIT2'].text[0] if 'TIT2' in audio else "Unknown"
        album_art_image = MediaInfoHandler.get_album_art_mp3(audio)
        return song_name, album_art_image

    @staticmethod
    def process_flac_file(file_path):
        audio = FLAC(file_path)
        song_name = audio['title'][0] if audio.get('title') else "Unknown"
        album_art_image = MediaInfoHandler.get_album_art_flac(audio)
        return song_name, album_art_image

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
