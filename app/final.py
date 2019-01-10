from googleDrive import GoogleDriveApi, GoogleDriveApiException
import pprint
import re
g = GoogleDriveApi()
while True:
    user_in = input(g.pwd()+">")    
    # args=re.findall(r"[\^\s]*[\"\']*([\w.-/\\]+)[\"\']*[\s\$]*", user_in)
    args=re.findall(r"^|[\s\"\']*([\w.-/\\]+)[\"\']*(?=\s+|$)", user_in)
    command=args[0]
    # args=args[1:]
    print(args)
    cd_dir = re.match(r"\s*cd\s*[\"']*([\w./\s]+)[\"']*\s*$", user_in)
    ls_dir = re.match(r"\s*ls\s*$", user_in)
    if cd_dir != None:
        args = cd_dir.group(1)
        try:
            g.to_folder(args)
        except GoogleDriveApiException as e:            
            if e.args[0]==GoogleDriveApiException.NO_DIR:
                print("No such directory!!")
    if ls_dir != None:
        try:
            pprint.PrettyPrinter(indent=2).pprint(g.list_content())
        except GoogleDriveApiException as e:
            if e.args[0]==GoogleDriveApiException.NOT_SIGNIN_EXP:
                print("You are not signed in. To sign in type the command 'signin'")
    if command == "exit":
        exit()
    elif command == "signin":
        g.signin()
    elif command == "signout":
        g.signout()
        