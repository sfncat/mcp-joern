import os
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

async def test_connection(client):
    """Test server connection"""
    print("Testing [check_connection] server connection...")
    try:
        result = await client.call_tool("check_connection")
        print(f"Connection test result: {result[0].text}")
        return True
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False

async def test_ping(client):
    """Test ping functionality"""
    print("Testing [ping] ping...")
    try:
        result = await client.call_tool("ping")
        print(f"Ping result: {result[0].text}")
        return True
    except Exception as e:
        print(f"Ping test failed: {str(e)}")
        return False

async def test_load_cpg(client, cpg_path):
    """Test loading CPG file"""
    print("Testing [load_cpg] CPG file loading...")
    try:
        result = await client.call_tool("load_cpg", {"cpg_filepath": cpg_path})
        print(f"CPG loading result: {result[0].text}")
        return True
    except Exception as e:
        print(f"CPG loading failed: {str(e)}")
        return False

async def test_method_info_queries(client, method_full_name, method_id, full_name_without_signature):
    """Test method-related queries"""
    print("Testing method queries...")
    success = True
    
    try:
        # Test getting method callers
        print("Testing [get_method_callers] get method callers...")
        callers = await client.call_tool("get_method_callers", {"method_full_name": method_full_name})
        if callers:
            print(f"Method callers: {callers[0].text}")
        else:
            print(f"Method callers: []")
    except Exception as e:
        print(f"Failed to get method callers: {str(e)}")
        success = False
    
    try:
        # Test getting method callees
        print("Testing [get_method_callees] get method callees...")
        callees = await client.call_tool("get_method_callees", {"method_full_name": method_full_name})
        if callees:
            print(f"Method callees: {callees[0].text}")
        else:
            print(f"Method callees: []")
    except Exception as e:
        print(f"Failed to get method callees: {str(e)}")
        success = False

    try:
        # Test getting method full name by ID
        print("Testing [get_method_full_name_by_id] get method full name by ID...")
        full_name = await client.call_tool("get_method_full_name_by_id", {"id": method_id})
        print(f"Method full name: {full_name[0].text}")
    except Exception as e:
        print(f"Failed to get method full name: {str(e)}")
        success = False   


    try:
        # Test getting method by full name without signature
        print("Testing [get_method_by_full_name_without_signature] get method by full name without signature...")
        method = await client.call_tool("get_method_by_full_name_without_signature", {"full_name_without_signature": full_name_without_signature})
        print(f"Method info: {method[0].text}")
    except Exception as e:
        print(f"Failed to get method info: {str(e)}")
        success = False
    
    return success

async def test_class_info_queries(client, class_full_name):
    """Test class-related queries"""
    print("Testing class queries...")
    success = True
    
    try:
        # Test getting class methods
        print("Testing [get_class_methods_by_class_full_name] get class methods...")
        methods = await client.call_tool("get_class_methods_by_class_full_name", {"class_full_name": class_full_name})
        if methods:
            print(f"Class methods: {methods[0].text}")
        else:
            print(f"Class methods: []")
    except Exception as e:
        print(f"Failed to get class methods: {str(e)}")
        success = False
    
    try:
        # Test getting derived classes
        print("Testing [get_derived_classes_by_class_full_name] get derived classes...")
        derived = await client.call_tool("get_derived_classes_by_class_full_name", {"class_full_name": class_full_name})
        if derived:
            print(f"Derived classes: {derived[0].text}")
        else:
            print(f"Derived classes: []")
    except Exception as e:
        print(f"Failed to get derived classes: {str(e)}")
        success = False
    
    try:
        # Test getting parent classes
        print("Testing [get_parent_classes_by_class_full_name] get parent classes...")
        parents = await client.call_tool("get_parent_classes_by_class_full_name", {"class_full_name": class_full_name})
        if parents:
            print(f"Parent classes: {parents[0].text}")
        else:
            print(f"Parent classes: []")
    except Exception as e:
        print(f"Failed to get parent classes: {str(e)}")
        success = False
    
    return success

async def test_call_info_queries(client, call_id, method_full_name):
    """Test call-related queries"""
    print("\nTesting call queries...")
    success = True
    
    try:
        # Test getting call code
        print("Testing [get_call_code_by_id] get call code...")
        code = await client.call_tool("get_call_code_by_id", {"id": call_id})
        print(f"Call code: {code[0].text}")
    except Exception as e:
        print(f"Failed to get call code: {str(e)}")
        success = False
    
    try:
        # Test getting method by call ID
        print("Testing [get_method_by_call_id] get method by call ID...")
        method = await client.call_tool("get_method_by_call_id", {"id": call_id})
        print(f"Method info: {method[0].text}")
    except Exception as e:
        print(f"Failed to get method by call ID: {str(e)}")
        success = False
    
    try:
        # Test getting referenced method full name
        print("Testing [get_referenced_method_full_name_by_call_id] get referenced method full name...")
        ref_method = await client.call_tool("get_referenced_method_full_name_by_call_id", {"id": call_id})
        print(f"Referenced method: {ref_method[0].text}")
    except Exception as e:
        print(f"Failed to get referenced method: {str(e)}")
        success = False
    
    print("Testing [get_calls_in_method_by_method_full_name] get calls in method...")
    try:
        calls = await client.call_tool("get_calls_in_method_by_method_full_name", {"method_full_name": method_full_name})
        if calls:
            print(f"Calls in method: {calls[0].text}")
        else:
            print(f"Calls in method: []")
        success =  True
    except Exception as e:
        print(f"Failed to get calls in method: {str(e)}")
        success =  False
    return success

async def test_method_code_queries(client, method_full_name, class_full_name, method_name, method_id):
    """Test method name-related queries"""
    print("Testing method name queries...")
    success = True
    
    try:
        # Test getting method code
        print("Testing [get_method_code_by_full_name] get method code...")
        code = await client.call_tool("get_method_code_by_full_name", {"method_full_name": method_full_name})
        print(f"Method code: {code[0].text}")
    except Exception as e:
        print(f"Failed to get method code: {str(e)}")
        success = False

    try:
        # Test getting method code by class full name and method name
        print("Testing [get_method_code_by_class_full_name_and_method_name] get method code by class and method name...")
        codes = await client.call_tool("get_method_code_by_class_full_name_and_method_name", {
            "class_full_name": class_full_name,
            "method_name": method_name
        })
        print(f"Method codes: {codes[0].text}")
    except Exception as e:
        print(f"Failed to get method codes: {str(e)}")
        success = False    

    try:
        # Test getting method code by ID
        print("Testing [get_method_code_by_id] get method code by ID...")
        code = await client.call_tool("get_method_code_by_id", {"id": method_id})
        print(f"Method code: {code[0].text}")
    except Exception as e:
        print(f"Failed to get method code: {str(e)}")
        success = False
    
    return success


async def main():
    """Main test function"""
    print("Starting MCP server test...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    # Create client
    client = Client(
        transport=PythonStdioTransport('server.py'),
        roots=[f"file://{SCRIPT_DIR}"]  # Replace with actual workspace directory
    )
    
    async with client:
        # Test basic connection
        if not await test_connection(client):
            print("Server connection test failed, terminating test")
            return
        
        # Test ping
        if not await test_ping(client):
            print("Ping test failed, terminating test")
            return
        
        # Test CPG loading
        cpg_path = os.path.join(SCRIPT_DIR,"com.android.nfc.cpg")  # Replace with actual CPG file path
        if not await test_load_cpg(client, cpg_path):
            print("CPG loading test failed, terminating test")
            return
        
        # Test method queries
        method_full_name = "com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent)"
        method_name = "onReceive"
        method_id = "111669160511L"
        call_id = "30064950783L"
        full_name_without_signature = "com.android.nfc.NfcService$6.onReceive"
        class_full_name = "com.android.nfc.NfcService"  # Replace with actual class name
        
        if not await test_method_info_queries(client, method_full_name, method_id, full_name_without_signature):
            print("Method queries test failed")
        
        # Test class queries
        if not await test_class_info_queries(client, class_full_name):
            print("Class queries test failed")

        # Test method code queries
        if not await test_method_code_queries(client, method_full_name, class_full_name, method_name, method_id):
            print("Method ID queries test failed")
        
        # Test call queries
        if not await test_call_info_queries(client, call_id, method_full_name):
            print("Call queries test failed")
        

    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())