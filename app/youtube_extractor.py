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

        fields = re.split(r"[&?]", videoURL)
        result = dict()
        for key in fields:
            i = key.split("=")
            if len(i) == 2 and i[1] != "":
                result[i[0]] = i[1]
        return result

    def _getTitle(self, videoID):
        video_info = self._downloadWeb(
            "http://www.youtube.com/get_video_info?video_id="+videoID)
        video_info = unquote(unquote(video_info)).replace(
            "\\u0026", "").replace("+", " ")
        # print(video_info)
        fail = re.findall(
            r"&status=fail|errorcode|reason=Invalid parameters", video_info)

        titles = re.findall(r'&title=(.*?)&', 
        unquote(unquote(video_info)).replace("\\u0026", "").replace("+", " "))

        if len(titles) == 0 and len(fail) == 0:
            raise YouTubeError(YouTubeError.TITLE_ERROR)
        if len(titles) == 0 and len(fail) > 0:
            raise YouTubeError(YouTubeError.MAL_FORMED_VIDEO_ID)
        # print(titles)
        return titles[0]

    def getVideoUrls(self, id):
        videoHTML = self._downloadWeb("https://www.youtube.com/watch?v=" + id)

        # print(videoHTML)
        s = BeautifulSoup(videoHTML, "html.parser")
        title = self._getTitle(id)

        videoURLs = list()
        target = list()
        results = dict()
        for s in s.find_all("script"):
            target = re.findall(self.ytplayer_configReg, s.text)
            if len(target) > 0:
                break
        else:
            raise YouTubeError(YouTubeError.YT_CONFIG_ERROR)
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

                finalUrl = keymap.get(
                    "url", "")+"?signature="
                if "s" in keymap:
                    fake_cipher = keymap.get("s")
                    if fake_cipher == None:
                        raise YouTubeError(YouTubeError.DECIPHER_ERROR)
                    else:
                        finalUrl += self._decipher(fake_cipher)
                else:
                    finalUrl += keymap.get("signature", "")
                for key, value in keymap.items():
                    finalUrl += "&"+key+"="+value

                results[keymap.get("itag")] = finalUrl

                pass
            # print(results)
            # print(self.basejsurl)
            # self._decipher("sdsk")
            print("Success!")

        return title, results

    def _decipher(self, fake_cipher):
        result = ""

        if self.decipherFunc == None:
            # print(fake_cipher)
            basejs = self._downloadWeb(self.basejsurl)

            for i in range(len(self.funcNameReg)):
                found = re.search(self.funcNameReg[i], basejs)
                if found != None:
                    break
            else:
                raise YouTubeError(YouTubeError.DICPH_NAME)
            decipherFuncName = found.group("sig")
            print("evaluating")

            funcalls = re.findall(
                r'%s=function\(\w\){[a-z=\.\(\"\)]*;(.*);(?:.+)}' %
                decipherFuncName, basejs)
            if len(funcalls) == 0:
                raise YouTubeError(YouTubeError.DICPH_BODY)
            funcalls = funcalls[0].split(";")
            objname = funcalls[0].split(".")[0]
            funcbases = self._get_transform_func(basejs, objname)
            funcmap = self._mapper(funcbases)

            result = self._apply_decipher_func(
                fake_cipher, funcmap, [self._get_func_param(p) for p in funcalls])

            self.decipherFunc = self._apply_decipher_func

        else:
            result = self.decipherFunc(fake_cipher)
        return result

    def _get_transform_func(self, basejs, objname):
        pattern = r'var %s={((?:.|\n)*?)};' % re.escape(objname)
        match = re.findall(pattern, basejs)
        # print(match)

        if len(match) == 0:
            pass
        return match[0].replace("\n", " ").split(", ")

    def _apply_decipher_func(self, cipher, map=None, procedures=None):
        self.decipher_procedures = procedures if procedures != None else self.decipher_procedures
        self.funcCallMaps = map if map != None else self.funcCallMaps
        if self.decipher_procedures == None or self.funcCallMaps == None:
            raise YouTubeError(YouTubeError.ARGUMENT_ERROR)
        for procedure in self.decipher_procedures:
            fn, arg = procedure
            # print(fn, arg)
            cipher = self.funcCallMaps[fn](cipher, int(arg))

        # print(cipher)
        return "".join(cipher)

    def _get_func_param(self, func):

        match = re.search(r'\w+\.(\w+)\(\w,(\d+)\)', func)
        if match != None:
            return(match.group(1), match.group(2))

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
            raise YouTubeError(YouTubeError.TRANSLATE_ERROR)
        return mapping

    def _splice(self, arr, b):
        # print(arr)
        # print(arr[:b] + arr[b*2:])
        return arr[:b] + arr[b*2:]
        # return arr[b:]

    def _reverse(self, arr, b):
        return arr[::-1]

    def _swap(self, arr, b):
        a = b % len(arr)
        return list(chain([arr[a]], arr[1:a], [arr[0]], arr[a+1:]))


class YouTubeError(Exception):
    DECIPHER_ERROR = "Error deciphering code"
    DOWNLOAD_ERROR = "Error downloading file"
    DICPH_NAME = "Unable to find decipher function name"
    DICPH_BODY = "Unable to find function body"
    TRANSLATE_ERROR = "Could not translate javascript function to python"
    ARGUMENT_ERROR = "Too few arguments to decipher code"
    MAL_FORMED_VIDEO_ID = "Video url is incorrect or something bad has happened"
    YT_CONFIG_ERROR = "No ytplater config"
    TITLE_ERROR = " Unable to get title"
    pass


# k = Extractor()
# print(k.getVideoUrls("Ubx6wqxocyU"))
# print(k._splice([1,2,3,4,5,6,7,8,9], 4))
