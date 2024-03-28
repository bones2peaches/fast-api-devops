import os
import requests as rs
from requests.auth import HTTPBasicAuth
import json
import logging
from app.schema.nchan import NchanEvent, NchanResponse, ChatroomUsers
import uuid
from json import JSONDecodeError


class HttpPublisher:
    def __init__(
        self,
        protocol: str = os.getenv("NCHAN_PROTOCOL"),
        host: str = os.getenv("NCHAN_HOST"),
        port: str = os.getenv("NCHAN_PORT"),
        username: str = os.getenv("NCHAN_USERNAME"),
        password: str = os.getenv("NCHAN_PASSWORD"),
    ):

        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.headers = {"Content-Type": "text/json"}
        self.basic_auth = HTTPBasicAuth(self.username, self.password)
        self.base_url = f"{self.protocol}://{self.host}:{self.port}"
        logging.info(f"NCHAN BASE URL: {self.base_url}")

    def publish_chatroom_users(
        self, event: NchanResponse, chatroom_id: uuid.UUID | str
    ):
        if isinstance(event.data, ChatroomUsers) is False:
            raise ValueError("Nchan Response data must be ChatroomUsers")
        if event.event != "user":
            event.event = "user"
        else:
            url = f"{self.base_url}/internal/chatroom/{chatroom_id}/user"
            logging.warn(f"NCHAN URL: {url} ")
            post = rs.post(
                url, auth=self.basic_auth, headers=self.headers, json=event.dict()
            )
            if post.status_code not in [200, 201, 202]:
                logging.warn(
                    f"Nchan Status Code was not successful : {post.status_code}"
                )
            else:
                try:
                    return post.json()
                except JSONDecodeError:
                    logging.warn(f"NCHAN RESPONSE WAS NOT JSON : {post.text}")
                    return post.text
                except Exception as e:
                    logging.warn(f"UNKNOWN ERROR : {e}")
                    return post.text


nchan_client = HttpPublisher()
