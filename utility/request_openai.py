import calendar, datetime, os, sys, time, openai, json, traceback
from contextlib import contextmanager
from types import SimpleNamespace
from dotenv import load_dotenv
import numpy as np
from openai import OpenAI
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)


@contextmanager
def openai_request(input, temperature=0.1, max_tokens=1000, frequency_penalty=0, presence_penalty=0):
    try:
        response = client.completions.create(prompt=input,
        model="gpt-3.5-turbo-instruct",
        #api_key=api_key,  # Ensure api_key is set using openai.api_key
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty)
        try:
            total_tokens = response.usage.total_tokens
        except KeyError:
            total_tokens = 0

    except Exception as e:
        raise
    yield response

@contextmanager
def openai_embedding(message, model="gpt-3.5-turbo-instruct"):
    try:
        response = client.embeddings.create(input=message,
        model=model,
        #api_key=api_key
        )
    except Exception as e:
        raise

    yield [np.array(embedding.embedding for embedding in response.data)]