# NOTE: This file has been automatically generated, do not modify!
# Architecture based on https://github.com/mrexodia/ida-pro-mcp (MIT License)
from http.client import responses
from typing import Annotated, Optional, TypedDict, Generic, TypeVar
from pydantic import Field

T = TypeVar("T")

@mcp.tool()
def ping()->str:
    """Checks if the Joern server is running and responsive by querying its version
    
    @return: The Joern server version if successful, 'Query Failed' if the server is not responding
    """
    response = joern_remote('version')
    if response:
        return extract_value(response)
    else:
        return 'Query Failed'

@mcp.tool()
def load_script(filepath: str) -> str:
    """Loads and executes a Scala script file in the Joern shell
    
    @param filepath: Absolute path to the Scala script file (.sc extension)
    @return: The response from Joern after loading the script
    """
    return joern_remote(f':load "{filepath}"')

@mcp.tool()
def load_cpg(cpg_filepath: str) -> str:
    """Loads a Code Property Graph (CPG) file into Joern for analysis

    @param filepath: Absolute path to the CPG file
    @return: Response confirming CPG loading status
    """
    
    return extract_value(joern_remote(f'val cpg = CpgLoader.load("{cpg_filepath}")'))

@mcp.tool()
def check_cpg_loaded() -> bool:
    """Check if a CPG file is loaded"""
    cur_cpg_file_path =  extract_value(joern_remote("cpg.metaData.head.root"))
    if cur_cpg_file_path.find('Not Found Error') >= 0:
        return False
    else:
        return True

@mcp.tool()
def get_call_code_by_id(id:str) -> str:
    """Get the source code of a specific call node from the loaded CPG by the call id
    
    @param id: The unique identifier of the call node, the id is a Long int string, like '111669149702L'
    @return: The source code of the specified call
    """
    response =  joern_remote(f'cpg.call.id({id}).head.code')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by id'
    return extract_value(response)

@mcp.tool()
def get_method_id_by_call_id(id:str) -> str:
    """Retrieves the method ID containing a specific call node
    
    @param id: The unique identifier of the call node, the id is a Long int string, like '111669149702L'
    @return: The ID of the method containing the specified call
    """
    response =  joern_remote(f'cpg.call.id({id}).head.method.id')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by id'
    return extract_value(response)

@mcp.tool()
def get_method_code_by_id(id:str) -> str:
    """Retrieves the source code of a method by its ID
    
    @param id: The unique identifier of the method, the id is a Long int string, like '111669149702L'
    @return: The source code of the specified method
    """
    return joern_remote(f'cpg.method.id({id}).head.code')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by id'
    return extract_value(response)
@mcp.tool()
def get_method_code_by_class_full_name_and_method_name(class_full_name:str, method_name:str) -> list[str]:
    """get a method code in a class

    @param class_full_name: The fully qualified name of the class (e.g., com.android.nfc.NfcService$6)
    @param method_name: the name of method (e.g., onReceive)
    """
    cmd = f'cpg.typeDecl.filter(c => c.fullName == "{class_full_name}").method.filter(m => m.name == "{method_name}").code.l'
    responses = joern_remote(cmd)
    result = extract_list(responses)
    return result
@mcp.tool()
def get_method_full_name_by_id(id:str) -> str:
    """Retrieves the fully qualified name of a method by its ID
    
    @param id: The unique identifier of the method, the id is a Long int string, like '111669149702L'
    @return: The fully qualified name of the method (e.g., package.class.method)
    """
    response = joern_remote(f'cpg.method.id({id}).head.fullName')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by id'
    return extract_value(response)

@mcp.tool()
def get_method_code_by_full_name(method_full_name:str) -> str:
    """Retrieves the source code of a method using its fully qualified name
    
    @param method_full_name: The fully qualified name of the method (e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
    @return: The source code of the specified method
    """
    response = joern_remote(f'cpg.method.fullNameExact("{method_full_name}").head.code')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by full name'
    return extract_value(response)

@mcp.tool()
def get_class_code_by_id(id:str) -> str:
    """Retrieves the source code of a class by its ID
    
    @param id: The unique identifier of the class (typeDecl), the id is a Long int string, like '111669149702L'
    @return: The source code of the specified class
    """
    response = joern_remote(f'cpg.typeDecl.id({id}).head.code')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by id'
    return extract_value(response)

@mcp.tool()
def get_class_full_name_by_id(id:str) -> str:
    """Retrieves the fully qualified name of a class by its ID
    
    @param id: The unique identifier of the class (typeDecl), the id is a Long int string, like '111669149702L'
    @return: The fully qualified name of the class (e.g., package.class)
    """
    response =  joern_remote(f'cpg.typeDecl.id({id}).head.fullName')
    if response.find('java.util.NoSuchElementException') >=0:
        return 'Not find by full name'
    return extract_value(response)

@mcp.tool()
def get_class_methods_by_fullName(class_full_name:str) -> list[str]:
    """Retrieves a list of methods defined within a class using its fully qualified name

    @param class_full_name: The fully qualified name of the class (e.g., com.android.nfc.NfcService$6)
    """
    cmd = f'cpg.typeDecl.filter(_.fullName=="{class_full_name}").head.method.map(m => (s"methodFullName=$' + '{m.fullName} methodId=${m.id}L")).l'
    responses = joern_remote(cmd)
    result = extract_list(responses)
    return result
@mcp.tool()
def get_method_callers(method_full_name: str) -> list[str]:
    """Retrieves a list of methods that call the specified method
    
    @param method_full_name: The fully qualified name of the target method(e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
    @return: List of fully qualified names of methods that call the target method
    """
    responses = joern_remote(f'cpg.method.fullNameExact("{method_full_name}").head.caller.fullName.l')
    return extract_list(responses)

@mcp.tool()
def get_method_callees(method_full_name: str) -> list[str]:
    """Retrieves a list of methods that are called by the specified method
    
    @param method_full_name: The fully qualified name of the source method(e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
    @return: List of full name and id of methods called by the source method
    """
    responses =  joern_remote(f'cpg.method.fullNameExact("{method_full_name}").head.callee.distinct.map(m => (s"methodFullName=$' + '{m.fullName} methodId=${m.id}L")).l')
    return extract_list(responses)  
@mcp.tool()
def get_anonymous_classes_in_class(class_full_name:str) -> list[str]:
    """Retrieves a list of anonymous classes defined within a class

    @param class_full_name: The fully qualified name of the class (e.g., com.android.nfc.NfcService)
    @return: List of full name and id of classes in the source method
    """
    responses =  joern_remote(f'getAnonymousClasses("{class_full_name}")')
    return extract_list(responses)
@mcp.tool()
def run_query(query: str) -> str:
    """Executes a custom Joern query on the loaded CPG,Strings in joern must use double quotes instead of single quotes
    
    @param query: A valid Joern/Scala query to execute
    @return: The query results as returned by the Joern server
    """
    return joern_remote(f'{query}')