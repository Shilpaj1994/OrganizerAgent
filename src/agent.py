#! /usr/bin/env python3
"""
Agent to create prompts with tools and send them to AI models. Get the response and process it.
Author: Shilpaj Bhalerao
Date: Feb 9, 2025
"""
# Standard Library Imports
import os
from collections import OrderedDict
from typing import Any

# Third Party Imports

# Local Imports
from ai_models import GeminiIntegration, DeepSeekIntegration, OpenAIIntegration
from tools import list_directory_files, get_directory_name, organize_files, compress_image, compress_pdf, create_schema, send_email, add_calendar_event, share_stock_market_data, send_daily_stock_update
from prompts import organizer_prompt


class Agent:
    """
    Class to create prompts with tools and send them to AI models. Get the response and process it.
    """
    __slots__ = ['ai_model', 'ai_provider']

    def __init__(self, ai_provider: str = "gemini"):
        """
        Constructor for Agent class
        :param ai_provider: Name of the AI provider to use [default: gemini] [options: gemini, openai, anthropic]
        """
        self.ai_model = None
        self.ai_provider = ai_provider

    def collect_tools(self) -> list[dict]:
        """
        Method to collect tools from the tools directory
        :return: List of tool schemas
        """
        # Create Tool wrappers with function declarations
        tools = [
            create_schema(organize_files),
            create_schema(compress_image),
            create_schema(compress_pdf),
            create_schema(send_email),
            create_schema(add_calendar_event),
            create_schema(share_stock_market_data),
            create_schema(send_daily_stock_update)
            # create_schema(list_directory_files),
            # create_schema(get_directory_name)
        ]
        return tools

    def _initialize_ai_model(self, tools: list) -> None:
        """
        Initialize the AI model based on the provider
        :param tools: List of tools to use
        :raises ValueError: If AI provider is not supported
        """
        ai_providers = {
            "gemini": lambda: GeminiIntegration(tools),
            "deepseek": lambda: DeepSeekIntegration(tools),
            "openai": lambda: OpenAIIntegration(tools),
            # "anthropic": lambda: AnthropicIntegration(tools),
        }

        if self.ai_provider not in ai_providers:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
        
        self.ai_model = ai_providers[self.ai_provider]()

    def process_response(self, path: str) -> None:
        """
        Method to process the response from AI model
        :param path: Path to the directory to organize
        """
        try:
            # Get the tools
            tools = self.collect_tools()
            print(f"Tools: {tools}\n")

            # Initialize AI model
            self._initialize_ai_model(tools)

            # Create the prompt
            prompt = organizer_prompt()
            print(f"Prompt: {prompt}\n")

            # Send the prompt to AI model
            response = self.ai_model.generate_response(prompt)
            if response is None:
                raise ValueError("No response received from AI model")
            print(f"Response: {response}")

            # Extract and process function calls
            function_calls = self.ai_model.extract_function_call(response)
            if not isinstance(function_calls, OrderedDict):
                raise TypeError(f"Expected OrderedDict, got {type(function_calls)}")
            
            self.action(function_calls, path)

        except Exception as e:
            print(f"Error in process_response: {str(e)}")

    def action(self, function_calls: OrderedDict, path: str) -> None:
        """
        Method to execute the code using a dispatcher.
        :param function_calls: OrderedDict containing multiple function call details
        :param path: Path to the directory
        """
        try:
            # Execute each function call in order
            for call_id, function_call in function_calls.items():
                if not all(key in function_call for key in ['name', 'args']):
                    raise KeyError(f"Function call {call_id} missing required keys: 'name' and 'args'")
                
                # Add path to arguments if not present
                if 'path' not in function_call['args']:
                    function_call['args']['path'] = path
                
                # result = self.dispatch_function(function_call, path)
                # print(f"Result of {function_call['name']}: {result}")
                print(f"Function call: {function_call} with args: {function_call['args']}\n")
                
        except Exception as e:
            print(f"Error executing functions: {e}")

    def dispatch_function(self, function_call: OrderedDict, path: str) -> Any:
        """
        Dispatcher function to call the appropriate function based on the function call name.
        Uses a dictionary for function mapping.
        :param function_call: OrderedDict containing function call details
        :param path: Path to the directory
        :return: Result of the function call
        :raises ValueError: If function name is not found in function_map
        """
        function_map = {
            "list_directory_files": list_directory_files,
            "organize_files": organize_files,
            "compress_image": compress_image,
            "compress_pdf": compress_pdf,
            "send_email": send_email,
            "add_calendar_event": add_calendar_event,
            "share_stock_market_data": share_stock_market_data,
            "send_daily_stock_update": send_daily_stock_update
        }

        function_name = function_call['name']
        if function_name not in function_map:
            raise ValueError(f"Unknown function call: {function_name}")

        function_to_call = function_map[function_name]
        arguments = function_call['args']
        
        # Map argument names if needed
        arg_mapping = {
            'email_address': 'recipient',
            'email_subject': 'subject',
            'email_body': 'body',
            'event_date': 'date',
            'event_start_time': 'time',
            'shared_with': 'attendees',
            'stock_symbol': 'symbol'
        }
        
        # Update argument names based on mapping
        mapped_args = {}
        for key, value in arguments.items():
            mapped_key = arg_mapping.get(key, key)
            mapped_args[mapped_key] = value
            
            # Convert string to list for attendees
            if mapped_key == 'attendees' and isinstance(value, str):
                mapped_args[mapped_key] = [value]

        return function_to_call(**mapped_args)


if __name__ == "__main__":
    try:
        # Get the path from the user
        default_path = "/media/shilpaj/2A42A8EC42A8BDC7/Udacity/EPAi/Agent/experiments"
        path = input("Enter the path to the directory to organize (default: current directory): ") or default_path
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory not found: {path}")
            
        agent = Agent(ai_provider="gemini")
        agent.process_response(path)
    except Exception as e:
        print(f"Error: {str(e)}")
