from googleDrive import GoogleDriveApi, GoogleDriveApiException
import pprint
import re
from youtube_extractor import YouTubeError, Extractor
from cloudConvert import cloudConvert
from formats import _formats

COMMANDS = ["cd", "ls", "signin", "signout", "download", "exit", ]

drive = GoogleDriveApi()
yt = Extractor()
converter = cloudConvert()


def empty(x):
    if x == None:
        return False
    else:
        return True

acceptable_range = [(5, 78), 139, 140, 141, 256, 258, 325, 328, 171, 172, 249,
                    250, 251]


def get_candidates(itags):
    keys = itags.keys()
    suitable=list()
    for key in keys:
        if ((int(key) in acceptable_range) or
                (int(key) >= acceptable_range[0][0] and int(key) <= acceptable_range[0][1])):
            suitable.append(key)

    return suitable

def download_complete(kwargs):
    local_filename=kwargs["local_filename"]
    remote_filename=kwargs["remote_filename"]
    print("download_complete called")
    drive.createFile(local_filename, remote_filename)

def download(videoID, filename=None):
    converter.registerCallback(download_complete)
    if not drive.isSignedin():
        print("Not signed in yet")
        return
    try:    
        title, itags = yt.getVideoUrls(videoID)
    except YouTubeError as e:
        print(e.with_traceback.value)
        return 
    out_format="mp3"
    candidates = get_candidates(itags)
    filename = filename if filename != None else title+"."+out_format
    if len(candidates)==0:
        print("Sorry, this seems to be a no sound video")
        return 
    converter.upload(itags[candidates[0]], _formats[candidates[0]]["ext"], 
    out_format, videoID, filename)
    

print("Enter command or 'help' for a list of commands")
while True:
    user_in = input(drive.pwd()+">")
    argsF = re.findall(
        r"(?:^|\s)*(?:[\"\']+?([\s\w.\-_/\\]+)[\"\']+?|([\w.\-_/\\]+))(?:^|\s)*", user_in)
    if len(argsF) == 0:
        continue
    command = argsF[0][1]
    args = list()
    for a in range(1, len(argsF)):
        q1 = argsF[a][0] != ''
        q0 = argsF[a][1] != ''
        if q1 or q0:
            args.append((argsF[a][0] if q1 else argsF[a][1], q1))
            # (str, bool) => (argument, isQuoted)

    # print(args)

    # download = re.search(r"download\s*([\w.-/\\]+)")
    if command == "cd":
        try:
            if len(args) > 0:
                drive.to_folder(args[0][0])

        except GoogleDriveApiException as e:
            if e.args[0] == GoogleDriveApiException.NO_DIR:
                print("No such directory!!")
    elif command == "ls":
        try:
            pprint.PrettyPrinter(indent=2).pprint(drive.list_content())
        except GoogleDriveApiException as e:
            if e.args[0] == GoogleDriveApiException.NOT_SIGNIN_EXP:
                print("You are not signed in. To sign in type the command 'signin'")
    elif command == "mkdir":
        drive.createFolder(args[0][0])
    elif command == "download":
        if len(args) == 2:
            download(args[0][0], args[1][0])
        elif len(args) == 1:
            download(args[0][0])
        else:
            print("command with too few arguments")
    elif command == "upload":
        drive.createFile(args[0][0], args[0][0])
    elif command == "exit":
        exit()
    elif command == "signin":
        drive.signin()
    elif command == "signout":
        drive.signout()
    elif command == "help":
        printer = pprint.PrettyPrinter()
        print(" ".join(COMMANDS))
    else:
        print("Unknown command '%s'" % command)
