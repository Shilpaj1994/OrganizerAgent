#! /usr/bin/env python3
"""
Agent to create prompts with tools and send them to AI models. Get the response and process it.
Author: Shilpaj Bhalerao
Date: Feb 9, 2025
"""
# Standard Library Imports
import os
from pathlib import Path
from collections import OrderedDict
from typing import Any

# Third Party Imports
from dotenv import load_dotenv

# Local Imports
from ai_models import GeminiIntegration, DeepSeekIntegration, OpenAIIntegration
from tools import (get_directory_name, scan_directory, identify_file_types,
                   organize_files_by_type, compress_image, compress_pdf,
                   create_schema, send_email, add_calendar_event,
                   schedule_daily_stock_update)
from prompts import organizer_prompt

load_dotenv()


class Agent:
    """
    Class to create prompts with tools and send them to AI models. Get the response and process it.
    """
    __slots__ = ['ai_model', 'ai_provider']

    # Function and argument mapping (instance variables)
    function_map = {
        "get_directory_name": get_directory_name,
        "scan_directory": scan_directory,
        "identify_file_types": identify_file_types,
        "organize_files_by_type": organize_files_by_type,
        "compress_image": compress_image,
        "compress_pdf": compress_pdf,
        "send_email": send_email,
        "add_calendar_event": add_calendar_event,
        "schedule_daily_stock_update": schedule_daily_stock_update,
    }

    # Create a dictionary for argument mapping (make it an instance variable)
    arg_mapping = {
        'email_address': 'recipient',
        'email_subject': 'email_subject',
        'email_body': 'email_body',
        'event_name': 'event_name',
        'event_date': 'event_date',
        'event_start_time': 'event_start_time',
        'event_end_time': 'event_end_time',
        'shared_with': 'shared_with',
        'stock_symbol': 'stock_symbol',
        'scheduled_time': 'scheduled_time',
        'recipient': 'recipient'
    }

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
            create_schema(schedule_daily_stock_update),
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
            # Collect tools
            tools = self.collect_tools()
            print(f"{100 * '='} Tools {100 * '='}")
            [print(f"{tool}\n") for tool in tools]
            print(f"{200 * '='}")

            # Initialize the AI model
            self._initialize_ai_model(tools)

            # Create the prompt with the todo list (if it exists on the desktop)
            todo_list = []
            # Check if todo.txt exists on the desktop
            desktop_path = Path.home() / "Desktop"
            if (desktop_path / "todo.txt").exists():
                with open(desktop_path / "todo.txt", "r") as file:
                    todo_list = file.readlines()
            prompt = organizer_prompt(todo_list)
            print(f"{100 * '='} Prompt {100 * '='}")
            print(f"{prompt}\n")
            print(f"{200 * '='}")

            # Generate the response
            response = self.ai_model.generate_response(prompt)
            if response is None:
                raise ValueError("No response received from AI model")
            print(f"{100 * '='} Response {100 * '='}")
            print(f"{response}\n")
            print(f"{200 * '='}")

            # Extract the function calls from the response
            function_calls = self.ai_model.extract_function_call(response, set(self.function_map.keys()))
            if not isinstance(function_calls, OrderedDict):
                raise TypeError(f"Expected OrderedDict, got {type(function_calls)}")

            # Print the function calls to be executed
            print(f"{100 * '='} Function to be executed {100 * '='}")
            [print(f"{call_id + 1}. {function_call} with args: {function_call['args']}") for call_id, function_call in enumerate(function_calls.values())]
            print(f"{200 * '='}")

            # Execute the function calls
            self.execute_function_calls(function_calls)

        except Exception as e:
            print(f"Error in process_response: {str(e)}")

    def execute_function_calls(self, function_calls: OrderedDict) -> None:
        """
        Executes a sequence of function calls, handling dependencies.
        """
        results = {}
        current_path = None
        print(f"{100 * '='} Actions {100 * '='}")

        try:
            for call_id, function_call in function_calls.items():
                function_name = function_call['name']
                args = function_call['args']

                # Prepare arguments (mapping and path)
                mapped_args = self.prepare_arguments(function_call)

                # Handle result substitution
                for arg_name, arg_value in mapped_args.items():
                    if isinstance(arg_value, str) and arg_value.startswith('<result_from_'):
                        source_call_id = arg_value[len('<result_from_'):-1]
                        if source_call_id in results:
                            mapped_args[arg_name] = results[source_call_id]
                        else:
                            raise ValueError(f"Result from call ID '{source_call_id}' not found!")

                # --- Special handling for extract_info_from_todo ---
                if function_name == "extract_info_from_todo":
                    if 'file_path' in mapped_args:
                        # Find todo.txt in the file list
                        file_list = mapped_args['file_path']
                        todo_file_path = None
                        for f_path in file_list:
                            if os.path.basename(f_path) == 'todo.txt':
                                todo_file_path = f_path
                                break
                        if todo_file_path:
                            mapped_args['file_path'] = todo_file_path
                            todo_tasks = self.dispatch_function({'name': function_name, 'args': mapped_args})
                            results[call_id] = todo_tasks

                            # Immediately execute extracted tasks
                            if todo_tasks:
                                for task_name, task_args in todo_tasks:
                                    task_result = self.dispatch_function({'name': task_name, 'args': task_args})
                                    print(f"Result of (todo) {task_name}: {task_result}")
                        else:
                            print("Warning: todo.txt not found.")
                    continue  # Skip to the next function call

                # --- Dynamic dispatch for all other functions ---
                result = self.dispatch_function({'name': function_name, 'args': mapped_args})

                # Special handling for get_directory_name
                if function_name == "get_directory_name":
                    current_path = result

                results[call_id] = result
                print(f"\nResult of {function_name}: {result}")

        except Exception as e:
            print(f"Error executing functions: {e}")
        finally:
            print(f"{200 * '='}")

    def prepare_arguments(self, function_call: OrderedDict) -> dict:
        """
        Prepares arguments: maps names, adds path if needed, handles attendees.
        """
        function_name = function_call['name']
        function_to_call = self.function_map[function_name]
        arguments = function_call['args']

        mapped_args = {}
        for key, value in arguments.items():
            mapped_key = self.arg_mapping.get(key, key)
            mapped_args[mapped_key] = value
            if mapped_key == 'attendees' and isinstance(value, str):
                mapped_args[mapped_key] = [value]
        return mapped_args


    def dispatch_function(self, function_call: OrderedDict) -> Any:
        """
        Dispatches function calls.
        :param function_call: An OrderedDict containing 'name' and 'args'.
        :return: The result of the function call.
        :raises ValueError: If the function name is unknown.
        """
        function_name = function_call['name']
        function_to_call = self.function_map.get(function_name)

        if function_to_call is None:
            raise ValueError(f"Unknown function call: {function_name}")

        arguments = function_call.get('args', {})
        return function_to_call(**arguments)


if __name__ == "__main__":
    try:
        agent = Agent(ai_provider="gemini")
        agent.process_response()
    except Exception as e:
        print(f"Error: {str(e)}")
