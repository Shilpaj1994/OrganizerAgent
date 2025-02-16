"""
Abstract Base Class for AI Integration
Author: Shilpaj Bhalerao
Date: Feb 10, 2025
"""
# Standard Library Imports
from abc import ABC, abstractmethod
from collections import OrderedDict


class AIIntegration(ABC):
    """
    Abstract base class that defines the interface for AI model integrations
    """
    
    @abstractmethod
    def __init__(self, tools: list, model_name: str):
        """
        Constructor for AIIntegration class
        :param tools: List of tools to use
        :param model_name: Name of the AI model to use
        """
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Method to generate response from AI API
        :param prompt: Input prompt
        :return: AI response
        """
        pass

    @abstractmethod
    def extract_function_call(self, response: str) -> OrderedDict:
        """
        Method to extract function calls from the response
        :param response: Response from AI API
        :return: OrderedDict containing function call details to preserve call sequence
        """
        pass 