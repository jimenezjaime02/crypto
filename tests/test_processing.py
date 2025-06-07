import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from processing import transform_json, validate_records, enrich_indicators


def sample_raw():
    return {
        "prices": [[0, 1.0], [86400, 2.0]],
        "total_volumes": [[0, 10], [86400, 20]],
        "market_caps": [[0, 100], [86400, 200]],
    }


def sample_ohlc():
    return [[0, 0.5, 1.5, 0.4, 1.0], [86400, 1.5, 2.2, 1.0, 2.0]]


def test_transform_and_validate():
    recs = transform_json(sample_raw(), "tst", sample_ohlc())
    recs = validate_records(recs)
    assert len(recs) == 2
    assert recs[0]["Open"] == 0.5


def test_enrich_indicators():
    recs = transform_json(sample_raw(), "tst", sample_ohlc())
    recs = validate_records(recs)
    enriched = enrich_indicators(recs, [7])
    # macd etc produce None for early rows; just check key exists
    assert "macd" in enriched[-1]
