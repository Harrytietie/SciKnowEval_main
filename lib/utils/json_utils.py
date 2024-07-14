import json
import os

def read_jsonl(file_path):
    """
    Read a JSONL file and return its filename and a list of dictionaries.
    """
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f]

def read_in_folder(folder_path):
    """
    Read all JSONL files in a folder and return a list of dictionaries, every dictionary contains the filename and a list of dictionaries.
    """
    names = []
    data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.jsonl'):
            names.append(file_name)
            file_path = os.path.join(folder_path, file_name)
            data.append(read_jsonl(file_path))
    # print("names: ", names)
    # print("data: ", data[0])
    return names, data

def write_jsonl(file_path, data):
    """
    Write a list of dictionaries to a JSONL file.
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass
    with open(file_path, 'a') as f:
        for d in data:
            f.write(json.dumps(d) + '\n')
    print(f"Data written to {file_path}")

def write_folder(folder_path, names, data):
    """
    Write a list of dictionaries to a folder of JSONL files.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for name, d in zip(names, data):
        file_path = os.path.join(folder_path, name)
        write_jsonl(file_path, d)
    print(f"Data written to {folder_path}")