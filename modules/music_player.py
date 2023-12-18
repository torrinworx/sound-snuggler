import os
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import vlc
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.flac import FLAC

class MusicPlayer(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        self.is_slider_active = False

        self.create_widgets()
        self.update_progress()

    def create_widgets(self):
        # Load Button
        self.load_button = ttk.Button(self, text="Load Song", command=self.load_song)
        self.load_button.pack()

        # Album Cover
        self.album_cover_label = ttk.Label(self)
        self.album_cover_label.pack()

        # Control Panel (Play/Pause, Stop)
        control_frame = ttk.Frame(self)
        control_frame.pack()

        self.play_icon = tk.PhotoImage(file='./assets/play_icon.png')
        self.pause_icon = tk.PhotoImage(file='./assets/pause_icon.png')

        self.play_pause_button = ttk.Button(control_frame, image=self.play_icon, command=self.toggle_play_pause)
        self.play_pause_button.pack(side=tk.LEFT)

        # Time Slider
        self.time_slider = ttk.Scale(self, from_=0, to=100, orient='horizontal', command=self.on_slider_move)
        self.time_slider.pack(fill='x', expand=True)
        self.time_slider.bind("<ButtonRelease-1>", self.on_slider_release)

        # Song Information
        self.song_info = ttk.Label(self, text="Song: Unknown")
        self.song_info.pack()

        # Time Information
        self.time_info = ttk.Label(self, text="00:00 / 00:00")
        self.time_info.pack()

        # Current Song
        self.current_song = ""
        self.is_playing = False

    def load_song(self):
        song_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.flac")])
        if song_path:
            self.current_song = song_path
            media = self.vlc_instance.media_new(self.current_song)
            media.parse()  # Call parse on the Media object
            self.player.set_media(media)
            self.time_slider.configure(to=media.get_duration() / 1000)
            self.update_song_info()

    def update_song_info(self):
        if self.current_song:
            try:
                song_name = "Unknown"
                album_art_path = None

                if self.current_song.lower().endswith('.mp3'):
                    audio = MP3(self.current_song, ID3=ID3)
                    if 'TIT2' in audio:
                        song_name = audio['TIT2'].text[0]  # Song title
                    if 'APIC:' in audio:
                        album_art_data = audio['APIC:'].data
                        with open('temp_album_art.jpg', 'wb') as img_file:
                            img_file.write(album_art_data)
                        album_art_path = 'temp_album_art.jpg'

                elif self.current_song.lower().endswith('.flac'):
                    audio = FLAC(self.current_song)
                    if audio.get('title'):
                        song_name = audio['title'][0]
                    if audio.pictures:
                        album_art_data = audio.pictures[0].data
                        with open('temp_album_art.jpg', 'wb') as img_file:
                            img_file.write(album_art_data)
                        album_art_path = 'temp_album_art.jpg'

                self.song_info.config(text=f"Song: {song_name}")

                if album_art_path and os.path.exists(album_art_path):
                    image = Image.open(album_art_path)
                    image = image.resize((200, 200), Image.Resampling.LANCZOS)  # Updated line
                    photo = ImageTk.PhotoImage(image)
                    self.album_cover_label.config(image=photo)
                    self.album_cover_label.image = photo  # Keep a reference
                else:
                    self.album_cover_label.config(image='')
                    self.album_cover_label.image = None

            except mutagen.MutagenError as e:
                # Handle the error (e.g., display a message or log the error)
                print(f"Error: Unable to process the file {self.current_song} - {e}")
                # Set default values or clear the labels
                self.song_info.config(text="Song: Unknown")
                self.album_cover_label.config(image='')
                self.album_cover_label.image = None

        # Update lyrics
        self.update_lyrics()

    def toggle_play_pause(self):
        if self.current_song:
            if self.is_playing:
                self.player.pause()
                self.play_pause_button.config(image=self.play_icon)
            else:
                self.player.play()
                self.play_pause_button.config(image=self.pause_icon)
            self.is_playing = not self.is_playing

    def stop_song(self):
        self.player.stop()
        self.is_playing = False
        self.play_pause_button.config(image=self.play_icon)
        self.time_slider.set(0)

    def update_progress(self):
        if self.is_playing:
            print("Updating progress...")  # Debug print
            if not self.is_slider_active:
                current_time = self.player.get_time() / 1000
                print(f"Current time from player: {current_time}")  # Debug print
                self.time_slider.set(current_time)

            total_time = self.time_slider.cget("to")
            current_time = self.time_slider.get()
            print(f"Current time: {current_time}, Total time: {total_time}")  # Debug print
            self.time_info.config(text=f"{self.format_time(current_time)} / {self.format_time(total_time)}")

        self.after(1000, self.update_progress)

        # Schedule this method to be called again after 1000 milliseconds
        self.after(1000, self.update_progress)

    def on_slider_move(self, value):
        self.is_slider_active = True  # Set the flag when the slider is being moved

    def on_slider_release(self, event):
        if self.current_song:
            new_time = int(float(self.time_slider.get()) * 1000)
            self.player.set_time(new_time)

        self.is_slider_active = False
        self.after(500, self.sync_slider_with_media)  # Sync after a short delay

    def sync_slider_with_media(self):
        # This method synchronizes the slider position with the media time.
        if self.current_song and not self.is_slider_active:
            current_time = self.player.get_time() / 1000
            self.time_slider.set(current_time)

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02}:{seconds:02}"
    
    def update_progress(self):
        # Updated to check if the slider is active or not
        if self.is_playing and not self.is_slider_active:
            self.sync_slider_with_media()

        total_time = self.time_slider.cget("to")
        current_time = self.time_slider.get()
        self.time_info.config(text=f"{self.format_time(current_time)} / {self.format_time(total_time)}")
        self.after(1000, self.update_progress)
