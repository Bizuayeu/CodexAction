from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from adapters.rss.rss_xml_gateway import RssXmlGateway
from domain.exceptions import RssFetchError

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_rss.xml"
SAMPLE_XML = FIXTURE_PATH.read_bytes()


def _mock_urlopen(content: bytes = SAMPLE_XML, status: int = 200):
    """contextmanager 互換の mock response を返すヘルパー."""
    response = MagicMock()
    response.read.return_value = content
    response.status = status
    response.getcode.return_value = status
    response.__enter__ = lambda self: response
    response.__exit__ = lambda self, *args: None
    return response


def test_sends_chrome_user_agent_header():
    captured = {}

    def fake_urlopen(request, timeout=None):
        captured["headers"] = dict(request.header_items())
        captured["url"] = request.full_url
        return _mock_urlopen()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        gw = RssXmlGateway(
            rss_url="https://news.nullevi.app/rss",
            user_agent="Mozilla/5.0 Chrome/124.0 TestUA",
        )
        gw.fetch_all()

    ua_value = None
    for key, val in captured["headers"].items():
        if key.lower() == "user-agent":
            ua_value = val
    assert ua_value is not None
    assert "Mozilla" in ua_value
    assert "Chrome" in ua_value
    assert captured["url"] == "https://news.nullevi.app/rss"


def test_parses_cdata_titles():
    with patch("urllib.request.urlopen", return_value=_mock_urlopen()):
        gw = RssXmlGateway(rss_url="https://news.nullevi.app/rss", user_agent="UA")
        items = gw.fetch_all()
    titles = [i.title for i in items]
    assert "グーグル、AIを悪用した大規模ハッキング未遂を初検知" in titles
    assert "危険すぎるAI「クロード・ミュトス」対策、週内にも作業部会" in titles


def test_parses_categories_as_csv_tuple():
    with patch("urllib.request.urlopen", return_value=_mock_urlopen()):
        gw = RssXmlGateway(rss_url="https://news.nullevi.app/rss", user_agent="UA")
        items = gw.fetch_all()

    google_item = [i for i in items if "グーグル" in i.title][0]
    assert google_item.categories == (
        "Google",
        "AI悪用",
        "サイバーセキュリティ",
        "脆弱性",
    )


def test_handles_item_without_category():
    with patch("urllib.request.urlopen", return_value=_mock_urlopen()):
        gw = RssXmlGateway(rss_url="https://news.nullevi.app/rss", user_agent="UA")
        items = gw.fetch_all()
    no_cat = [i for i in items if i.title == "カテゴリ無しエントリ"][0]
    assert no_cat.categories == ()


def test_parses_three_items_total():
    with patch("urllib.request.urlopen", return_value=_mock_urlopen()):
        gw = RssXmlGateway(rss_url="https://news.nullevi.app/rss", user_agent="UA")
        items = gw.fetch_all()
    assert len(items) == 3


def test_http_error_raises_rss_fetch_error():
    import urllib.error

    def raising(*args, **kwargs):
        raise urllib.error.HTTPError(
            "https://news.nullevi.app/rss", 403, "Forbidden", {}, None
        )

    with patch("urllib.request.urlopen", side_effect=raising):
        gw = RssXmlGateway(rss_url="https://news.nullevi.app/rss", user_agent="UA")
        with pytest.raises(RssFetchError) as excinfo:
            gw.fetch_all()
        assert excinfo.value.status_code == 403


def test_url_error_raises_rss_fetch_error():
    import urllib.error

    def raising(*args, **kwargs):
        raise urllib.error.URLError("connection refused")

    with patch("urllib.request.urlopen", side_effect=raising):
        gw = RssXmlGateway(rss_url="https://news.nullevi.app/rss", user_agent="UA")
        with pytest.raises(RssFetchError) as excinfo:
            gw.fetch_all()
        assert excinfo.value.status_code is None


def test_malformed_xml_raises_rss_fetch_error():
    with patch(
        "urllib.request.urlopen", return_value=_mock_urlopen(content=b"<not-xml>")
    ):
        gw = RssXmlGateway(rss_url="https://news.nullevi.app/rss", user_agent="UA")
        with pytest.raises(RssFetchError):
            gw.fetch_all()
