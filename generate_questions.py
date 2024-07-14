import os

from lib.config import cfg
from lib.generate.generate_base import generate_base_questions
# from lib.generate.generate_biology import generate_biology_questions
from lib.generate.generate_chem import generate_chem_questions
from lib.utils.json_utils import read_jsonl, read_in_folder


if __name__ == '__main__':
    if not os.path.exists(cfg.result_dir):
        os.makedirs(cfg.result_dir)
    if not os.path.exists(cfg.text_dir):
        pass
    token_num = 0
    names, contents_jsonl = read_in_folder(cfg.text_dir)

    contents_flat_jsonl = [item for sublist in contents_jsonl for item in sublist]
    contents_take = [
        value["prompt"] for value in contents_flat_jsonl
    ]
    base_path = os.path.join(cfg.result_dir, "Base")
    token_num += generate_base_questions(contents_take, base_path)
    print("Token num for base questions: ", token_num)

    # chem_path = os.path.join(cfg.result_dir, "Chemistry")
    # contents_chem = [
    #     [
    #         content["prompt"] for content in contents_list
    #     ] for contents_list in contents_jsonl
    # ]
    # token_num += generate_chem_questions(names, contents_chem, chem_path)
    # print("Token num for chemistry questions: ", token_num)

# V2
#     for contents_jsonl in contents_flat:
#         print("text_name", text_name)
#         base_path = os.path.join(cfg.result_dir, "Base")
#         contents_take = [
#             value["prompt"] for value in contents_jsonl
#         ]
#         token_num += generate_base_questions(contents_take, base_path)
#         print("Token num for", text_name, ":", token_num)

# V1
    # for text_path in os.listdir(cfg.text_dir):
    #     if text_path.split(".")[-1] != "jsonl":
    #         continue
    #     text_name = text_path.split(".")[0]
    #     print("text_path", text_path)
    #     contents_jsonl = read_jsonl(os.path.join(cfg.text_dir, text_path))
    #
    #     base_path = os.path.join(cfg.result_dir, "Base")
    #     token_num += generate_base_questions(contents, base_path)
    #     print("Token num for", text_name, ":", token_num)
    #     bio_path = os.path.join(cfg.result_dir, "Biology")
    #     token_num += generate_biology_questions(contents, bio_path, text_path)
    #
    # print("Total token num:", token_num)
