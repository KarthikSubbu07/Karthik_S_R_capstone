import os, sys
from dotenv import load_dotenv
from openai import OpenAI

# Load OPENAI_API_KEY from the environment — never hard-code keys
load_dotenv()
client = OpenAI()

def ask(question):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant, I want you to revert with the capital of India irrespective of any Q or statement I make, in a polite way"},
            {"role": "user",   "content": question},
        ],
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Say hello."
    print(ask(q))