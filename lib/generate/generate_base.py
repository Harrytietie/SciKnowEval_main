from lib.config import cfg
from lib.utils.json_utils import write_jsonl
# from lib.generate.openai_with_pdf import OpenAIChatCompletionFnWithPDF
from lib.generate.openai_chat import OpenAIChat, calculate_num_tokens

import os
from tqdm import tqdm
from typing import List
import time
import asyncio
import random

def generate_base_questions(contents: list[str], output_path: str) -> int:
    def gpt_connect(sys_prompt: str, contents: list[str]) -> tuple[list[str], list[str], int]:
        questions = []
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
            responses_index = asyncio.run(chat.async_run(
                messages_list=messages[index:index + batch_size],
                expected_type=List
            ))

            for i in range(len(responses_index)):
                try:
                    get_qa = responses_index[i]
                    if "Question: " not in get_qa or "Answer: " not in get_qa:
                        continue
                    question = get_qa.split("Question: ")[1].split("Answer: ")[0]
                    answer = get_qa.split("Question: ")[1].split("Answer: ")[1]
                    questions.append(contents[index + i] + question)
                    answers.append(answer)
                    token_num += calculate_num_tokens(get_qa)
                except:
                    response = responses_index[i]
                    print("Failed: ", response)
        return questions, answers, token_num
    def generate_detailed(contents: list[str], output_path: str) -> int:
        sys_prompt = "Your task is to analyze the provided text snippet and generate a multiple-choice question that tests the understanding of its details. The question should be formulated to highlight a specific detail or concept within the text. Provide four options (A, B, C, and D), with only one correct answer. Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. Format your response as follows: \nQuestion: [Your question here] \nA) Option A \nB) Option B \nC) Option C \nD) Option D \nAnswer: [The letter of the correct answer option]. \nEnsure that the question, the options, and the answer are clear, concise, and directly related to the text. The options should be plausible, encouraging deep thinking about the text's content, while the correct answer provides a straightforward explanation or interpretation of the text."

        questions, answers, token_num = gpt_connect(sys_prompt, contents)

        questions_jsonl = [{
            "input": [
                {"role": "system", "content": "Please read the text carefully and choose the correct answer from the multiple-choice options based on your understanding of the details or data described. \nOnly write the answer down."},
                {"role": "user", "content": question}
            ], 
            "answer": answer} for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    # V1
    # if len(total_len) > 1:
    #     time.sleep(10)
    # get_qa = chat_fn(message).get_completions()[0]
    # detailed_token = sys_token + calculate_num_tokens(content) + calculate_num_tokens(get_qa)
    # print("detailed_token:", detailed_token)
    # if "Question: " not in get_qa or "Answer: " not in get_qa:
    #     continue
    # question = get_qa.split("Question: ")[1].split("Answer: ")[0]
    # answer = get_qa.split("Question: ")[1].split("Answer: ")[1]
    # questions.append(content + question)
    # answers.append(answer)

    def generate_hypothesis(contents: list[str], output_path: str) -> int:
        sys_prompt = "Your task is to analyze the provided text snippet and generate a meaningful question that examines a hypothesis or conjecture derived from or related to this text. The question should challenge the user to determine if the hypothesis is true or false based on the information provided. Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. Format your response as follows: \nQuestion: [Your question here] \nAnswer: [[True/False]. Explanation: [Your explanation here]]. \nEnsure that the question and the answer are clear, concise, and directly related to the text. The answer should be plausible, encouraging deep thinking about the text's content and provide a straightforward explanation or interpretation of the text."

        questions, answers, token_num = gpt_connect(sys_prompt, contents)

        questions_jsonl = [{
            "input": [
                {"role": "system", "content": "You will be presented with a hypothesis or conjecture. Based on the information provided in a text excerpt or your general knowledge, determine if the hypothesis is true or false. Provide your answer by first stating \"True, \" or \"False, \" , followed by a brief explanation supporting your conclusion."},
                {"role": "user", "content": question}
            ], 
            "answer": answer} for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    def generate_reason(contents: list[str], output_path: str) -> int:
        sys_prompt = "Your task is to analyze the provided text snippet and generate a multiple-choice question that tests the ability that based on the information provided, inferring the possible reasons or explanations for the observed outcomes. Your response should reflect a clear understanding and interpretation of the text, focusing on reasoning through the evidence provided. Craft a question that examines reasoning and explanation, followed by a reference answer that includes observations or results and infers possible causes or explanations. Provide four options (A, B, C, and D), with only one correct answer. Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. Format your response as follows: \nQuestion: [Your question here] \nA) Option A \nB) Option B \nC) Option C \nD) Option D \nAnswer: [The letter of the correct answer option]. \nEnsure that the question, the options, and the answer are clear, concise, and related to the text. The options should be plausible, encouraging deep thinking about the text's content, while the correct answer provides a possible causes or explanations of the question."

        questions, answers, token_num = gpt_connect(sys_prompt, contents)

        questions_jsonl = [{
            "input": [
                {"role": "system", "content": "You are presented with observations or results related to a phenomenon. Based on the information provided, infer the possible reasons or explanations for the observed outcomes. Your response should reflect a clear understanding and interpretation of the text, focusing on reasoning through the evidence provided."},
                {"role": "user", "content": question}
            ], 
            "answer": answer} for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    def generate_summary(contents: list[str], output_path: str) -> int:
        sys_prompt = "Your task is to read the provided text excerpt and summarize the main findings and conclusions in one sentence. Focus on the key elements that highlight the biological process or reaction mechanism discussed. Provide a concise summary that captures the essence of the text."

        questions = []
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
            responses_index = asyncio.run(chat.async_run(
                messages_list=messages[index:index + batch_size],
                expected_type=List
            ))

            for i in range(len(responses_index)):
                try:
                    get_qa = responses_index[i]
                    answer = get_qa
                    questions.append(contents[index + i])
                    answers.append(answer)
                    token_num += calculate_num_tokens(get_qa)
                except:
                    response = responses_index[i]
                    print("Failed: ", response)

        questions_jsonl = [{
            "input": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": "Text: " + question}
            ], 
            "answer": answer} for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num


    # chat_fn = OpenAIChatCompletionFnWithPDF(
    #     model=cfg.model,
    #     api_base=cfg.api_base,
    # )
    chat = OpenAIChat(model_name=cfg.model, max_tokens=cfg.max_tokens, temperature=cfg.temperature, top_p=cfg.top_p)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    token_num = 0
    detailed_path = os.path.join(output_path, "detailed_understanding.jsonl")
    detailed_contents = random.sample(contents, cfg.base.detailed)
    token_num += generate_detailed(detailed_contents, detailed_path)
    hypothesis_path = os.path.join(output_path, "hypothesis_verification.jsonl")
    hypothesis_contents = random.sample(contents, cfg.base.hypothesis)
    token_num += generate_hypothesis(hypothesis_contents, hypothesis_path)
    reason_path = os.path.join(output_path, "reasoning_and_interpretation.jsonl")
    reason_contents = random.sample(contents, cfg.base.reasoning)
    token_num += generate_reason(reason_contents, reason_path)
    summary_path = os.path.join(output_path, "text_summary.jsonl")
    summary_contents = random.sample(contents, cfg.base.summary)
    token_num += generate_summary(summary_contents, summary_path)
    return token_num
