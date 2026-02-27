import re

with open("project.txt", "r") as file:
    text = file.read()

sentences = re.split(r'[.!?]', text)
sentences = [s.strip() for s in sentences if s.strip()]

for s in sentences:
    print(s)

