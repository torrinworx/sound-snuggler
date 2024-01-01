import re

import vlc
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, filedialog, scrolledtext

from scripts.lyrics_handler import LyricsHandler
from scripts.media_handler import MediaInfoHandler

class MusicPlayer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.is_slider_active = False
        self.current_song = ""
        self.is_playing = False

        self.create_widgets()
        self.update_progress()

    def create_widgets(self):
        self.load_button = ttk.Button(self, text="Load Song", command=self.load_song)
        self.load_button.pack()

        self.album_cover_label = ttk.Label(self)
        self.album_cover_label.pack()

        control_frame = ttk.Frame(self)
        control_frame.pack()

        self.play_icon = tk.PhotoImage(file='./assets/play_icon.png')
        self.pause_icon = tk.PhotoImage(file='./assets/pause_icon.png')
        self.play_pause_button = ttk.Button(control_frame, image=self.play_icon, command=self.toggle_play_pause)
        self.play_pause_button.pack(side=tk.LEFT)

        self.time_slider = ttk.Scale(self, from_=0, to=100, orient='horizontal', command=self.on_slider_move, length=300)
        self.time_slider.pack(pady=10, padx=10)
        self.time_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.song_info = ttk.Label(self, text="Song: Unknown")
        self.song_info.pack()
        self.time_info = ttk.Label(self, text="00:00 / 00:00")
        self.time_info.pack()

        self.lyrics_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=40, height=10)
        self.lyrics_display.pack(pady=10)

        # Add this line to create the synchronized lyrics display
        self.sync_lyrics_display = ttk.Label(self, text="", wraplength=300)
        self.sync_lyrics_display.pack(pady=10)

    # Media Handling
    def load_song(self):
        song_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.flac")])
        if song_path:
            self.current_song = song_path
            media = self.vlc_instance.media_new(song_path)
            media.parse()
            self.player.set_media(media)
            self.time_slider.configure(to=media.get_duration() / 1000)
            self.update_song_info()

    # UI Update Methods
    def update_song_info(self):
        if self.current_song:
            song_name, artist_name, album_art_image = MediaInfoHandler.get_track_info(self.current_song)
            self.song_info.config(text=f"Song: {song_name}")
            self.update_album_art_ui(album_art_image)
            self.update_lyrics_display()

    def update_album_art_ui(self, album_art_image):
        self.album_cover_label.image = None
        if album_art_image:
            album_art_image = album_art_image.resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(album_art_image)
            self.album_cover_label.config(image=photo)
            self.album_cover_label.image = photo

    def update_lyrics_display(self):
        lyrics = LyricsHandler.retrieve_lyrics_from_file(self.current_song)
        self.lyrics_display.delete(1.0, tk.END)
        print(lyrics)
        self.lyrics_display.insert(tk.END, lyrics["unsynced_lyrics"] if lyrics["unsynced_lyrics"] else "Lyrics not available.")
        self.synced_lyrics = self.parse_synced_lyrics(lyrics["synced_lyrics"])

    def parse_synced_lyrics(self, synced_lyrics_raw):
        parsed_synced_lyrics = []
        lines = synced_lyrics_raw.split('\n')
        for line in lines:
            # Find all timestamps and text in the line
            parts = re.findall(r'\[\d\d:\d\d\.\d\d\]|\S+', line)

            # Check if line has at least two timestamps and text
            if len(parts) >= 3 and re.match(r'\[\d\d:\d\d\.\d\d\]', parts[0]) and re.match(r'\[\d\d:\d\d\.\d\d\]', parts[1]):
                start_time_str = parts[0].strip('[]')
                end_time_str = parts[1].strip('[]')

                start_minutes, start_seconds = map(float, start_time_str.split(':'))
                start_time_ms = int((start_minutes * 60 + start_seconds) * 1000)

                end_minutes, end_seconds = map(float, end_time_str.split(':'))
                end_time_ms = int((end_minutes * 60 + end_seconds) * 1000)

                text = ' '.join(parts[2:])  # Join remaining parts as text

                parsed_synced_lyrics.append((start_time_ms, end_time_ms, text))

        return parsed_synced_lyrics

    def update_synced_lyrics_display(self, current_time):
        if not hasattr(self, 'synced_lyrics') or not self.synced_lyrics:
            self.sync_lyrics_display.config(text="")
            return

        current_text = ""
        for start_time, end_time, text in self.synced_lyrics:
            if current_time >= start_time and (end_time is None or current_time < end_time):
                current_text = text
                break

        self.sync_lyrics_display.config(text=current_text)
        print("\nCurrent Synced Lyric:", current_text, "\ntime:", current_time, "\n")  # Debugging

    def update_progress(self):
        if not self.current_song:
            return

        try:
            current_time = self.player.get_time()

            total_time = self.time_slider.cget("to") * 1000
            self.time_slider.set(current_time / 1000)
            self.time_info.config(text=f"{self.format_time(current_time / 1000)} / {self.format_time(total_time / 1000)}")
            self.update_synced_lyrics_display(current_time)
            self.parent.update_idletasks()
            if self.is_playing:
                self.after(100, self.update_progress)
        except Exception as e:
            print(f"Error in update_progress: {e}")

    # Player Control Methods
    def toggle_play_pause(self):
        if self.current_song:
            if self.is_playing:
                self.player.pause()
            else:
                self.player.play()
            self.is_playing = not self.is_playing
            self.play_pause_button.config(image=self.pause_icon if self.is_playing else self.play_icon)
            self.update_progress()

    def on_slider_move(self, value):
        self.is_slider_active = True

    def on_slider_release(self, event):
        if self.current_song:
            new_time = int(float(self.time_slider.get()) * 1000)
            self.player.set_time(new_time)
            self.is_slider_active = False
            self.after(500, self.sync_slider_with_media)

    def sync_slider_with_media(self):
        if self.current_song and not self.is_slider_active:
            current_time = self.player.get_time() / 1000
            self.time_slider.set(current_time)

    # Utility Methods
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"
