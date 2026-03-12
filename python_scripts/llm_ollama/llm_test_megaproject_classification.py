import ollama

text = "Pexapark Records 24 European Ppas For Over 1.5 Gw In March"

prompt = f"Classify given title to megaproject or not, a megaproject is a large construction project and it must have scope of construction. Also extract any enitity information like company name, country: \n\n\"\"\"\n{text}\n\"\"\""
result = ollama.generate(model='llama2', prompt=prompt)
print("Summary:", result['response'])
