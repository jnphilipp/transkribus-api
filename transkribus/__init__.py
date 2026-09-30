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

from contextlib import contextmanager
from typing import Generator

from .api import TranskribusApi

__all__ = ["TranskribusApi"]

__app_name__ = "transkribus-api"
__author__ = "J. Nathanael Philipp"
__email__ = "jnathanael@philipp.land"
__copyright__ = "Copyright 2026 J. Nathanael Philipp"
__license__ = "GPL-3.0-or-later"
__version_info__ = (0, 1, 1)
__version__ = ".".join(str(e) for e in __version_info__)
__repository__ = "https://github.com/jnphilipp/transkribus-api"
VERSION = (
    f"%(prog)s v{__version__}\n{__copyright__}\n"
    + "License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>."
    + "\nThis is free software: you are free to change and redistribute it.\n"
    + "There is NO WARRANTY, to the extent permitted by law.\n\n"
    + f"Report bugs to {__repository__}/issues."
    + f"\nWritten by {__author__} <{__email__}>"
)


@contextmanager
def open(username: str, password: str) -> Generator:
    """Context manager for Transkribus API.

    Args:
     * username: username for API authentication
     * password: password for API authentication

    Returns:
     * an instance of `TranskribusApi`
    """
    api = TranskribusApi(username, password)
    yield api
    api.close()
