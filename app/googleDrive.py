import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools
import pprint


class GoogleDriveApi:
    # The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
    # the OAuth 2.0 information for this application, including its client_id and
    # client_secret.
    CLIENT_SECRETS_FILE = "client_secret.json"

    # This access scope grants read-only access to the authenticated user's Drive
    # account.
    SCOPES = ['https://www.googleapis.com/auth/drive']
    API_SERVICE_NAME = 'drive'
    API_VERSION = 'v3'
    api_service = None
    folderMap = dict()
    c_folder = None
    cur_dir_list = ["/"]
    root = None

    def __init__(self):

        self.c_folder = FolderStruct()        
        self.root = self.c_folder
    
    def signin(self):
        self.api_service = self.get_authenticated_service()
        self.list_content()
        pass

    def signout(self):
        store = file.Storage('token.json')
        store.locked_delete()
        self.api_service=None
        self.c_folder=FolderStruct()
        self.root=self.c_folder
        pass

    def get_authenticated_service(self):
        store = file.Storage('token.json')
        creds = store.get()
        
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(
                'client_secret.json', self.SCOPES)
            creds = tools.run_flow(flow, store)
        service = build(self.API_SERVICE_NAME, self.API_VERSION,
                        http=creds.authorize(Http()))
        return service

    def list_content(self, trashed="false", **kwargs):

        if self.api_service == None:
            raise GoogleDriveApiException(GoogleDriveApiException.NOT_SIGNIN_EXP)
        print(self.c_folder.current_path[-1])
        results = self.api_service.files().list(q=u"'{0}' in parents and trashed={1}".format(
            self.c_folder.current_path[-1]["id"], trashed), orderBy="folder, name", pageSize=50, spaces="drive", fields="nextPageToken, files(id, name)", **kwargs).execute()
        items = results.get("files", None)
        if items != None:
            self.c_folder.add_child(items)
        return items

    def pwd(self):
        str1 = "/"
        c = self.c_folder.current_path[1:]
        for x in range(len(c)):
            str1 += ("/" if x > 0 else "")+c[x]["name"]
        return str1

    def to_folder(self, name):

        print("name1", name)

        if name=="":
            return      
        
        elif name[0] == "/":            
            self.c_folder=self.root  
              
        if name == "../":
            self.c_folder = self.c_folder.parent() if \
            self.c_folder.parent() != None else self.c_folder
        elif name!="/":
            name = name.rstrip("/").lstrip("/")
            names=name.split("/")
            # print(names)
        
            for c in self.c_folder.child:
                
                if c.current_path[-1]["name"] == names[0]:
                    self.c_folder = c              
                    if name.find("/")!=-1:      
                        self.to_folder(name[name.find("/")+1:])
                    break
            else:
                raise GoogleDriveApiException(GoogleDriveApiException.NO_DIR)
                    
        self.list_content()
                

    def get_path_list(self):
        return self.c_folder.current_path

    def IdToPath(self, Id):
        pass

    def pathToId(self, path):
        path = path.lstrip().rstrip()
        folds = path.split('/')
        folds = folds[1:]
        if len(folds) == 1:
            return "root"
        elif len(folds) > 1:
            for folder in folds:
                id = self.folderMap.get(folder, None)
                if id == None:
                    items = self.list_content(self.current_dir_ID)

            return id

    def createFolder(self, des, name):
        file_metadata = {"name": name,
                         "mimeType": "application/vnd.google-apps.folder"}
        exec = self.api_service.files().create(body=file_metadata, fields="id")\
            .execute()
        print(exec.get("id"))

    def createFile(self, des, file):
        file1 = MediaFileUpload("client_secret.json", mimetype="text/json")
        pass


class FolderStruct:

    current_path = [{"id": "root", "name": "/"}]
    child = []
    parentFolder = None

    def __init__(self):
        self.child = list()

    def parent(self):
        return self.parentFolder
    
    def add_child(self, folders):

        for folder in folders:
            child_ = FolderStruct()
            # child_.parentFolder=self.parentFolder
            l = list(self.current_path)
            l.append(folder)
            child_.current_path = l
            child_.parentFolder = self
            self.child.append(child_)
            pass

class GoogleDriveApiException(Exception):

    NOT_SIGNIN_EXP="You are not signed in"
    NO_DIR="No such directory"
