from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

test = '''def test_add_positive_numbers(self):self.assertEqual(add(2, 3), 5)'''

def generate_implementation(test: str):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a programming helper and you only write code and no other text"},
        {"role": "user", "content": "Write the implementation for the testcase " + test}]
    )
    return completion;
