#!/usr/bin/env python3
"""
MCP Server Runner - Handles stdio transport for Stock Market Analyzer
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastMCP server from stock.server
# The module will execute and create the 'mcp' object
exec(open(os.path.join(os.path.dirname(__file__), 'stock.server.py')).read())

# The 'mcp' object is now available from the executed code
if __name__ == "__main__":
    # Run the server using stdio (default for FastMCP when called directly)
    mcp.run()
