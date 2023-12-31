import os
import re

import syncedlyrics
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.flac import FLAC

class LyricsHandler:
    # For retrieving lyrics embedded in a music file
    @staticmethod
    def retrieve_lyrics_from_file(file_path):
        if not file_path:
            return {"error": "No song loaded."}

        lyrics_data = {
            "unsynced_lyrics": None,
            "synced_lyrics": None
        }
        
        try:
            if file_path.lower().endswith('.mp3'):
                audio = MP3(file_path, ID3=ID3)

                # Retrieve unsynchronized lyrics
                lyrics_data["unsynced_lyrics"] = LyricsHandler._retrieve_unsynced_lyrics(audio)
                
                # Try to retrieve synced lyrics from enhanced LRC file
                lyrics_data["synced_lyrics"] = LyricsHandler._retrieve_enhanced_lrc_lyrics(file_path)
                
                # If no external synced lyrics found, search internally
                if not lyrics_data["synced_lyrics"]:
                    lyrics_data["synced_lyrics"] = LyricsHandler._retrieve_synced_lyrics(audio)

            elif file_path.lower().endswith('.flac'):
                audio = FLAC(file_path)

                # Retrieve lyrics from Vorbis comments
                lyrics_data["unsynced_lyrics"] = LyricsHandler._retrieve_lyrics_from_flac(audio)

                # Synced lyrics handling (if applicable)
                # FLAC doesn't support SYLT, so you might use external .lrc files
                lyrics_data["synced_lyrics"] = LyricsHandler._retrieve_enhanced_lrc_lyrics(file_path)


        except Exception as e:
            return {"error": f"Error extracting lyrics: {e}"}
        return lyrics_data
    
    @staticmethod
    def _retrieve_lyrics_from_flac(audio):
        # In Vorbis comments, lyrics might be under a 'LYRICS' tag
        # This can vary, so you might need to adjust based on your files
        if 'LYRICS' in audio:
            return audio['LYRICS'][0]
        return None

    @staticmethod
    def _retrieve_enhanced_lrc_lyrics(file_path):
        enhanced_lrc_path = file_path.rsplit('.', 1)[0] + '.enhanced.lrc'
        if os.path.exists(enhanced_lrc_path):
            with open(enhanced_lrc_path, 'r') as file:
                return file.read()
        return None

    @staticmethod
    def _retrieve_unsynced_lyrics(audio):
        for key in audio.keys():
            if key.startswith('USLT'):
                return audio[key].text
        return None

    @staticmethod
    def _retrieve_synced_lyrics(audio):
        for key in audio.keys():
            if key.startswith('SYLT'):
                return str(audio[key])
        return None

    # Fetch lyrics from an online database
    @staticmethod
    def search_lyrics_online(track_name, artist_name):
        try:
            online_lyrics = syncedlyrics.search(f"{track_name} {artist_name}")
            if online_lyrics:
                return LyricsHandler._process_online_lyrics(online_lyrics)
            else:
                return {"error": "Lyrics not found."}
        except Exception as e:
            return {"error": f"An error occurred: {e}"}

    @staticmethod
    def _process_online_lyrics(online_lyrics):
        lines = online_lyrics.split('\n')
        processed_lyrics = [re.sub(r'\[[^\]]*\]', '', line).strip() for line in lines if line.strip()]
        return {
            "original_lyrics": online_lyrics, 
            "processed_lyrics": '\n'.join(processed_lyrics)
        }
