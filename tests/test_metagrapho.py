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
"""Transkribus API Client metagrapho API Tests."""

import unittest
import lxml.etree

from datetime import datetime, timedelta
from transkribus import TranskribusApi
from unittest.mock import patch, MagicMock


class TestAccessToken(unittest.TestCase):
    """Tests for MetagraphoApi."""

    @patch("transkribus.api.requests")
    def test_metagrapho_api(self, mock_requests):
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
        mock_resp.headers = {"Content-Type": "application/json"}
        mock_resp.json.return_value = {"processId": 1, "status": "CREATED"}
        mock_resp.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_resp

        data = api.metagrapho.process(
            "https://transkribus.eu/processing/swagger/test-image.jpg",
            1,
            1,
        )
        mock_requests.post.assert_called_once_with(
            "https://transkribus.eu/processing/v1/processes",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Authorization": "Bearer ACCESSTOKEN",
            },
            params={},
            data={},
            json={
                "config": {
                    "textRecognition": {"htrId": 1},
                    "lineDetection": {"modelId": 1},
                },
                "image": {
                    "imageUrl": "https://transkribus.eu/processing/swagger/"
                    + "test-image.jpg"
                },
            },
        )
        self.assertEqual({"processId": 1, "status": "CREATED"}, data)

        mock_requests.reset_mock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/json"}
        mock_resp.json.return_value = {"processId": 1, "status": "RUNNING"}
        mock_resp.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_resp

        data = api.metagrapho.status(1)
        mock_requests.get.assert_called_once_with(
            "https://transkribus.eu/processing/v1/processes/1",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Authorization": "Bearer ACCESSTOKEN",
            },
            params={},
        )
        self.assertEqual({"processId": 1, "status": "RUNNING"}, data)

        mock_requests.reset_mock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/json"}
        mock_resp.json.return_value = {
            "processId": 1,
            "status": "FINISHED",
            "content": {
                "text": "The mischievousness of the office",
                "regions": [
                    {
                        "id": "tr_1",
                        "coords": {"points": "241,330 241,3917 1988,3917 1988,330"},
                        "orientation": 0.0,
                        "lines": [
                            {
                                "id": "tr_1_tl_1",
                                "coords": {
                                    "points": "319,420 545,459 838,422 916,493 1140,"
                                    + "422 1231,418 1306,472 1429,412 1429,343 1293,"
                                    + "274 914,297 800,353 659,289 586,317 319,276"
                                },
                                "baseline": {
                                    "points": "331,414 386,412 441,413 496,411 551,"
                                    + "411 607,410 662,410 717,411 772,411 827,410 883,"
                                    + "411 938,411 993,411 1048,411 1103,410 1159,"
                                    + "409 1214,409 1269,410 1324,408 1379,406 1435,403"
                                },
                                "text": "The mischievousness of the office",
                            },
                        ],
                    },
                ],
            },
        }
        mock_resp.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_resp

        data = api.metagrapho.status(1)
        mock_requests.get.assert_called_once_with(
            "https://transkribus.eu/processing/v1/processes/1",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Authorization": "Bearer ACCESSTOKEN",
            },
            params={},
        )
        self.assertEqual(
            {
                "processId": 1,
                "status": "FINISHED",
                "content": {
                    "text": "The mischievousness of the office",
                    "regions": [
                        {
                            "id": "tr_1",
                            "coords": {"points": "241,330 241,3917 1988,3917 1988,330"},
                            "orientation": 0.0,
                            "lines": [
                                {
                                    "id": "tr_1_tl_1",
                                    "coords": {
                                        "points": "319,420 545,459 838,422 916,"
                                        + "493 1140,422 1231,418 1306,472 1429,"
                                        + "412 1429,343 1293,274 914,297 800,353 659,"
                                        + "289 586,317 319,276"
                                    },
                                    "baseline": {
                                        "points": "331,414 386,412 441,413 496,411 551,"
                                        + "411 607,410 662,410 717,411 772,411 827,"
                                        + "410 883,411 938,411 993,411 1048,411 1103,"
                                        + "410 1159,409 1214,409 1269,410 1324,"
                                        + "408 1379,406 1435,403"
                                    },
                                    "text": "The mischievousness of the office",
                                },
                            ],
                        },
                    ],
                },
            },
            data,
        )

        with open("./tests/page.xml", "r", encoding="utf8") as f:
            page_xml = f.read()

        mock_requests.reset_mock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/xml"}
        mock_resp.content = page_xml.encode("utf8")
        mock_resp.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_resp

        data = api.metagrapho.page(1)
        mock_requests.get.assert_called_once_with(
            "https://transkribus.eu/processing/v1/processes/1/page",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Authorization": "Bearer ACCESSTOKEN",
            },
            params={},
        )
        self.assertEqual(
            page_xml.encode("utf8"), lxml.etree.tostring(data, pretty_print=True)
        )

        with open("./tests/alto.xml", "r", encoding="utf8") as f:
            alto_xml = f.read()

        mock_requests.reset_mock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/xml"}
        mock_resp.content = alto_xml.encode("utf8")
        mock_resp.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_resp

        data = api.metagrapho.alto(1)
        mock_requests.get.assert_called_once_with(
            "https://transkribus.eu/processing/v1/processes/1/alto",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Authorization": "Bearer ACCESSTOKEN",
            },
            params={},
        )
        self.assertEqual(
            alto_xml.encode("utf8"), lxml.etree.tostring(data, pretty_print=True)
        )

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
