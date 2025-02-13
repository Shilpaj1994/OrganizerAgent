#! /usr/bin/env python3
"""
DeepSeek Integration from their website
Author: Shilpaj Bhalerao
Date: 2025-02-08
"""

# Standard Library Imports
import os
import json
from collections import OrderedDict
from typing import Any

# Third Party Imports
import openai

# Local Imports
from ai_models.ai_integration import AIIntegration


class DeepSeekIntegration(AIIntegration):
    """
    Class to call DeepSeek API using OpenAI-compatible format
    """
    def __init__(self, tools: list, model_name: str = 'deepseek-chat'):
        """
        Constructor for DeepSeekIntegration class
        :param tools: List of tools to use
        :param model_name: Name of the DeepSeek model [default: deepseek-chat]
        """
        # Validate API key first
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek API key not found. Set DEEPSEEK_API_KEY environment variable")

        # Configure OpenAI client for DeepSeek
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        self.model_name = model_name
        self.tools = [self._convert_tool_schema(schema) for schema in tools]

    def _convert_tool_schema(self, schema: dict) -> dict:
        """Convert standard tool schema to OpenAI-compatible format"""
        return {
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema.get("description", ""),
                "parameters": schema.get("parameters", {})
            }
        }

    def generate_response(self, prompt: str) -> Any:
        """
        Generate response from DeepSeek API
        :param prompt: Input prompt
        :return: API response
        """
        try:
            return self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                tools=self.tools,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"API Error: {str(e)}")
            return None

    def extract_function_call(self, response: Any) -> OrderedDict:
        """
        Extract function calls from DeepSeek response
        :param response: API response
        :return: OrderedDict with function call details
        """
        try:
            if not response or not response.choices:
                return OrderedDict()

            tool_calls = response.choices[0].message.tool_calls
            if not tool_calls:
                return OrderedDict()

            # Get first function call (assuming single function call)
            function_call = tool_calls[0].function
            
            return OrderedDict([
                ('name', function_call.name),
                ('args', json.loads(function_call.arguments))  # Parse JSON arguments
            ])
        except Exception as e:
            print(f"Error extracting function call: {str(e)}")
            return OrderedDict()
