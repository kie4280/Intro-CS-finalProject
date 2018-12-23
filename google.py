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
    API_SERVICE = None
    current_dir="/"
    folderMap=dict()

    def __init__(self):
        if self.API_SERVICE == None:
            self.API_SERVICE = self.get_authenticated_service()

    def get_authenticated_service(self):
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', self.SCOPES)
            creds = tools.run_flow(flow, store)
        service = build(self.API_SERVICE_NAME, self.API_VERSION, http=creds.authorize(Http()))
        return service

    def list_content(self, id, trashed="false", **kwargs):
        results = self.API_SERVICE.files().list(q=u"'{0}' in parents and trashed={1}".format(id, trashed),\
        orderBy="folder, name", pageSize=50, spaces="drive", fields="nextPageToken, files(id, name)", **kwargs)\
        .execute()
        items = results.get("files", [])
        if len(items) > 0:
            for item in items:
                # self.addMap()
                pass

        return results
    
    def folder_list(self, path):
        pass
    
    def addMap(self, name, id):
        self.folderMap.get()
        pass
    


    def parsePath(self, path):
        path=path.lstrip().rstrip()
        folds=path.split('/')
        folds=folds[1:]
        if len(folds) == 1:
            return "root"
        elif len(folds) > 1:
            print(folds)



    def createFolder(self, des, name):
        file_metadata = {"name": name,
                         "mimeType": "application/vnd.google-apps.folder"}
        exec = self.API_SERVICE.files().create(body=file_metadata, fields="id")\
            .execute()
        print(exec.get("id"))

    def createFile(self, des, file):
        file1 = MediaFileUpload("client_secret.json", mimetype="text/json")
        pass


g = GoogleDriveApi()
pprint.PrettyPrinter(indent=2).pprint(g.list_content("root"))
g.parsePath("/roo/g")
# g.createFolder("fuck")
# g.createFile(open("client_secret.json"))
