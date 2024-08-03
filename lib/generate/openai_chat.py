# the async version is adapted from https://gist.github.com/neubig/80de662fb3e225c18172ec218be4917a

import os

#import httpx
import openai
from openai import OpenAI
#import ast
import asyncio
from openai import AsyncOpenAI
from typing import List, Tuple, Any
import tiktoken
from tqdm import tqdm


class OpenAIChat:
    # more details on: https://platform.openai.com/docs/api-reference/chat
    def __init__(
            self,
            model_name='gpt-3.5-turbo',
            max_tokens=2500,
            temperature=0.5,
            top_p=1.0,
            request_timeout=180,
            stop=None,
            response_format='text',  # text or json_object
            logprobs=False,
            top_logprobs=None,
            n=1,
    ):
        self.config = {
            'model_name': model_name,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'timeout': request_timeout,
            'stop': stop,
            'response_format': response_format,
            'logprobs': logprobs,
            'top_logprobs': top_logprobs,
            'sample_n': n,
        }
        if "gpt" in model_name or 'embedding' in model_name:
            # openai.api_key = os.getenv("OPENAI_API_KEY")
            self.client = OpenAI(
                #api_key=os.environ['OPENAI_API_KEY'],
                api_key="sk-KmLopBhOMFbaWEWK983e254826114f9fB9E4C974568224D3",
                base_url="https://api.ai-gaochao.cn/v1"
            )
        else:
            # openai.api_key = "EMPTY"
            self.client = OpenAI(
                api_key="EMPTY",
                base_url="http://127.0.0.1:8333/v1"
            )

    async def dispatch_openai_requests(
            self,
            messages_list,
    ) -> tuple[Any]:
        """Dispatches requests to OpenAI API asynchronously.

        Args:
            messages_list: List of messages to be sent to OpenAI ChatCompletion API.
        Returns:
            List of responses from OpenAI API.
        """
        async def _request_with_retry(messages, retry=3):
            client = AsyncOpenAI(
                base_url="https://api.ai-gaochao.cn/v1",  # 替换为你的 base_url
                #api_key=os.environ.get("OPENAI_API_KEY")  # 替换为你的 API 密钥
                api_key="sk-KmLopBhOMFbaWEWK983e254826114f9fB9E4C974568224D3"
            )
            for try_i in range(retry):
                try:
                    # for text embedding models
                    if "embedding" in self.config['model_name']:
                        response = await client.embeddings.create(
                        # response = await openai.Embedding.acreate(
                            model=self.config['model_name'],
                            input=messages,
                        )
                    else:
                        # for chat models
                        response = await client.chat.completions.create(
                        # response = await openai.ChatCompletion.acreate(
                            model=self.config['model_name'],
                            response_format={'type': self.config['response_format']},
                            messages=messages,
                            max_tokens=self.config['max_tokens'],
                            temperature=self.config['temperature'],
                            top_p=self.config['top_p'],
                            timeout=self.config['timeout'],
                            stop=self.config['stop'],
                            logprobs=self.config['logprobs'],
                            top_logprobs=self.config['top_logprobs'],
                            n=self.config['sample_n'],
                        )
                    return response

                except openai.BadRequestError as e:
                # except openai.error.InvalidRequestError as e:
                    print(e)
                    print(f'Retry {try_i + 1} Bad request error, waiting for 3 second...')
                    await asyncio.sleep(3)
                except openai.RateLimitError:
                # except openai.error.RateLimitError:
                    print(f'Retry {try_i + 1} Rate limit error, waiting for 40 second...')
                    await asyncio.sleep(40)
                except openai.APITimeoutError:
                # except openai.error.Timeout:
                    print(f'Retry {try_i + 1} Timeout error, waiting for 10 second...')
                    await asyncio.sleep(10)
                except openai.APIConnectionError as e:
                # except openai.error.APIConnectionError as e:
                    print(e)
                    print(f'Retry {try_i + 1} API connection error, waiting for 10 second...')
                    await asyncio.sleep(10)
                except openai.APIError:
                # except openai.error.APIError:
                    print(f'Retry {try_i + 1} API error, waiting for 5 second...')
                    await asyncio.sleep(5)
                except openai.AuthenticationError as e:
                # except openai.error.AuthenticationError as e:
                    print(e)
                    print(f'Retry {try_i + 1} Authentication error, waiting for 10 second...')
                    await asyncio.sleep(10)
                except openai.InternalServerError:
                # except openai.error.ServiceUnavailableError:
                    print(f'Retry {try_i + 1} Service unavailable error, waiting for 3 second...')
                    await asyncio.sleep(3)
            return None

        async_responses = [
            _request_with_retry(messages)
            for messages in messages_list
        ]
        results = await asyncio.gather(*async_responses)
        return results

    async def async_run(self, messages_list, expected_type):
        retry = 10
        responses = [None for _ in range(len(messages_list))]
        messages_list_cur_index = [i for i in range(len(messages_list))]

        while retry > 0 and len(messages_list_cur_index) > 0:
            # print(f'{retry} retry left...')
            messages_list_cur = [messages_list[i] for i in messages_list_cur_index]

            predictions = await self.dispatch_openai_requests(
                messages_list=messages_list_cur,
            )

            if "embedding" in self.config['model_name']:
                # preds = [prediction['data'][0]['embedding'] if prediction is not None else None for prediction in
                #         predictions]
                preds = [prediction.data[0].embedding if prediction is not None else None for prediction in
                         predictions]
            else:
                if self.config['logprobs'] == False:
                    # preds = [prediction['choices'][0]['message']['content'] if prediction is not None else None for
                    #         prediction in predictions]
                    preds = [prediction.choices[0].message.content if prediction is not None else None for
                             prediction in predictions]
                else:
                    preds = [
                        [
                            #prediction['choices'][0]['message']['content'],
                            prediction.choices[0].message.content,
                            [d['logprob'] for d in prediction.choices[0].logprobs.content]
                        ] if prediction is not None else None for prediction in predictions
                    ]

            finised_index = []
            for i, pred in enumerate(preds):
                if pred is not None:
                    responses[messages_list_cur_index[i]] = pred
                    finised_index.append(messages_list_cur_index[i])

            messages_list_cur_index = [i for i in messages_list_cur_index if i not in finised_index]

            retry -= 1

        return responses


def calculate_num_tokens(text):
    # calculate the number of tokens in the text (string or list of strings)
    tokenizer = tiktoken.encoding_for_model("gpt-4")
    if isinstance(text, str):
        return len(tokenizer.encode(text, disallowed_special=(tokenizer.special_tokens_set - {'<|endoftext|>'})))
    elif isinstance(text, list):
        return [
            len(tokenizer.encode(
                t, disallowed_special=(tokenizer.special_tokens_set - {'<|endoftext|>'})
            )) for t in tqdm(text, total=len(text), desc="Calculating number of tokens")
        ]


def segment_paper_into_paragraphs(corpus_text, max_tokens=2048):
    lines = corpus_text.split('\n')
    paragraphs, paragraph_text = [], ""
    current_tokens = 0
    for line in lines:
        line_tokens = calculate_num_tokens(line)  # calculate token num in this line
        if current_tokens + line_tokens < max_tokens:
            paragraph_text += line + '\n'
            current_tokens += line_tokens
        else:
            paragraphs.append(paragraph_text)
            paragraph_text = line + '\n' if line_tokens < max_tokens else ''
            current_tokens = line_tokens if line_tokens < max_tokens else 0

    # 添加最后一个段落（如果有）
    if current_tokens > 0:
        paragraphs.append(paragraph_text)

    # 从段落列表中过滤掉包含“Reference”的段落
    paragraphs = [para for para in paragraphs if 'Reference' not in para]
    return paragraphs


if __name__ == "__main__":

    chat = OpenAIChat(model_name='gpt-3.5-turbo-0125', max_tokens=4096, temperature=0.7, top_p=0.9)
    token_num = calculate_num_tokens("show either 'ab' or '['a']'. Do not do anything else.")
    print("token_num: ", token_num)
    loop = asyncio.get_event_loop()
    # predictions = asyncio.run(chat.async_run(
    predictions = loop.run_until_complete(chat.async_run(
        messages_list=[
            [
                {
                    "role": "user",
                    "content": "show either 'ab' or '['a']'. Do not do anything else."
                }
            ],
            [
                {
                    "role": "user",
                    "content": "show either 'cd' or '['c']'. Do not do anything else."
                }
            ]
        ],
        expected_type=List,
    ))

    for pred in predictions:
        print(pred)
