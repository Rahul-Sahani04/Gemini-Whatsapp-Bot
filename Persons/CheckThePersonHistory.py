import pickle as pkl
import json
person = pkl.load(open("person.pkl", "rb"))
print(person)
# Dump the history to a txt file
with open("person.txt", "w") as f:
    for p in person:
        f.write(str(p) + "\n")
    