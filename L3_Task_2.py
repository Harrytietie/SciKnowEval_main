import os
import openai
import json
import pandas as pd
import random


# 初始化OpenAI客户端
client = openai.OpenAI(
    api_key="sk-KmLopBhOMFbaWEWK983e254826114f9fB9E4C974568224D3",
    base_url='https://api.ai-gaochao.cn/v1'
)


# 从CSV文件中读取数据
def extract_questions_from_csv(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()
        if not content:
            raise ValueError(f"The file {file_path} is empty.")

    try:
        df = pd.read_csv(file_path)
        if df.empty:
            raise ValueError(f"The file {file_path} contains no data.")
    except pd.errors.EmptyDataError as e:
        raise ValueError(f"EmptyDataError: No columns to parse from file {file_path}")

    questions = df.to_dict(orient='records')
    return questions


# 定义一个函数来重构现有的QA问题
def refactor_existing_qas(question_data):
    system_message = (
        "You are a brilliant assistant. Please use the following existing questions and their answers that require students to have a undergraduate-level "
        "understanding of medical science topics to solve them to create new, challenging multiple-choice questions. "
        "The Questions are all about principles of medical science. "
        "Ensure the correct option is clear and reformat the question if necessary. Additionally, reorder the options to maintain difficulty and avoid patterns. "
        "Refactor the QAs in various forms, such as question rewriting and option reordering. Use the provided data for reference and include the key point of the question."
    )
    user_message = f"The data to be used is: {json.dumps(question_data)}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    # 解析响应内容
    result = response.choices[0].message.content
    return result


# 定义一个函数来生成选择题
def generate_mcq(content):
    system_message = (
        "You are a brilliant assistant. "
        "You need to generate the question in JSON format. "
    )
    user_message = (
        "Please use the following data to create a new multiple choice question (MCQ) that closely mirrors the original question. "
        "Ensure the new question maintains the same key concepts and difficulty level, but is rephrased and the answer choices are reordered. "
        "Use the provided data for reference and include the key point of the question. "
        "Your created <question> should include 4 multiple choice options, in the following format: "
        "{ "
        "\"question\": \"the new rephrased question\", "
        "\"options\": {"
        " \"correct_option\": \"the correct option that can be found in the data\","
        " \"wrong_option_1\": \"the wrong option 1\", "
        " \"wrong_option_2\": \"the wrong option 2\", "
        " \"wrong_option_3\": \"the wrong option 3\""
        "} "
        "} "
        "Output in this format in JSON. "
        "Ensure that the new question is challenging and reflects the professional knowledge in the original data and. "
        "And the model should have reasoning and computational abilities for scientific questions. "
        "Most importantly, the correct answer must be derived from the original question data."
        "<data>: "
        f"{json.dumps(question_data)}"
        "# Question: "
        "Now create the rephrased multiple choice <question>: "
        "<question>:"
    )

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        response_format={
            "type": "json_object"
        }
    )

    # 解析响应内容
    result = response.choices[0].message.content
    return result


# 确认CSV文件路径
csv_file_path = 'E:/data/Open-LLM-Benchmark_data/questions/MedMCQA_1.csv'
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"The file {csv_file_path} does not exist.")

# 读取现有的CSV数据集
try:
    all_questions = extract_questions_from_csv(csv_file_path)
except (FileNotFoundError, ValueError, pd.errors.EmptyDataError) as e:
    print(f"Error reading CSV file: {e}")
    raise

# 存储所有问题和回答的列表
all_questions_and_answers = []

# 打印当前工作目录
print(f"Current working directory: {os.getcwd()}")

# 目标生成的题目数量
target_question_count = 1000
generated_question_count = 0

# 遍历提取的问题并生成新的问题
for question_data in all_questions:
    if generated_question_count >= target_question_count:
        break

    print(f"Processing question data: {question_data}")  # 添加这一行来调试
    try:
        # 动态处理question_data中的任意数据
        refactored_question_data = refactor_existing_qas(question_data)

        if refactored_question_data:
            mcq_question_data = generate_mcq(refactored_question_data)
            if mcq_question_data:
                # 解析MCQ数据
                try:
                    mcq_question_data_json = json.loads(mcq_question_data)
                    mcq_question = mcq_question_data_json["question"]
                    choices = mcq_question_data_json["options"]

                    # 不含选项标识地处理选项
                    choices_text = [
                        choices["correct_option"],
                        choices["wrong_option_1"],
                        choices["wrong_option_2"],
                        choices["wrong_option_3"]
                    ]
                    random.shuffle(choices_text)
                    choices_label = ["A", "B", "C", "D"]
                    correct_choice = choices_label[choices_text.index(choices['correct_option'])]

                    question_and_answer = {
                        "prompt": {
                            "default": "Given a question and four options, please select the right answer. "
                                       "Your answer should be \"A\", \"B\", \"C\" or \"D\". "
                                       "Please directly give the answer without any explanation."
                        },
                        "question": mcq_question,
                        "choices": {
                            "text": choices_text,
                            "label": choices_label
                        },
                        "answerKey": correct_choice,
                        "type": "mcq-4-choices",
                        "domain": "Medicine",
                        "details": {
                            "level": "L3",
                            "task": "medical_principle_prediction",
                            "subtask": "refactored_QA",
                            "source": "Open-LLM-Benchmark"
                        }
                    }

                    all_questions_and_answers.append(question_and_answer)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Response content: {mcq_question_data}")
            else:
                print(f"生成选择题失败: {refactored_question_data}")
        else:
            print(f"重构问题失败: {question_data}")

    except Exception as e:
        print(f"处理问题时出错: {e}, question_data: {question_data}")

# 将所有问题和回答保存到文件
output_file_path = "L3_task_2.json"
print(f"Saving results to {output_file_path}")
try:
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(all_questions_and_answers, file, ensure_ascii=False, indent=4)
    print(f"All questions and answers saved successfully to {output_file_path}")
except Exception as e:
    print(f"Error saving file: {e}")

print("所有问题生成完成。")
