# Joern MCP Server

A simple Joern MCP Server.

## Project Introduction

This project is a Joern-based MCP Server that provides a series of features to help developers with code review and security analysis.

## Environment Requirements

- Python >= 3.12 & uv
- Joern

## Installation Steps

1. Clone the project locally:
   ```bash
   git clone [project address]
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
├── server.py           # MCP Server main program
├── demo.sc             # joern sc example script
├── demo.py             # joern server and mcp tool test program
├── common_tools.py     # common utility functions
├── server_tools.py     # server utility functions
└── requirements.txt    # Python dependency file
└── env_example.txt     # environment variables example file
```

## Usage Instructions

1. Start the Joern server:
   ```bash
   joern -J-xmx40G --server --server-host 127.0.0.1 --server-port 16162 --server-auth-username user --server-auth-password password
   ```
2. Copy env_example.txt to .env
   Modify the configuration information to match the joern server settings

3. Run connection test:
   Modify the information in demo.py to confirm joern server is working normally
   ```bash
   python demo.py
   ```

4. Configure MCP server
   Configure the mcp server in cline, refer to `sample_cline_mcp_settings.json`.

5. Use MCP server
   Ask questions to the large language model, refer to prompts_en.md

## Development Notes

- `.env` file is used to store environment variables
- `.gitignore` file defines which files Git version control should ignore
- `pyproject.toml` defines the Python configuration for the project

## License

[To be added]

## Contribution Guidelines

Issues and Pull Requests are welcome to help improve the project.

## Contact Information

[To be added]