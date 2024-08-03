import os
import json
from lib.utils.json_utils import read_in_folder


L1_data_folder = "./results/generate_questions/L1"
L2_data_folder = "./results/generate_questions/L2"
L3_data_folder = "./results/generate_questions/L3"
L4_data_folder = "./results/generate_questions/L4"
L5_data_folder = "./results/generate_questions/L5"

L4_1_data_folder = os.path.join(L4_data_folder, "ethic_problem")
L4_2_data_folder = os.path.join(L4_data_folder, "laboratory_safety_test")
L4_3_data_folder = os.path.join(L4_data_folder, "toxicity_prediction")

# use generators instead of lists to save memory
L1_name, L1_data = read_in_folder(L1_data_folder)
L2_name, L2_data = read_in_folder(L2_data_folder)
L3_name, L3_data = read_in_folder(L3_data_folder)
L4_1_name, L4_1_data = read_in_folder(L4_1_data_folder)
L4_2_name, L4_2_data = read_in_folder(L4_2_data_folder)
L4_3_name, L4_3_data = read_in_folder(L4_3_data_folder)
L5_name, L5_data = read_in_folder(L5_data_folder)


# use sum() function and generator expressions to calculate the length of each dataset
L1_length = sum(len(item) for item in L1_data)
L2_length = sum(len(item) for item in L2_data)
L3_length = sum(len(item) for item in L3_data)
L4_1_length = sum(len(item) for item in L4_1_data)
L4_2_length = sum(len(item) for item in L4_2_data)
L4_3_length = sum(len(item) for item in L4_3_data)
L4_length = L4_1_length + L4_2_length + L4_3_length
L5_length = sum(len(item) for item in L5_data)


print("### Summary ###")
print("***Total question number: ", L1_length + L2_length + L3_length + L4_length + L5_length, "***")

print(f"Total L1 question number: {L1_length}")
print(f"Total L2 question number: {L2_length}")
print(f"Total L3 question number: {L3_length}")
print(f"Total L4 question number: {L4_length}")
print(f"Total L5 question number: {L5_length}")

print()
print("### L1 questions ###")
for name, data in zip(L1_name, L1_data):
    print(f"{len(data)} questions in {name}.")
print()
print("### L2 questions ###")
for name, data in zip(L2_name, L2_data):
    print(f"{len(data)} questions in {name}.")
print()
print("### L3 questions ###")
for name, data in zip(L3_name, L3_data):
    print(f"{len(data)} questions in {name}.")
print()
print("### L4 questions ###")
for name, data in zip(L4_1_name, L4_1_data):
    print(f"{len(data)} questions in {name}.")
for name, data in zip(L4_2_name, L4_2_data):
    print(f"{len(data)} questions in {name}.")
for name, data in zip(L4_3_name, L4_3_data):
    print(f"{len(data)} questions in {name}.")
print()
print("### L5 questions ###")
for name, data in zip(L5_name, L5_data):
    print(f"{len(data)} questions in {name}.")