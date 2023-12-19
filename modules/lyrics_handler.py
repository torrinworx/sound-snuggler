from mutagen.mp3 import MP3
from mutagen.id3 import ID3

class LyricsHandler:
    # For loading and displaying lyrics from a file in the music player
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
                    # This is a more complex case, as you need to parse the synchronized lyrics
                    # Here, we just return the raw data, but you should implement a parser
                    lyrics = str(audio['SYLT::'].data)

            elif file_path.lower().endswith('.flac'):
                # Add logic for FLAC files if necessary
                pass

        except Exception as e:
            print(f"Error extracting lyrics: {e}")

        return lyrics

    @staticmethod
    def parse_sylt_frame(sylt_frame):
        # This is a simplistic parser; you may need to adjust it based on the actual format
        lyrics = []
        for line in sylt_frame.data.decode('utf-8').split('\n'):
            parts = line.split(' ')
            if len(parts) >= 2:
                time, text = parts[0], ' '.join(parts[1:])
                lyrics.append((int(time), text))
        return lyrics
