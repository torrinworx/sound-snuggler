import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from threading import Thread
from time import sleep

from scripts.media_handler import MediaInfoHandler
from scripts.lyrics_handler import LyricsHandler
from scripts.transcription_handler import TranscriptionHandler


class LyricsSynchronizer(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.album_art_label = None
        self.loading_label = None
        self.max_image_size = (200, 200)
        self.default_album_art = Image.new('RGB', self.max_image_size, color='grey')

        self.album_info_var = tk.StringVar()
        self.download_path_info_var = tk.StringVar()

        self._create_widgets()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Initialize the transcription handler
        self.transcription_handler = TranscriptionHandler()

    def _create_widgets(self):
        self.album_art_frame = tk.Frame(self)
        self.album_art_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self._display_album_art(self.default_album_art, self.album_art_frame)

        control_frame = tk.Frame(self)
        control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)

        # Add a button for transcription
        self.transcribe_music_button = tk.Button(control_frame, text="Transcribe Music File", command=self._transcribe_music_file)
        self.transcribe_music_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.loading_label = tk.Label(control_frame, text="")
        self.loading_label.grid(row=1, column=0)

        self.lyrics_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.lyrics_text.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

    def _transcribe_music_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.flac")])
        if file_path:
            self._start_loading()
            Thread(target=self._transcription_thread, args=(file_path,), daemon=True).start()

    def _transcription_thread(self, file_path):
        try:
            song_name, artist_name, album_art_image = MediaInfoHandler.get_track_info(file_path)
            self.album_info_var.set(f"Song: {song_name}")
            if album_art_image:
                self._display_album_art(album_art_image, self.album_art_frame)

            self.transcription_handler(file_path)
            lyrics_data = LyricsHandler.retrieve_lyrics_from_file(file_path)
            self._stop_loading()
            # Update UI with lyrics
            self._update_lyrics_display(lyrics_data)
        except Exception as e:
            self._stop_loading()
            messagebox.showerror("Error", f"An error occurred during transcription: {e}")

    def _update_lyrics_display(self, lyrics_data):
            # This method will update the UI with the lyrics
            def update():
                if 'error' in lyrics_data:
                    messagebox.showerror("Error", lyrics_data['error'])
                else:
                    unsynced = lyrics_data['unsynced_lyrics']
                    synced = lyrics_data['synced_lyrics']

                    lyrics_to_display = f"Unsynced Lyrics:\n{unsynced}\n\nSynced Lyrics:\n{synced}"
                    self.lyrics_text.delete('1.0', tk.END)
                    self.lyrics_text.insert(tk.END, lyrics_to_display)

            # Safely update the UI from the main thread
            self.parent.after(0, update)
    
    def _start_loading(self):
        def animate():
            for frame in ['-', '\\', '|', '/']:
                if self.loading_label:
                    self.loading_label.config(text=f"Loading {frame}")
                    self.parent.update_idletasks()
                    sleep(0.25)

        Thread(target=animate, daemon=True).start()

    def _stop_loading(self):
        if self.loading_label:
            self.loading_label.config(text="")

    def _display_album_art(self, image, parent_frame):
        if self.album_art_label:
            self.album_art_label.destroy()

        image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.album_art_label = tk.Label(parent_frame, image=photo)
        self.album_art_label.image = photo
        self.album_art_label.pack()

    def _display_lyrics(self, lyrics):
        self.lyrics_text.delete('1.0', tk.END)
        self.lyrics_text.insert(tk.END, lyrics)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricsSynchronizer(root)
    app.pack(expand=True, fill="both")
    root.mainloop()
