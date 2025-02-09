#!/usr/bin/env python3
"""
Test SchemaBuilder for Gemini, OpenAI, and Anthropic
Author: Shilpaj Bhalerao
Date: Feb 9, 2025
"""
# Local Imports
from tools.tool_schema import create_schema


def test_get_user_gemini():
    """
    Test get_user function
    """
    def get_user(self, key: str, value: str) -> None:
        """
        Looks up a user by email, phone, or username.
    
        :param key: The attribute to search for a user by (email, phone, or username).
        :param value: The value to match for the specified attribute.
        :return: 
        """
        if key in {"email", "phone", "username"}:
            for customer in self.customers:
                if customer[key] == value:
                    return customer
            return f"Couldn't find a user with {key} of {value}"
        else:
            raise ValueError(f"Invalid key: {key}")
        return None

    # Required schema
    required_schema = {
        "name": "get_user",
        "description": "Looks up a user by email, phone, or username.",
        "parameters": {
            "type_": "OBJECT",
            "properties": {
                "key": {
                    "type_": "STRING", 
                    "description": "The attribute to search for a user by (email, phone, or username)."
                },
                "value": {
                    "type_": "STRING",
                    "description": "The value to match for the specified attribute."
                }
            },
            "required": ["key", "value"]
        }
    }

    # Actual schema
    actual_schema = create_schema(get_user)
    assert required_schema == actual_schema


def test_get_user_openai():
    """
    Test OpenAI schema format
    """
    def get_user(self, key: str, value: str) -> None:
        """
        Looks up a user by email, phone, or username.
    
        :param key: The attribute to search for a user by (email, phone, or username).
        :param value: The value to match for the specified attribute.
        """
        if key in {"email", "phone", "username"}:
            for customer in self.customers:
                if customer[key] == value:
                    return customer
            return f"Couldn't find a user with {key} of {value}"
        else:
            raise ValueError(f"Invalid key: {key}")
        return None

    required_schema = {
        "name": "get_user",
        "description": "Looks up a user by email, phone, or username.",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string", 
                    "description": "The attribute to search for a user by (email, phone, or username)."
                },
                "value": {
                    "type": "string",
                    "description": "The value to match for the specified attribute."
                }
            },
            "required": ["key", "value"]
        }
    }

    actual_schema = create_schema(get_user, tool_type='openai')
    assert required_schema == actual_schema


def test_get_user_anthropic():
    """
    Test Anthropic schema format
    """
    def get_user(self, key: str, value: str) -> None:
        """
        Looks up a user by email, phone, or username.
    
        :param key: The attribute to search for a user by (email, phone, or username).
        :param value: The value to match for the specified attribute.
        """
        if key in {"email", "phone", "username"}:
            for customer in self.customers:
                if customer[key] == value:
                    return customer
            return f"Couldn't find a user with {key} of {value}"
        else:
            raise ValueError(f"Invalid key: {key}")
        return None

    required_schema = {
        "name": "get_user",
        "description": "Looks up a user by email, phone, or username.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "STRING", 
                    "description": "The attribute to search for a user by (email, phone, or username)."
                },
                "value": {
                    "type": "STRING",
                    "description": "The value to match for the specified attribute."
                }
            },
            "required": ["key", "value"]
        }
    }

    actual_schema = create_schema(get_user, tool_type='anthropic')
    assert required_schema == actual_schema
