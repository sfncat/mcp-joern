import os
import requests
import json
import re
import sys

def remove_ansi_escape_sequences(text: str) -> str:
    """Remove ANSI escape sequences from a string.
    
    Args:
        text (str): Input string containing ANSI escape sequences
        
    Returns:
        str: String with ANSI escape sequences removed
    """
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
    return ansi_escape.sub('', text)

def extract_code_between_triple_quotes(input_str):
    """Extract content between triple quotes from a string.
    
    Args:
        input_str (str): Input string containing triple-quoted content
        
    Returns:
        str: Extracted content between triple quotes, or empty string if not found
    """
    import re
    
    # Find content between triple quotes
    pattern = r'"""(.*?)"""'
    match = re.search(pattern, input_str, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return ''

def extract_list(input_str):    
    """Extract a list of elements from a string representation of a Scala List.
    
    Parameters:
    input_str -- The input string containing a Scala List representation
    
    Returns:
    A Python list containing the extracted elements with cleaned data
    """
    # 首先检查输入是否为空或None
    if not input_str:
        return []
    
    # 使用正则表达式匹配List内容
    list_pattern = r'List\((.*?)\)$'
    list_match = re.search(list_pattern, input_str, re.DOTALL)
    if not list_match:
        return []
        
    content = list_match.group(1).strip()
    
    # 尝试匹配三引号内容
    triple_quote_pattern = r'"""(.*?)"""'
    triple_quote_matches = re.findall(triple_quote_pattern, content, re.DOTALL)
    
    if triple_quote_matches:
        return triple_quote_matches
    
    # 如果没有三引号内容，尝试匹配普通引号内容
    single_quote_pattern = r'"((?:\\.|[^"\\])*?)"'
    single_quote_matches = re.findall(single_quote_pattern, content, re.DOTALL)
    
    elements = []
    for item in single_quote_matches:
        if item.strip():
            # 处理转义字符
            cleaned = item.replace("\\\"", "\"").replace("\\\\", "\\")
            elements.append(cleaned)
    
    return elements

def extract_quoted_string(input_str: str) -> str:
    """Extract content between quotes from a string.
    
    Args:
        input_str (str): Input string containing quoted content
        
    Returns:
        str: Extracted content between quotes, or empty string if not found
    """
    pattern = r'"(.*?)"'
    match = re.search(pattern, input_str)
    
    if match:
        return match.group(1)
    return ''

def extract_long_value(input_str: str) -> str:
    """Extract Long value from a string representation of a Scala Long variable.
    
    Args:
        input_str (str): Input string containing a Scala Long value (e.g. 'val res4: Long = 90194313219L')
        
    Returns:
        str: Extracted Long value including the 'L' suffix, or empty string if not found
    """
    pattern = r'= (\d+L)'
    match = re.search(pattern, input_str)
    
    if match:
        return match.group(1)
    return ''

def extract_value(input_str: str) -> str:
    """Extract value from a string based on its pattern.
    
    This function automatically selects the appropriate extraction method based on
    the input string format:
    * If contains 'Long =', uses extract_long_value
    * If contains triple quotes, uses extract_code_between_triple_quotes
    * If contains single quotes, uses extract_quoted_string
    
    Args:
        input_str (str): Input string containing a value to extract
        
    Returns:
        str: Extracted value based on the detected pattern
    """
    if 'Long =' in input_str:
        return extract_long_value(input_str)
    elif 'String = """' in input_str:
        return extract_code_between_triple_quotes(input_str)
    elif 'String = "' in input_str:
        return extract_quoted_string(input_str)
    else:
        return input_str