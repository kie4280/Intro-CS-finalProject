import json
import cloudconvert
import threading
import time
from formats import _formats

# test_url="https://r3---sn-un57en7l.googlevideo.com/videoplayback?sparams=clen,dur,ei,expire,gir,id,ip,ipbits,itag,lmt,mime,mm,mn,ms,mv,pl,ratebypass,requiressl,source&ratebypass=yes&lmt=1537596754559668&expire=1547490127&mime=video/mp4&id=o-APMraSM2HJ6ruE7HiMjeZibNCIU-PyxpO6tqwGlX9TNw&dur=238.422&gir=yes&c=WEB&ip=140.113.139.244&clen=18570777&fvip=3&ei=7348XLiGIY7b4QK5oongCw&requiressl=yes&itag=18&source=youtube&key=cms1&ipbits=0&pl=17&signature=06BD82D6FE3622777B097F56E6002869B9E66735.68BE9A37B4066C31BE42D263AF11FB456B45D641&title=Bad+Blood+-+Taylor+Swift+-+ONE+TAKE%21%21+Macy+Kate+%26+Ben+Kheng+Cover&redirect_counter=1&cm2rm=sn-oju0-u2xl7l&req_id=2dbb706e1a6a3ee&cms_redirect=yes&mm=29&mn=sn-un57en7l&ms=rdu&mt=1547468811&mv=m"

class cloudConvert:
    
    apikey=None
    api=None
    process=None
    checker=None
    fileName="a"
    extension=""
    des=None
    _callback=None
    def __init__(self):
        j=json.load(open("apikey.json"))        
        try:
            apikey=j["cloud_convert"]["api_key"]
            self.api=cloudconvert.Api(apikey)
        except KeyError:
            raise CException(CException.NO_KEY)
    def convert(self, videoURLs, fromf, tof, videoID):
        
        pass
    def _upload(self, videoURLs, fromf, tof, videoID):
        self.extension = fromf
        self.videoID=videoID
        self.process=self.api.convert({"inputformat":fromf,
        "outputformat":tof, "input":"download", "file":videoURLs, 
        "filename":self.fileName+"."+fromf})
        checker=statusChecker("status", 1, self.process, self._updatestatus, 
        self._download)
        checker.run()

    def _updatestatus(self):
        print(self.process["message"] + "...")
        pass
        
    def registerCallback(self, func, filename="converted.mp3", des=None):
        self._callback=func
        self.des=des

    def _download(self):
        if self._callback != None:
            self._callback({"filename":self.videoID, "des":self.des})
        self.process.download(self.videoID + self.extension)
    

class statusChecker(threading.Thread):

    prevstat="convert"
    def __init__(self, name, ID, ConvertProcess, _callback_update, 
    _callback_download):
        threading.Thread.__init__(self)
        self.threadID=ID
        self.name=name
        self.ConvertProcess=ConvertProcess
        self.update=_callback_update
        self.finished=_callback_download

    def run(self):
        self.ConvertProcess.refresh()
        self.prevstat=self.ConvertProcess["message"]
        while True:
            self.ConvertProcess.refresh()
            
            if self.ConvertProcess["message"]!=self.prevstat:
                self.update()
                self.prevstat=self.ConvertProcess["message"]
                
            if self.ConvertProcess["message"]=="Conversion finished!":
                self.finished()
                break
            else:
                time.sleep(1)


class CException(Exception):
    NO_KEY="No api key"
    CONVERT_ERROR="convert error"
    NO_TARGET="no target format"

# c=cloudConvert()
# c.upload(test_url, "mp4", "mp3")
