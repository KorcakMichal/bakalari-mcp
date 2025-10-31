from typing import Any, Tuple, Dict, Callable
import httpx
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
import logging
import coloredlogs

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

mcp = FastMCP("bakalari")

class Client:
    def __init__(self, pwd: str, user: str, base_url: str) -> None:
        self.pwd: str = pwd
        self.user: str = user
        self.base_url: str = base_url
        self.access_token: str
        self.refresh_token: str
        self.access_token, self.refresh_token = self._get_access_token()
        self.headers: dict[str, str] = {
            "Authorization": f"Bearer {self.access_token}",
        }

    def set_tokens(self):
        self.access_token, self.refresh_token = self._get_access_token()
        self.headers["Authorization"] = f"Bearer {self.access_token}"

    def _get_access_token(self) -> tuple[str, str]:
        response = httpx.post(
            self.base_url + "/api/login",
            data={
            "client_id": "ANDR",
            "grant_type": "password",
            "username": self.user,
            "password": self.pwd,
            },
            headers={},
        )

        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")

        assert access_token is not None, "Failed to obtain access token"
        assert refresh_token is not None, "Failed to obtain refresh token"
        
        return access_token, refresh_token
    
    def update_tokens_with_refresh_token(self) -> None:
        response = httpx.post(
            self.base_url + "/api/login",
            data={
                "client_id": "ANDR",
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
            headers={},
        )

        self.access_token = response.json().get("access_token")
        self.refresh_token = response.json().get("refresh_token")
        self.headers["Authorization"] = f"Bearer {self.access_token}"

    def handle_login(function):
        def wrapper(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
            try:
                return function(self, *args, **kwargs)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    logger.info("Access token expired, refreshing...")
                    self.update_tokens()
                    return function(self, *args, **kwargs)
                else:
                    raise e
        return wrapper

    @handle_login
    def get_permanent_timetable(self) -> dict:
        response = httpx.get(
            self.base_url + "/api/3/timetable/permanent",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_actual_timetable(self, **kwargs: Any) -> dict[str, Any]:
        if "date" not in kwargs:
            kwargs["date"] = date.today().strftime("%Y-%m-%d")

        response = httpx.get(
            f"{self.base_url}/api/3/timetable/actual?date={kwargs['date']}",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    

client = Client(os.getenv("BK_PWD"), os.getenv("BK_USER"), os.getenv("BK_API_BASE"))
