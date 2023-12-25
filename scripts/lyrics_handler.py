import syncedlyrics
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT

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
                return lrc
            else:
                return "Lyrics not found."
        except Exception as e:
            return f"An error occurred: {e}"

    # Method to format lyrics for LRC
    @staticmethod
    def format_lyrics_for_lrc(json_data):
        lyrics = ""
        for segment in json_data['segments']:
            time_stamp = LyricsHandler.convert_timestamp(segment['start'])
            line = f"[{time_stamp}]{segment['text']}\n"
            lyrics += line
        return lyrics

    # Method to convert timestamps
    @staticmethod
    def convert_timestamp(seconds):
        m, s = divmod(seconds, 60)
        return f"{int(m):02d}:{s:05.2f}"

    # Method to embed lyrics into an MP3 file
    @staticmethod
    def embed_lyrics_to_mp3(mp3_path, lyrics):
        audio = MP3(mp3_path, ID3=ID3)
        audio.tags.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=lyrics))
        audio.save()
    
    # Example methods for displaying synchronized lyrics
    @staticmethod
    def parse_sylt_frame(sylt_frame):
        # This is a simplistic parser; may need to adjust it based on the actual format
        lyrics = []
        for line in sylt_frame.data.decode('utf-8').split('\n'):
            parts = line.split(' ')
            if len(parts) >= 2:
                time, text = parts[0], ' '.join(parts[1:])
                lyrics.append((int(time), text))
        return lyrics
    
