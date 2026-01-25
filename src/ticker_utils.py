import re
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta

__compiled_pattern = re.compile('^([1-9][0-9]*)(d|mo|y)$')

def get_latest_close(ticker_data):
    return ticker_data['Close'].iloc[-1]

def get_interval_text(ticker_data):
    start_date = get_start_date(ticker_data)
    end_date = get_end_date(ticker_data)
    return f'vom {start_date.strftime("%d.%m.%Y")} bis {end_date.strftime("%d.%m.%Y")}'

def get_start_date(ticker_data):
    return ticker_data.index.min().date()

def get_end_date(ticker_data):
    return ticker_data.index.max().date()

def get_high_market_price(ticker_data):
    high_market_price_date = ticker_data['High'].idxmax()
    return ticker_data.loc[high_market_price_date]['High'], high_market_price_date

def get_low_market_price(ticker_data):
    low_market_price_date = ticker_data['Low'].idxmin()
    return ticker_data.loc[low_market_price_date]['Low'], low_market_price_date

def get_min_date_in_period_from_now(period, now):
    period = get_next_suitable_period(period)
    print(f'found period: {period}')
    match period:
        case '1d': return (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        case '5d': return (now - timedelta(days=5)).replace(hour=0, minute=0, second=0, microsecond=0)
        case '1mo': return (now - relativedelta(month=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        case '3mo': return (now - relativedelta(month=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        case '6mo': return (now - relativedelta(month=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        case '1y': return (now - relativedelta(year=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        case '2y': return (now - relativedelta(year=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        case '5y': return (now - relativedelta(year=5)).replace(hour=0, minute=0, second=0, microsecond=0)
        case '10y': return (now - relativedelta(year=10)).replace(hour=0, minute=0, second=0, microsecond=0)
        case 'ytd': return datetime(datetime.now().year, 1, 1)
    return None

def get_next_suitable_period(period_input):
    # 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    if not period_input or period_input == 'max':
        return None

    if period_input == 'ytd':
        return period_input

    match = __compiled_pattern.match(period_input)

    if match is None:
        raise ValueError('Invalid input')

    days = 0
    months = 0
    years = 0

    match match.group(2):
        case 'd':
            days = int(match.group(1))
            months = days / 30
            years = days / 365
        case 'mo':
            months = int(match.group(1))
            years = months / 12
        case 'y':
            years = int(match.group(1))

    if years >= 1:
        if (years == 1 or years == 2) and months == 0:
            return str(years) + 'y'
        if years <= 5:
            return '5y'
        if years <= 10:
            return '10y'
    elif months >= 1:
        if months == 1:
            return '1mo'
        if months <= 3:
            return '3mo'
        if months <= 6:
            return '6mo'
        return '1y'
    elif days >= 1:
        if days == 1:
            return '1d'
        if days <= 5:
            return '5d'
        return '1mo'

    return None