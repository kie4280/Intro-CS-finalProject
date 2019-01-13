import re
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import unquote
from itertools import chain


class Extractor:
    decipherFunc = None
    # funcNameReg = r";(\w*)\(\w*,[\"\']signature\"\s*,\s*[a-zA-Z0-9$]+" not correct    
    funcNameReg = [
        r'\bc\s*&&\s*d\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
        r'yt\.akamaized\.net/\)\s*\|\|\s*',
        r'.*?\s*c\s*&&\s*d\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\bc\s*&&\s*d\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(']

    sigFuncReg = r"(?x)(?:function\\s+%s|[{;,]\\s*%s\\s*=\\s*function|var" +\
        "\\s+%s\\s*=\\s*function)\\s*\\(([^)]*)\\)\\s*" +\
        "\\{([^}]+)\\}"
    ytplayer_configReg = r"ytplayer\.config\s=\s(.*)"
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
                result[i[0]] = i[1]
        return result

    def getVideoUrls(self, id):
        videoHTML = self._downloadWeb("https://www.youtube.com/watch?v=" + id)
        # videoHTML=self._downloadWeb("http://www.youtube.com/get_video_info?video_id=zjosQxz_b44")
        s = BeautifulSoup(videoHTML, "html.parser")
        videoURLs = list()
        target = list()
        results = dict()
        for s in s.find_all("script"):
            target = re.findall(self.ytplayer_configReg, s.text)
            if len(target) > 0:
                break

        ytplayer = self._matchBrack(target[0])
        # print(ytplayer)
        if ytplayer != "":
            j = json.loads(ytplayer)
            args = j["args"]
            self.basejsurl = "https://www.youtube.com" + \
                j["assets"]["js"].replace("\"", "")
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
                parameters = keymap.get("sparams", None).split(",")
                finalUrl = keymap.get(
                    "url", "")+"?"+"sparams="+keymap.get("sparams")+"&signature="
                if "s" in keymap:
                    fake_cipher = keymap.get("s")
                    if fake_cipher == None:
                        raise YouTubeError(YouTubeError.ERROR_1)
                    else:
                        finalUrl += self._decipher(fake_cipher)
                else:
                    finalUrl += keymap.get("signature", "")
                for par in parameters:
                    finalUrl += "&"+par+"="+keymap.get(par, "")

                results[keymap.get("itag")] = finalUrl

                pass
            # print(results)
            # print(self.basejsurl)
            # self._decipher("sdsk")

        return results

    def _decipher(self, fake_cipher):
        result = ""
        
        if self.decipherFunc == None:
            print(fake_cipher)
            basejs = self._downloadWeb(self.basejsurl)
            found = list()
            for i in range(len(self.funcNameReg)):
                found = re.findall(self.funcNameReg[i], basejs)
                if len(found) > 0:
                    break
            if len(found) == 0:
                raise YouTubeError(YouTubeError.ERROR_0)
            self.decipherFunc = found[0]
            print("evaluating")
            print(found[0])
            funcalls = re.findall(
                r'%s=function\(\w\){[a-z=\.\(\"\)]*;(.*);(?:.+)}' % self.decipherFunc, basejs)
            if len(funcalls) == 0:
                raise YouTubeError(YouTubeError.DICPH_BODY)
            funcalls=funcalls[0].split(";")
            objname = funcalls[0].split(".")[0]
            funcbases = self._get_transform_func(basejs, objname)
            funcmap = self._mapper(funcbases)

            result = self._apply_func([s for s in fake_cipher], funcmap,
            [self._get_func_param(p) for p in funcalls])

            print("complete")

            print(result)
        return result

    def _get_transform_func(self, basejs, objname):
        pattern = r'var %s={((?:.|\n)*?)};' % re.escape(objname)
        match = re.findall(pattern, basejs)
        print(match)

        if len(match) == 0:
            pass
        return match[0].replace("\n", " ").split(", ")

    def _apply_func(self, cipher, map, procedures):
        for procedure in procedures:
            fn, arg = procedure
            print(fn, arg)
            cipher = map[fn](cipher, int(arg))

        # print(cipher)
        return "".join(cipher)

    def _get_func_param(self, func):

        match = re.search(r'\w+\.(\w+)\(\w,(\d+)\)', func)
        if match != None:
            return(match.group(1), match.group(2))

    def _js2py(self, ):
        pass

    def _mapper(self, functions):

        mapping = dict()
        maps = (
            (r"(\w+?):function\(\w+\){\w\.reverse\(\)", self._reverse),
            (r"(\w+?):function\(.+?\){\w\.splice\(0,\w\)}", self._splice),
            (r"(\w+?):function\(.+?\){var\s\w=\w\[0\];\w\[0\]=\w\[\w\%\w.length\];\w\[\w\]=\w}", self._swap),
            (r"(\w+?):function\(.+?\){var\s\w=\w\[0\];\w\[0\]=\w\[\w\%\w.length\];\w\[\w\%\w.length\]=\w}", self._swap))

        for function in functions:
            for pattern, sol in maps:
                match = re.search(pattern, function)
                if match != None:
                    mapping[match.group(1)] = sol
        if len(mapping) == 0:
            raise YouTubeError(YouTubeError.REGEX_NOT_MATCH)
        return mapping

    def _splice(self, arr, b):
        # return arr[:b] + arr[b*2:]
        return arr[b:]

    def _reverse(self, arr, b):
        return arr[::-1]

    def _swap(self, arr, b):
        a = b % len(arr)
        return list(chain([arr[a]], arr[1:a], [arr[0]], arr[a+1:]))


class YouTubeError(Exception):
    ERROR_0 = "Error finding decipher function"
    ERROR_1 = "Error deciphering code"
    ERROR_2 = "Error downloading file"
    DICPH_NAME = "Unable to find decipher function name"
    DICPH_BODY = "Unable to find function body"
    REGEX_NOT_MATCH = "Could not translate javascript function to python"
    pass


k = Extractor()
print(k.getVideoUrls("nfWlot6h_JM"))
# print(k._splice([1,2,3,4,5,6,7,8,9], 4))
