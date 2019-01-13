import json
import cloudconvert
import threading
import time

class cloudConvert:
    
    apikey=None
    api=None
    process=None
    def __init__(self):
        j=json.load(open("client_secret.json"))
        try:
            apikey=j["cloud_convert"]["api_key"]
            api=cloudconvert.Api(apikey)
        except KeyError:
            raise CException(CException.NO_KEY)
    def createNewProcess(self, fromf, tof):
        pass
    def upload(self, videoURLs, fromf, tof):
        self.process=self.api.convert({"inputformat":fromf,
         "outputformat":tof, "input":"download", "files":videoURLs})

    def updatestatus(self):
        print(self.process["messages"])
        pass
        

    def download(self, url):
        pass
class statusChecker(threading.Thread):

    prevstat="convert"
    def __init__(self, name, ID, ConvertProcess, _callback):
        threading.Thread.__init__(self)
        self.threadID=ID
        self.name=name
        self.ConvertProcess=ConvertProcess
        self.callback=_callback

    def run(self):
        self.ConvertProcess.refresh()
        self.prevstat=self.ConvertProcess["messages"]
        while True:
            self.ConvertProcess.refresh()
            if self.ConvertProcess["messages"]!=self.prevstat:
                self.callback()


class CException(Exception):
    NO_KEY="No api key"
    CONVERT_ERROR="convert error"
    NO_TARGET="no target format"

c=cloudConvert()
