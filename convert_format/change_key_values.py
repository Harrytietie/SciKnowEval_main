import json


# 读取JSON文件
with open("E:/SciKnowEval_main/results/json/L3/MCQ_medical_image_diagnosis_prediction.json", "r", encoding='utf-8') as file:
    datas = json.load(file)

# 修改JSON数据
for data in datas:
    # data["type"] = "gen"
    # data["domain"] = "Medicine"
    data["details"]["task"] = "medical_image_diagnosis_prediction"
    # data["details"]["subtask"] = "toxicity_prediction_judge"
    # data["details"]["source"] = "PubMed"

# 将修改后的数据写回文件中
with open("E:/SciKnowEval_main/results/json/L3/MCQ_medical_image_diagnosis_prediction.json", "w", encoding='utf-8') as file:
    json.dump(datas, file, indent=4)

print("JSON文件已成功修改。")
