import re
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import unquote
# from js2py.internals import seval
import js2py

class Extractor:
    decipherFunc = None
    # funcNameReg = r";(\w*)\(\w*,[\"\']signature\"\s*,\s*[a-zA-Z0-9$]+" not correct
    funcNameReg=r'\bc\s*&&\s*d\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\('
    sigFuncReg=r"(?x)(?:function\\s+%s|[{;,]\\s*%s\\s*=\\s*function|var" +\
                    "\\s+%s\\s*=\\s*function)\\s*\\(([^)]*)\\)\\s*" +\
                    "\\{([^}]+)\\}"
    ytplayer_configReg=r"ytplayer\.config\s=\s(.*)"
    basejsurl = ""

    def _matchBrack(self, in_str):
        ln = 0
        rn = 0
        li = 0
        ri = 0
        for index in range(len(in_str)):
            if in_str[index] == '{':
                ln += 1
            elif in_str[index] == '}':
                rn += 1
                ri = index
            if rn == ln and ln != 0:
                return in_str[in_str.find("{"):ri+1]

        # r=re.findall(r"(?<!\\)\{(\\\{|\\\}|[^\{\}]|(?<!\\)\{.*(?<!\\)\})*(?<!\\)\}", in_str)
        # r.reverse()
        # for a in r:
        #     print(a)

    def _downloadWeb(self, url):
        headers = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}
        s = requests.get(url, headers=headers)
        s.close()

        return s.text

    def _getFields(self, videoURL):

        fields = re.split(r"[&\\?;]", videoURL)
        result = dict()
        for key in fields:
            i = key.split("=")
            if len(i) == 2:
                result[i[0]]=i[1]
        return result

    def getVideoUrls(self, id):
        videoHTML = self._downloadWeb("https://www.youtube.com/watch?v=" + id)
        s = BeautifulSoup(videoHTML, "html.parser")
        videoURLs=list()
        target=list()
        results=dict()
        for s in s.find_all("script"):
            target = re.findall(self.ytplayer_configReg, s.text)
            if len(target) > 0:
                break
                
        ytplayer = self._matchBrack(target[0])
        # print(ytplayer)
        if ytplayer != "":
            j = json.loads(ytplayer)
            args = j["args"]
            self.basejsurl =  "https://www.youtube.com" + j["assets"]["js"].replace("\"", "")
            adaptive_fmts = args.get("adaptive_fmts", None)
            fmts_encoded = args.get("url_encoded_fmt_stream_map", None)
            if adaptive_fmts != None:
                for x in adaptive_fmts.split(","):
                    videoURLs.append(unquote(unquote(x)))
            if fmts_encoded != None:
                for x in fmts_encoded.split(","):
                    videoURLs.append(unquote(unquote(x))) 
            for x in videoURLs:
                # print(x)
                keymap = self._getFields(x)
                # print(keymap)
                parameters=keymap.get("sparams", None).split(",")
                finalUrl=keymap.get("url", "")+"?"+"sparams="+keymap.get("sparams")+"&signature="
                if "s" in keymap:
                    fake_cipher=keymap.get("s")
                    if fake_cipher == None:
                        raise YouTubeError(YouTubeError.ERROR_1)
                    else:
                        finalUrl+=self._decipher(fake_cipher)
                else:
                    finalUrl+=keymap.get("signature", "")
                for par in parameters:
                    finalUrl+="&"+par+"="+keymap.get(par, "")                    

                results[keymap.get("itag")]=finalUrl
                
                pass
            # print(results)
            # print(self.basejsurl)
            # self._decipher("sdsk")
                
                
        return videoURLs 

    def _decipher(self, fake_cipher):
        result=""
        fake_cipher=fake_cipher.replace(".","")
        if self.decipherFunc == None:
            basejs=self._downloadWeb(self.basejsurl)
            found=re.findall(self.funcNameReg, basejs)
            if len(found) == 0:
                raise YouTubeError(YouTubeError.ERROR_0)
            self.decipherFunc=found[0]
            print("evaluating")
            print(found[0])
            func=re.findall(r'%s=function\(\w\){[a-z=\.\(\"\)]*;(.*);(?:.+)}' % self.decipherFunc, basejs)
            l=js2py.eval_js(basejs)
            print("complete")
            print(l)

            print(found)
        return result     

        
class YouTubeError(Exception):
    ERROR_0="Error finding decipher function"
    ERROR_1="Error deciphering code"
    ERROR_2="Error downloading file"
    pass


k = Extractor()
k.getVideoUrls("AOPMlIIg_38")
