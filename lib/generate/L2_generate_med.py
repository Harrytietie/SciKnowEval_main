from lib.config import cfg
from lib.utils.json_utils import write_jsonl
# from lib.generate.openai_with_pdf import OpenAIChatCompletionFnWithPDF
from lib.generate.openai_chat import OpenAIChat, calculate_num_tokens

import os
from tqdm import tqdm
from typing import List
# import time
import asyncio
import random


def generate_med_questions(contents: list[str], output_path: str) -> int:
    def gpt_connect(sys_prompt: str, contents: list[str]) -> tuple[list[str], list[list[str]], list[str], int]:
        questions = []
        options = []
        answers = []
        messages = []
        token_num = 0
        sys_token = calculate_num_tokens(sys_prompt)
        for content in contents:
            token_num += sys_token + calculate_num_tokens(content)
            message = [{"role": "system", "content": sys_prompt},
                       {"role": "user", "content": content}]
            messages.append(message)
        batch_size = cfg.api_batch
        total_len = range(0, len(messages), batch_size)
        for index in tqdm(total_len, total=len(total_len)):

            loop = asyncio.get_event_loop()
            responses_index = loop.run_until_complete(chat.async_run(
                messages_list=messages[index:index + batch_size],
                expected_type=List
            ))

            # responses_index = asyncio.run(chat.async_run(
            #    messages_list=messages[index:index + batch_size],
            #    expected_type=List
            # ))

            for i in range(len(responses_index)):
                try:
                    get_qa = responses_index[i]
                    if "Question: " not in get_qa or "Answer: " not in get_qa:
                        continue
                    elif "Options: " in get_qa:
                        option = [
                            get_qa.split("A: ")[1].split("\n")[0],
                            get_qa.split("B: ")[1].split("\n")[0],
                            get_qa.split("C: ")[1].split("\n")[0],
                            get_qa.split("D: ")[1].split("\n")[0]
                        ]
                        options.append(option)
                        answer = get_qa.split("Answer: ")[1].split(":")[0]
                    else:
                        answer = get_qa.split("Answer: ")[1].split("\n")[0]
                    question = get_qa.split("Question: ")[1].split("\n")[0]
                    questions.append(contents[index + i] + question)
                    answers.append(answer)
                    token_num += calculate_num_tokens(get_qa)
                except:
                    response = responses_index[i]
                    print("Failed:", response)
        return questions, options, answers, token_num

    def generate_drug(contents: list[str], output_path: str) -> int:
        sys_prompt = (
            "Your task is to analyze the following text to determine if it mentions medical drugs, their structures, or properties. "
            "If it does, generate a multiple-choice question that tests the understanding of the drugs. "
            "The question should be formulated to highlight a specific detail or concept within the text. "
            "Provide four options (A, B, C, and D), with only one correct answer. "
            "DO NOT always set the correct answer to the same option "
            "Make each option's frequency of occurrence in the correct answer roughly the same. "
            "Your answer should be 'A', 'B', 'C' or 'D'. Please directly give the answer without any explanation. "
            "Do not include any other text, just the single letter answer. "
            "Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. "
            "Format your response as follows:\n"
            "Question: [your question here]\n"
            "Options: "
            "A: [just text, no \"A\"\"B\"\"C\"\"D\"]\n"
            "B: [just text, no \"A\"\"B\"\"C\"\"D\"]\n"
            "C: [just text, no \"A\"\"B\"\"C\"\"D\"]\n"
            "D: [just text, no \"A\"\"B\"\"C\"\"D\"]\n"
            "Answer: [the letter of the correct answer option, just the single letter, no any other text]\n"
            "Ensure that the question, the options, and the answer are clear, concise, and directly related to the text. "
            "The options should be plausible, encouraging deep thinking about the text's content, "
            "while the correct answer provides a straightforward explanation or interpretation of the text."
            "You should incorporate specific scenarios or contexts in the question, "
            "allowing the professional knowledge in the provided text to serve as a comprehensive and precise answer. "
            "Ensure that the question is formulated in English language. "
            "The question is a close-book question that is used to evaluate human experts, "
            "please ensure the difficulty of the question is really challenging and has no dependence on the provided text, "
            "that is, please pay more attention to the professional information of the field rather than the methods designed in the provided text. "
            "Most importantly, the correct answer of the question must paraphrase the idea in the provided text, rather than copy it"
        )

        questions, options, answers, token_num = gpt_connect(sys_prompt, contents)

        choices_label = ["A", "B", "C", "D"]
        questions_jsonl = [{
            "prompt": {
                "default": "Please read the text carefully and choose the correct answer from the multiple-choice options "
                           "based on your understanding of the details or data described. "
                           "Your answer should be \"A\", \"B\", \"C\" or \"D\". "
                           "Please directly give the answer without any explanation."
            },
            "question": question,
            "choices": {
                "text": choices_text,
                "label": choices_label
            },
            "answerKey": answer,
            "type": "mcq-4-choices",
            "domain": "Medicine",
            "details": {
                "level": "L2",
                "task": "L2_Medicine",
                "subtask": "drug_identification_and_properties",
                "source": "PubMed"
            }
        } for question, choices_text, answer, in zip(questions, options, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    def generate_hypothesis(contents: list[str], output_path: str) -> int:
        sys_prompt = (
            "Your task is to analyze the provided text snippet and generate a meaningful question that examines a conjecture about a therapy derived from or related to this text. "
            "The question should challenge the user to determine if the conjecture is true or false based on the information provided. "
            "Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. "
            "Format your response as follows:\n"
            "Question: [Your question here]\n"
            "Answer: [Yes/No]\n"
            "Ensure that the question and the answer are clear, concise, and directly related to the text. "
            "The answer should be plausible, encouraging deep thinking about the text's content, "
            "and provide a straightforward explanation or interpretation of the text."
        )

        questions, options, answers, token_num = gpt_connect(sys_prompt, contents)

        questions_jsonl = [{
            "prompt": {
                "default": "The following is a text on therapy and a true or false question for this text. "
                           "Your task is to analyze the provided text and give me the answer of the question. "
                           "Your answer should be \"Yes\" or \"No\" . "
                           "Please directly give the answer, DO NOT output any other characters."
            },
            "question": question,
            "answer": answer,
            "type": "true_or_false",
            "domain": "Medicine",
            "details": {
                "level": "L2",
                "task": "L2_Medicine",
                "subtask": "therapy_judgment_and_interpretation",
                "source": "PubMed"
            }
        } for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    def generate_preparation(contents: list[str], output_path: str) -> int:
        sys_prompt = (
            "Your task is to analyze the following text to determine if it mentions the preparation process of drugs. "
            "If it does, generate a multiple-choice question that tests the understanding of the preparation process. "
            "The question should be formulated to highlight a specific detail or concept within the text. "
            "Provide four options (A, B, C, and D), with only one correct answer. "
            "DO NOT always set the correct answer to the same option "
            "Make each option's frequency of occurrence in the correct answer roughly the same. "
            "Your answer should be 'A', 'B', 'C' or 'D'. Please directly give the answer without any explanation. "
            "Do not include any other text, just the single letter answer. "
            "Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. "
            "Format your response as follows:\n"
            "Question: [your question here]\n"
            "Options: "
            "A: [just text, no \"A\"\"B\"\"C\"\"D\"]\n"
            "B: [just text, no \"A\"\"B\"\"C\"\"D\"]\n"
            "C: [just text, no \"A\"\"B\"\"C\"\"D\"]\n"
            "D: [just text, no \"A\"\"B\"\"C\"\"D\"]\n"
            "Answer: [the letter of the correct answer option, just the single letter, no any other text]\n"
            "Ensure that the question, the options, and the answer are clear, concise, and directly related to the text. "
            "The options should be plausible, encouraging deep thinking about the text's content, "
            "while the correct answer provides a straightforward explanation or interpretation of the text."
            "You should incorporate specific scenarios or contexts in the question, "
            "allowing the professional knowledge in the provided text to serve as a comprehensive and precise answer. "
            "Ensure that the question is formulated in English language. "
            "The question is a close-book question that is used to evaluate human experts, "
            "please ensure the difficulty of the question is really challenging and has no dependence on the provided text, "
            "that is, please pay more attention to the professional information of the field rather than the methods designed in the provided text. "
            "Most importantly, the correct answer of the question must paraphrase the idea in the provided text, rather than copy it"
        )

        questions, options, answers, token_num = gpt_connect(sys_prompt, contents)

        choices_label = ["A", "B", "C", "D"]
        questions_jsonl = [{
            "prompt": {
                "default": "Please read the text carefully and choose the correct answer from the multiple-choice options "
                           "based on your understanding of the details or data described. "
                           "Your answer should be \"A\", \"B\", \"C\" or \"D\". "
                           "Please directly give the answer without any explanation."
            },
            "question": question,
            "choices": {
                "text": choices_text,
                "label": choices_label
            },
            "answerKey": answer,
            "type": "mcq-4-choices",
            "domain": "Medicine",
            "details": {
                "level": "L2",
                "task": "L2_Medicine",
                "subtask": "drug_preparation_process_inference",
                "source": "PubMed"
            }
        } for question, choices_text, answer, in zip(questions, options, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    chat = OpenAIChat(model_name=cfg.model, max_tokens=cfg.max_tokens, temperature=cfg.temperature, top_p=cfg.top_p)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    token_num = 0

    drug_path = os.path.join(output_path, "drug_identification_and_properties.jsonl")
    drug_contents = random.sample(contents, cfg.med.drug)
    token_num += generate_drug(drug_contents, drug_path)

    therapy_path = os.path.join(output_path, "therapy_judgment_and_interpretation.jsonl")
    therapy_contents = random.sample(contents, cfg.med.therapy)
    token_num += generate_hypothesis(therapy_contents, therapy_path)

    preparation_path = os.path.join(output_path, "drug_preparation_process_inference.jsonl")
    preparation_contents = random.sample(contents, cfg.med.preparation)
    token_num += generate_preparation(preparation_contents, preparation_path)

    return token_num
