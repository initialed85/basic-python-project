import datetime
import time
import unittest

from hamcrest import assert_that, calling, equal_to, raises
from mock import MagicMock, call, patch
from requests.exceptions import ReadTimeout

from basic_project import Fortune, FortuneRequestFailed

_TEST_RAW_DATA = b'"Append your ssh key to your server\'s authorized keys file using the command\\n\'ssh-copy-id user@server_address\'\\n"'

_TEST_DECODED_DATA = "Append your ssh key to your server's authorized keys file using the command\n'ssh-copy-id user@server_address'"

_TEST_TIMESTAMP = datetime.datetime(year=1991, month=2, day=6)


class FortuneTest(unittest.TestCase):
    @patch('basic_project.fortune.Session')
    def setUp(self, Session):
        self._subject = Fortune()

    def test_singleton(self):
        # these two instances should be the same as self._subject (because Fortune is a singleton)
        a = Fortune()
        b = Fortune()

        assert_that(
            a is self._subject,
            equal_to(True)
        )

        assert_that(
            b is self._subject,
            equal_to(True)
        )

    def test_get_fortune_pass(self):
        response = MagicMock()
        response.status_code = 200
        response.content = _TEST_RAW_DATA

        session = MagicMock()
        session.get.return_value = response

        self._subject._session.__enter__.return_value = session

        # one call to the get_fortune method
        assert_that(
            self._subject.get_fortune(now=_TEST_TIMESTAMP),
            equal_to(_TEST_DECODED_DATA)
        )

        # results in one call to the Session
        assert_that(
            session.mock_calls,
            equal_to([
                call.get(self._subject._api_url)
            ])
        )

        # and recording of the timestamp the call was made
        assert_that(
            self._subject._last_request,
            equal_to(_TEST_TIMESTAMP)
        )

    def test_get_fortune_pass_cached_request(self):
        session = MagicMock()
        self._subject._session.__enter__.return_value = session

        self._subject._last_request = _TEST_TIMESTAMP - datetime.timedelta(seconds=0.9)
        self._subject._last_response = _TEST_DECODED_DATA

        assert_that(
            self._subject.get_fortune(now=_TEST_TIMESTAMP),
            equal_to(_TEST_DECODED_DATA)
        )

        assert_that(
            session.mock_calls,
            equal_to([])
        )

        assert_that(
            self._subject._last_request,
            equal_to(_TEST_TIMESTAMP - datetime.timedelta(seconds=0.9))
        )

    def test_get_fortune_request_404(self):
        response = MagicMock()
        response.status_code = 404
        response.content = b"URL not found"

        session = MagicMock()
        session.get.return_value = response

        self._subject._session.__enter__.return_value = session

        assert_that(
            calling(self._subject.get_fortune).with_args(now=_TEST_TIMESTAMP),
            raises(FortuneRequestFailed)
        )

        assert_that(
            session.mock_calls,
            equal_to([
                call.get(self._subject._api_url)
            ])
        )

        assert_that(
            self._subject._last_request,
            equal_to(_TEST_TIMESTAMP)
        )

    def test_get_fortune_request_timeout(self):
        session = MagicMock()
        session.get.side_effect = ReadTimeout('request timed out')

        self._subject._session.__enter__.return_value = session

        assert_that(
            calling(self._subject.get_fortune),
            raises(FortuneRequestFailed)
        )

        assert_that(
            session.mock_calls,
            equal_to([
                call.get(self._subject._api_url)
            ])
        )

        assert_that(
            self._subject._last_request,
            equal_to(None)
        )

    def test_get_fortune_pass_many_attempts_at_str_magic_method(self):
        response = MagicMock()
        response.status_code = 200
        response.content = _TEST_RAW_DATA

        session = MagicMock()
        session.get.return_value = response

        self._subject._session.__enter__.return_value = session

        # handful of calls
        [
            assert_that(
                str(self._subject),
                equal_to(_TEST_DECODED_DATA)
            ) for _ in range(0, 32)
        ]

        time.sleep(1)

        # a handful more calls
        for _ in range(0, 32):
            assert_that(
                str(self._subject),
                equal_to(_TEST_DECODED_DATA)
            )

        # but there are only two calls to the Session
        assert_that(
            session.mock_calls,
            equal_to([
                call.get(self._subject._api_url),
                call.get(self._subject._api_url),
            ])
        )
