import os

# Assuming 'HOME' is an existing environment variable
home_directory = os.getenv('HOME')
print(f"Home Directory: {home_directory}")

# Using a default value if the variable doesn't exist
db_host = os.getenv('DB_HOST', 'localhost')
print(f"Database Host: {db_host}")
