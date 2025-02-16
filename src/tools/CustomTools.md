# Custom Tools

- Tools are the function provided to the AI model which can be used to achieve the task

- If you want to write your own tools and add them to the repository, follow the below instructions

- The tool should be a Python function

- It should have annotations i.e. datatypes and return value should be mentioned

- The function should contain docstrings i.e. detailed description of the function along with the arguments description and return value

- Below is the Python function which can be used as a Tool

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

- Once the function is written in this format, use `create_schema()`  to convert this Python code to a tool which can be used by an AI model

  ```python
  # Import to convert Python function into a AI compatible tool
  from tools import create_schema
  
  # Code to extract the information and put it in the required schema
  user_tool = create_schema(get_user, tool_type='gemini')
  ```

- Now, this can be passed to the API of the AI model