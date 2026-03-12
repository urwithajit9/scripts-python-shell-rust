import ollama

# Use the generate function for a one-off prompt
result = ollama.generate(model='llama2', prompt='Why is the sky blue?')
print(result['response'])
