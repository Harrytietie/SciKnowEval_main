import os

from lib.config import cfg
from lib.utils.random_prompt import get_prompt
from lib.utils.json_utils import write_jsonl

if __name__ == '__main__':
    if not os.path.exists(cfg.result_dir):
        os.makedirs(cfg.result_dir)
    if not os.path.exists(cfg.text_dir):
        pass
    token_num = 0
    for i, text_path in enumerate(os.listdir(cfg.text_dir)):
        print("i", i, "text_path", text_path)
        if text_path.split(".")[-1] != "txt":
            continue
        text_name = text_path[:-4]
        output_path = os.path.join(cfg.result_dir, text_name) + ".jsonl"
        if os.path.exists(output_path):
            print("File already exists, skip: ", output_path)
            continue
        contents = get_prompt(text_path=os.path.join(cfg.text_dir, text_path), num=cfg.num, length=cfg.length,
                              pdf_path=None, add_page_num=False)
        contents_jsonl = [
            {
                "prompt": content,
            } for content in contents
        ]
        write_jsonl(output_path, contents_jsonl)
