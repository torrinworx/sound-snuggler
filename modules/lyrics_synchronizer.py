import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
from .media_info_handler import MediaInfoHandler

class LyricsSynchronizer(tk.Frame):
    # Generating out lyrics and syncing lyrics for a song
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.album_art_label = None
        self.max_image_size = (200, 200)  # Maximum size for the album art
        self.default_album_art = Image.new('RGB', self.max_image_size, color = 'grey')  # Default album art

        self.album_info_var = tk.StringVar()  # To store album info
        self.lyric_file_info_var = tk.StringVar()  # To store lyric file info
        self.download_path_info_var = tk.StringVar()  # To store download path info

        self.create_widgets()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_widgets(self):
        # Album art label
        self.display_album_art(self.default_album_art)  # Display default album art initially

        # Lyrics text area
        self.lyrics_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.lyrics_text.grid(row=1, column=1, sticky="nsew")

        # Label to display album info
        tk.Label(self, textvariable=self.album_info_var).grid(row=2, column=0, sticky="w")

        # Label to display lyric file info
        tk.Label(self, textvariable=self.lyric_file_info_var).grid(row=2, column=1, sticky="w")

        # Label to display download path info
        tk.Label(self, textvariable=self.download_path_info_var).grid(row=2, column=2, sticky="w")

        # Buttons for uploading music and lyrics files
        self.upload_music_button = tk.Button(self, text="Upload Music File", command=self.upload_music_file)
        self.upload_music_button.grid(row=0, column=0, padx=10, pady=10)

        self.upload_lyrics_button = tk.Button(self, text="Upload Lyrics File", command=self.upload_lyrics_file)
        self.upload_lyrics_button.grid(row=0, column=1, padx=10, pady=10)

        # Button to set download path
        self.set_download_path_button = tk.Button(self, text="Set Download Path", command=self.set_download_path)
        self.set_download_path_button.grid(row=0, column=2, padx=10, pady=10)


    def upload_music_file(self):
        # Logic to upload and handle music files (MP3 and FLAC)
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3"), ("FLAC Files", "*.flac")])
        if file_path:
            song_name, album_art_image = MediaInfoHandler.get_song_info(file_path)
            self.album_info_var.set(f"Song: {song_name}")
            if album_art_image:
                self.display_album_art(album_art_image)

            # Handle synchronized lyrics if available
            synchronized_lyrics = MediaInfoHandler.extract_synchronized_lyrics(file_path)
            if synchronized_lyrics:
                self.display_synchronized_lyrics(synchronized_lyrics)

    def display_album_art(self, image):
        if self.album_art_label:
            self.album_art_label.destroy()

        # Resize while maintaining aspect ratio
        image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(image)
        self.album_art_label = tk.Label(self, image=photo)
        self.album_art_label.image = photo  # keep a reference!
        self.album_art_label.grid(row=1, column=0, padx=10, pady=10)

    def display_synchronized_lyrics(self, lyrics):
        # Logic to display the synchronized lyrics
        lyrics_text = '\n'.join([f"{time}: {text}" for time, text in lyrics])
        self.lyrics_text.delete('1.0', tk.END)
        self.lyrics_text.insert(tk.END, lyrics_text)

    def upload_lyrics_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("LRC Files", "*.lrc")])
        if file_path:
            self.lyric_file_info_var.set(f"Lyric File: {file_path}")  # Update lyric file info label
            self.load_lyrics_file(file_path)

    def set_download_path(self):
        download_path = filedialog.askdirectory()
        if download_path:
            self.download_path_info_var.set(f"Download Path: {download_path}")  # Update download path info label


    def load_lyrics_file(self, file_path):
        # Logic to load and parse the lyrics file
        try:
            with open(file_path, 'r') as file:
                lyrics_content = file.read()
                self.display_lyrics(lyrics_content)
        except IOError as e:
            messagebox.showerror("Error", f"Error opening file: {e}")

    def display_lyrics(self, lyrics):
        # Logic to display the lyrics
        self.lyrics_text.delete('1.0', tk.END)
        self.lyrics_text.insert(tk.END, lyrics)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricsSynchronizer(root)
    app.pack(expand=True, fill="both")
    root.mainloop()
