#! /usr/bin/env python3
"""
OpenAI Integration
Author: Shilpaj Bhalerao
Date: 2025-02-08
"""

# Standard Library Imports
import os
import json
from collections import OrderedDict
from typing import Any

# Third Party Imports
from openai import OpenAI

# Local Imports
from ai_models.ai_integration import AIIntegration


class OpenAIIntegration(AIIntegration):
    """
    Class to call OpenAI API and get the response
    """
    def __init__(self, tools: list, model_name: str = 'gpt-4'):
        """
        Constructor for OpenAIIntegration class
        :param tools: List of tools to use
        :param model_name: Name of the OpenAI model to use [default: gpt-4]
        """
        # Validate API key first
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable")

        # Configure OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate_response(self, prompt: str) -> str:
        """
        Generate response from OpenAI API
        :param prompt: Input prompt
        :return: OpenAI response
        """
        try:
            response = self.client.chat.completions.create(model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150)
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API Error: {str(e)}")
            return ""

    def extract_function_call(self, response: Any) -> OrderedDict:
        """
        Extract function calls from OpenAI response
        :param response: API response
        :return: OrderedDict with function call details
        """
        # Since the current implementation doesn't support function calling,
        # we'll return an empty OrderedDict
        return OrderedDict()
