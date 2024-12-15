import sys
import os
import subprocess

hello = "hello"

class Hello:
    def hello(self):
        print("Hello World")
    
    def bye(self):
        """
        By World function
        this is a docstring
        """
        print("By World")
        return "By World"


if __name__ == "__main__":
    hello = Hello()
    hello.hello()
