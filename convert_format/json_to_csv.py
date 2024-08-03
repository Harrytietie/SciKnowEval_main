import json
import csv
import os


# 1.分别 读，创建文件
filenames = os.listdir(r'E:/Open-LLM-Benchmark/questions/')
for filename in filenames:
    json_fp = open("E:/Open-LLM-Benchmark/questions/"+filename, "r", encoding='utf-8')
    csv_fp = open("E:/Open-LLM-Benchmark/questions/"+filename.split("json")[0]+"csv", "w", encoding='utf-8', newline='')

    # 2.提出表头和表的内容
    data_list = json.load(json_fp)
    sheet_title = data_list[0].keys()
    # sheet_title = {"姓名","年龄"}  # 将表头改为中文
    sheet_data = []
    for data in data_list:
        sheet_data.append(data.values())

    # 3.csv 写入器
    writer = csv.writer(csv_fp)

    # 4.写入表头
    writer.writerow(sheet_title)

    # 5.写入内容
    writer.writerows(sheet_data)

    # 6.关闭两个文件
    json_fp.close()
    csv_fp.close()
