import json
import sys
import os
import re
import time
from typing import Dict, Any

import requests
from fastmcp import FastMCP
from dotenv import load_dotenv
from common_tools import *

load_dotenv()


def load_server_config(config_file: str = "mcp_settings.json") -> Dict[str, Any]:
    """load server config from config file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('mcpServers').get('joern').get('config')
    except FileNotFoundError:
        print(f"config file {config_file} not exist")
        return {}
    except json.JSONDecodeError:
        print(f"config file {config_file} format error")
        return {}
joern_config = load_server_config()
# server_endpoint = f'{os.getenv("HOST")}:{os.getenv("PORT")}'
server_endpoint = f'{joern_config.get('host')}:{joern_config.get("port")}'
log_level = joern_config.get('log_level', 'ERROR')
joern_mcp = FastMCP("joern-mcp", log_level=log_level)
# joern_mcp._tool_manager.
print(server_endpoint)
basic_auth = (os.getenv("JOERN_AUTH_USERNAME"), os.getenv("JOERN_AUTH_PASSWORD"))
timeout = int(joern_config.get('timeout', '300'))

def joern_remote(query):
    """
    Execute remote query and return results
    
    Parameters:
    query -- The query string to execute
    
    Returns:
    Returns the server response stdout content on success
    Returns None on failure, error message will be output to stderr
    """
    data = {"query": query}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(
            f'http://{server_endpoint}/query-sync',
            data=json.dumps(data),
            headers=headers,
            auth=basic_auth,
            timeout=timeout
        )
        response.raise_for_status()  
        
        result = response.json()
        return remove_ansi_escape_sequences(result.get('stdout', ''))
        
    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"Request Error: {str(e)}\n")
    except json.JSONDecodeError:
        sys.stderr.write("Error: Invalid JSON response\n")
    
    return None


@joern_mcp.tool()
def get_help():
    """Get help information from joern server"""
    response = joern_remote('help')
    if response:
        return response
    else:
        return 'Query Failed'


@joern_mcp.tool()
def check_connection() -> str:
    """Check if the Joern MCP plugin is running"""
    try:
        metadata = extract_value(joern_remote("version"))
        if not metadata:
            return f"Failed to connect to Joern MCP! Make sure the Joern MCP server is running."
        return f"Successfully connected to Joern MCP, joern server version is {metadata}"
    except Exception as e:
        return f"Failed to connect to Joern MCP! Make sure the Joern MCP server is running."

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
GENERATED_PY = os.path.join(SCRIPT_DIR, "server_tools.py")
def generate():
    """Generate and execute additional server tools from server_tools.py file.
    
    This function reads the content of server_tools.py and executes it to add
    more functionality to the server.
    """
    with open(GENERATED_PY, "r") as f:
        code = f.read()
        exec(compile(code, GENERATED_PY, "exec"))

generate()


def main():
    """Start the MCP server using stdio transport.
    
    This is the main entry point for running the Joern MCP server.
    """
    joern_mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
