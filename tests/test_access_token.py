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
"""Transkribus API Client access token Tests."""

import transkribus as tr
import unittest

from datetime import datetime, timedelta
from transkribus import TranskribusApi
from unittest.mock import patch, MagicMock


class TestAccessToken(unittest.TestCase):
    """Testss for TranskribusApi.AccessToken."""

    @patch("transkribus.api.requests")
    def test_obtain_revoke(self, mock_requests):
        """Test obtain and revoke of AP API access token."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "ACCESSTOKEN",
            "expires_in": 300,
            "refresh_expires_in": 14400,
            "refresh_token": "REFRESHTOKEN",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "session_state": "sessionstate",
            "scope": "profile email",
        }
        mock_resp.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_resp

        now = datetime.now()

        api = TranskribusApi("username", "password")
        mock_requests.post.assert_called_once_with(
            "https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/"
            + "token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "password",
                "username": "username",
                "password": "password",
                "client_id": "transkribus-api-client",
            },
        )
        self.assertEqual(api.access_token.access_token, "ACCESSTOKEN")
        self.assertGreaterEqual(api.access_token.expires, now + timedelta(minutes=300))
        self.assertGreaterEqual(
            api.access_token.refresh_expires, now + timedelta(minutes=14400)
        )
        self.assertEqual(api.access_token.refresh_token, "REFRESHTOKEN")
        self.assertEqual(api.access_token.token_type, "Bearer")
        self.assertEqual(api.access_token.not_before_policy, 0)
        self.assertEqual(api.access_token.session_state, "sessionstate")
        self.assertEqual(api.access_token.scope, "profile email")
        self.assertFalse(api.access_token.is_expired())
        self.assertFalse(api.access_token.is_refresh_expired())

        mock_requests.reset_mock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text.return_value = ""
        mock_resp.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_resp

        api.close()

        mock_requests.post.assert_called_once_with(
            "https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/"
            + "logout",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": "transkribus-api-client",
                "refresh_token": "REFRESHTOKEN",
            },
        )
        self.assertEqual(api.access_token.access_token, "")
        self.assertGreaterEqual(api.access_token.expires, now)
        self.assertGreaterEqual(api.access_token.refresh_expires, now)
        self.assertEqual(api.access_token.refresh_token, "")
        self.assertEqual(api.access_token.token_type, "")
        self.assertEqual(api.access_token.not_before_policy, -1)
        self.assertEqual(api.access_token.session_state, "")
        self.assertEqual(api.access_token.scope, "")
        self.assertTrue(api.access_token.is_expired())
        self.assertTrue(api.access_token.is_refresh_expired())

    @patch("transkribus.api.requests")
    def test_contextmanager(self, mock_requests):
        """Test contextmanager."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "ACCESSTOKEN",
            "expires_in": 300,
            "refresh_expires_in": 14400,
            "refresh_token": "REFRESHTOKEN",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "session_state": "sessionstate",
            "scope": "profile email",
        }
        mock_resp.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_resp

        now = datetime.now()
        with tr.open("username", "password") as api:
            mock_requests.post.assert_called_once_with(
                "https://account.readcoop.eu/auth/realms/readcoop/protocol/"
                + "openid-connect/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "password",
                    "username": "username",
                    "password": "password",
                    "client_id": "transkribus-api-client",
                },
            )
            self.assertEqual(api.access_token.access_token, "ACCESSTOKEN")
            self.assertGreaterEqual(
                api.access_token.expires, now + timedelta(minutes=300)
            )
            self.assertGreaterEqual(
                api.access_token.refresh_expires, now + timedelta(minutes=14400)
            )
            self.assertEqual(api.access_token.refresh_token, "REFRESHTOKEN")
            self.assertEqual(api.access_token.token_type, "Bearer")
            self.assertEqual(api.access_token.not_before_policy, 0)
            self.assertEqual(api.access_token.session_state, "sessionstate")
            self.assertEqual(api.access_token.scope, "profile email")
            self.assertFalse(api.access_token.is_expired())
            self.assertFalse(api.access_token.is_refresh_expired())

            mock_requests.reset_mock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text.return_value = ""
            mock_resp.raise_for_status.return_value = None
            mock_requests.post.return_value = mock_resp
        mock_requests.post.assert_called_once_with(
            "https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/"
            + "logout",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": "transkribus-api-client",
                "refresh_token": "REFRESHTOKEN",
            },
        )
        self.assertEqual(api.access_token.access_token, "")
        self.assertGreaterEqual(api.access_token.expires, now)
        self.assertGreaterEqual(api.access_token.refresh_expires, now)
        self.assertEqual(api.access_token.refresh_token, "")
        self.assertEqual(api.access_token.token_type, "")
        self.assertEqual(api.access_token.not_before_policy, -1)
        self.assertEqual(api.access_token.session_state, "")
        self.assertEqual(api.access_token.scope, "")
        self.assertTrue(api.access_token.is_expired())
        self.assertTrue(api.access_token.is_refresh_expired())

    @patch("transkribus.api.requests")
    def test_refresh(self, mock_requests):
        """Test refreshing API access token."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "ACCESSTOKEN",
            "expires_in": 300,
            "refresh_expires_in": 14400,
            "refresh_token": "REFRESHTOKEN",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "session_state": "sessionstate",
            "scope": "profile email",
        }
        mock_resp.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_resp

        now = datetime.now()

        api = TranskribusApi("username", "password")
        mock_requests.post.assert_called_once_with(
            "https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/"
            + "token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "password",
                "username": "username",
                "password": "password",
                "client_id": "transkribus-api-client",
            },
        )
        self.assertEqual(api.access_token.access_token, "ACCESSTOKEN")
        self.assertGreaterEqual(api.access_token.expires, now + timedelta(minutes=300))
        self.assertGreaterEqual(
            api.access_token.refresh_expires, now + timedelta(minutes=14400)
        )
        self.assertEqual(api.access_token.refresh_token, "REFRESHTOKEN")
        self.assertEqual(api.access_token.token_type, "Bearer")
        self.assertEqual(api.access_token.not_before_policy, 0)
        self.assertEqual(api.access_token.session_state, "sessionstate")
        self.assertEqual(api.access_token.scope, "profile email")
        self.assertFalse(api.access_token.is_expired())
        self.assertFalse(api.access_token.is_refresh_expired())

        self.assertFalse(api.access_token.refresh())

        mock_requests.reset_mock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "NEWACCESSTOKEN",
            "expires_in": 300,
            "refresh_expires_in": 14400,
            "refresh_token": "NEWREFRESHTOKEN",
            "token_type": "Bearer",
            "not-before-policy": 0,
            "session_state": "SESSIONSTATE",
            "scope": "profile email",
        }
        mock_resp.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_resp

        self.assertTrue(api.access_token.refresh(True))

        mock_requests.post.assert_called_once_with(
            "https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/"
            + "token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "client_id": "transkribus-api-client",
                "refresh_token": "REFRESHTOKEN",
            },
        )
        self.assertEqual(api.access_token.access_token, "NEWACCESSTOKEN")
        self.assertGreaterEqual(api.access_token.expires, now + timedelta(minutes=300))
        self.assertGreaterEqual(
            api.access_token.refresh_expires, now + timedelta(minutes=14400)
        )
        self.assertEqual(api.access_token.refresh_token, "NEWREFRESHTOKEN")
        self.assertEqual(api.access_token.token_type, "Bearer")
        self.assertEqual(api.access_token.not_before_policy, 0)
        self.assertEqual(api.access_token.session_state, "SESSIONSTATE")
        self.assertEqual(api.access_token.scope, "profile email")

        mock_requests.reset_mock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text.return_value = ""
        mock_resp.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_resp

        api.close()

        mock_requests.post.assert_called_once_with(
            "https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/"
            + "logout",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": "transkribus-api-client",
                "refresh_token": "NEWREFRESHTOKEN",
            },
        )
        self.assertEqual(api.access_token.access_token, "")
        self.assertGreaterEqual(api.access_token.expires, now)
        self.assertGreaterEqual(api.access_token.refresh_expires, now)
        self.assertEqual(api.access_token.refresh_token, "")
        self.assertEqual(api.access_token.token_type, "")
        self.assertEqual(api.access_token.not_before_policy, -1)
        self.assertEqual(api.access_token.session_state, "")
        self.assertEqual(api.access_token.scope, "")
        self.assertTrue(api.access_token.is_expired())
        self.assertTrue(api.access_token.is_refresh_expired())
