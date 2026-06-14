import filecmp
import json
import os
from unittest import TestCase

from courtside_data import client
from courtside_data.data import OutputType, OutputWriteOption
from tests import http_mock as requests_mock
from tests.integration.client import raw_fixtures


def _dump_results(results):
    return [result.model_dump(mode="python") for result in results]


@requests_mock.Mocker()
class TestJa(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_ja_page(0)
        self._1_html = raw_fixtures.search_ja_page(1)
        self._2_html = raw_fixtures.search_ja_page(2)
        self._3_html = raw_fixtures.search_ja_page(3)
        self._4_html = raw_fixtures.search_ja_page(4)
        self._5_html = raw_fixtures.search_ja_page(5)
        self._6_html = raw_fixtures.search_ja_page(6)
        self._7_html = raw_fixtures.search_ja_page(7)
        self._8_html = raw_fixtures.search_ja_page(8)

    def test_length(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja",
            text=self._html,
            status_code=200,
            complete_qs=True,
        )  # Exact match: prevents subset fallback to this mock from later pagination requests
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&idx=players&offset=100",
            text=self._1_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&idx=players&offset=200",
            text=self._2_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&idx=players&offset=300",
            text=self._3_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&idx=players&offset=400",
            text=self._4_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&idx=players&offset=500",
            text=self._5_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&idx=players&offset=600",
            text=self._6_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&idx=players&offset=700",
            text=self._7_html,
            status_code=200,
        )
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=ja&idx=players&offset=800",
            text=self._8_html,
            status_code=200,
        )
        results = client.search(term="ja")
        # 1 initial request + 8 paginated requests = 9 total
        self.assertEqual(9, m.call_count)
        self.assertEqual(888, len(results))
        self.assertEqual(
            {"name": "LeBron James", "identifier": "jamesle01", "leagues": set()}, results[0].model_dump(mode="python")
        )


@requests_mock.Mocker()
class TestAlonzoMourning(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("Alonzo Mourning")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=Alonzo+Mourning",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="Alonzo Mourning")
        self.assertEqual(
            [
                {
                    "name": "Alonzo Mourning",
                    "identifier": "mournal01",
                    # Basketball-Reference moved leagues from the search results
                    "leagues": set(),
                }
            ],
            _dump_results(results),
        )


@requests_mock.Mocker()
class TestDominiqueWilkins(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("Dominique Wilkins")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=Dominique+Wilkins",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="Dominique Wilkins")
        self.assertEqual(
            [{"name": "Dominique Wilkins", "identifier": "wilkido01", "leagues": set()}], _dump_results(results)
        )


@requests_mock.Mocker()
class TestRickBarry(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("Rick Barry")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=Rick+Barry",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="Rick Barry")
        self.assertEqual([{"name": "Rick Barry", "identifier": "barryri01", "leagues": set()}], _dump_results(results))


@requests_mock.Mocker()
class TestJaebaebae(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("jaebaebae")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=jaebaebae", text=self._html, status_code=200
        )
        results = client.search(term="jaebaebae")
        self.assertEqual([], results)


@requests_mock.Mocker()
class TestKobeBryant(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("kobe bryant")

    def test_result(self, m):
        m.get(
            "https://www.basketball-reference.com/search/search.fcgi?search=kobe+bryant",
            text=self._html,
            status_code=200,
        )
        results = client.search(term="kobe bryant")
        self.assertEqual([{"name": "Kobe Bryant", "identifier": "bryanko01", "leagues": set()}], _dump_results(results))


@requests_mock.Mocker()
class TestKobe(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("kobe")

    def test_result(self, m):
        m.get("https://www.basketball-reference.com/search/search.fcgi?search=kobe", text=self._html, status_code=200)
        results = client.search(term="kobe")
        self.assertEqual(
            [
                {"name": "Kobe Bryant", "identifier": "bryanko01", "leagues": set()},
                {"name": "Ruben Patterson", "identifier": "patteru01", "leagues": set()},
                {"name": "Dion Waiters", "identifier": "waitedi01", "leagues": set()},
                {"name": "Austin Reaves", "identifier": "reaveau01", "leagues": set()},
                {"name": "Kobe Brown", "identifier": "brownko01", "leagues": set()},
                {"name": "Kobe Sanders", "identifier": "sandeko01", "leagues": set()},
                {"name": "Kobe Bufkin", "identifier": "bufkiko01", "leagues": set()},
                {"name": "Kobe Johnson", "identifier": "johnsko01", "leagues": set()},
                {"name": "Oleksandr Kobets", "identifier": "kobetol01", "leagues": set()},
            ],
            _dump_results(results),
        )


@requests_mock.Mocker()
class TestSearchJSONFileOutput(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("kobe")
        self.output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/generated/search/kobe.json",
        )
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/expected/search/kobe.json",
        )

    def tearDown(self):
        os.remove(self.output_file_path)

    def test_file_output(self, m):
        m.get("https://www.basketball-reference.com/search/search.fcgi?search=kobe", text=self._html, status_code=200)

        client.search(
            term="kobe",
            output_type=OutputType.JSON,
            output_file_path=self.output_file_path,
            output_write_option=OutputWriteOption.WRITE,
        )
        self.assertTrue(filecmp.cmp(self.output_file_path, self.expected_output_file_path))


@requests_mock.Mocker()
class TestSearchJSONInMemoryOutput(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("kobe")
        self.output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/generated/search/kobe.json",
        )
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/expected/search/kobe.json",
        )

    def test_in_memory_output(self, m):
        m.get("https://www.basketball-reference.com/search/search.fcgi?search=kobe", text=self._html, status_code=200)

        results = client.search(
            term="kobe",
            output_type=OutputType.JSON,
        )
        with open(self.expected_output_file_path, encoding="utf8") as expected_output_file:
            self.assertEqual(
                json.loads(results),
                json.load(expected_output_file),
            )


@requests_mock.Mocker()
class TestSearchCSVOutput(TestCase):
    def setUp(self):
        self._html = raw_fixtures.search_term("kobe")
        self.output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/generated/search/kobe.csv",
        )
        self.expected_output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/expected/search/kobe.csv",
        )

    def tearDown(self):
        os.remove(self.output_file_path)

    def test_file_output(self, m):
        m.get("https://www.basketball-reference.com/search/search.fcgi?search=kobe", text=self._html, status_code=200)

        client.search(
            term="kobe",
            output_type=OutputType.CSV,
            output_file_path=self.output_file_path,
            output_write_option=OutputWriteOption.WRITE,
        )

        self.assertTrue(filecmp.cmp(self.output_file_path, self.expected_output_file_path))
