# Stock MCP Server - Project Structure

## 📁 Organized File Structure

```
stock_mcp_server/
│
├── 📄 Python Modules (Core Application)
│   ├── stock.server.py         # Main MCP server entry point
│   ├── run_mcp_server.py       # Helper script to start server
│   ├── utils.py                # Shared utilities (load/save functions)
│   ├── price_data.py           # Price and stock information tools
│   ├── portfolio.py            # Portfolio management tools
│   ├── analysis.py             # Technical analysis indicators
│   ├── alerts.py               # Alert system (price & RSI)
│   ├── dividends.py            # Dividend tracking and analysis
│   ├── sector.py               # Sector analysis and comparison
│   ├── risk.py                 # Risk metrics (Sharpe, Beta, VaR, etc.)
│   └── sentiment.py            # Market sentiment tracker ✨ NEW
│
├── 📊 data/ (Your Personal Data - Auto-generated)
│   ├── portfolio.json          # Your stock holdings and transactions
│   ├── alerts.json             # Your price and RSI alerts
│   ├── sentiment_history.json  # Sentiment tracking history (90 days)
│   └── .gitkeep                # Keeps folder in version control
│
├── 📚 docs/ (Documentation)
│   ├── TOOLS_REFERENCE.md              # Complete guide to all 48+ tools
│   ├── SENTIMENT_TRACKER_SUMMARY.md    # Sentiment tracker technical docs
│   ├── CURRENT_MARKET_ANALYSIS.md      # Example market analysis
│   ├── IMPLEMENTATION_SUMMARY.md       # Implementation details
│   ├── ROADMAP.md                      # Future features and enhancements
│   └── .gitkeep                        # Keeps folder in version control
│
├── 📦 Configuration & Setup
│   ├── requirements.txt        # Python dependencies
│   ├── .gitignore              # Git ignore rules (keeps data private)
│   ├── README.md               # Main documentation and setup guide
│   └── PROJECT_STRUCTURE.md    # This file
│
└── 🐍 venv/ (Virtual Environment)
    └── [Python packages installed here]
```

## 📋 File Categories

### Core Python Modules (Root Directory)
All Python source code remains in the root directory for easy imports. Each module is self-contained and registers its tools with the MCP server.

| Module | Tools | Purpose |
|--------|-------|---------|
| `price_data.py` | 3 | Basic stock data retrieval |
| `portfolio.py` | 4 | Holdings and transaction management |
| `analysis.py` | 5 | Technical indicators (RSI, MACD, etc.) |
| `alerts.py` | 6 | Price and RSI alert system |
| `dividends.py` | 4 | Dividend tracking and income |
| `sector.py` | 4 | Sector analysis and rotation |
| `risk.py` | 5 | Risk metrics and portfolio risk |
| `sentiment.py` | 8 | Market sentiment aggregation ✨ |
| **Total** | **48+** | **Complete stock analysis suite** |

### Data Files (`data/` folder)
All JSON data files are now organized in the `data/` folder:

- **Private Data**: Your portfolio, alerts, and sentiment history
- **Auto-generated**: Created automatically when you use features
- **Git-ignored**: Won't be committed to version control (keeps private)
- **Easy Backup**: Copy entire `data/` folder to backup

### Documentation (`docs/` folder)
All markdown documentation organized in the `docs/` folder:

- **User Guides**: How to use tools and features
- **Technical Docs**: Implementation details and architecture
- **Examples**: Market analysis examples and use cases
- **Roadmap**: Future features and enhancements

## 🔐 Privacy & Security

### What's Git-Ignored (Private)
The `.gitignore` file keeps these private:
- `data/*.json` - All your personal data files
- `venv/` - Virtual environment (large, not needed in repo)
- `__pycache__/` - Python cache files
- `.DS_Store` - macOS system files

### What's Version Controlled (Shared)
- All Python source code (`.py` files)
- Documentation files (`.md` files)
- Configuration files (`requirements.txt`, `.gitignore`)
- Folder structure markers (`.gitkeep`)

## 📦 Setup & Installation

### Quick Start
```bash
# 1. Navigate to project
cd stock_mcp_server

# 2. Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 3. Verify structure
ls -la data/  # Should see .gitkeep and any existing .json files
ls -la docs/  # Should see all .md documentation files

# 4. Run server (via MCP config in Cursor)
# The server will automatically create data files as needed
```

## 🔄 Migration from Old Structure

### What Changed (v0.4.0)
**Before:**
```
stock_mcp_server/
├── [python files]
├── portfolio.json
├── alerts.json
├── TOOLS_REFERENCE.md
├── ROADMAP.md
└── [other .md files]
```

**After:**
```
stock_mcp_server/
├── [python files]
├── data/
│   ├── portfolio.json
│   ├── alerts.json
│   └── sentiment_history.json
└── docs/
    ├── TOOLS_REFERENCE.md
    ├── ROADMAP.md
    └── [other .md files]
```

### Automatic Path Updates
✅ All file paths updated in `utils.py`  
✅ No code changes needed in your MCP configuration  
✅ Existing data automatically found in new locations  
✅ All imports and tools work seamlessly

## 📊 Data Management

### Accessing Your Data
```bash
# View your portfolio
cat data/portfolio.json | python -m json.tool

# View your alerts
cat data/alerts.json | python -m json.tool

# View sentiment history
cat data/sentiment_history.json | python -m json.tool
```

### Backing Up Your Data
```bash
# Backup all data
cp -r data/ data_backup_$(date +%Y%m%d)/

# Restore from backup
cp -r data_backup_20251023/* data/
```

### Resetting Data
```bash
# Clear all data (keeps folder structure)
rm data/*.json

# Data will be recreated automatically when you use features
```

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| `README.md` | Main documentation, setup guide, features overview |
| `docs/TOOLS_REFERENCE.md` | Complete reference for all 48+ tools |
| `docs/SENTIMENT_TRACKER_SUMMARY.md` | Market sentiment tracker technical docs |
| `docs/CURRENT_MARKET_ANALYSIS.md` | Example market analysis with sentiment data |
| `docs/IMPLEMENTATION_SUMMARY.md` | Technical implementation details |
| `docs/ROADMAP.md` | Future features and enhancement roadmap |
| `PROJECT_STRUCTURE.md` | This file - project organization |

## 🎯 Benefits of New Structure

### ✅ Better Organization
- Clear separation: Code vs Data vs Docs
- Easier to navigate and find files
- Professional project structure

### ✅ Privacy First
- All personal data in one folder
- Easy to gitignore and keep private
- Simple backup and restore

### ✅ Documentation Hub
- All guides in one place (`docs/`)
- Easy to reference and share
- Clean separation from code

### ✅ Scalability
- Easy to add new data files
- Easy to add new documentation
- Maintains clean root directory

## 🚀 Next Steps

1. **Explore Documentation**
   - Read `docs/TOOLS_REFERENCE.md` for complete tool guide
   - Check `docs/SENTIMENT_TRACKER_SUMMARY.md` for sentiment features

2. **Start Using Features**
   - Portfolio tracking → Data saved in `data/portfolio.json`
   - Set alerts → Saved in `data/alerts.json`
   - Track sentiment → History in `data/sentiment_history.json`

3. **Backup Regularly**
   - Copy `data/` folder to safe location
   - Consider cloud backup for important portfolios

4. **Share Knowledge**
   - Share `docs/` folder with team
   - Keep `data/` private
   - Contribute improvements to code

---

**Project Structure Version:** 0.4.0  
**Last Updated:** October 23, 2025  
**Status:** ✅ Production Ready

