import os
from typing import List, Protocol
from dotenv import load_dotenv
from flask import json
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

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

    def uploadFile(self, location_id: str, filepath: str) -> bool:
        pass

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
        fields = "id,type,name"
        r = self.oauthlib_conn.get(f"https://www.zohoapis.{os.getenv('Z_REGION')}/workdrive/api/v1/files/{id}/files?filter%5Btype%5D=folder&fields%5Bfiles%5D=" + fields)
        if (r.status_code != 200):
            return []
        return json.loads(r.content)["data"]

if __name__ == "__main__":

    test_wd = WorkDrive()
    folders = test_wd.get_locations()
    for folder in folders:
        print(folder)
        if isinstance(folder[1], List):
            for subfolder in folder[1]:
                print("|->", subfolder)
