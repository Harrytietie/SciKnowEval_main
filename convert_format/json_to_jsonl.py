import json


# 从JSON文件读取数据
with open('E:/SciKnowEval_main/results/json/L3/MCQ_medical_image_diagnosis_prediction.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 将数据保存为JSONL文件
with open('E:/SciKnowEval_main/results/generate_questions/L3/MCQ_medical_image_diagnosis_prediction.jsonl', 'w', encoding='utf-8') as f:
    for item in data:
        f.write(json.dumps(item) + '\n')
