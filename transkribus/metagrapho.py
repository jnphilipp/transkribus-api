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
"""Transkribus metagrapho/processing API module."""

import base64
import re

from io import BytesIO
from lxml import etree
from pathlib import Path
from PIL import Image
from typing import Final, TYPE_CHECKING, TypeVar
from urllib.parse import urlparse

from .types import JsonType
from .utils import MAX_IMAGE_SIZE

if TYPE_CHECKING:
    from transkribus.api import TranskribusApi


class MetagraphoApi:
    """Handles all Transkribus Metagrapho/Processing API endpoints.

    https://transkribus.eu/processing/swagger/
    """

    T = TypeVar("T", bound="MetagraphoApi")

    BASE_URL: Final[str] = "https://transkribus.eu/processing/v1"
    access_token: "TranskribusApi.AccessToken"

    def __init__(self, api: "TranskribusApi"):
        """Init new metagrapho/processing API client.

        Args:
         * api: transkribus api
        """
        self.api = api

    def alto(
        self, process_id: int, image_filename: str | None = None
    ) -> etree._Element:
        """Retrive ALTO-XML for a given process ID.

        Args:
         * process_id: a process id
         * image_filename: changes the image filename in the ALTO-XML to the given
           value if not `None`

        Returns:
         * ALTO-XML
        """
        alto_xml = self.api._get(f"{self.BASE_URL}/processes/{process_id}/alto")
        if not isinstance(alto_xml, etree._Element):
            raise RuntimeError(f"Unexpected response type, got {type(alto_xml)}.")
        return (
            alto_xml
            if image_filename is None
            else re.sub(
                r"<fileName>.+?</fileName>",
                f"<fileName>{image_filename}</fileName>",
                alto_xml,
            )
        )

    def page(
        self, process_id: int, image_filename: str | None = None
    ) -> etree._Element:
        """Retrive PAGE-XML for a given process ID.

        Args:
         * process_id: a process id
         * image_filename: changes the image filename in the PAGE-XML to the given value
           if not `None`

        Returns:
         * PAGE-XML
        """
        page_xml = self.api._get(f"{self.BASE_URL}/processes/{process_id}/page")
        if not isinstance(page_xml, etree._Element):
            raise RuntimeError(f"Unexpected response type, got {type(page_xml)}.")
        return (
            page_xml
            if image_filename is None
            else re.sub(
                r'<Page imageFilename="[^"]+"',
                f'<Page imageFilename="{image_filename}"',
                page_xml,
            )
        )

    def process(
        self,
        image: str | Path,
        htr_id: int,
        line_detection: int | None = None,
        language_model: str | None = None,
        text: str | None = None,
        regions: list[dict] | None = None,
        **kwargs: float | int,
    ) -> JsonType:
        """Send an image to be transcribed.

        All the arguements are send to the API in the header.

        Args:
         * image: path of a image or URL to an image to be send to the API, for local
           image a size check will be performed, and if to large converted to jpg and
           reduced in size by lowering image quality
         * htr_id: ID for the HTR model to use
         * line_detection: ID for the line detection model to use
         * language_model: ID for the language detection model to use
         * text: text
         * regions: text regions

        Returns:
         * the JSON response with thr process ID, as return by the API
        """
        json_data: dict = {
            "config": {
                "textRecognition": {
                    "htrId": htr_id,
                }
            }
        }
        if language_model is not None:
            json_data["config"]["textRecognition"]["languageModel"] = language_model
        if line_detection is not None:
            json_data["config"]["lineDetection"] = {"modelId": line_detection}
            if "minimalBaselineLength" in kwargs:
                json_data["config"]["lineDetection"]["minimalBaselineLength"] = kwargs[
                    "minimalBaselineLength"
                ]
            if "baselineAccuracyThreshold" in kwargs:
                json_data["config"]["lineDetection"]["baselineAccuracyThreshold"] = (
                    kwargs["baselineAccuracyThreshold"]
                )
            if "maxDistForMerging" in kwargs:
                json_data["config"]["lineDetection"]["maxDistForMerging"] = kwargs[
                    "maxDistForMerging"
                ]
            if "numTextRegions" in kwargs:
                json_data["config"]["lineDetection"]["numTextRegions"] = kwargs[
                    "numTextRegions"
                ]

        if text is not None:
            json_data["content"]["text"] = text
        if regions is not None:
            json_data["content"]["regions"] = regions

        if isinstance(image, str):
            parsed_url = urlparse(image)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                image = Path(image).absolute()

        image_base64 = None
        if isinstance(image, Path):
            if not image.is_file():
                raise TypeError(f"The image {image} is not a file.")
            image_base64 = base64.b64encode(open(image, "rb").read()).decode()
            if (
                image.stat().st_size > MAX_IMAGE_SIZE
                or len(image_base64) > MAX_IMAGE_SIZE
            ):
                quality = 95
                while True:
                    img: Image.Image = Image.open(image)
                    buffered = BytesIO()
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.save(buffered, format="JPEG", quality=quality, optimize=True)
                    image_base64 = base64.b64encode(buffered.getvalue()).decode()
                    if (
                        buffered.getbuffer().nbytes > MAX_IMAGE_SIZE
                        or len(image_base64) > MAX_IMAGE_SIZE
                    ):
                        quality -= 3
                    else:
                        break
        if image_base64 is None:
            json_data["image"] = {"imageUrl": image}
        else:
            json_data["image"] = {"base64": image_base64}
        return self.api._post(f"{self.BASE_URL}/processes", json=json_data)

    def status(self, process_id: int) -> JsonType:
        """Make an API call to retrive the state for a process ID.

        Args:
         * process_id: a process id

        Returns:
         * JSON response from the API
        """
        return self.api._get(f"{self.BASE_URL}/processes/{process_id}")
