import codecs
import datetime
from sys import version_info

from requests import Session

# this is one of the URLs from https://helloacm.com/fortune/
_API_URL = 'https://happyukgo.com/api/fortune/'

_ESCAPE_ENCODING = 'string_escape' if version_info[0] < 3 else 'unicode_escape'


class FortuneRequestFailed(Exception):
    pass


class Fortune(object):
    """Fortune is a rate-limited singleton interface to an internet Fortune API"""

    _instance = None  # variable to hold the singleton instance

    def __new__(cls):
        if cls._instance is None:  # if the instance is not yet defined, create a new instance
            cls._instance = object.__new__(cls)

        return cls._instance

    def __init__(self, api_url=None, rate_limit_seconds=None):
        """
        :param api_url: override default Fortune API URL of https://happyukgo.com/api/fortune/
        :param rate_limit_seconds: override default period between requests of 1 second
        """

        self._api_url = api_url if api_url is not None else _API_URL
        self._rate_limit_seconds = rate_limit_seconds if rate_limit_seconds is not None else 1

        self._session = Session()

        self._last_request = None
        self._last_response = None

    def get_fortune(self, now=None):
        """
        :param now: override current timestamp (for testing)
        :return: Fortune as a string
        """
        now = now if now is not None else datetime.datetime.now()

        # handle the rate limiting
        if self._last_request is not None and (now - self._last_request).total_seconds() < self._rate_limit_seconds:
            return self._last_response

        with self._session as s:
            try:
                r = s.get(self._api_url)
                self._last_request = now
            except Exception as e:
                raise FortuneRequestFailed(e)

            if r.status_code != 200:
                raise FortuneRequestFailed('fortune request to {0} returned status code {1} - {2}'.format(
                    repr(self._api_url),
                    r.status_code,
                    repr(r.content)
                ))

            text = r.content.decode(_ESCAPE_ENCODING).strip(' \r\n\t"')

            self._last_response = text

            return text

    def __str__(self):
        """duck-typing for the Fortune instance as a string"""
        
        return self.get_fortune()
