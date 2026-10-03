# navd
A simple single-song downloader with a simple auto 16:9 thumbnail into 1:1 cropper, metadata embed and search by song's name option.
Written in python, it uses YT-DLP and YTMUSICAPI as its download and search engines.

---

### YT-DLP and FFMPEG are CRUCIAL for it to run. Add them to your path before running NAVD.

---

NAVD is a simple single-song downloader.

It's metadata focused, so your tracks will belong to real artists, and not just "Unknown".

It automatically crops the thumbnail into a 1:1 square, so it will look good in most of music players.

It can download in most of the formats, though m4a is recommended as it being on the YouTube server (which means no conversion after download) and program being able to put cover in it using ffmpeg command. MP3 will work as well though.
> [!WARNING]
> Opus and similar containers will fail, they aren't recommended.

> [!NOTE]
> ### COOKIES.
> Sometimes YouTube will require cookies. NAVD will auto-detect file named cookies.txt in the same directory.
>
> If you have issues with auto-detection, you may use the 'Add cookies.txt' button on top. It will add them to NAVD temp folder, so until PC restart, it should automatically fetch cookies.

If you want to report issues, go to [Github Issues](<https://www.github.com/qmicropi/wavedown/issues>)
> README.md not finished, may cover more information further on.

###### NAVD * 2026 * qmicropi
