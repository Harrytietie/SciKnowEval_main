from huggingface_hub import hf_hub_download
import re
from PIL import Image

from transformers import NougatProcessor, VisionEncoderDecoderModel
import torch

def nougat_ocr(input_path: str, output_path: str) -> None:
    """
    Extracts text from all PDF files in a directory and stores it in text files.
    Args:
        input_path: The path to the PDF file.
        output_path: The path to the output directory.
    """
    processor = NougatProcessor.from_pretrained("facebook/nougat-base")
    model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-base")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    
    # Extract text from the PDF file
    with open(input_path, "rb") as file:
        pdf_bytes = file.read()
        pdf_text = processor.extract_text(pdf_bytes)