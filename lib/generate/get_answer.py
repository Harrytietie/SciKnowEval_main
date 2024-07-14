from lib.config import cfg
from lib.generate.openai_with_pdf import OpenAIChatCompletionFnWithPDF
from lib.utils.json_utils import read_in_folder, write_folder
from tqdm import tqdm
import os

def generate_one_pdf(file_name, result_folder, question_folder,  model, api_base) -> None:

    chat_fn = OpenAIChatCompletionFnWithPDF(
        model=model,
        api_base=api_base,
    )
    names, data = read_in_folder(question_folder)
    for name, questions in zip(names, data):
        for question in questions:
            result = chat_fn(question["input"], file_name=os.path.join(cfg.data_dir, file_name))
            answer = result.get_completions()


def generate_without_pdf(result_folder, question_folder, model, api_base) -> None:

    chat_fn = OpenAIChatCompletionFnWithPDF(
        model=model,
        api_base=api_base,
    )
    names, data = read_in_folder(question_folder)
    for name, questions in zip(names, data):
        print("Processing questions in", os.path.join(question_folder, name))
        for question in tqdm(questions):
            result = chat_fn(question["input"])
            answer = result.get_completions()
            question["answer"] = answer[0]

    write_folder(result_folder, names, data)
