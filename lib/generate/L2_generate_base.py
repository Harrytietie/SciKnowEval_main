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


def generate_base_questions(contents: list[str], output_path: str) -> int:
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

    def generate_detailed(contents: list[str], output_path: str) -> int:
        sys_prompt = (
            "Your task is to analyze the provided text snippet and generate a multiple-choice question that tests the understanding of its details. "
            "The question should be formulated to highlight a specific detail or concept within the text. "
            "Provide four options (A, B, C, and D), with only one correct answer. "
            "Don't always set the correct answer to the same option "
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
                "subtask": "detail_understanding",
                "source": "PubMed"
            }
        } for question, choices_text, answer, in zip(questions, options, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    def generate_hypothesis(contents: list[str], output_path: str) -> int:
        sys_prompt = (
            "Your task is to analyze the provided text snippet and generate a meaningful question that examines a hypothesis or conjecture derived from or related to this text. "
            "The question should challenge the user to determine if the hypothesis is true or false based on the information provided. "
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
                "default": "You will be presented with a hypothesis or conjecture. "
                           "Based on the information provided in a text excerpt or your general knowledge, determine if the hypothesis is true (yes) or false (no). "
                           "Your answer should be \"Yes\" or \"No\" , followed by a brief explanation supporting your conclusion. "
                           "Please directly give the answer, DO NOT output any other characters."
            },
            "question": question,
            "answer": answer,
            "type": "true_or_false",
            "domain": "Medicine",
            "details": {
                "level": "L2",
                "task": "L2_Medicine",
                "subtask": "hypothesis_verification",
                "source": "PubMed"
            }
        } for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    def generate_reason(contents: list[str], output_path: str) -> int:
        sys_prompt = (
            "Your task is to analyze the provided text snippet and generate a multiple-choice question that tests the ability that based on the information provided, "
            "inferring the possible reasons or explanations for the observed outcomes. "
            "Your response should reflect a clear understanding and interpretation of the text, focusing on reasoning through the evidence provided. "
            "Craft a question that examines reasoning and explanation, "
            "followed by a reference answer that includes observations or results and infers possible causes or explanations. "
            "Provide four options (A, B, C, and D), with only one correct answer. "
            "Don't always set the correct answer to the same option "
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
                "default": "You are presented with observations or results related to a phenomenon. "
                           "Based on the information provided, infer the possible reasons or explanations for the observed outcomes. "
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
                "subtask": "reasoning_and_interpretation",
                "source": "PubMed"
            }
        } for question, choices_text, answer, in zip(questions, options, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    def generate_summary(contents: list[str], output_path: str) -> int:
        sys_prompt = (
            "Your task is to read the provided text excerpt and summarize the main findings and conclusions in one sentence. "
            "Focus on the key elements that highlight the medical treatment or medicines discussed. "
            "Provide a concise summary that captures the essence of the text."
        )
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
            "prompt": {
                "default": "Your task is to read the provided text excerpt and summarize the main findings and conclusions in one sentence. "
                           "Focus on the key elements that highlight the biological process or reaction mechanism discussed. "
                           "Provide a concise summary that captures the essence of the text."
            },
            "question": "Text: " + question,
            "answer": answer,
            "type": "open-ended-qa",
            "domain": "Medicine",
            "details": {
                "level": "L2",
                "task": "L2_Medicine",
                "subtask": "text_summary",
                "source": "PubMed"
            }
        } for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num

    # chat_fn = OpenAIChatCompletionFnWithPDF(
    #     model=cfg.model,
    #     api_base=cfg.api_base
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
