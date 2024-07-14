from lib.config import cfg, args
from lib.utils.extract_pdf import extract_and_store_text
import os


if __name__ == '__main__':
    pdf_files = []
    for root, dirs, files in os.walk(cfg.data_dir):
        for file in files:
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    for file_path in pdf_files:
        extract_and_store_text(file_path, cfg.result_dir)