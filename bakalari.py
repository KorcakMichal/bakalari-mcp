from typing import Any, Tuple, Dict, Callable
from datetime import date as dt_date
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
    def get_actual_timetable(self, date: str = None) -> dict:
        if date is None:
            date = dt_date.today().strftime("%Y-%m-%d")
        response = httpx.get(
            f"{self.base_url}/api/3/timetable/actual?date={date}",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    # --- Additional endpoints ---
    @handle_login
    def get_absence_student(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/absence/student", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_classbook(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/classbook", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_classbook_lesson_tags(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/classbook/lessonTags", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_events(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/events", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_events_my(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/events/my", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_events_public(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/events/public", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_homeworks(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/homeworks", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_homeworks_count_actual(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/homeworks/count-actual", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_attachment(self, id: str) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/attachment/{id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_message(self, data: dict) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/komens/message", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_message(self, id: str) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/message/{id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_message_mark_as_read(self, id: str) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/komens/message/{id}/mark-as-read", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_message_types(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/message-types", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_message_types_edit(self, data: dict) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/komens/message-types/edit", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_message_types_reply(self, data: dict) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/komens/message-types/reply", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_messages_apology(self, data: dict) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/komens/messages/apology", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_noticeboard(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/messages/noticeboard", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_noticeboard_unread(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/messages/noticeboard/unread", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_rating(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/messages/rating", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_received(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/messages/received", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_received_id(self, id: str) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/messages/received/{id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_sent_id(self, id: str) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/messages/sent/{id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_received_unread(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/messages/received/unread", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_sent(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/komens/messages/sent", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_login(self, data: dict) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/login", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_logintoken(self, data: dict) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/logintoken", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_marks(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/marks", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_marks_count_new(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/marks/count-new", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_marks_final(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/marks/final", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_marks_measures(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/marks/measures", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_marks_what_if(self, data: dict) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/marks/what-if", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_payments_classfund(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/payments/classfund", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_payments_classfund_paymentsinfo(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/payments/classfund/paymentsinfo", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_payments_classfund_summary(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/payments/classfund/summary", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_register_notification(self, data: dict) -> dict:
        response = httpx.post(f"{self.base_url}/api/3/register-notification", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_subjects(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/subjects", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_subjects_themes_id(self, id: str) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/subjects/themes/{id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_substitutions(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/substitutions", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_user(self) -> dict:
        response = httpx.get(f"{self.base_url}/api/3/user", headers=self.headers)
        response.raise_for_status()
        return response.json()

    # --- End of endpoints ---

client = Client(os.getenv("BK_PWD"), os.getenv("BK_USER"), os.getenv("BK_API_BASE"))
