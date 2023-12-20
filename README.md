# SoundSnuggler

<p align="center">
  <img src="/assets/sound_snuggler_logo.png" alt="SoundSnuggler Logo" width="50%">
</p>

SoundSnuggler is an innovative tool designed to enhance your music experience. It completes your MP3 files by automatically fetching animated album art from Apple Music, searching for song lyrics online, and synchronizing them with audio using advanced AI. This process creates enriched files with embedded Enhanced LRC (ELRC), offering a more immersive listening experience.

## Features

- **Automated Album Art Downloading:** Fetches and embeds animated album art from Apple Music into your MP3 files.
- **Lyrics Search & Synchronization:** Scours the internet for song lyrics and uses AI to synchronize these lyrics with your music tracks.
- **ELRC Embedding:** Enhances your music files with ELRC, allowing for synchronized lyric display as the song plays.

## Enhanced LRC Format (A2 Extension)

SoundSnuggler utilizes an advanced version of the Simple LRC Format, known as the Enhanced LRC Format (A2 Extension). This extension differs in two significant ways:

1. **Line Timestamps:** These indicate the end of the previous word, enabling LRC players to determine the duration of each word and the timing for the next line display.
2. **Word Time Tag Format:** Incorporates tags in the `<mm:ss.xx>` format for precise synchronization.

## Getting Started

To run SoundSnuggler, follow these simple steps:

```bash
pipenv install
pipenv shell

pipenv run python ./main.py

or

py ./main.py
```

## Roadmap (TODO)

- **Enhanced Transcription Accuracy:** Investigate [stable-ts](https://github.com/jianfch/stable-ts) for improved timestamped transcription in ELRC lyrics.
- **Speaker Diarization Integration:** Explore combining Whisper's capabilities with speaker diarization tools for complex audio files. This integration would help in identifying not only the timing of the words but also the speaker, particularly in songs with multiple vocalists. More details can be found in this [discussion on Hugging Face](https://huggingface.co/spaces/openai/whisper/discussions/29).
- **Animated Album Art Integration:** Implement functionality to use the [Apple Music Animated Artwork Fetcher](https://github.com/bunnykek/Apple-Music-Animated-Artwork-Fetcher) for retrieving and embedding animated album art into songs.
