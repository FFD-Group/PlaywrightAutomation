from typing import Protocol
from flask import json
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from dotenv import load_dotenv
import os

class CommsProtocol(Protocol):

    def post_message(self) -> None:
        pass


class Cliq:

    oauthlib_conn: OAuth2Session

    def __init__(self) -> None:
        """Initialise the Cliq instance, primarily to setup the
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
    
    def post_message(self, channel_id: str, message: dict) -> None:
        url = f"https://cliq.zoho.{os.getenv('Z_REGION')}/api/v2/channelsbyname/{channel_id}/message?bot_unique_name={os.getenv('Z_CLIQ_BOT_NAME')}"
        data = json.dumps(message)
        self.oauthlib_conn.post(url, data=data)


if __name__ == "__main__":
    print("Testing Cliq authorisation and credentials")
    cliq = Cliq()
    print("Testing sending a message to the set Cliq channel")
    message = {
        "text": "I have gathered this file as asked, it is ready to view.",
        "card": {
            "theme": "modern-inline"
        },
        "buttons": [{
            "label": "View file",
            "type": "+",
            "action": {
                "type": "open.url",
                "data": {
                    "web": "https://www.google.co.uk"
                }
            }
        }]
    }
    cliq.post_message(os.getenv("Z_CLIQ_CHANNEL_NAME"), message)
    