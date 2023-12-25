import re

import syncedlyrics
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

class LyricsHandler:
    # For retreiving lyrics from a file
    @staticmethod
    def extract_lyrics(file_path):
        if not file_path:
            return "No song loaded."

        lyrics = "Lyrics not available."
        try:
            if file_path.lower().endswith('.mp3'):
                audio = MP3(file_path, ID3=ID3)
                # Check for unsynchronized lyrics
                if 'USLT::' in audio:
                    lyrics = audio['USLT::'].text
                # Check for synchronized lyrics
                elif 'SYLT::' in audio:
                    # TODO: This is a more complex case, as you need to parse the synchronized lyrics
                    # Here, we just return the raw data, need to implement a parser
                    lyrics = str(audio['SYLT::'].data)

            elif file_path.lower().endswith('.flac'):
                # Add logic for FLAC files if necessary
                pass

        except Exception as e:
            print(f"Error extracting lyrics: {e}")

        return lyrics

    # Fetch lyrics from online db's (uses syncedlyrics library: https://github.com/lo3me/syncedlyrics)
    @staticmethod
    def fetch_lyrics(track_name, artist_name):
        try:
            lrc = syncedlyrics.search(f"{track_name} {artist_name}")
            if lrc:
                # Process the lyrics to remove time codes
                lines = lrc.split('\n')
                cleaned_lyrics = []
                for line in lines:
                    # Remove the timestamp using a regular expression
                    cleaned_line = re.sub(r'\[.*?\]', '', line).strip()
                    if cleaned_line:
                        cleaned_lyrics.append(cleaned_line)
                return lrc, '\n'.join(cleaned_lyrics)  # Return both synced and unsynced lyrics
            else:
                return "Lyrics not found.", ""
        except Exception as e:
            return f"An error occurred: {e}", ""
