#! /usr/bin/env python3
"""
Gemini Integration
Author: Shilpaj Bhalerao
Date: 2025-02-08
"""

# Standard Library Imports
import os
from collections import OrderedDict
from datetime import datetime

# Third Party Imports
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

# Local Imports
from ai_models.ai_integration import AIIntegration


class GeminiIntegration(AIIntegration):
    """
    Class to call Gemini API and get the response
    """
    def __init__(self, tools: list, model_name: str = 'gemini-2.0-flash-exp'):
        """
        Constructor for GeminiIntegration class
        :param tools: List of tools to use
        :param model_name: Name of the Gemini model to use [default: gemini-2.0-flash-exp] [options: gemini-1.5-flash, gemini-1.5-pro, gemini-1.5-pro-exp-0801]
        """
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))    # Store API key in .env file OR use `export GEMINI_API_KEY=<your_api_key>`

        # Convert tools to Gemini Tools format
        gemini_tools = [Tool(function_declarations=[FunctionDeclaration(**schema)]) for schema in tools]

        # Create model with tools
        self.model = genai.GenerativeModel(model_name, tools=gemini_tools)

    def generate_response(self, prompt: str) -> str:
        """
        Method to generate response from Gemini API
        :param prompt: Input prompt
        :return: Gemini response
        """
        try:
            response = self.model.generate_content(prompt)
            return response
        except Exception as e:
            print(f"API Error: {str(e)}")

    def extract_function_call(self, response: str) -> OrderedDict:
        """
        Method to take the response, extract all the function calls with arguments and return an ordered dict of function calls
        :param response: Response from Gemini API
        :return: OrderedDict containing function call details to preserve call sequence
        """
        # Create an OrderedDict to store function calls
        ordered_function_calls = OrderedDict()

        # Extract the function calls from the response
        for part in response.candidates[0].content.parts:
            if part.function_call:
                function_call = part.function_call
                # Create an OrderedDict with function call details
                ordered_function_call = OrderedDict([
                    ('name', function_call.name),
                    ('args', function_call.args)
                ])

                # Append to the main OrderedDict
                ordered_function_calls[function_call.name] = ordered_function_call
        
        return ordered_function_calls
