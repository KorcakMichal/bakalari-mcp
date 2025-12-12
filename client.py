from typing import Any, Callable
from datetime import date as dt_date
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, pwd, user, base_url):
        """
        Initialize the Client with user credentials and base API URL.
        Obtains access and refresh tokens for authentication.
        """
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
        """
        Refreshes the access and refresh tokens and updates the authorization header.
        """
        self.access_token, self.refresh_token = self._get_access_token()
        self.headers["Authorization"] = f"Bearer {self.access_token}"

    def _get_access_token(self) -> tuple[str, str]:
        """
        Requests new access and refresh tokens using user credentials.
        Returns:
            Tuple of (access_token, refresh_token)
        """
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
        """
        Updates access and refresh tokens using the current refresh token.
        """
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

#TODO: přijde mi že každý call je provoláván dvakrát
    def handle_login(function):
        """
        Decorator to handle automatic token refresh on 401 errors.
        """

        def wrapper(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
            try:
                return function(self, *args, **kwargs)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    logger.info("Access token expired, refreshing...")
                    self.update_tokens_with_refresh_token()
                    return function(self, *args, **kwargs)
                else:
                    raise e
            finally:
                logger.info("Request to %s completed.", function.__name__)

        return wrapper

    @handle_login
    def get_permanent_timetable(self) -> dict:
        """
        Fetches the permanent timetable for the user.
        Returns:
            dict: {
                "Days": [
                    {
                        "Date": str,
                        "DayType": str,
                        "Atoms": [ {...} ]
                    },
                    ...
                ]
            }
        """
        response = httpx.get(
            self.base_url + "/api/3/timetable/permanent",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_actual_timetable(self, date: str = None) -> dict:
        """
        Fetches the actual timetable for the user for a given date.
        Args:
            date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
        Returns:
            dict: {
                "Days": [
                    {
                        "Date": str,
                        "DayType": str,
                        "Atoms": [ {...} ]
                    },
                    ...
                ]
            }
        """
        if date is None:
            date = dt_date.today().strftime("%Y-%m-%d")
        response = httpx.get(
            f"{self.base_url}/api/3/timetable/actual?date={date}",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_absence_student(self) -> dict:
        """
        Fetches absence information for the student.
        Returns:
            dict: {
                "PercentageThreshold": float,
                "Absences": [ {...} ],
                "AbsencesPerSubject": [ {...} ]
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/absence/student", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_events(self) -> dict:
        """
        Fetches all events.
        Returns:
            dict: {
                "Events": [ {...} ]
            }
        """
        response = httpx.get(f"{self.base_url}/api/3/events", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_events_my(self) -> dict:
        """
        Fetches events specific to the user.
        Returns:
            dict: {
                "Events": [ {...} ]
            }
        """
        response = httpx.get(f"{self.base_url}/api/3/events/my", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_events_public(self) -> dict:
        """
        Fetches public events.
        Returns:
            dict: {
                "Events": [ {...} ]
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/events/public", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_homeworks(self) -> dict:
        """
        Fetches all homeworks.
        Returns:
            dict: {
                "Homeworks": [ {...} ]
            }
        """
        response = httpx.get(f"{self.base_url}/api/3/homeworks", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_homeworks_count_actual(self) -> dict:
        """
        Fetches the count of actual homeworks.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.get(
            f"{self.base_url}/api/3/homeworks/count-actual", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_attachment_by_id(self, id: str) -> dict:
        """
        Fetches a Komens attachment by ID.
        Args:
            id (str): Attachment ID.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/attachment/{id}", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_message_by_id(self, id: str) -> dict:
        """
        Fetches a Komens message by ID.
        Args:
            id (str): Message ID.
        Returns:
            dict: {
                "Message": {...}
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/message/{id}", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_message_types(self) -> dict:
        """
        Fetches Komens message types.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/message-types", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_noticeboard(self) -> dict:
        """
        Fetches Komens noticeboard messages.
        Returns:
            dict: {
                "Messages": [ {...} ]
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/messages/noticeboard", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_noticeboard_unread(self) -> dict:
        """
        Fetches unread Komens noticeboard messages.
        Returns:
            dict: int (count of unread messages)
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/messages/noticeboard/unread",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_rating(self) -> dict:
        """
        Fetches Komens rating messages.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/messages/rating", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_messages_received(self) -> dict:
        """
        Fetches received Komens messages.
        Returns:
            dict: {
                "Messages": [ {...} ]
            }
        """
        response = httpx.post(
            f"{self.base_url}/api/3/komens/messages/received", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_received_id(self, id: str) -> dict:
        """
        Fetches a received Komens message by ID.
        Args:
            id (str): Message ID.
        Returns:
            dict: {
                "Message": {...}
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/messages/received/{id}", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_sent_id(self, id: str) -> dict:
        """
        Fetches a sent Komens message by ID.
        Args:
            id (str): Message ID.
        Returns:
            dict: {
                "Message": {...}
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/messages/sent/{id}", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_komens_messages_received_unread(self) -> dict:
        """
        Fetches number of unread received Komens messages.
        Returns:
            dict: int (count of unread messages)
        """
        response = httpx.get(
            f"{self.base_url}/api/3/komens/messages/received/unread",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_messages_sent(self) -> dict:
        """
        Fetches sent Komens messages.
        Returns:
            dict: {
                "Messages": [ {...} ]
            }
        """
        response = httpx.post(
            f"{self.base_url}/api/3/komens/messages/sent", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_marks(self) -> dict:
        """
        Fetches marks for the user.
        Returns:
            dict: {
                "Subjects": [ {...} ]
            }
        """
        response = httpx.get(f"{self.base_url}/api/3/marks", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_marks_count_new(self) -> dict:
        """
        Fetches count of new marks.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.get(
            f"{self.base_url}/api/3/marks/count-new", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_marks_final(self) -> dict:
        """
        Fetches final marks.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.get(f"{self.base_url}/api/3/marks/final", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_marks_measures(self) -> dict:
        """
        Fetches marks measures.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.get(
            f"{self.base_url}/api/3/marks/measures", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_payments_classfund(self) -> dict:
        """
        Fetches class fund payment information.
        Returns:
            dict: {
                "MonthlyData": [ {...} ]
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/payments/classfund", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_payments_classfund_paymentsinfo(self) -> dict:
        """
        Fetches class fund payments info.
        Returns:
            dict: {
                "Instructions": str,
                "BankAccount": str,
                "VariableSymbol": int,
                "SpecificSymbol": int,
                "Amount": float,
                "Message": str
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/payments/classfund/paymentsinfo",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_payments_classfund_summary(self) -> dict:
        """
        Fetches class fund summary.
        Returns:
            dict: {
                "StudentNameWithClass": str,
                "Balance": float,
                "Spent": float
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/payments/classfund/summary", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_subjects(self) -> dict:
        """
        Fetches subjects for the user.
        Returns:
            dict: {
                "Subjects": [ {...} ]
            }
        """
        response = httpx.get(f"{self.base_url}/api/3/subjects", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_subjects_themes_id(self, id: str) -> dict:
        """
        Fetches subject themes by ID.
        Args:
            id (str): Theme ID.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.get(
            f"{self.base_url}/api/3/subjects/themes/{id}", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_substitutions(self) -> dict:
        """
        Fetches substitutions for the user.
        Returns:
            dict: {
                "From": str,
                "To": str,
                "Changes": [ {...} ]
            }
        """
        response = httpx.get(
            f"{self.base_url}/api/3/substitutions", headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def get_user(self) -> dict:
        """
        Fetches user information.
        Returns:
            dict: {
                "UserUID": str,
                "CampaignCategoryCode": str,
                "Class": {...},
                "FullName": str,
                "SchoolOrganizationName": str,
                "SchoolType": str | None,
                "UserType": str,
                "UserTypeText": str,
                "StudyYear": int,
                "EnabledModules": [ {...} ],
                "SettingModules": {...}
            }
        """
        response = httpx.get(f"{self.base_url}/api/3/user", headers=self.headers)
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_message(self, data: dict) -> dict:  # TODO does not match docs
        """
        Sends a Komens message.
        Args:
            data (dict): Message data, e.g.:
                {
                    "Recipients": [str],  # List of recipient IDs
                    "Title": str,         # Message subject
                    "Text": str,          # Message body (HTML encoded)
                    "Attachments": [      # Optional list of attachments
                        {
                            "Id": str,
                            "Name": str,
                            "Type": str,
                            "Size": int
                        },
                        ...
                    ],
                    "Type": str           # Message type (e.g. "OBECNA")
                }
        Returns:
            dict: {
                "Message": {
                    "$type": "GeneralMessage",
                    "Id": str,
                    "Title": str,
                    "Text": str,  # HTML encoded
                    "SentDate": str,  # ISO datetime
                    "Sender": {
                        "Id": str,
                        "Type": str,
                        "Name": str
                    },
                    "Attachments": [
                        {
                            "Id": str,
                            "Name": str,
                            "Type": str,
                            "Size": int
                        },
                        ...
                    ],
                    "Read": bool,
                    "LifeTime": str,
                    "DateFrom": str | None,
                    "DateTo": str | None,
                    "Confirmed": bool,
                    "CanConfirm": bool,
                    "Type": str,
                    "CanAnswer": bool,
                    "Hidden": bool,
                    "CanHide": bool,
                    "RelevantName": str,
                    "RelevantPersonType": str
                }
            }
        """
        response = httpx.post(
            f"{self.base_url}/api/3/komens/message", headers=self.headers, json=data
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_message_mark_as_read(self, id: str) -> dict:
        """
        Marks a Komens message as read by ID.
        Args:
            id (str): Message ID.
        Returns:
            dict: Empty response (HTTP 204 No Content).
        """
        response = httpx.post(
            f"{self.base_url}/api/3/komens/message/{id}/mark-as-read",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_message_types_edit(self, data: dict) -> dict:
        """
        Edits Komens message types.
        Args:
            data (dict): Edit data.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.post(
            f"{self.base_url}/api/3/komens/message-types/edit",
            headers=self.headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_message_types_reply(
        self, data: dict
    ) -> dict:  # TODO: specify input
        """
        Replies to Komens message types.
        Args:
            data (dict): Reply data.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.post(
            f"{self.base_url}/api/3/komens/message-types/reply",
            headers=self.headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_komens_messages_apology(self, data: dict) -> dict:  # specify input
        """
        Sends an apology message via Komens.
        Args:
            data (dict): Apology data.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.post(
            f"{self.base_url}/api/3/komens/messages/apology",
            headers=self.headers,
            json=data,
        )
        response.raise_for_status()
        return response.json()

    @handle_login
    def post_marks_what_if(self, data: dict) -> dict:  # TODO: specify input
        """
        Performs a 'what-if' analysis for marks.
        Args:
            data (dict): Analysis data.
        Returns:
            dict: See Bakaláři API documentation for details (endpoint not documented in public API).
        """
        response = httpx.post(
            f"{self.base_url}/api/3/marks/what-if", headers=self.headers, json=data
        )
        response.raise_for_status()
        return response.json()
