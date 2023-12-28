from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT, SYLT

def display_embedded_lyrics(mp3_file_path):
    try:
        audio = MP3(mp3_file_path, ID3=ID3)

        # Check and display USLT (Unsynchronized lyrics)
        if 'USLT:enhanced:eng' in audio:
            print("Unsynchronized Lyrics:")
            print(audio['USLT:enhanced:eng'].text)
            print("\n-----------------------\n")
        else:
            print("No unsynchronized lyrics found.")

        # Check and display SYLT (Synchronized lyrics)
        if 'SYLT:enhanced:eng' in audio:
            print("Synchronized Lyrics:")
            for lyric, timestamp in audio['SYLT:enhanced:eng'].text:
                print(f"{lyric} [timestamp: {timestamp}ms]")
            print("\n-----------------------\n")
        else:
            print("No synchronized lyrics found.")

    except Exception as e:
        print(f"Error reading the file: {e}")

# Example usage
mp3_file_path = "./Green Day - American Idiot - 10 - Letterbomb.mp3"
display_embedded_lyrics(mp3_file_path)
