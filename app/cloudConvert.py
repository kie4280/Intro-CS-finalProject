import json
import cloudconvert
import threading
import time
from formats import _formats
import requests
import json
from urllib.parse import quote
from pathlib import Path
import sys, os

# test_url="https://r3---sn-un57en7l.googlevideo.com/videoplayback?sparams=clen,dur,ei,expire,gir,id,ip,ipbits,itag,lmt,mime,mm,mn,ms,mv,pl,ratebypass,requiressl,source&ratebypass=yes&lmt=1537596754559668&expire=1547490127&mime=video/mp4&id=o-APMraSM2HJ6ruE7HiMjeZibNCIU-PyxpO6tqwGlX9TNw&dur=238.422&gir=yes&c=WEB&ip=140.113.139.244&clen=18570777&fvip=3&ei=7348XLiGIY7b4QK5oongCw&requiressl=yes&itag=18&source=youtube&key=cms1&ipbits=0&pl=17&signature=06BD82D6FE3622777B097F56E6002869B9E66735.68BE9A37B4066C31BE42D263AF11FB456B45D641&title=Bad+Blood+-+Taylor+Swift+-+ONE+TAKE%21%21+Macy+Kate+%26+Ben+Kheng+Cover&redirect_counter=1&cm2rm=sn-oju0-u2xl7l&req_id=2dbb706e1a6a3ee&cms_redirect=yes&mm=29&mn=sn-un57en7l&ms=rdu&mt=1547468811&mv=m"


class cloudConvert:

    apikey = None
    api = None
    process = None
    checker = None
    fileName = "a"
    extension = ""
    des = None
    _callback = None

    def __init__(self):
        j = json.load(open("apikey.json"))
        try:
            self.apikey = j["cloud_convert"]["api_key"]
            self.api = cloudconvert.Api(self.apikey)
        except KeyError:
            raise CException(CException.NO_KEY)

    def convert(self, videoURLs, fromf, tof, videoID):
        # self._get_download()
        pass

    def _try_upload(self, videoURLs, fromf, tof, videoID, out_filename):
        self.extension = tof
        self.videoID = videoID
        self.out_filename = out_filename
        self.process = self.api.convert({"inputformat": fromf,
                                         "outputformat": tof, "input": "download", "file": videoURLs,
                                         "filename": self.videoID+"."+fromf,
                                         "save": "true"})
    def upload(self, videoURLs, fromf, tof, videoID, out_filename):
        self._try_upload(videoURLs, fromf, tof, videoID, out_filename)
        try:
            self.process.refresh()
        except:
            self._try_upload(videoURLs, fromf, tof, videoID, out_filename) #retry in case something odd happened
        checker = statusChecker("status", 1, self.videoID+"."+tof, out_filename, self.process, {
                                "update": self._updatestatus, "complete": self._get_download, "download": self._callback})
        checker.run()

    prevlen=0
    def _updatestatus(self):
        
        a=self.process["message"]
        if a=="Conversion finished!":
            sys.stdout.write("\r"+" "*self.prevlen+"\r")
            sys.stdout.flush()
            print(a)
        else:
            sys.stdout.write("\r"+" "*self.prevlen)
            sys.stdout.flush()
            sys.stdout.write("\r"+a)
            sys.stdout.flush()
            self.prevlen=len(a)        
        pass

    def registerCallback(self, func, filename="", des=None):
        self._callback = func
        self.des = des

    def _get_download(self):
        # if self._callback != None:
        #     self._callback({"filename": self.videoID, "des": self.des})
        # for i in self.list_previous_conversions():
        #     s = i["output"]["filename"]
        #     s = s[0:s.find(".")]
        #     if s==self.videoID:
        #         f = open(self.videoID + self.extension, 'wb')
        #         f.write(requests.get("https://" + i["output"]["url"]).text)
        # else:
        #     self.process.download(self.videoID + self.extension)
        folder=Path("tmp")
        if not folder.exists():
            folder.mkdir()
        self.process.download("tmp/"+self.videoID + "." + self.extension)

    def list_previous_conversions(self):
        videos = list()
        headers = {"Authorization": "Bearer " + self.apikey}
        l = requests.get(
            "https://api.cloudconvert.com/processes", headers=headers)
        l.close()

        for item in json.loads(l.text):
            print(quote("https://api.cloudconvert.com/processes/"+item["id"]))
            d = requests.get(
                "https://api.cloudconvert.com/processes/"+item["id"])
            print(d.text)
            videos.append(json.loads(d.text))
        d.close()
        return videos


class statusChecker(threading.Thread):

    prevstat = "convert"
    _callbacks = None

    def __init__(self, name, ID, in_filename, out_filename, ConvertProcess, _callbacks):
        threading.Thread.__init__(self)
        self.threadID = ID
        self.name = name
        self.in_filename = in_filename
        self.out_filename = out_filename
        self._callbacks = _callbacks
        self.ConvertProcess = ConvertProcess
        self.update = _callbacks["update"]
        self.finished = _callbacks["complete"]
        self.download = _callbacks["download"]

    def run(self):
        self.ConvertProcess.refresh()
        self.prevstat = self.ConvertProcess["message"]
        while True:
            self.ConvertProcess.refresh()

            if self.ConvertProcess["message"] != self.prevstat:
                if self.update != None:
                    self.update()
                self.prevstat = self.ConvertProcess["message"]

            if self.ConvertProcess["message"] == "Conversion finished!":
                if self.finished != None:
                    self.finished()
                self.prevstat = "convert"
                break
            else:
                time.sleep(1)
        while True:
            print("downloading... ", end="")
            myfile = Path("tmp/" + self.in_filename)
            if myfile.is_file():
                func = self._callbacks["download"]
                print("downloaded")
                if func != None:
                    func({"local_filename": self.in_filename, "remote_filename": self.out_filename})
                break
            else:
                time.sleep(0.3)


class CException(Exception):
    NO_KEY = "No api key"
    CONVERT_ERROR = "convert error"
    NO_TARGET = "no target format"


# c = cloudConvert()
# c.list_previous_conversions()
# c.upload(test_url, "mp4", "mp3")
