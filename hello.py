import sys
import os
import subprocess

hello = "hello"

def save_context(file_path: str, context: str) -> str:
    if not file_path or not os.path.isabs(file_path):
        raise ValueError("Invalid file path. Please provide an absolute path.")
    if not context:
        raise ValueError("Context cannot be empty.")
    try:
        with open(file_path, "w") as f:
            f.write(context)
        return f"Context saved successfully to {file_path}"
    except IOError as e:
        raise IOError(f"Error writing to file: {e}")

class Hello:
    def hello(self):
        print("Hello World")
    
    def bye(self):
        """
        By World function
        this is a docstring
        """
        return "By World"

if __name__ == "__main__":
    hello = Hello()
    hello.hello()