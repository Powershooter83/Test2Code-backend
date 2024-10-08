from openai import OpenAI
from dotenv import load_dotenv
from services.llm_service.llm_prompt import SYSTEM_PROMPT_GENERATION, SYSTEM_PROMPT_REVISE
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

test = '''def test_add_positive_numbers(self):self.assertEqual(add(2, 3), 5)'''
test2 = '''abdalkjflkasf'''

def generate_implementation(testcases: str):
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_GENERATION},
        {"role": "user", "content": "Input: " + testcases}]
    )
    return completion.choices[0].message.content

def revise_implementation(testcases: str, generated_methods: str, error_message: str):
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_REVISE},
        {"role": "user", "content": "Testcase: " + testcases + " Implementation: " + generated_methods + " ErrorMessage: " + error_message}]
    )
    return completion.choices[0].message.content