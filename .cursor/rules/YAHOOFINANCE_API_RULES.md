# Yahoo Finance API Rules & Reference Guide

## Overview
This document provides structured rules and guidelines for using the `yahoofinance` Python library API.

**Note**: The API is currently under development and things may change rapidly. Classes marked as **EXPERIMENTAL** may have varying results as data is scraped from the website. Use at your own risk!

---

## Core Interface

### `IYahooData` Base Interface
All classes in the library implement this interface.

**Rules:**
- This class is NOT instantiable
- All implementing classes must accept a `locale` parameter
- All implementing classes provide `to_csv()` and `to_dfs()` methods

**Methods:**
- `to_csv()` - Generates a CSV file
- `to_dfs()` - Generates a dictionary containing `pandas.DataFrame`

---

## Historical Data Classes

### `HistoricalPrices`
Retrieves historical data from Yahoo Finance.

**Example URL:** https://finance.yahoo.com/quote/AAPL/history

**Parameters:**
- `instrument` (required) - Stock instrument code to query
- `start_date` (required) - Start date for query (inclusive)
- `end_date` (required) - End date for query (inclusive)
- `date_format_string` (optional) - Format string for date parsing. Default: `'%Y-%m-%d'`
- `event` (optional) - DataEvent constant for event type. Default: `DataEvent.HISTORICAL_PRICES`
- `frequency` (optional) - DataFrequency constant for interval. Default: `DataFrequency.DAILY`
- `locale` (optional) - Locale constant for domain. Default: `Locale.US`

**Usage:**
```python
from yahoofinance import HistoricalPrices
req = HistoricalPrices('AAPL')
```

**Methods:**
- `to_csv(path=None, sep=',', data_format='raw', csv_dialect='excel')`
  - `path` - File location path. If None, returns CSV as string
  - `sep` - Separator between elements (NOT USED)
  - `data_format` - DataFormat constant (NOT USED)
  - `csv_dialect` - CSV dialect for writing
  
- `to_dfs(data_format='raw')`
  - Returns: `pandas.DataFrame`
  - Dictionary key: "Historical Prices"

---

## Balance Sheet Classes

### `BalanceSheet` (EXPERIMENTAL)
Retrieves annual balance sheet information.

**Example URL:** https://finance.yahoo.com/quote/AAPL/balance-sheet

**Parameters:**
- `stock` (required) - Stock code to query
- `locale` (optional) - Locale constant. Default: `Locale.US`

**Usage:**
```python
from yahoofinance import BalanceSheet
req = BalanceSheet('AAPL')
```

**Methods:**
- `to_csv(path=None, sep=',', data_format='raw', csv_dialect='excel')`
- `to_dfs(data_format='raw')` - Returns pandas.DataFrame

**Dictionary Keys:**
- Cash Flow
- Overall
- Operating activities
- Investment activities
- Financing activities
- Changes in Cash

### `BalanceSheetQuarterly` (EXPERIMENTAL)
Retrieves quarterly balance sheet information.

**Example URL:** https://finance.yahoo.com/quote/AAPL/balance-sheet

**Parameters:** Same as `BalanceSheet`

**Usage:**
```python
from yahoofinance import BalanceSheetQuarterly
req = BalanceSheetQuarterly('AAPL')
```

---

## Cash Flow Classes

### `CashFlow` (EXPERIMENTAL)
Retrieves annual cash flow information.

**Example URL:** https://finance.yahoo.com/quote/AAPL/cash-flow

**Parameters:**
- `stock` (required) - Stock code to query
- `locale` (optional) - Locale constant. Default: `Locale.US`

**Usage:**
```python
from yahoofinance import CashFlow
req = CashFlow('AAPL')
```

**Methods:**
- `to_csv(path=None, sep=',', data_format='raw', csv_dialect='excel')`
- `to_dfs(data_format='raw')` - Returns pandas.DataFrame

**Dictionary Keys:**
- Cash Flow
- Overall
- Operating activities
- Investment activities
- Financing activities
- Changes in Cash

### `CashFlowQuarterly` (EXPERIMENTAL)
Retrieves quarterly cash flow information.

**Example URL:** https://finance.yahoo.com/quote/AAPL/cash-flow

**Parameters:** Same as `CashFlow`

**Usage:**
```python
from yahoofinance import CashFlowQuarterly
req = CashFlowQuarterly('AAPL')
```

---

## Income Statement Classes

### `IncomeStatement` (EXPERIMENTAL)
Retrieves annual income statement information.

**Example URL:** https://finance.yahoo.com/quote/AAPL/financials

**Parameters:**
- `stock` (required) - Stock code to query
- `locale` (optional) - Locale constant. Default: `Locale.US`

**Usage:**
```python
from yahoofinance import IncomeStatement
req = IncomeStatement('AAPL')
```

**Methods:**
- `to_csv(path=None, sep=',', data_format='raw', csv_dialect='excel')`
- `to_dfs(data_format='raw')` - Returns pandas.DataFrame

**Dictionary Keys:**
- Cash Flow
- Overall
- Operating activities
- Investment activities
- Financing activities
- Changes in Cash

### `IncomeStatementQuarterly` (EXPERIMENTAL)
Retrieves quarterly income statement information.

**Example URL:** https://finance.yahoo.com/quote/AAPL/financials

**Parameters:** Same as `IncomeStatement`

**Usage:**
```python
from yahoofinance import IncomeStatementQuarterly
req = IncomeStatementQuarterly('AAPL')
```

---

## Asset Profile Classes

### `AssetProfile` (EXPERIMENTAL)
Retrieves the asset profile information.

**Example URL:** https://finance.yahoo.com/quote/AAPL/profile

**Parameters:**
- `stock` (required) - Stock ticker
- `locale` (optional) - Locale constant. Default: `Locale.US`

**Usage:**
```python
from yahoofinance import AssetProfile
req = AssetProfile('AAPL')
```

**Methods:**
- `to_csv(path, sep=',', data_format='raw', csv_dialect='excel')`
  - `path` (required) - File location path. If None, returns CSV as string
  - `sep` - Separator (NOT USED)
  - `data_format` - DataFormat constant (NOT USED)
  - `csv_dialect` - CSV dialect
  
- `to_dfs(data_format='raw')` - Returns pandas.DataFrame

---

## Configuration Classes

### `Locale`
Provides locale information to any `IYahooData` implementations.

**Purpose:** Using your local domain may speed up queries or bypass certain country domain filters.

**Constants:**
- `Locale.US = ''` - United States domain (https://finance.yahoo.com/quote/AAPL/)
- `Locale.AU = 'au'` - Australian domain (https://au.finance.yahoo.com/quote/AAPL/)
- `Locale.CA = 'ca'` - Canadian domain (https://ca.finance.yahoo.com/quote/AAPL/)

**Static Methods:**
- `locale_url(locale)` - Determines the domain URL for a locale
  - Parameters: locale string constant
  - Returns: URL string

### `DataEvent`
Provides data event information for `HistoricalData`.

**Purpose:** Yahoo provides 3 different types of historical data sets.

**Constants:**
- `DataEvent.HISTORICAL_PRICES` - Historical price data
- `DataEvent.DIVIDENDS` - Dividend data
- `DataEvent.STOCK_SPLITS` - Stock split data

### `DataFrequency`
Provides data frequency information for `HistoricalData`.

**Purpose:** Yahoo provides data at 3 different time granularities.

**Constants:**
- `DataFrequency.DAILY = '1d'` - Retrieve data at daily intervals
- `DataFrequency.WEEKLY = '1wk'` - Retrieve data at weekly intervals
- `DataFrequency.MONTHLY = '1mo'` - Retrieve data at monthly intervals

### `DataFormat`
Selects the way data is formatted for `IYahooData` implementations.

**Constants:**
- `DataFormat.RAW = 'raw'` - Raw numerical value (e.g., 1000000.0)
- `DataFormat.SHORT = 'fmt'` - Shorter formatted value (e.g., 1.0M)
- `DataFormat.LONG = 'longFmt'` - Longer formatted value (e.g., 1,000,000.0)

---

## Usage Rules & Best Practices

### General Rules
1. **Always check EXPERIMENTAL status** - Classes marked as EXPERIMENTAL may have inconsistent results
2. **Handle locale appropriately** - Use appropriate locale for your region or needs
3. **Date formatting** - Default date format is `'%Y-%m-%d'` but can be customized
4. **Error handling** - Always wrap API calls in try-except blocks as data is scraped

### CSV Export Rules
- If `path=None` in `to_csv()`, method returns CSV as string instead of writing to file
- Use appropriate `csv_dialect` for your needs (default: 'excel')
- Some parameters like `sep` and `data_format` are NOT USED in certain methods

### DataFrame Export Rules
- `to_dfs()` always returns a pandas DataFrame or dictionary of DataFrames
- `data_format` parameter may not be used in all implementations
- Check dictionary keys for specific data structure

### Performance Considerations
1. Use appropriate locale to minimize query time
2. Limit date ranges for historical data when possible
3. Cache results when making multiple queries for same data
4. Consider using quarterly vs annual data based on needs

---

## Complete Example Workflow

```python
from yahoofinance import (
    HistoricalPrices, 
    IncomeStatement, 
    BalanceSheet,
    AssetProfile,
    Locale,
    DataFrequency,
    DataFormat
)

# Get historical prices
hist = HistoricalPrices(
    'AAPL',
    start_date='2023-01-01',
    end_date='2023-12-31',
    frequency=DataFrequency.DAILY,
    locale=Locale.US
)
df_hist = hist.to_dfs()

# Get income statement (EXPERIMENTAL)
income = IncomeStatement('AAPL', locale=Locale.US)
df_income = income.to_dfs(data_format=DataFormat.RAW)

# Get balance sheet (EXPERIMENTAL)
balance = BalanceSheet('AAPL')
csv_output = balance.to_csv(path='output.csv')

# Get asset profile (EXPERIMENTAL)
profile = AssetProfile('AAPL')
df_profile = profile.to_dfs()
```

---

## Reference Links
- Main Documentation: https://python-yahoofinance.readthedocs.io/
- API Documentation: https://python-yahoofinance.readthedocs.io/en/latest/api.html
- Yahoo Finance: https://finance.yahoo.com/

---

## Version Notes
- API is under active development
- Changes may occur rapidly
- Always refer to latest documentation for updates
- Test experimental features thoroughly before production use

