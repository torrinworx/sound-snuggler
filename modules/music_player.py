import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import vlc
from PIL import Image, ImageTk

from .lyrics_handler import LyricsHandler
from .media_info_handler import MediaInfoHandler

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

    def load_song(self):
        song_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.flac")])
        if song_path:
            self.current_song = song_path
            media = self.vlc_instance.media_new(song_path)
            media.parse()
            self.player.set_media(media)
            self.time_slider.configure(to=media.get_duration() / 1000)
            self.update_song_info()

    def update_song_info(self):
        if self.current_song:
            song_name, album_art_image = MediaInfoHandler.get_song_info(self.current_song)
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
        lyrics = LyricsHandler.extract_lyrics(self.current_song)
        self.lyrics_display.delete(1.0, tk.END)
        self.lyrics_display.insert(tk.END, lyrics if lyrics else "Lyrics not available.")

    def toggle_play_pause(self):
        if self.current_song:
            if self.is_playing:
                self.player.pause()
            else:
                self.player.play()
            self.is_playing = not self.is_playing
            self.play_pause_button.config(image=self.pause_icon if self.is_playing else self.play_icon)
            self.update_progress()

    def update_progress(self):
        if self.current_song:
            try:
                current_time = self.player.get_time() / 1000
                total_time = self.time_slider.cget("to")
                self.time_slider.set(current_time)
                self.time_info.config(text=f"{self.format_time(current_time)} / {self.format_time(total_time)}")
                self.parent.update_idletasks()
                if self.is_playing:
                    self.after(1000, self.update_progress)
            except Exception as e:
                print(f"Error in update_progress: {e}")

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

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"
