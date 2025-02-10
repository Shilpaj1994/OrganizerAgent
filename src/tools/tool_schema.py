#!/usr/bin/env python3
"""
Tools schema for Gemini, OpenAI/DeepSeek, and Anthropic
Author: Shilpaj Bhalerao
Date: 2025-02-08
"""
# Standard Library Imports
from typing import Callable
import inspect


# ---------------------------- Google Gemini ----------------------------
class SchemaBuilderGemini:
    """
    Class for building tool schemas
    """
    def __init__(self, func: Callable):
        self.func = func
        self.schema = {
            'name': func.__name__,
            'description': '',
            'parameters': {
                'type': 'OBJECT', 
                'properties': {},
                'required': []
            }
        }
        self._build_schema()

    def _build_schema(self):
        """
        Build the complete schema
        """
        sig = inspect.signature(self.func)
        doc = inspect.getdoc(self.func) or ""
        
        # Set description from first docstring paragraph
        self.schema['description'] = doc.split('\n\n')[0] if doc else ''
        
        # Process parameters
        param_descriptions = {}
        for line in doc.split('\n'):
            if line.strip().startswith(':param '):
                param_name = line.split(':param ')[1].split(':')[0].strip()
                description = line.split(':', 2)[-1].strip()
                param_descriptions[param_name] = description

        # Build properties and required list
        for name, param in sig.parameters.items():
            if name == 'self':
                continue
                
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            json_type = 'STRING'
            if param_type in [int, float]:
                json_type = 'NUMBER'
            elif param_type == bool:
                json_type = 'BOOLEAN'
                
            self.schema['parameters']['properties'][name] = {
                'type': json_type,
                'description': param_descriptions.get(name, '')
            }
            
            if param.default == inspect.Parameter.empty:
                self.schema['parameters']['required'].append(name)


# ---------------------------- OpenAI ----------------------------
class SchemaBuilderOpenAI:
    """
    Class for building OpenAI-compatible tool schemas
    """
    def __init__(self, func: Callable):
        self.func = func
        self.schema = {
            'name': func.__name__,
            'description': '',
            'parameters': {
                'type': 'object', 
                'properties': {},
                'required': []
            }
        }
        self._build_schema()

    def _build_schema(self):
        """Build schema in OpenAI format"""
        sig = inspect.signature(self.func)
        doc = inspect.getdoc(self.func) or ""
        
        self.schema['description'] = doc.split('\n\n')[0] if doc else ''
        
        param_descriptions = {}
        for line in doc.split('\n'):
            if line.strip().startswith(':param '):
                param_name = line.split(':param ')[1].split(':')[0].strip()
                description = line.split(':', 2)[-1].strip()
                param_descriptions[param_name] = description

        for name, param in sig.parameters.items():
            if name == 'self':
                continue
                
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            json_type = 'string'
            if param_type in [int, float]:
                json_type = 'number'
            elif param_type == bool:
                json_type = 'boolean'
                
            self.schema['parameters']['properties'][name] = {
                'type': json_type,
                'description': param_descriptions.get(name, '')
            }
            
            if param.default == inspect.Parameter.empty:
                self.schema['parameters']['required'].append(name)


# ---------------------------- Anthropic ----------------------------
class SchemaBuilderAnthropic:
    """
    Class for building Anthropic-compatible tool schemas
    """
    def __init__(self, func: Callable):
        self.func = func
        self.schema = {
            'name': func.__name__,
            'description': '',
            'input_schema': {
                'type': 'object',
                'properties': {},
                'required': []
            }
        }
        self._build_schema()

    def _build_schema(self):
        """
        Build schema in Anthropic format
        """
        sig = inspect.signature(self.func)
        doc = inspect.getdoc(self.func) or ""
        
        self.schema['description'] = doc.split('\n\n')[0] if doc else ''
        
        param_descriptions = {}
        for line in doc.split('\n'):
            if line.strip().startswith(':param '):
                param_name = line.split(':param ')[1].split(':')[0].strip()
                description = line.split(':', 2)[-1].strip()
                param_descriptions[param_name] = description

        for name, param in sig.parameters.items():
            if name == 'self':
                continue
                
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            json_type = 'STRING'
            if param_type in [int, float]:
                json_type = 'NUMBER'
            elif param_type == bool:
                json_type = 'BOOLEAN'
                
            self.schema['input_schema']['properties'][name] = {
                'type': json_type,
                'description': param_descriptions.get(name, '')
            }
            
            if param.default == inspect.Parameter.empty:
                self.schema['input_schema']['required'].append(name)


# ---------------------------- Main ----------------------------
def create_schema(func: Callable, tool_type: str = 'gemini') -> dict:
    """
    Generate tool schema using SchemaBuilder class.
    
    Usage:
    schema = create_schema(get_user)
    """
    if tool_type == 'gemini':
        builder = SchemaBuilderGemini(func)
    elif tool_type == 'openai':
        builder = SchemaBuilderOpenAI(func)
    elif tool_type == 'anthropic':
        builder = SchemaBuilderAnthropic(func)
    else:
        raise ValueError(f"Invalid tool type: {tool_type}")
    return builder.schema
