from lib.config import cfg
from lib.utils.extract_pdf import extract_and_store_nougat
# from lib.generate.openai_with_pdf import OpenAIChatCompletionFnWithPDF
from lib.generate.openai_chat import OpenAIChat, calculate_num_tokens

from tqdm import tqdm
from typing import List
import random
import time
import asyncio

def get_prompt(text_path: str, num: int, length: int, pdf_path: str, add_page_num: bool = False):
    """
    Extracts text from a PDF file and returns a random prompt.
    Args:
        length: expected length of the text
        text_path: text file path
        pdf_path: The path to the PDF file.
        num: The number of prompts to extract.
        add_page_num: Whether to add the page number to the beginning of each page's text.

    Returns:
        prompt: Random prompts extracted from the PDF file.
        total_token: The total number of tokens in the prompts.
    """
    # chat_fn = OpenAIChatCompletionFnWithPDF(
    #     model=cfg.model,
    #     api_base=cfg.api_base,
    # )
    chat = OpenAIChat(model_name=cfg.model, max_tokens=cfg.max_tokens, temperature=cfg.temperature, top_p=cfg.top_p)

    if text_path:
        with open(text_path, 'r', encoding='utf-8') as f:
            texts = f.readlines()
    elif pdf_path:
        texts = extract_and_store_nougat(pdf_path, cfg.text_dir)

    prompts = []
    messages = []
    token_num = 0
    text = "".join(texts)
    sys_prompt = "Analyze the following text to determine if it contains useful knowledge or information. If it does, reorganize the information into a coherent and logically structured paragraph, maintaining the original meaning of the text, and directly return the coherent and logically structured paragraph. Don't return anything useless. If the text does not contain useful knowledge or information, return 'False'."
    sys_token = calculate_num_tokens(sys_prompt)

    # 以length为长度，遍历所有text，提取出所有文本
    total_length = len(text)
    totle_parts = total_length // length
    p_ = float(num) / totle_parts
    print("p_:", p_)
    for i in range(total_length // length):
        if random.random() > p_:
            continue
        start = length * i
        prompt = "The text to be analyzed is: '[" + text[start:start + length] + "]'."
        token_num += calculate_num_tokens(prompt) + sys_token
        message = [{"role": "system", "content": sys_prompt},
                   {"role": "user", "content": prompt}]
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
                response = responses_index[i]
                token_num += calculate_num_tokens(response)
                if response.startswith("False") or response.startswith("false") or response.startswith("FALSE") or \
                        response.startswith("True"):
                    continue
                else:
                    prompts.append(response)
            except:
                response = responses_index[i]
                print("Failed: ", response)

            # f.write(json.dumps(save_list[index + i], ensure_ascii=False) + "\n")

        if len(total_len) > 1:
            time.sleep(10)
    print("Total token:", token_num)
    return prompts

# V2
#         content = chat_fn(message).get_completions()
#         token_num = calculate_num_tokens(content[0]) + calculate_num_tokens(prompt) + sys_token
#         # print("token_num:", token_num)
#         total_token += token_num
#         # 如果content以False开头
#         if content[0].startswith("False") or content[0].startswith("false") or content[0].startswith("FALSE") or \
#                 content[0].startswith("True"):
#             # 本次循环不计数
#             i -= 1
#             # print("False")
#             continue
#         # print("content:", content)
#         prompts.append(content[0])
#     print("Total token:", total_token)
#     return prompts

# V1
    # for _ in tqdm(range(num)):
    #     start = random.randint(0, len(text) - length)
    #     # prompt = text[start:start + length + random.randint(-length // 10, length // 10)]
    #     prompt = "The text to be analyzed is: '["+ text[start:start + length + random.randint(-length // 10, length // 10)] + "]'."
    #     # print("prompt:", prompt)
    #     # 调用OpenAI API将随机提取出的文本组织为一段通顺的话
    #     message = [{"role": "system", "content": "Analyze the following text to determine if it contains useful knowledge or information. If it does, reorganize the information into a coherent and logically structured paragraph, maintaining the original meaning of the text, and directly return the coherent and logically structured paragraph. Don't return anything useless. If the text does not contain useful knowledge or information, return 'False'."},
    #                {"role": "user", "content": prompt}]
    #     content = chat_fn(message).get_completions()
    #     # 如果content以False开头
    #     if content[0].startswith("False") or content[0].startswith("false") or content[0].startswith("FALSE") or content[0].startswith("True"):
    #         # 本次循环不计数
    #         _ -= 1
    #         print("False")
    #         continue
    #     print("content:", content)
    #     prompts.append(content[0])
    # return prompts
