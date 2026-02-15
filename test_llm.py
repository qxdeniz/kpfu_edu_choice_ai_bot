from llm import *

model = LLM("gemini")
r = model.generate_response("Привет")
print(r)