# SciKnowEval

Please remember export your OPENAI_API_KEY in your environment.

## Create environment

```bash

conda env create -f environment.yaml

```

## Extract pdfs

```python

python extract_pdf_to_text.py --cfg_file configs/extract_pdfs.yaml

```

## Generate prompts from text folder for question generation

```python

python generate_prompts.py --cfg_file configs/generate_prompts.yaml

```

## Generate questions from prompts folder

```python

python generate_questions.py --cfg_file configs/generate_questions.yaml

```

## Generate answer from questions folder

```python

python generate_answer.py --cfg_file configs/generate_answer.yaml

```

## Count the total number of literature reading questions

```python

python summary.py

```