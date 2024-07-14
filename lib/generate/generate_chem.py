from lib.config import cfg
from lib.utils.json_utils import write_jsonl
# from lib.generate.openai_with_pdf import OpenAIChatCompletionFnWithPDF
from lib.generate.openai_chat import OpenAIChat, calculate_num_tokens
from lib.utils.question_utils import compound_identification_and_properties_valid_address, reaction_mechanism_inference_valid_address, cation_characterization_valid_address

import os
from tqdm import tqdm
from typing import List
import time
import asyncio
import random


def generate_chem_questions(names: list[str], contents: list[list[str]], output_path: str) -> int:
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
                    if get_qa.startswith("False") or get_qa.startswith("false") or get_qa.startswith("FALSE") or \
                            get_qa.startswith("True"):
                        continue
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

    def generate_compound(contents: list[str], output_path: str) -> int:
        sys_prompt = "Analyze the following text to determine if it mentions chemical compounds, their structures, or properties. If it does, generate a multiple-choice question that tests the understanding of the chemical compounds. The question should be formulated to highlight a specific detail or concept within the text. Provide four options (A, B, C, and D), with only one correct answer. Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. Format your response as follows: \nQuestion: [Your question here] \nA) Option A \nB) Option B \nC) Option C \nD) Option D \nAnswer: [The letter of the correct answer option]. \nEnsure that the question, the options, and the answer are clear, concise, and directly related to the text. If the text does not mentions chemical compounds, their structures, or properties, return 'False' directly. Don't return anything useless. "
        questions, answers, token_num = gpt_connect(sys_prompt, contents)

        questions_jsonl = [{
            "input": [
                {"role": "system",
                 "content": "Please read the text carefully and choose the correct answer from the multiple-choice options based on your understanding of the details or data described. \nOnly write the answer down."},
                {"role": "user", "content": question}
            ],
            "answer": answer} for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num
    def generate_reaction(contents: list[str], output_path: str) -> int:
        sys_prompt = "Analyze the following text to determine if it describes a chemical reaction, its equation, or reaction mechanism. If it does, generate a multiple-choice question based on that information. The question should be formulated to highlight a specific detail or concept within the text. Provide four options (A, B, C, and D), with only one correct answer. Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. Format your response as follows: \nQuestion: [Your question here] \nA) Option A \nB) Option B \nC) Option C \nD) Option D \nAnswer: [The letter of the correct answer option]. \nEnsure that the question, the options, and the answer are clear, concise, and directly related to the text. If the text does not mentions a chemical reaction, its equation, or reaction mechanism, return 'False' directly. Don't return anything useless. "
        questions, answers, token_num = gpt_connect(sys_prompt, contents)

        questions_jsonl = [{
            "input": [
                {"role": "system",
                 "content": "Please read the text carefully and choose the correct answer from the multiple-choice options based on your understanding of the details or data described. \nOnly write the answer down."},
                {"role": "user", "content": question}
            ],
            "answer": answer} for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num
    def generate_cation(contents: list[str], output_path: str) -> int:
        sys_prompt = "Analyze the following text to determine if it mentions the qualitative analysis of common cations. If it does, generate a multiple-choice question based on that information related to the specific cations and types of reactions mentioned. Provide four options (A, B, C, and D), with only one correct answer. Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. Format your response as follows: \nQuestion: [Your question here] \nA) Option A \nB) Option B \nC) Option C \nD) Option D \nAnswer: [The letter of the correct answer option]. \nEnsure that the question, the options, and the answer are clear, concise, and directly related to the text. If the text does not mentions the qualitative analysis of common cations, return 'False' directly. Don't return anything useless. "

        questions, answers, token_num = gpt_connect(sys_prompt, contents)

        questions_jsonl = [{
            "input": [
                {"role": "system",
                 "content": "Please read the text carefully and choose the correct answer from the multiple-choice options based on your understanding of the details or data described. \nOnly write the answer down."},
                {"role": "user", "content": question}
            ],
            "answer": answer} for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)
        return token_num
    
    chat = OpenAIChat(model_name=cfg.model, max_tokens=cfg.max_tokens, temperature=cfg.temperature, top_p=cfg.top_p)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    token_num = 0

    compound_path = os.path.join(output_path, "compound_identification_and_properties.jsonl")
    compound_contents = []
    for name, content_list in zip(names, contents):
        if name[:-6] in compound_identification_and_properties_valid_address:
            compound_contents.extend(content_list)
    compound_contents = random.sample(compound_contents, min(cfg.chem.compound, len(compound_contents)))
    token_num += generate_compound(compound_contents, compound_path)

    reaction_path = os.path.join(output_path, "reaction_mechanism_inference.jsonl")
    reaction_contents = []
    for name, content_list in zip(names, contents):
        if name[:-6] in reaction_mechanism_inference_valid_address:
            reaction_contents.extend(content_list)
    reaction_contents = random.sample(reaction_contents, min(cfg.chem.reaction, len(reaction_contents)))
    token_num += generate_reaction(reaction_contents, reaction_path)

    cation_path = os.path.join(output_path, "cation_characterization.jsonl")
    cation_contents = []
    for name, content_list in zip(names, contents):
        if name[:-6] in cation_characterization_valid_address:
            cation_contents.extend(content_list)
    cation_contents = random.sample(cation_contents, min(cfg.chem.cation, len(cation_contents)))
    token_num += generate_cation(cation_contents, cation_path)

    return token_num