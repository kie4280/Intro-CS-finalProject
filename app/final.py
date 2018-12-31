from googleDrive import GoogleDriveApi, GoogleDriveApiException
import pprint
import re
g = GoogleDriveApi()
while True:
    command = input(g.pwd()+">")
    cd_dir = re.match(r"\s*cd\s*[\"']*([\w./\s]+)[\"']*\s*$", command)
    ls_dir = re.match(r"\s*ls\s*$", command)
    if cd_dir != None:
        args = cd_dir.group(1)
        g.to_folder(args)
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
        
