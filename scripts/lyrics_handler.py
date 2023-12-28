import re
import syncedlyrics
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

class LyricsHandler:
    # For retrieving lyrics embedded in a music file
    @staticmethod
    def get_embedded_lyrics_from_file(file_path):
        if not file_path:
            return "No song loaded."

        lyrics = "Lyrics not available."
        try:
            if file_path.lower().endswith('.mp3'):
                audio = MP3(file_path, ID3=ID3)

                # Print all tag keys for diagnostic purposes
                print("Available tags in the file:", audio.keys())

                # Retrieve unsynchronized lyrics (USLT) if available
                lyrics = LyricsHandler._get_uslt_lyrics(audio)

                # If USLT not found, try retrieving synchronized lyrics (SYLT)
                if lyrics == "Lyrics not available.":
                    lyrics = LyricsHandler._get_sylt_lyrics(audio)

            elif file_path.lower().endswith('.flac'):
                # Future implementation for FLAC files
                pass

        except Exception as e:
            print(f"Error extracting lyrics: {e}")

        return lyrics

    @staticmethod
    def _get_uslt_lyrics(audio):
        for key in audio.keys():
            if key.startswith('USLT'):
                return audio[key].text
        return "Lyrics not available."

    @staticmethod
    def _get_sylt_lyrics(audio):
        for key in audio.keys():
            if key.startswith('SYLT'):
                # TODO: Implement parsing for synchronized lyrics
                return str(audio[key].data)
        return "Lyrics not available."

    # Fetch lyrics from an online database (uses syncedlyrics library: https://github.com/lo3me/syncedlyrics)
    @staticmethod
    def retrieve_lyrics_online(track_name, artist_name):
        try:
            lrc_content = syncedlyrics.search(f"{track_name} {artist_name}")
            if lrc_content:
                return LyricsHandler._process_lrc_content(lrc_content)
            else:
                return "Lyrics not found.", ""
        except Exception as e:
            return f"An error occurred: {e}", ""

    @staticmethod
    def _process_lrc_content(lrc_content):
        lines = lrc_content.split('\n')
        cleaned_lyrics = [re.sub(r'\[.*?\]', '', line).strip() for line in lines if line.strip()]
        return lrc_content, '\n'.join(cleaned_lyrics)  # Return both synced and unsynced lyrics
