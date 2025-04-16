import os
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

async def test_connection(client):
    """Test server connection"""
    print("Testing server connection...")
    try:
        result = await client.call_tool("check_connection")
        print(f"Connection test result: {result}")
        return True
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False

async def test_ping(client):
    """Test ping functionality"""
    print("Testing ping...")
    try:
        result = await client.call_tool("ping")
        print(f"Ping result: {result}")
        return True
    except Exception as e:
        print(f"Ping test failed: {str(e)}")
        return False

async def test_load_cpg(client, cpg_path):
    """Test loading CPG file"""
    print("Testing CPG file loading...")
    try:
        result = await client.call_tool("load_cpg", {"cpg_filepath": cpg_path})
        print(f"CPG loading result: {result}")
        return True
    except Exception as e:
        print(f"CPG loading failed: {str(e)}")
        return False

async def test_method_queries(client, method_full_name):
    """Test method-related queries"""
    print("Testing method queries...")
    success = True
    
    try:
        # Test getting method callers
        print("Testing get method callers...")
        callers = await client.call_tool("get_method_callers", {"method_full_name": method_full_name})
        print(f"Method callers: {callers}")
    except Exception as e:
        print(f"Failed to get method callers: {str(e)}")
        success = False
    
    try:
        # Test getting method callees
        print("Testing get method callees...")
        callees = await client.call_tool("get_method_callees", {"method_full_name": method_full_name})
        print(f"Method callees: {callees}")
    except Exception as e:
        print(f"Failed to get method callees: {str(e)}")
        success = False
    
    try:
        # Test getting method code
        print("Testing get method code...")
        code = await client.call_tool("get_method_code_by_full_name", {"method_full_name": method_full_name})
        print(f"Method code: {code}")
    except Exception as e:
        print(f"Failed to get method code: {str(e)}")
        success = False
    
    return success

async def test_class_queries(client, class_name):
    """Test class-related queries"""
    print("Testing class queries...")
    success = True
    
    try:
        # Test getting class methods
        print("Testing get class methods...")
        methods = await client.call_tool("get_class_methods_by_class_full_name", {"class_full_name": class_name})
        print(f"Class methods: {methods}")
    except Exception as e:
        print(f"Failed to get class methods: {str(e)}")
        success = False
    
    try:
        # Test getting derived classes
        print("Testing get derived classes...")
        derived = await client.call_tool("get_derived_classes_by_class_full_name", {"class_full_name": class_name})
        print(f"Derived classes: {derived}")
    except Exception as e:
        print(f"Failed to get derived classes: {str(e)}")
        success = False
    
    try:
        # Test getting parent classes
        print("Testing get parent classes...")
        parents = await client.call_tool("get_parent_classes_by_class_full_name", {"class_full_name": class_name})
        print(f"Parent classes: {parents}")
    except Exception as e:
        print(f"Failed to get parent classes: {str(e)}")
        success = False
    
    return success

async def main():
    """Main test function"""
    print("Starting MCP server test...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Create client
    client = Client(
        transport=PythonStdioTransport('server.py'),
        roots=["file:///path/to/mcp-joern"]  # Replace with actual workspace directory
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
        cpg_path = "/path/to/com.android.nfc.cpg"  # Replace with actual CPG file path
        if not await test_load_cpg(client, cpg_path):
            print("CPG loading test failed, terminating test")
            return
        
        # Test method queries
        method_full_name = "com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent)"  # Replace with actual method full name
        if not await test_method_queries(client, method_full_name):
            print("Method queries test failed")
        
        # Test class queries
        class_name = "com.android.nfc.NfcService"  # Replace with actual class name
        if not await test_class_queries(client, class_name):
            print("Class queries test failed")
    
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 