from nselib import capital_market
import pandas as pd
import argparse
import re
from prettytable import PrettyTable


def get_adjustment_factor(subject: str):
    subject = (subject or '').lower()
    if 'bonus' in subject:
        m = re.search(r'bonus\s*(\d+)\s*[:\-]\s*(\d+)', subject)
        if m:
            bonus = int(m.group(1))
            existing = int(m.group(2))
            if existing + bonus > 0:
                return existing / (existing + bonus)
    if 'face value' in subject or 'sub-division' in subject or 'split' in subject or 'consolidation' in subject:
        m = re.search(r'from\s*(?:rs|re)\s*([0-9.]+).*to\s*(?:rs|re)\s*([0-9.]+)', subject)
        if m:
            old_face = float(m.group(1))
            new_face = float(m.group(2))
            if old_face > 0:
                return new_face / old_face
    return 1.0


def historical_for_date(trade_date: str):
    """Return a dataframe of Nifty50 symbols with perChange for the given date.

    Expects `trade_date` in 'dd-mm-YYYY' format (same as `bhav_copy_equities`).
    """
    bhav = capital_market.bhav_copy_equities(trade_date)
    if bhav.empty:
        return pd.DataFrame()

    # Normalize column names to upper for safety
    bhav.columns = bhav.columns.str.upper()
    cols = set(bhav.columns)

    # detect symbol / close / prevclose column names from common bhav variants
    def find_col(candidates):
        for c in candidates:
            if c in cols:
                return c
        for c in cols:
            for pat in candidates:
                if pat in c:
                    return c
        return None

    symbol_col = find_col(['SYMBOL', 'TCKRSYMB', 'TCKR', 'SYMB'])
    close_col = find_col(['CLOSE', 'CLSPRICE', 'CLSPRIC', 'CLS', 'CLOSEPR'])
    prev_col = find_col(['PREVCLOSE', 'PRVSCLSGPRIC', 'PRVS', 'PREV'])
    series_col = find_col(['SCTYSRS', 'SCTY', 'SERIES'])

    if not symbol_col or not close_col or not prev_col:
        raise RuntimeError(f'Unexpected bhav columns; found: {list(cols)[:20]}')

    bhav_nifty = bhav[bhav[symbol_col].isin(capital_market.nifty50_equity_list()['Symbol'])]
    if series_col is not None:
        bhav_nifty = bhav_nifty[bhav_nifty[series_col] == 'EQ']
    if bhav_nifty.empty:
        return pd.DataFrame()

    # prefer one row per symbol when there are still duplicates
    if 'TTLTRADGVOL' in bhav_nifty.columns:
        bhav_nifty = bhav_nifty.sort_values('TTLTRADGVOL', ascending=False)
    bhav_nifty = bhav_nifty.drop_duplicates(subset=symbol_col, keep='first')

    # compute percent change
    bhav_nifty = bhav_nifty.copy()
    bhav_nifty['symbol'] = bhav_nifty[symbol_col]
    bhav_nifty['close'] = bhav_nifty[close_col]
    bhav_nifty['raw_prev'] = bhav_nifty[prev_col]

    # apply corporate action adjustment if the trade date is an ex-date
    date = pd.to_datetime(trade_date, format='%d-%m-%Y')
    ca = capital_market.corporate_actions_for_equity(
        from_date=date.strftime('%d-%m-%Y'),
        to_date=(date + pd.Timedelta(days=1)).strftime('%d-%m-%Y'),
    )
    ca = ca[ca['symbol'].isin(bhav_nifty['symbol'].unique())]
    adjustments = {}
    for _, row in ca.iterrows():
        factor = get_adjustment_factor(str(row['subject']))
        if factor != 1.0:
            adjustments[row['symbol']] = factor

    bhav_nifty['adjust_factor'] = bhav_nifty['symbol'].map(adjustments).fillna(1.0)
    bhav_nifty['prev_price'] = bhav_nifty['raw_prev'] * bhav_nifty['adjust_factor']
    bhav_nifty['perChange'] = (bhav_nifty['close'] - bhav_nifty['prev_price']) / bhav_nifty['prev_price'] * 100

    bhav_nifty['ltp'] = bhav_nifty['close']
    result = bhav_nifty[['symbol', 'perChange', 'ltp', 'prev_price']]
    return result.sort_values('perChange', ascending=False)


def current_market():
	nifty50 = capital_market.nifty50_equity_list()
	nifty_symbols = set(nifty50['Symbol'].tolist())

	gainers = capital_market.top_gainers_or_losers(to_get='gainers')
	losers = capital_market.top_gainers_or_losers(to_get='loosers')

	all_moves = pd.concat([gainers, losers], ignore_index=True)
	nifty_only = all_moves[all_moves['symbol'].isin(nifty_symbols)]
	nifty_sorted = nifty_only.sort_values('perChange', ascending=False)
	nifty_unique = nifty_sorted.drop_duplicates(subset='symbol', keep='first')
	return nifty_unique[['symbol', 'perChange', 'ltp', 'prev_price']]


def format_market_output(df: pd.DataFrame) -> str:
    if df.empty:
        return 'No data found for the requested date or market.'
    return df.reset_index(drop=True).to_string(index=False)


def pretty_table_from_text(text: str) -> str:
    """Convert whitespace-separated table text into a PrettyTable string."""
    if not text or not text.strip():
        return ''

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return ''

    rows = [line.split() for line in lines]
    header, *data_rows = rows

    table = PrettyTable()
    table.field_names = header
    for row in data_rows:
        if len(row) == len(header):
            table.add_row(row)
        else:
            # preserve the row as a single cell when splitting does not match
            table.add_row([text])
            break

    return table.get_string()


def get_market_summary_nseLandG(date: str = None) -> str:
    if date:
        df = historical_for_date(date)
    else:
        df = current_market()
    return format_market_output(df)


def run_cli() -> str:
    parser = argparse.ArgumentParser(description='Fetch Nifty50 gainers/losers (current or historical)')
    parser.add_argument('--date', '-d', help="Historical trade date in dd-mm-YYYY format. If omitted, uses live top gainers/losers.")
    args = parser.parse_args()
    return get_market_summary_nseLandG(args.date)


if __name__ == '__main__':
    print(pretty_table_from_text(run_cli()))
