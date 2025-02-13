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
from tools.system_tools.system_tools import list_directory_files, get_directory_name, organize_files
from tools.tool_schema import create_schema
from prompts.prompt import organizer_prompt


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
            create_schema(organize_files)
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
            function_call = self.ai_model.extract_function_call(response)
            if not isinstance(function_call, OrderedDict):
                raise TypeError(f"Expected OrderedDict, got {type(function_call)}")
            
            self.action(function_call, path)

        except Exception as e:
            print(f"Error in process_response: {str(e)}")

    def action(self, function_call: OrderedDict, path: str) -> None:
        """
        Method to execute the code using a dispatcher.
        :param function_call: OrderedDict containing function call details
        :param path: Path to the directory
        """
        try:
            if not all(key in function_call for key in ['name', 'args']):
                raise KeyError("Function call missing required keys: 'name' and 'args'")
            
            result = self.dispatch_function(function_call, path)
            print(f"Result of {function_call['name']}: {result}")
        except Exception as e:
            print(f"Error executing {function_call.get('name', 'unknown')}: {e}")

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
            # Add more mappings here as you add more tools
        }

        function_name = function_call['name']
        if function_name not in function_map:
            raise ValueError(f"Unknown function call: {function_name}")

        function_to_call = function_map[function_name]
        arguments = function_call['args']
        print(f"\nArguments: {arguments}")
        
        arguments['path'] = path
        print(f"\nPath: {arguments['path']}")
        return function_to_call(**arguments)


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
