import os
import json
from lib.utils.json_utils import read_in_folder

data_folder = "./data/questions"

base_folder = os.path.join(data_folder, "base")
bio_folder = os.path.join(data_folder, "bio")
chem_folder = os.path.join(data_folder, "chem")

# use generators instead of lists to save memory
base_name, base_data = read_in_folder(base_folder)
bio_name, bio_data = read_in_folder(bio_folder)
chem_name, chem_data = read_in_folder(chem_folder)

# use sum() function and generator expressions to calculate the length of each dataset
base_length = sum(len(item) for item in base_data)
bio_length = sum(len(item) for item in bio_data)
chem_length = sum(len(item) for item in chem_data)

print("### Summary ###")
print("***Total question number: ", base_length + bio_length + chem_length, "***")

print(f"Total base question number: {base_length}")
print(f"Total bio question number: {bio_length}")
print(f"Total chem question number: {chem_length}")

print("### Base questions ###")
for name, data in zip(base_name, base_data):
    print(f"{len(data)} questions in {name}.")
    
print("### Bio questions ###")
for name, data in zip(bio_name, bio_data):
    print(f"{len(data)} questions in {name}.")

print("### Chem questions ###")
for name, data in zip(chem_name, chem_data):
    print(f"{len(data)} questions in {name}.")