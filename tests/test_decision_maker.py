import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from decision_maker import decide


def test_decide_buy():
    row = {"RSI_14": "25", "MACD_hist": "0.5"}
    assert decide(row) == "BUY"


def test_decide_sell():
    row = {"RSI_14": "75", "MACD_hist": "-1"}
    assert decide(row) == "SELL"


def test_decide_hold():
    row = {"RSI_14": "50", "MACD_hist": "0"}
    assert decide(row) == "HOLD"
