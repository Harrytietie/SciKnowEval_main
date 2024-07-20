# This code is based on https://github.com/sci-assess/SciAssess

import PyPDF2
import os
from tqdm import tqdm


def extract_text(pdf_path, add_page_num: bool = False) -> list[str]:
    """
    Extracts text from a PDF file and returns it as a list of strings.
    Args:
        pdf_path: The path to the PDF file.
        add_page_num: Whether to add the page number to the beginning of each page's text.

    Returns:
        texts: A list of strings, where each string is the text from a page.
    """
    texts = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        print("Extracting text from PDF ", pdf_path)
        for page_num in tqdm(range(len(reader.pages))):
            page = reader.pages[page_num]
            text = page.extract_text()
            text = f"Page {page_num + 1}:\n{text}\n" if add_page_num else text + "\n"
            texts.append(text)
    return texts

def extract_and_store_text(pdf_path, output_path, add_page_num: bool = False) -> None:
    """
    Extracts text from a PDF file and stores it in a text file.
    Args:
        pdf_path: The path to the PDF file.
        output_path: The path to the output text file.
        add_page_num: Whether to add the page number to the beginning of each page's text.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    text_name = os.path.basename(pdf_path).replace('.pdf', '.txt')
    text_path = os.path.join(output_path, text_name)
    # 如果text_path已经有文件了
    if os.path.exists(text_path):
        print("File already exists, skipping")
        return
    print("Writing text to ", text_path)
    texts = extract_text(pdf_path, add_page_num)
    with open(text_path, 'w', encoding='utf-8') as file:
        file.writelines(texts)

def extract_and_store_nougat(input_path, output_path) -> str:
    """
    Extracts text from all PDF files in a directory and stores it in text files.
    Args:
        input_path: The path to the PDF file.
        output_path: The path to the output directory.
    Returns:
        text: string of extracted text
    """
    # 使用shell命令$ nougat path/to/file.pdf -o output_directory提取
    print("Extracting text from PDF ", input_path)
    print("Using command: nougat", input_path, "-o", output_path)
    os.system(f"nougat {input_path} -o {output_path}")
    # 读取提取的文本
    text = ""
    input_name = os.path.basename(input_path).replace('.pdf', '.txt')
    text_path = os.path.join(output_path, input_name)
    with open(text_path, 'r') as file:
        text = file.read()
    return text