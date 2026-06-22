import pytest

from src.helpers import parse_insight


SAMPLE_CORRECT_INSIGHT = """ Here is the structured analysis for the Reliance Industries Limited (RIL) news item:
{"sentiment": "neutral",
"urgency_score": 2,
"catalyst_type": "corporate",
"catalyst_summary": "Institutional investors prepare to participate in Jio's upcoming listing, raising analytical questions regarding potential holding company valuation discounts for Reliance Industries Ltd (RIL).",
"is_market_moving": true
}
"""


def test_parse_insights():
    """
    Test for correct insight
    """
    parsed = parse_insight(SAMPLE_CORRECT_INSIGHT)
    assert parsed.get('sentiment')
    assert parsed.get('urgency_score')
    assert parsed.get('catalyst_type')
    assert parsed.get('catalyst_summary')
    assert parsed.get('is_market_moving')


def test_parse_no_json():
    """
    Test for empty json in insight
    """
    SAMPLE_INCORRECT_INSIGHT = """
        (
            "sentiment": "neutral",
            "urgency_score": 2,
            "catalyst_type": "corporate",
            "catalyst_summary": "Institutional investors prepare to participate in Jio's upcoming listing, raising analytical questions regarding potential holding company valuation discounts for Reliance Industries Ltd (RIL).",
            "is_market_moving": true
        )
        """
    with pytest.raises(ValueError):
        parse_insight(SAMPLE_INCORRECT_INSIGHT)
