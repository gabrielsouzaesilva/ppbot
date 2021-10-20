from re import search
import youtube_dl
import requests
import discord

YDL_OPTIONS = {'format': 'bestaudio'}

class MusicYTB():
    def get_ffmpeg_url(self, url):
        ydl = youtube_dl.YoutubeDL(YDL_OPTIONS)
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        del ydl
        return (url2)

    def search_url(self, query:str):
        search_url = f"https://www.youtube.com/results?search_query={query}"
        req = requests.get(search_url)
        http_text = req.text

        # Find video url in http
        idx = http_text.find('watch?v')
        video_url = ""

        while True:
            char = http_text[idx]
            if (char == '"'):
                break
            video_url += char
            idx += 1

        video_url = f"https://www.youtube.com/{video_url}"
        return (video_url)