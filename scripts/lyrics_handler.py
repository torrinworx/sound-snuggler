import re
import syncedlyrics
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

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

                # Print all tag keys for diagnostic purposes
                print("Available tags in the file:", audio.keys())

                # Retrieve unsynchronized lyrics (USLT)
                lyrics_data["unsynced_lyrics"] = LyricsHandler._retrieve_unsynced_lyrics(audio)

                # Retrieve synchronized lyrics (SYLT)
                lyrics_data["synced_lyrics"] = LyricsHandler._retrieve_synced_lyrics(audio)

            elif file_path.lower().endswith('.flac'):
                # Future implementation for FLAC files
                pass

        except Exception as e:
            return {"error": f"Error extracting lyrics: {e}"}

        return lyrics_data

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
        processed_lyrics = [re.sub(r'\[.*?\]', '', line).strip() for line in lines if line.strip()]
        return {
            "original_lyrics": online_lyrics, 
            "processed_lyrics": '\n'.join(processed_lyrics)
        }  # Return both original and processed lyrics

