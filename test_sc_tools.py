import json
import sys
import os
import requests
import re
from dotenv import load_dotenv
from urllib3 import response
from common_tools import *
load_dotenv()
server_endpoint = f'{os.getenv("HOST")}:{os.getenv("PORT")}'
print(server_endpoint)
basic_auth = (os.getenv("USER_NAME"), os.getenv("PASSWORD"))

def joern_remote(query):
    """
    Execute remote query and return results

    Parameters:
    query -- The query string to execute

    Returns:
    Returns the server response's stdout content on success
    Returns None on failure, error messages will be output to stderr
    """
    data = {"query": query}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(
            f'http://{server_endpoint}/query-sync',
            data=json.dumps(data),
            auth=basic_auth,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()  # 自动处理HTTP错误状态码

        result = response.json()
        return remove_ansi_escape_sequences(result.get('stdout', ''))

    except requests.exceptions.RequestException as e:
        sys.stderr.write(f"Request Error: {str(e)}\n")
    except json.JSONDecodeError:
        sys.stderr.write("Error: Invalid JSON response\n")

    return None
def get_calls_in_method_by_method_full_name(method_full_name:str) -> list[str]:
    """Get the calls info by the method full name which the call is in the method

    @param method_full_name: The full name of the method
    @return: The calls info of the method
    """
    response = joern_remote(f'get_calls_in_method_by_method_full_name("{method_full_name}")')
    return extract_list(response)
if __name__ == "__main__":
    method_full_name = "com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent)"
    print(get_calls_in_method_by_method_full_name(method_full_name))