import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv(dotenv_path='set.env')
# Example: Test if environment variables are loaded and print them
print("Testing environment variables...")

for key, value in os.environ.items():
    print(f"{key} = {value}")