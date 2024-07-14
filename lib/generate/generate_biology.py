from lib.config import cfg
from lib.utils.json_utils import write_jsonl
from lib.generate.openai_with_pdf import OpenAIChatCompletionFnWithPDF
from lib.generate.openai_chat import OpenAIChat

import os
from tqdm import tqdm

compound_identification_and_properties_valid_address = [
    "Structure & Reactivity in Organic, Biological and Inorganic Chemistry I: Chemical Structure and Properties.txt",
    "Structure & Reactivity in Organic, Biological and Inorganic Chemistry III: Reactivity in Organic, Biological and Inorganic Chemistry 1.txt",
    "Structure & Reactivity in Organic, Biological and Inorganic Chemistry IV: Reactivity in Organic, Biological and Inorganic Chemistry 2.txt",
    "Structure & Reactivity in Organic, Biological and Inorganic Chemistry V: Reactivity in Organic, Biological and Inorganic Chemistry 3.txt",
    "Structure and Reactivity in Organic, Biological and Inorganic Chemistry II: Practical Aspects of Structure - Purification and Spectroscopy.txt",
    "Chemistry 1e (OpenSTAX).txt",
    "ChemPRIME (Moore et al.).txt"
]

def generate_biology_questions(contents: list[str], output_path: str, text_path: str) -> int:
    def generate_compound(contents: list[str], output_path: str, text_path: str) -> int:
        questions = []
        answers = []
        for content in tqdm(contents):
            message = [{"role": "system", "content": "Your task is to analyze the provided text snippet and generate a multiple-choice question that tests the understanding of its details. The question should be formulated to highlight a specific detail or concept within the text. Provide four options (A, B, C, and D), with only one correct answer. Follow the question with the correct answer option, reflecting accurately on the content or the implications of the text. Format your response as follows: \nQuestion: [Your question here] \nA) Option A \nB) Option B \nC) Option C \nD) Option D \nAnswer: [The letter of the correct answer option]. \nEnsure that the question, the options, and the answer are clear, concise, and directly related to the text. The options should be plausible, encouraging deep thinking about the text's content, while the correct answer provides a straightforward explanation or interpretation of the text."},
                       {"role": "user", "content": content}]
            get_qa = chat_fn(message).get_completions()[0]
            # print("get_qa:", get_qa)
            if "Question: " not in get_qa or "Answer: " not in get_qa:
                continue
            question = get_qa.split("Question: ")[1].split("Answer: ")[0]
            answer = get_qa.split("Question: ")[1].split("Answer: ")[1]
            questions.append(content + question)
            answers.append(answer)
        questions_jsonl = [{
            "input": [
                {"role": "system", "content": "Please read the text carefully and choose the correct answer from the multiple-choice options based on your understanding of the details or data described. \nOnly write the answer down."},
                {"role": "user", "content": question}
            ], 
            "answer": answer} for question, answer in zip(questions, answers)]
        write_jsonl(output_path, questions_jsonl)

    chat_fn = OpenAIChatCompletionFnWithPDF(
        model=cfg.model,
        api_base=cfg.api_base,
    )
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    detailed_path = os.path.join(output_path, "detailed_understanding.jsonl")
    generate_detailed(contents, detailed_path)