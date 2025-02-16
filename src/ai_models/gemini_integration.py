#! /usr/bin/env python3
"""
Gemini Integration
Author: Shilpaj Bhalerao
Date: Feb 08, 2025
"""

# Standard Library Imports
import os
from collections import OrderedDict

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
        Generates a response from the Gemini API.
        :param prompt: The input prompt.
        :return: The Gemini response, or None on error.
        """
        try:
            # Try slightly different generation parameters
            generation_config = {
                "temperature": 0.2,  # Slightly more creative
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=False
            )

            if not response.candidates[0].content.parts:
                raise ValueError("Empty response received")

            return response
        except Exception as e:
            print(f"API Error: {str(e)}")
            return None

    def extract_function_call(self, response: str, valid_function_names: set) -> OrderedDict:
        """
        Extracts function calls from the Gemini API response.  Handles both
        'function_call' objects and text-based function calls.  Robustly
        handles extra text or newlines.

        :param response: The response from the Gemini API.
        :param valid_function_names: Set of valid function names
        :return: An OrderedDict containing function call details, preserving order.
        """
        ordered_function_calls = OrderedDict()

        try:
            for candidate in response.candidates:
                for part_index, part in enumerate(candidate.content.parts):
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = OrderedDict([
                            ('name', part.function_call.name),
                            ('args', dict(part.function_call.args))  # Convert to dict
                        ])
                        ordered_function_calls[str(len(ordered_function_calls))] = function_call

                    elif hasattr(part, 'text') and part.text:
                        # Robustly handle text-based function calls
                        lines = part.text.strip().split('\n')
                        for line in lines:
                            line = line.strip()
                            if not line:  # Skip empty lines
                                continue
                            if '(' not in line or ')' not in line:
                                print(f"Skipping invalid line: '{line}'")
                                continue

                            try:
                                name = line[:line.index('(')].strip()
                                # Remove 'default_api.' prefix if present
                                if name.startswith("default_api."):
                                    name = name[len("default_api."):]

                                # Validate function name
                                if name not in valid_function_names:
                                    print(f"Skipping invalid function name: '{name}'")
                                    continue

                                args_str = line[line.index('(') + 1:line.rindex(')')]
                                args = {}
                                for arg_pair in args_str.split(','):
                                    arg_pair = arg_pair.strip()
                                    if not arg_pair or '=' not in arg_pair:
                                        continue
                                    key, value = arg_pair.split('=', 1)
                                    key = key.strip().strip("'\"")
                                    value = value.strip().strip("'\"")
                                    args[key] = value

                                function_call = OrderedDict([('name', name), ('args', args)])
                                ordered_function_calls[str(len(ordered_function_calls))] = function_call

                            except (ValueError, IndexError) as e:
                                print(f"Error parsing: '{line}' - {e}")
                                continue

            return ordered_function_calls

        except Exception as e:
            print(f"Error extracting function calls: {e}")
            return OrderedDict()
