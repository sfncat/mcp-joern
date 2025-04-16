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
def load_cpg(cpg_filepath: str) -> str:
    """
    Loads a CPG from a file if the cpg is not loaded or the cpg is not the same as the filepath
    
    @param cpg_filepath: The path to the CPG file, the filepath is absolute path
    @return: True if the CPG is loaded successfully, False otherwise
    """
    
    # return extract_value(joern_remote(f'val cpg = CpgLoader.load("{cpg_filepath}")'))
    return extract_value(joern_remote(f'load_cpg("{cpg_filepath}")'))

@mcp.tool()
def get_method_callees(method_full_name: str) -> list[str]:
    """Retrieves a list of methods info that are called by the specified method
    
   @param method_full_name: The fully qualified name of the source method(e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
   @return: List of full name, name, signature and id of methods which call the source method
    """
    # responses =  joern_remote(f'cpg.method.fullNameExact("{method_full_name}").head.callee.distinct.map(m => (s"methodFullName=$' + '{m.fullName} methodId=${m.id}L")).l')
    responses = joern_remote(f'get_method_callees("{method_full_name}")')
    return extract_list(responses)  

@mcp.tool()
def get_method_callers(method_full_name: str) -> list[str]:
    """Retrieves a list of methods that call the specified method
    
    @param method_full_name: The fully qualified name of the source method(e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
    @return: List of full name, name, signature and id of methods called by the source method
    """
    responses = joern_remote(f'get_method_callers("{method_full_name}")')
    return extract_list(responses)

@mcp.tool()
def get_class_full_name_by_id(id:str) -> str:
    """Retrieves the fully name of a class by its ID
    
    @param id: The unique identifier of the class (typeDecl), the id is a Long int string, like '111669149702L'
    @return: The fully name of the class (e.g., com.android.nfc.NfcService$6)
    """
    response =  joern_remote(f'get_class_full_name_by_id("{id}")')
    return extract_value(response)

@mcp.tool()
def get_class_methods_by_class_full_name(class_full_name:str) -> list[str]:
    """Get the methods of a class by its fully qualified name
  
    @param class_full_name: The fully qualified name of the class
    @return: List of full name, name, signature and id of methods in the class
    """
    response = joern_remote(f'get_class_methods_by_class_full_name("{class_full_name}")')
    return extract_list(response)

@mcp.tool()
def get_method_code_by_full_name(method_full_name:str) -> str:
    """Get the code of a method by its fully name
    @param method_full_name: The fully qualified name of the method (e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
    @return: The source code of the specified method
    """
    response = joern_remote(f'get_method_code_by_method_full_name("{method_full_name}")')
    return extract_value(response)

@mcp.tool()
def get_method_code_by_id(id:str) -> str:
    """Get the code of a method by its class full name and method name
  
    @param class_full_name: The fully qualified name of the class
    @param method_name: The name of the method
    @return: List of full name, name, signature and id of methods in the class
    """
    response =  joern_remote(f'get_method_code_by_id("{id}")')
    return extract_value(response)

@mcp.tool()
def get_method_full_name_by_id(id:str) -> str:
    """Retrieves the fully qualified name of a method by its ID
    
    @param id: The unique identifier of the method, the id is a Long int string, like '111669149702L'
    @return: The fully qualified name of the method (e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
    """
    response = joern_remote(f'get_method_full_name_by_id("{id}")')
    return extract_value(response)

@mcp.tool()
def get_call_code_by_id(id:str) -> str:
    """Get the source code of a specific call node from the loaded CPG by the call id
    
    @param id: The unique identifier of the call node, the id is a Long int string, like '111669149702L'
    @return: The source code of the specified call
    """
    response =  joern_remote(f'get_call_code_by_id("{id}")')
    return extract_value(response)

@mcp.tool()
def get_method_code_by_class_full_name_and_method_name(class_full_name:str, method_name:str) -> list[str]:
    """Get the code of a method by its class full name and method name
  
    @param class_full_name: The fully qualified name of the class
    @param method_name: The name of the method
    @return: List of full name, name, signature and id of methods in the class
    """
    responses = joern_remote(f'get_method_code_by_class_full_name_and_method_name("{class_full_name}", "{method_name}")')
    return extract_list(responses)

@mcp.tool()
def get_method_by_full_name_without_signature(full_name_without_signature:str) -> str:
    """Get the info of a method list by its fully qualified name without signature
    
    @param full_name_without_signature: fully qualified name of methodwithout signature,like com.android.nfc.NfcService.onReceive
    @return: The info of the methods, including the full name, name, signature and id
    """
    response = joern_remote(f'get_method_by_full_name_without_signature("{full_name_without_signature}")')
    return extract_value(response)

@mcp.tool()
def get_derived_classes_by_class_full_name(class_full_name:str) -> list[str]:
    """Get the derived classes of a class
    
    @param class_full_name: The fully qualified name of the class
    @return: The derived classes info of the class, including the full name, name and id
    """
    response = joern_remote(f'get_derived_classes_by_class_full_name("{class_full_name}")')
    return extract_list(response)

@mcp.tool()
def get_parent_classes_by_class_full_name(class_full_name:str) -> list[str]:
    """Get the parent classes of a class
    
    @param class_full_name: The fully qualified name of the class
    @return: The parent classes info of the class, including the full name, name and id
    """
    response = joern_remote(f'get_parent_classes_by_class_full_name("{class_full_name}")')
    return extract_list(response)

@mcp.tool()
def get_method_by_call_id(id:str) -> str:
    """Get the method info by the call id which the call is in the method
  
    @param id: The id of the call
    @return: The method info of the call
    """
    response =  joern_remote(f'get_method_by_call_id("{id}")')
    return extract_value(response)

@mcp.tool()
def get_referenced_method_full_name_by_call_id(id:str) -> str:
    """Get the method info by the call id which the call is referenced the method
    
    @param id: The id of the call
    @return: The method info of the call
    """
    response =  joern_remote(f'get_referenced_method_full_name_by_call_id("{id}")')
    return extract_value(response)   

@mcp.tool()
def get_calls_in_method_by_method_full_name(method_full_name:str) -> list[str]:
    """Get the calls info by the method full name which the call is in the method

    @param method_full_name: The full name of the method
    @return: The calls info of the method
    """
    response = joern_remote(f'get_calls_in_method_by_method_full_name("{method_full_name}")')
    return extract_list(response)