import json
import os


def jsonl_to_json(jsonl_file, json_file):
    dict_list = []

    with open(jsonl_file, 'r', encoding='utf-8') as f:
        jsonl_data = f.readlines()
        for line in jsonl_data:
            line_dict = json.loads(line)
            dict_list.append(line_dict)

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(dict_list, f, indent=4, ensure_ascii=False)


filenames = os.listdir(r'E:/SciKnowEval_main/results/generate_questions/L4/toxicity_prediction/')
for filename in filenames:
    jsonl_file = 'E:/SciKnowEval_main/results/generate_questions/L4/toxicity_prediction/' + filename
    json_file = 'E:/SciKnowEval_main/results/generate_questions/L4/toxicity_prediction/' + filename.split('.jsonl')[0] + '.json'
    jsonl_to_json(jsonl_file, json_file)
