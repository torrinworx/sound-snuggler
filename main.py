import tkinter as tk

from modules.music_player import MusicPlayer

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Music Player with Lyrics")
        self.geometry("800x600")

        self.music_player = MusicPlayer(self)
        self.music_player.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
