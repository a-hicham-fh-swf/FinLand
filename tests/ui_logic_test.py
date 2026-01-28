import pandas as pd

from ui_logic import fmt, format_percent_change, should_show_chart


def test_TC_UI_001_fmt_none_returns_dash():
    # GIVEN: value ist None
    value = None

    # WHEN: fmt wird aufgerufen
    result = fmt(value)

    # THEN: UI zeigt einen Platzhalter
    assert result == "–"


def test_TC_UI_001_fmt_number_is_formatted_german_style():
    # GIVEN: value ist eine Zahl
    value = 12345.6789

    # WHEN: fmt wird aufgerufen
    result = fmt(value)

    # THEN: 2 Dezimalstellen + Tausenderpunkt (deutsches Format)
    assert result == "12.345,68"


def test_TC_UI_002_percent_change_positive_has_plus():
    # GIVEN: positive Prozentänderung
    change = 1.234

    # WHEN: format_percent_change wird aufgerufen
    result = format_percent_change(change)

    # THEN: Plus-Zeichen und Prozentformat
    assert result == "+1.23%"


def test_TC_UI_002_percent_change_negative_has_no_plus():
    # GIVEN: negative Prozentänderung
    change = -2.5

    # WHEN: format_percent_change wird aufgerufen
    result = format_percent_change(change)

    # THEN: Minus ist automatisch enthalten, kein extra Plus
    assert result == "-2.50%"


def test_TC_UI_003_should_show_chart_true_for_non_empty_dataframe():
    # GIVEN: ein nicht-leeres DataFrame
    df = pd.DataFrame({"Close": [1, 2, 3]})

    # WHEN: should_show_chart wird aufgerufen
    result = should_show_chart(df)

    # THEN: Chart darf angezeigt werden
    assert result is True


def test_TC_UI_003_should_show_chart_false_for_empty_dataframe():
    # GIVEN: ein leeres DataFrame
    df = pd.DataFrame()

    # WHEN: should_show_chart wird aufgerufen
    result = should_show_chart(df)

    # THEN: Chart darf NICHT angezeigt werden
    assert result is False


def test_TC_UI_003_should_show_chart_false_for_none():
    # GIVEN: keine Daten
    df = None

    # WHEN: should_show_chart wird aufgerufen
    result = should_show_chart(df)

    # THEN: Chart darf NICHT angezeigt werden
    assert result is False
