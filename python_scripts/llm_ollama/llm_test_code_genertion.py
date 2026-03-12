import ollama
code_prompt = "Write a Python function that checks if a number is prime."
response = ollama.generate(model='codellama', prompt=code_prompt)
print(response['response'])
