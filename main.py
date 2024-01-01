import tkinter as tk

from modules.music_player import MusicPlayer
from modules.lyrics_synchronizer import LyricsSynchronizer

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Music Player with Lyrics")
        self.geometry("800x800")

        self.create_widgets()

    def create_widgets(self):
        # Menu Button Frame
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", pady=20)

        # Music Player Button
        self.music_player_button = tk.Button(button_frame, text="Music Player", command=lambda: self.show_view('music_player'))
        self.music_player_button.pack(side="left", padx=10)

        # Lyrics Synchronizer Button
        self.lyrics_synchronizer_button = tk.Button(button_frame, text="Lyrics Synchronizer", command=lambda: self.show_view('lyrics_synchronizer'))
        self.lyrics_synchronizer_button.pack(side="right", padx=10)

        # Initialize Music Player and Lyrics Synchronizer (hidden by default)
        self.music_player = MusicPlayer(self)
        self.lyrics_synchronizer = LyricsSynchronizer(self)

        # Default view
        self.current_view = None
        self.show_view('music_player')

    def show_view(self, view_name):
        # Hide the current view, if any
        if self.current_view:
            self.current_view.pack_forget()

        # Show the selected view
        if view_name == 'music_player':
            self.current_view = self.music_player
        elif view_name == 'lyrics_synchronizer':
            self.current_view = self.lyrics_synchronizer

        self.current_view.pack(fill="both", expand=True, pady=(0, 20))  # Add padding at the bottom

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
