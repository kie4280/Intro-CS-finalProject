from googleDrive import GoogleDriveApi, GoogleDriveApiException
import pprint
import re
g = GoogleDriveApi()
while True:
    user_in = input(g.pwd()+">")    
    args=re.findall(r"(?:^|\s)*(?:[\"\']+?([\s\w.-/\\]+)[\"\']+?|([\w.-/\\]+))(?:^|\s)*", user_in)
    command=args[0]
    # args=args[1:]
    print(args)
    cd_dir = re.search(r"cd\s*[\"']*([\w./\s]+)[\"']*\s*$", user_in)
    ls_dir = re.search(r"ls\s*$", user_in)
    # download = re.search(r"download\s*([\w.-/\\]+)")
    if cd_dir != None:
        args = cd_dir.group(1)
        try:
            g.to_folder(args)
        except GoogleDriveApiException as e:            
            if e.args[0]==GoogleDriveApiException.NO_DIR:
                print("No such directory!!")
    elif ls_dir != None:
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
        