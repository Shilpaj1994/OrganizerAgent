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
from tools import get_directory_name, scan_directory, identify_file_types, organize_files_by_type, compress_image, compress_pdf, create_schema, send_email, add_calendar_event, share_stock_market_data, send_daily_stock_update
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
            create_schema(get_directory_name),
            create_schema(scan_directory),
            create_schema(identify_file_types),
            create_schema(organize_files_by_type),
            create_schema(compress_image),
            create_schema(compress_pdf),
            create_schema(send_email),
            create_schema(add_calendar_event),
            create_schema(share_stock_market_data),
            create_schema(send_daily_stock_update)
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

    def process_response(self) -> None:
        """
        Processes the response from the AI model.
        """
        try:
            tools = self.collect_tools()
            print(f"{100 * '='} Tools {100 * '='}")
            [print(f"{tool}\n") for tool in tools]
            print(f"{200 * '='}")

            self._initialize_ai_model(tools)

            prompt = organizer_prompt()
            print(f"{100 * '='} Prompt {100 * '='}")
            print(f"{prompt}\n")
            print(f"{200 * '='}")

            response = self.ai_model.generate_response(prompt)
            if response is None:
                raise ValueError("No response received from AI model")
            print(f"{100 * '='} Response {100 * '='}")
            print(f"{response}\n")
            print(f"{200 * '='}")

            function_calls = self.ai_model.extract_function_call(response)
            if not isinstance(function_calls, OrderedDict):
                raise TypeError(f"Expected OrderedDict, got {type(function_calls)}")

            print(f"{100 * '='} Function to be executed {100 * '='}")
            [print(f"{call_id + 1}. {function_call} with args: {function_call['args']}") for call_id, function_call in enumerate(function_calls.values())]
            print(f"{200 * '='}")

            self.execute_function_calls(function_calls)

        except Exception as e:
            print(f"Error in process_response: {str(e)}")

    def execute_function_calls(self, function_calls: OrderedDict) -> None:
        """
        Executes a sequence of function calls, handling dependencies.
        :param function_calls: An OrderedDict of function calls.
        """
        results = {}  # Store results of function calls
        print(f"{100 * '='} Actions {100 * '='}")
        try:
            count = 1
            for call_id, function_call in function_calls.items():
                count += 1
                if not all(key in function_call for key in ['name', 'args']):
                    raise KeyError(f"Function call {call_id} missing 'name' or 'args'")

                # Get the function name
                function_name = function_call['name']

                # If it's get_directory_name, call it and store the result
                if function_name == 'get_directory_name':
                    current_path = self.dispatch_function(function_call)
                    results[call_id] = current_path  # Store the result
                    print(f"Result of {function_name}: {current_path}")
                    continue  # Move to the next function call

                # For other functions, prepare arguments
                mapped_args = self.prepare_arguments(function_call, current_path)

                # Substitute results from previous calls if needed
                for arg_name, arg_value in mapped_args.items():
                    if isinstance(arg_value, str) and arg_value.startswith('<result_from_'):
                        # Extract the call ID from the placeholder
                        source_call_id = arg_value[len('<result_from_'):-1]
                        # Get result from previous call
                        if source_call_id in results:
                            mapped_args[arg_name] = results[source_call_id]
                        else:
                            raise ValueError(f"Result from call ID '{source_call_id}' not found!")

                # Call the function with prepared arguments
                result = self.dispatch_function({'name': function_name, 'args': mapped_args})
                results[call_id] = result  # Store the result
                print(f"{count}. Result of {function_name}: {result}\n")
                # print(f"Result of {function_name}: {mapped_args}")

        except Exception as e:
            print(f"Error executing functions: {e}")
        finally:
            print(f"{200 * '='}")

    def prepare_arguments(self, function_call: OrderedDict, path: str) -> dict:
        """Prepares arguments for a function call, including mapping and path."""
        function_name = function_call['name']
        function_to_call = self.function_map[function_name]  # Access function_map directly
        arguments = function_call['args']

        mapped_args = {}
        for key, value in arguments.items():
            mapped_key = self.arg_mapping.get(key, key)
            mapped_args[mapped_key] = value
            if mapped_key == 'attendees' and isinstance(value, str):
                mapped_args[mapped_key] = [value]

        if 'path' in function_to_call.__code__.co_varnames:
            mapped_args['path'] = path

        return mapped_args

    # Create a dictionary for function mapping (make it an instance variable)
    function_map = {
        "get_directory_name": get_directory_name,
        "scan_directory": scan_directory,
        "identify_file_types": identify_file_types,
        "organize_files_by_type": organize_files_by_type,
        "compress_image": compress_image,
        "compress_pdf": compress_pdf,
        "send_email": send_email,
        "add_calendar_event": add_calendar_event,
        "share_stock_market_data": share_stock_market_data,
        "send_daily_stock_update": send_daily_stock_update
    }

    # Create a dictionary for argument mapping (make it an instance variable)
    arg_mapping = {
        'email_address': 'recipient',
        'email_subject': 'subject',
        'email_body': 'body',
        'event_date': 'date',
        'event_start_time': 'time',
        'shared_with': 'attendees',
        'stock_symbol': 'symbol'
    }

    def dispatch_function(self, function_call: OrderedDict) -> Any:
        """
        Dispatches function calls to the appropriate functions.

        Args:
            function_call: An OrderedDict containing 'name' and 'args'.

        Returns:
            The result of the function call.

        Raises:
            ValueError: If the function name is unknown.
        """
        function_name = function_call['name']
        if function_name not in self.function_map:
            raise ValueError(f"Unknown function call: {function_name}")

        function_to_call = self.function_map[function_name]
        arguments = function_call['args']

        # Argument name mapping (as before)
        mapped_args = {}
        for key, value in arguments.items():
            mapped_key = self.arg_mapping.get(key, key)  # Use .get() for safety
            mapped_args[mapped_key] = value

            if mapped_key == 'attendees' and isinstance(value, str):
                mapped_args[mapped_key] = [value]

        # Add path argument ONLY if the function expects it
        # if 'path' in function_to_call.__code__.co_varnames:
        #     mapped_args['path'] = path

        return function_to_call(**mapped_args)


if __name__ == "__main__":
    try:
        agent = Agent(ai_provider="gemini")
        agent.process_response()
    except Exception as e:
        print(f"Error: {str(e)}")
