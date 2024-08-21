import os
from typing import List, Protocol
from dotenv import load_dotenv
from flask import json
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import mimetypes
from pathlib import Path
import time

class StorageProtocol(Protocol):
    """StorageProtocol outlines methods for interacting with storage."""

    def upload_file(self, location_id: str, filepath: str) -> bool:
        pass

    def get_locations(self) -> List:
        pass


class WorkDrive:
    """WorkDrive class utilises the Zoho WorkDrive REST API.
    Implements StorageProtocol."""

    oauthlib_conn: OAuth2Session

    def __init__(self) -> None:
        """Initialise the WorkDrive instance, primarily to setup the
        OAuth2.0 credentials and make sure they are authorised."""

        load_dotenv()
        client_id = os.getenv("Z_CLIENT_ID")
        client_secret = os.getenv("Z_CLIENT_SECRET")
        scope = os.getenv("Z_SCOPE")
        refresh_token = os.getenv("Z_REFRESH_TOKEN")
        
        client = BackendApplicationClient(client_id=client_id,refresh_token=refresh_token)
        self.oauthlib_conn = OAuth2Session(client=client)
        if not self.oauthlib_conn.authorized:
            self.oauthlib_conn.fetch_token(
                token_url=f"https://accounts.zoho.{os.getenv('Z_REGION')}/oauth/v2/token",
                client_id=client_id,
                client_secret=client_secret,
                scope=scope
            )

    def upload_file(self, location_id: str, file_path: str) -> str:
        """Uploads the file at the given filepath to the folder location indicated
        by the location_id parameter. Uses mimetypes to auto-detect type. If a file
        already exists with the same name, WorkDrive automatically appends a 
        timestamp to the end."""

        file_type = mimetypes.guess_type(file_path)
        file_name = Path(file_path).name
        url = f"https://www.zohoapis.{os.getenv('Z_REGION')}/workdrive/api/v1/upload"
        payload = {'parent_id': location_id, 'override-name-exist': 'false'}
        try:
            with open(file_path, 'rb') as file:
                files = [
                    ('content',(file_name,file.read(),file_type))
                ]
        except OSError as e:
            print(e)
        response = self.oauthlib_conn.post(url,data=payload, files=files)

        if response.status_code != 200:
            print(response.status_code, response.content)
            return
        
        os.remove(file_path)

        return response.json()["data"][0]["attributes"]["Permalink"]


    def get_locations(self) -> List:
        """Fetches a list of tuples which represent subfolder names & IDs
        from the defined root folder and all subfolders one level deep
        from those."""

        locations = [(os.getenv("Z_ROOT_FOLDER_NAME"), os.getenv("Z_ROOT_FOLDER_ID"))]
        folders = self._list_folders(locations[0][1])
        for folder in folders:
            id = folder["id"]
            name = folder["attributes"]["name"]
            locations.append((name, id))
            subfolders = self._list_folders(id)
            for subfolder in subfolders:
                subf_name = f"{name} > {subfolder['attributes']['name']}"
                locations.append((subf_name, subfolder["id"]))
        return locations
    
    def _list_folders(self, id) -> List:
        """Fetches a list of folders within the folder with the given
        id parameter. Returns a list of tuples with the folder name &
        IDs."""

        fields = "id,type,name"
        r = self.oauthlib_conn.get(f"https://www.zohoapis.{os.getenv('Z_REGION')}/workdrive/api/v1/files/{id}/files?filter%5Btype%5D=folder&fields%5Bfiles%5D=" + fields)
        if (r.status_code != 200):
            return []
        return json.loads(r.content)["data"]

if __name__ == "__main__":

    print("Testing WorkDrive authorization and settings")
    test_wd = WorkDrive()
    print("Uploading a test file to the root folder")
    r = test_wd.upload_file(os.getenv("Z_ROOT_FOLDER_ID"), "walkthrough/add-client.jpg")
    print("File uploaded:", r)
    print("Testing fetching folder structure from set root folder")
    folders = test_wd.get_locations()
    for folder in folders:
        print(folder)
