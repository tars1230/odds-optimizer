import pytest
from app.scrapers.parser import parse_odds_page, parse_match_row


class TestParseMatchRow:
    def test_parse_simple_row(self):
        html = """
        <tr>
            <td>英超</td>
            <td>利物浦</td>
            <td>曼城</td>
            <td>2025-01-15 20:00</td>
            <td>2.10</td>
            <td>3.40</td>
            <td>3.20</td>
        </tr>
        """
        result = parse_match_row(html)
        assert result is not None
        assert result["league"] == "英超"
        assert result["home_team"] == "利物浦"
        assert result["away_team"] == "曼城"
        assert result["odds"]["home"] == 2.10
        assert result["odds"]["draw"] == 3.40
        assert result["odds"]["away"] == 3.20

    def test_returns_none_for_invalid(self):
        result = parse_match_row("<div>not a match</div>")
        assert result is None