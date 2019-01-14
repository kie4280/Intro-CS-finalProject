from googleDrive import GoogleDriveApi, GoogleDriveApiException
import pprint
import re

COMMANDS=["cd", "ls", "signin", "signout", "download", "exit", ]

g = GoogleDriveApi()

def empty(x):
    if x==None:
        return False
    else:
        return True

print("Enter command or 'help' for a list of commands")
while True:
    user_in = input(g.pwd()+">")    
    argsF=re.findall(r"(?:^|\s)*(?:[\"\']+?([\s\w.-/\\]+)[\"\']+?|([\w.-/\\]+))(?:^|\s)*", user_in)
    if len(argsF)==0:
        continue
    command=argsF[0][1]        
    args=list()
    for a in range(1, len(argsF)):
        q1=argsF[a][0]!=''
        q0=argsF[a][1]!=''
        if q1 or q0:            
            args.append((argsF[a][0] if q1 else argsF[a][1], q1)) 
             #(str, bool) => (argument, isQuoted)

    # print(args)
    
    # download = re.search(r"download\s*([\w.-/\\]+)")
    if command == "cd":        
        try:
            if len(args)>0:                
                g.to_folder(args[0][0])            
            
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
    elif command == "help":
        printer=pprint.PrettyPrinter()        
        print(" ".join(COMMANDS))