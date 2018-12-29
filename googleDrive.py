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
    folderMap=dict()
    c_folder=None
    cur_dir_list=["/"]
    root=None
    

    def __init__(self):
        
        
        if self.api_service == None:
            self.api_service = self.get_authenticated_service()

        self.c_folder=FolderStruct()
        self.list_content()
        self.root=self.c_folder       
        
    def get_authenticated_service(self):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', self.SCOPES)
            creds = tools.run_flow(flow, store)
        service = build(self.API_SERVICE_NAME, self.API_VERSION, http=creds.authorize(Http()))
        return service

    def list_content(self, trashed="false", **kwargs):
        

        print(self.c_folder.current_path[-1])
        results = self.api_service.files().list(q=u"'{0}' in parents and trashed={1}".format(self.c_folder.current_path[-1]["id"], trashed), orderBy="folder, name", pageSize=50, spaces="drive", fields="nextPageToken, files(id, name)", **kwargs).execute()
        items = results.get("files", None)     
        if items !=None:
            self.c_folder.add_child(items)   
        return items

    def pwd(self):
        str1=""
        for x in self.c_folder.current_path[1:]:
            str1+="/"+x["name"]
        return str1

    def to_folder(self, name):
        
        if name[0]=="/":
            ss=name.split("/")            
            pass
        elif name == "../":
            self.c_folder=self.c_folder.parent() if self.c_folder.parent()!=None else self.c_folder
        else:
            name=name.rstrip("/")
            for c in range(len(self.c_folder.child)):
                
                if self.c_folder.child[c].current_path[-1]["name"]==name:
                    self.c_folder=self.c_folder.child[c]
                    break
                    

    def get_path_list(self):
        return self.c_folder.current_path
       

    def IdToPath(self, Id):
        pass

    def pathToId(self, path):
        path=path.lstrip().rstrip()
        folds=path.split('/')
        folds=folds[1:]
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

    current_path=[{"id": "root", "name":"/"}]    
    child=[]
    parentFolder=None

    def __init__(self):
        self.child=list()

    def parent(self):
        return self.parentFolder 
   
    def add_child(self, folders):
        
        for folder in folders:
            child_=FolderStruct()
            # child_.parentFolder=self.parentFolder 
            l=list(self.current_path) 
            l.append(folder) 
            child_.current_path=l
            child_.parentFolder=self
            self.child.append(child_)
            pass

