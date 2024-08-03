
from lib.config import cfg, args
from lib.generate.get_answer import generate_one_pdf, generate_without_pdf
import os
def generate_answer(result_folder, question_folder, model, api_base, file_name=None) -> None:
    """
    Generate answers for a PDF file and a list of questions.
    Args:
        file_name: The name of the PDF file.
        question_folder: The path to the folder containing the questions.
        model: The OpenAI model to use.
        api_base: The OpenAI API base URL.
    """
    if file_name is not None:
        generate_one_pdf(file_name, result_folder, question_folder, model, api_base)
    else:
        generate_without_pdf(result_folder, question_folder, model, api_base)


if __name__ == '__main__':
    if not os.path.exists(cfg.result_dir):
        os.makedirs(cfg.result_dir)
    for question_folder in os.listdir(cfg.data_dir):
        result_dir = os.path.join(cfg.result_dir, question_folder)
        generate_answer(result_dir, os.path.join(cfg.data_dir, question_folder), cfg.model, cfg.api_base)