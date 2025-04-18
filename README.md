# Joern MCP Server

A simple MCP Server for Joern.

## Project Introduction

This project is an MCP Server based on Joern, providing a series of features to help developers with code review and security analysis.

## Environment Requirements

- Python >= 3.10 (default 3.12) & uv
- Joern

## Installation Steps

1. Clone the project locally:
   ```bash
   git clone https://github.com/sfncat/mcp-joern.git
   cd mcp-joern
   ```

2. Install Python dependencies:
   ```bash
   uv venv .venv
   source .venv/bin/activate
   uv sync
   ```

## Project Structure

```
├── server.py                       # MCP Server main program
├── test_mcp_client.py              # Test program for joern server and mcp tool
├── test_sc_tools.py                # Direct test program for sc tools
├── common_tools.py                 # Common utility functions
├── server_tools.py                 # Server utility functions
├── server_tools.sc                 # Scala implementation of server utility functions
├── server_tools_source.sc          # Scala implementation of server utility functions,use sourceCode to get the source code of method
├── requirements.txt                # Python dependency file
├── sample_cline_mcp_settings.json  # Sample cline mcp configuration file
└── env_example.txt                 # Environment variables example file
```

## Usage

1. Start the Joern server:
   ```bash
   joern -J-Xmx40G --server --server-host 127.0.0.1 --server-port 16162 --server-auth-username user --server-auth-password password --import server_tools.sc
   Or
   joern -J-Xmx40G --server --server-host 127.0.0.1 --server-port 16162 --server-auth-username user --server-auth-password password --import server_tools_source.sc
   ```

2. Copy env_example.txt to .env
   Modify the configuration information to match the joern server startup configuration

3. Run the test connection:
   Modify the information in `test_mcp_client.py` to confirm the joern server is working properly

   ```bash
   uv run test_mcp_client.py
   Starting MCP server test...
   ==================================================
   Testing server connection...
   [04/16/25 20:38:54] INFO     Processing request of type CallToolRequest                                                                                                                     server.py:534
   Connection test result: Successfully connected to Joern MCP, joern server version is XXX
   ```

4. Configure MCP server
   Configure the mcp server in cline, refer to `sample_cline_mcp_settings.json`.

5. Use MCP server
   Ask questions to the large language model, refer to `prompts_en.md`

## Development Notes

- `.env` file is used to store environment variables
- `.gitignore` file defines files to be ignored by Git version control
- `pyproject.toml` defines the Python configuration for the project
- MCP tool development
  - Implement in `server_tools.sc`, add definitions in `server_tools.py`, and add tests in `test_mcp_client.py`

## Contribution Guidelines

Welcome to submit Issues and Pull Requests to help improve the project.

Welcome to add more tools.

## References

https://github.com/flankerhqd/jebmcp

https://docs.joern.io/server/

https://docs.joern.io/interpreter/