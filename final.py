from googleDrive import GoogleDriveApi
import pprint, re
g = GoogleDriveApi()
while True:
    command=input(g.pwd()+">")
    cd_dir=re.match(r"\s*cd\s*([\w./]+)\s*$",command)
    ls_dir=re.match(r"\s*ls\s*$",command)
    if cd_dir!= None:
        args=cd_dir.group(1)    
        g.to_folder(args)
    if ls_dir != None:
        pprint.PrettyPrinter(indent=2).pprint(g.list_content())
    