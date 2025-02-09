# Custom Tools



If you want to write your own tools and add them to the LLM, follow the below instructions



- The tool should be a Python function

  ```python
  from tool import Tool
  
  class NewTool(Tool):
      name = "Name which LLM will use for this tool"
      description = "Description of the class"
      inputs = {"arg": {"type": "int", "description": "What is this param and why it is used"}}
      output_type = "bool"
      
      def forward(self, arg: int, arg2: str) -> bool:
          return True
  ```



Either do this OR



```python
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
```



- Once the function is written in this format, use another class to extract the information from this function and arrange it in a schema to send to the LLMs

  ```python
  from tools import create_schema
  
  # Code to extract the information and put it in the required schema
  output_schema = create_schema(get_user)
  ```

- Now, pass this output schema to the LLM