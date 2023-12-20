import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import syncedlyrics
from .media_info_handler import MediaInfoHandler

class LyricsSynchronizer(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.album_art_label = None
        self.max_image_size = (200, 200)
        self.default_album_art = Image.new('RGB', self.max_image_size, color='grey')

        self.album_info_var = tk.StringVar()
        self.download_path_info_var = tk.StringVar()

        self.create_widgets()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def create_widgets(self):
        self.album_art_frame = tk.Frame(self)
        self.album_art_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        self.display_album_art(self.default_album_art, self.album_art_frame)

        control_frame = tk.Frame(self)
        control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        control_frame.grid_columnconfigure(0, weight=1)

        upload_button_frame = tk.Frame(control_frame)
        upload_button_frame.grid(row=0, column=0, sticky="w")

        self.upload_music_button = tk.Button(upload_button_frame, text="Upload Music File", command=self.upload_music_file)
        self.upload_music_button.grid(row=0, column=0, padx=5, pady=5)

        self.set_download_path_button = tk.Button(upload_button_frame, text="Set Download Path", command=self.set_download_path)
        self.set_download_path_button.grid(row=1, column=0, padx=5, pady=5)

        info_label_frame = tk.Frame(control_frame)
        info_label_frame.grid(row=1, column=0, sticky="ew")

        tk.Label(info_label_frame, textvariable=self.album_info_var).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(info_label_frame, textvariable=self.download_path_info_var).grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.lyrics_text = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.lyrics_text.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

    def display_album_art(self, image, parent_frame):
        if self.album_art_label:
            self.album_art_label.destroy()

        image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.album_art_label = tk.Label(parent_frame, image=photo)
        self.album_art_label.image = photo
        self.album_art_label.pack()

    def upload_music_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3"), ("FLAC Files", "*.flac")])
        if file_path:
            try:
                song_name, album_art_image = MediaInfoHandler.get_song_info(file_path)
                self.album_info_var.set(f"Song: {song_name}")
                if album_art_image:
                    self.display_album_art(album_art_image, self.album_art_frame)

                self.fetch_lyrics(song_name, '')  # Assuming artist name is not available
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while processing the music file: {e}")

    def fetch_lyrics(self, track_name, artist_name):
        try:
            lrc = syncedlyrics.search(f"{track_name} {artist_name}")
            if lrc:
                self.display_lyrics(lrc)
            else:
                messagebox.showinfo("Info", "Lyrics not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def set_download_path(self):
        download_path = filedialog.askdirectory()
        if download_path:
            self.download_path_info_var.set(f"Download Path: {download_path}")

    def display_lyrics(self, lyrics):
        self.lyrics_text.delete('1.0', tk.END)
        self.lyrics_text.insert(tk.END, lyrics)

if __name__ == "__main__":
    root = tk.Tk()
    app = LyricsSynchronizer(root)
    app.pack(expand=True, fill="both")
    root.mainloop()
