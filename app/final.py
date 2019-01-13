from googleDrive import GoogleDriveApi, GoogleDriveApiException
import pprint
import re

g = GoogleDriveApi()

def empty(x):
    if x==None:
        return False
    else:
        return True
while True:
    user_in = input(g.pwd()+">")    
    args=re.findall(r"(?:^|\s)*(?:[\"\']+?([\s\w.-/\\]+)[\"\']+?|([\w.-/\\]+))(?:^|\s)*", user_in)
    if len(args)==0:
        continue
    command=args[0][1]    
    args_q=list(filter(empty, [q[0] if q[0]!='' else None for q in args[1:]]))
    args_nq=list(filter(empty, [q[1] if q[1]!='' else None for q in args[1:]]))
    print(args_q, args_nq)
    
    # download = re.search(r"download\s*([\w.-/\\]+)")
    if command == "cd":
        
        try:
            if len(args_nq)>0:
                g.to_folder(args_nq[0])
            elif len(args_q)>0:
                g.to_folder(args_q[0])
            
        except GoogleDriveApiException as e:            
            if e.args[0]==GoogleDriveApiException.NO_DIR:
                print("No such directory!!")
    elif command == "ls":
        try:
            pprint.PrettyPrinter(indent=2).pprint(g.list_content())
        except GoogleDriveApiException as e:
            if e.args[0]==GoogleDriveApiException.NOT_SIGNIN_EXP:
                print("You are not signed in. To sign in type the command 'signin'")

    elif command =="download":
        pass
    if command == "exit":
        exit()
    elif command == "signin":
        g.signin()
    elif command == "signout":
        g.signout()
        