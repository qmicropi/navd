# wavedown
A simple single-song downloader with a simple auto 16:9 thumbnail into 1:1 cropper, metadata embed and search by song's name option.
Written in python, it uses YT-DLP and YTMUSICAPI as its search and download engines.

---

### YT-DLP and FFMPEG are CRUCIAL for it to run.
Add them to your path before running wavedown.

Wavedown is a simple single-song downloader.
It automatically crops the thumbnail into a 1:1 square, so it will look good in most of music players.
It can download in most of the formats, though m4a is recommended as it being on the YouTube server (which means no conversion after download) and program being able to put cover in it using ffmpeg command.
MP3 will work as well.
> Opus and similar containers will fail, they are not recommended.

If you want to report issues, go to [Github Issues](<https://www.github.com/qmicropi/wavedown/issues>)
> README.md not finished, may cover more information further on.
