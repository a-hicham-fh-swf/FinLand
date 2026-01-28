def fmt(value):
    """
    Formatierung für UI-Anzeige:
    - None -> "–"
    - Zahlen -> mit Tausenderpunkten und 2 Dezimalstellen
    - alles andere -> string
    """
    if value is None:
        return "–"
    if isinstance(value, (int, float)):
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(value)


def format_percent_change(change):
    """
    UI-Logik für Prozentanzeige:
    - None -> "–"
    - >= 0 -> "+x.xx%"
    - < 0  -> "-x.xx%"
    """
    if change is None:
        return "–"
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.2f}%"


def should_show_chart(dataframe):
    """
    UI-Logik:
    - Chart nur anzeigen, wenn dataframe nicht None und nicht leer ist.
    """
    return dataframe is not None and not dataframe.empty
