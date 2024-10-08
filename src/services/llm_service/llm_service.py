from openai import OpenAI
from dotenv import load_dotenv
from services.llm_service.llm_prompt import SYSTEM_PROMPT_GENERATION
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

test = '''def test_add_positive_numbers(self):self.assertEqual(add(2, 3), 5)'''
test2 = '''abdalkjflkasf'''

def generate_implementation(testcases: str):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_GENERATION},
        {"role": "user", "content": "Input: " + testcases}]
    )
    return completion.choices[0].message.content;