import datetime
import unittest

from hamcrest import assert_that, equal_to, calling, raises
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
        f = Fortune()

        assert_that(
            self._subject is f,
            equal_to(True)
        )

    def test_get_fortune_pass(self):
        response = MagicMock()
        response.status_code = 200
        response.content = _TEST_RAW_DATA

        session = MagicMock()
        session.get.return_value = response

        self._subject._session.__enter__.return_value = session

        assert_that(
            self._subject.get_fortune(),
            equal_to(_TEST_DECODED_DATA)
        )

        assert_that(
            session.mock_calls,
            equal_to([
                call.get(self._subject._api_url)
            ])
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

    def test_get_fortune_request_404(self):
        response = MagicMock()
        response.status_code = 404
        response.content = b"URL not found"

        session = MagicMock()
        session.get.return_value = response

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
