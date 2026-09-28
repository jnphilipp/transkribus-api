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
"""Transkribus API client utils module."""

from lxml import etree
from typing import Final

MAX_IMAGE_SIZE: Final[int] = 20000000
"""Maximum image size (in bytes) that Transkribus accepts, lager images while converted
to reduce the size."""


def parse_xml(text: bytes | str) -> etree._Element:
    """Parse bytes/string to XML-doc.

    Args:
     * text: XML-str/bytes to be parsed

    Returns:
     * XML as parsed `lxml.etree._Element`
    """
    if isinstance(text, str):
        text = text.encode("utf8")
    parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
    return etree.fromstring(text, parser=parser)
