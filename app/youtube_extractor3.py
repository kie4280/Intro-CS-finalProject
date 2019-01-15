import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re

youtube_url = "https://www.youtube.com/watch?v="
kej_url = "http://kej.tw/flvretriever/"
video_info_url = ""

headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", "Accepted-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ny;q=0.6,gu;q=0.5", "Host": "kej.tw", "Connection": "keep-alive",
    "Content-type": "application/x-www-form-urlencoded"}


class YouTubeExtractor:

    def _downloadWeb(self, url):

        s = requests.get(url, headers=headers)
        s.close()

        return s.text

    def _submit_data(self, targeturl, Data):
        response = requests.post(
            targeturl, headers=headers, data=Data, files=Data)
        response.close()
        return response.text

    def get_video(self, videoID):
        url = quote(youtube_url+videoID)
        kej_b1 = BeautifulSoup(self._downloadWeb(
            kej_url+"youtube.php?videoUrl="+url), "html.parser")
        video_info_url = kej_b1.find_all(attrs={"id": "linkVideoInfoURL"})[0]
        video_info_url = re.search(
            r"href=\"(.*)\"\s", str(video_info_url)).group(1)
        print(video_info_url)
        get_video_info = self._downloadWeb(video_info_url)
        self._submit_data(kej_url+"index.php", {""})


y = YouTubeExtractor()
# print(y._downloadWeb(kej_url+"index.php"))
y.get_video("s44whB4w1Jw")
