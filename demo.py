import json
from sqlite3 import connect
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
    执行远程查询并返回结果

    参数：
    query -- 要执行的查询字符串

    返回值：
    成功时返回服务器响应的stdout内容
    失败时返回None，错误信息会输出到stderr
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
def get_method_callers(method_full_name: str) -> list[str]:
    """Get the callers of a method from the loaded CPG
    
    @param filepath: the path to the CPG file, must be a fully-qualified absolute path
    @param method_name: the name of the method to get callers for
    """
    response = joern_remote(f'cpg.method.fullNameExact("{method_full_name}").head.caller.fullName.l')
    lst = extract_list(response)
    return lst
def get_method_callees(method_full_name: str) -> list[str]:
    """Retrieves a list of methods that are called by the specified method
    
    @param method_full_name: The fully qualified name of the source method(e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
    @return: List of full name and id of methods called by the source method
    """
    responses =  joern_remote(f'cpg.method.fullNameExact("{method_full_name}").head.callee.distinct.map(m => (s"methodFullName=$' + '{m.fullName} methodId=${m.id}L")).l')
    return extract_list(responses)    
def load_cpg(filepath: str) -> str:
    """Load a CPG file into Joern for analysis
    
    @param filepath: the path to the CPG file, must be a fully-qualified absolute path
    """
    return joern_remote(f'val cpg = CpgLoader.load("{filepath}")')

def get_method_code_by_id(id:str) -> str:
    """Retrieves the source code of a method by its ID
    
    @param id: The unique identifier of the method, the id is a Long int string, like '111669149702L'
    @return: The source code of the specified method
    """
    response = joern_remote(f'cpg.method.id({id}).head.code')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by id'
    return extract_value(response)
def check_connection() -> str:
    """Check if the Joern MCP plugin is running"""
    try:
        metadata = extract_value(joern_remote("version"))
        if not metadata:
            return f"Failed to connect to Joern MCP! Make sure the Joern MCP server is running."
        return f"Successfully connected to Joern MCP, joern server version is {metadata}"
    except Exception as e:
        return f"Failed to connect to Joern MCP! Make sure the Joern MCP server is running."
def get_class_code_by_fullName(class_full_name:str) -> str:
    """Retrieves the source code of a class using its fully qualified name
    
    @param class_full_name: The fully qualified name of the class (e.g., package.class)
    @return: The source code of the specified class
    """
    response = joern_remote(f'cpg.typeDecl.filter(_.fullName == "{class_full_name}").head.code')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by full name'
    return extract_value(response)
def get_class_code_by_id(id:str) -> str:
    """Retrieves the source code of a class by its ID
    
    @param id: The unique identifier of the class (typeDecl), the id is a Long int string, like '111669149702L'
    @return: The source code of the specified class
    """
    response = joern_remote(f'cpg.typeDecl.id({id}).head.code')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by id'
    return extract_value(response)
def get_class_methods_by_fullName(class_full_name:str) -> list[str]:
    """Retrieves a list of methods defined within a class using its fully qualified name

    @param class_full_name: The fully qualified name of the class (e.g., com.android.nfc.NfcService$6)
    """
    cmd = f'cpg.typeDecl.filter(_.fullName=="{class_full_name}").head.method.map(m => (s"methodFullName=$' + '{m.fullName} methodId=${m.id}L")).l'
    responses = joern_remote(cmd)
    result = extract_list(responses)
    return result

def get_method_code_by_class_full_name_and_method_name(class_full_name:str, method_name:str) -> list[str]:
    """get a method code in a class

    @param class_full_name: The fully qualified name of the class (e.g., com.android.nfc.NfcService$6)
    @param method_name: the name of method (e.g., onReceive)
    """
    cmd = f'cpg.typeDecl.filter(c => c.fullName == "{class_full_name}").method.filter(m => m.name == "{method_name}").code.l'
    responses = joern_remote(cmd)
    result = extract_list(responses)
    return result

def check_cpg_loaded() -> bool:
    """Check if a CPG file is loaded"""
    cur_cpg_file_path =  extract_value(joern_remote("cpg1.metaData.head.root"))
    if cur_cpg_file_path.find('Not Found Error') >= 0:
        return False
    else:
        return True

if __name__ == "__main__":
    connect_status = check_connection()
    print(connect_status)
    print(check_cpg_loaded())
    filepath = '/home/kali/cpg/com.android.nfc.cpg'
    load_result = load_cpg(filepath=filepath)
    print(load_result)
    method_name = 'onReceive'
    class_full_name = 'com.android.nfc.NfcService$6'
    # print(get_class_methods_by_fullName(class_full_name))
    # print(get_method_code_by_class_full_name_and_method_name(class_full_name, method_name))
    mth = "com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent)"
    print(get_method_callees(mth))
