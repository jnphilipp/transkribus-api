# Copyright (C) 2026 J. Nathanael Philipp <jnathanael@philipp.land>
#
# Transkribus API Client
#
# This file is part of transkribus-api.
#
# transkribus-api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# transkribus-api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with transkribus-api. If not, see <http://www.gnu.org/licenses/>
"""Transkribus API Client."""

import requests

from datetime import datetime, timedelta
from lxml import etree
from typing import Final, Type, TypeVar

from .metagrapho import MetagraphoApi
from .types import JsonType
from .utils import parse_xml


class TranskribusApi:
    """Transkribus API."""

    T = TypeVar("T", bound="TranskribusApi")

    access_token: "TranskribusApi.AccessToken"
    metagrapho: MetagraphoApi

    class AccessToken:
        """API access token."""

        T = TypeVar("T", bound="TranskribusApi.AccessToken")
        BASE_URL: Final[str] = (
            "https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect"
        )

        client_id: str
        access_token: str
        expires: datetime
        refresh_expires: datetime
        refresh_token: str
        token_type: str
        not_before_policy: int
        session_state: str
        scope: str

        def __init__(
            self,
            client_id: str,
            access_token: str,
            expires: datetime,
            refresh_expires: datetime,
            refresh_token: str,
            token_type: str,
            not_before_policy: int,
            session_state: str,
            scope: str,
        ) -> None:
            """Create new access token."""
            self.client_id = client_id
            self.access_token = access_token
            self.expires = expires
            self.refresh_expires = refresh_expires
            self.refresh_token = refresh_token
            self.token_type = token_type
            self.not_before_policy = not_before_policy
            self.session_state = session_state
            self.scope = scope

        def get_auth_token(self) -> str:
            """Get auth token for request header.

            Auto refreshes if token is expired.
            """
            self.refresh()
            return f"{self.token_type} {self.access_token}"

        def get_request_header(self) -> dict[str, str]:
            """Get auth token for request header.

            Auto refreshes the token if it is expired.
            """
            return {"Authorization": self.get_auth_token()}

        def is_expired(self) -> bool:
            """Check if the access token is expired."""
            return datetime.now() > self.expires

        def is_refresh_expired(self) -> bool:
            """Check if the refresh token is expired."""
            return datetime.now() > self.refresh_expires

        def refresh(self, force: bool = False) -> bool:
            """Refresh access token."""
            if force or self.is_expired():
                if self.is_refresh_expired():
                    raise RuntimeError(
                        "Refresh token is expired, need to reauthenticate."
                    )
                now = datetime.now()
                r = requests.post(
                    f"{self.BASE_URL}/token",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self.client_id,
                        "refresh_token": self.refresh_token,
                    },
                )
                r.raise_for_status()
                data = r.json()
                self.access_token = data["access_token"]
                self.expires = now + timedelta(minutes=data["expires_in"])
                self.refresh_expires = now + timedelta(
                    minutes=data["refresh_expires_in"]
                )
                self.refresh_token = data["refresh_token"]
                self.token_type = data["token_type"]
                self.not_before_policy = data["not-before-policy"]
                self.session_state = data["session_state"]
                self.scope = data["scope"]
                return True
            return False

        def revoke(self) -> bool:
            """Revoke access token."""
            r = requests.post(
                f"{self.BASE_URL}/logout",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "client_id": self.client_id,
                    "refresh_token": self.refresh_token,
                },
            )
            r.raise_for_status()
            self.access_token = ""
            self.expires = datetime.now()
            self.refresh_expires = datetime.now()
            self.refresh_token = ""
            self.token_type = ""
            self.not_before_policy = -1
            self.session_state = ""
            self.scope = ""
            return True

        @classmethod
        def obtain(
            cls: Type[T],
            username: str,
            password: str,
            client_id: str = "transkribus-api-client",
        ) -> T:
            """Obtain access token."""
            now = datetime.now()
            r = requests.post(
                f"{cls.BASE_URL}/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                    "client_id": client_id,
                },
            )
            r.raise_for_status()
            data = r.json()
            return cls(
                client_id=client_id,
                access_token=data["access_token"],
                expires=now + timedelta(minutes=data["expires_in"]),
                refresh_expires=now + timedelta(minutes=data["refresh_expires_in"]),
                refresh_token=data["refresh_token"],
                token_type=data["token_type"],
                not_before_policy=data["not-before-policy"],
                session_state=data["session_state"],
                scope=data["scope"],
            )

    def __init__(
        self, username: str, password: str, client_id: str = "transkribus-api-client"
    ):
        """Init."""
        self.metagrapho = MetagraphoApi(self)

        self.open(username, password, client_id)

    def _delete(self, url: str, params: dict = {}) -> JsonType:
        """Make a delete request."""
        r = requests.delete(
            url,
            headers={"Accept": "application/json, text/plain, */*"}
            | self.access_token.get_request_header(),
            params=params,
        )
        if r.status_code == requests.codes.unauthorized:
            self.access_token.refresh(True)
            r = requests.delete(
                url,
                headers={"Accept": "application/json, text/plain, */*"}
                | self.access_token.get_request_header(),
                params=params,
            )
        r.raise_for_status()
        return self._handle_response(r)

    def _get(self, url: str, params: dict = {}) -> JsonType:
        """Make a get request."""
        r = requests.get(
            url,
            headers={"Accept": "application/json, text/plain, */*"}
            | self.access_token.get_request_header(),
            params=params,
        )
        if r.status_code == requests.codes.unauthorized:
            self.access_token.refresh(True)
            r = requests.get(
                url,
                headers={"Accept": "application/json, text/plain, */*"}
                | self.access_token.get_request_header(),
                params=params,
            )
        r.raise_for_status()
        return self._handle_response(r)

    def _handle_response(
        self, response: requests.models.Response
    ) -> etree._Element | JsonType:
        """Convert response to JSON if content type indicates it."""
        content_type = response.headers.get("Content-Type", "")
        media_type = content_type.partition(";")[0].strip().lower()
        if media_type in {"application/json", "application/problem+json"}:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return response.text
        elif media_type == "application/xml":
            return parse_xml(response.content)
        else:
            return response.text

    def _post(
        self,
        url: str,
        params: dict = {},
        data: dict = {},
        json: JsonType = None,
    ) -> JsonType:
        """Make a post request."""
        r = requests.post(
            url,
            headers={"Accept": "application/json, text/plain, */*"}
            | self.access_token.get_request_header(),
            params=params,
            data=data,
            json=json,
        )
        if r.status_code == requests.codes.unauthorized:
            self.access_token.refresh(True)
            r = requests.post(
                url,
                headers={"Accept": "application/json, text/plain, */*"}
                | self.access_token.get_request_header(),
                params=params,
                data=data,
                json=json,
            )
        r.raise_for_status()
        return self._handle_response(r)

    def _put(self, url: str, files: dict[str, tuple]) -> JsonType:
        """Make a put request."""
        r = requests.put(
            url,
            headers={"Accept": "application/json, text/plain, */*"}
            | self.access_token.get_request_header(),
            files=files,
        )
        if r.status_code == requests.codes.unauthorized:
            self.access_token.refresh(True)
            r = requests.put(
                url,
                headers={"Accept": "application/json, text/plain, */*"}
                | self.access_token.get_request_header(),
                files=files,
            )
        r.raise_for_status()
        return self._handle_response(r)

    def open(
        self, username: str, password: str, client_id: str = "processing-api-client"
    ):
        """Open this API.

        Obtain an access token.

        Args:
         * username: username
         * password: password
         * client_id: the API client id to use
        """
        self.access_token = TranskribusApi.AccessToken.obtain(
            username, password, client_id
        )

    def close(self) -> bool:
        """Close this API.

        Sends a requests to revoke the access token.

        Returns:
         * `True` if request was successful
        """
        return self.access_token.revoke()
