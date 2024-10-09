from openai import OpenAI
from dotenv import load_dotenv
from llm_prompt import SYSTEM_PROMPT_GENERATION, SYSTEM_PROMPT_REVISE
import os
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

test = '''
def test_add_positive_numbers(self):
    self.assertEqual(add(2, 3), 5)
'''
test2 = '''abdalkjflkasf'''

def generate_implementation(testcases: str):
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_GENERATION},
        {"role": "user", "content": "Input: " + testcases}]
    )
    
    result = completion.choices[0].message.content
    
   # print(result["test2code"][0]["testcase"])
    
    
    parsed_result = json.loads(completion.choices[0].message.content)
    testcases, implementations = parse_testcase_and_implementation(parsed_result)
        
    return completion.choices[0].message.content

def parse_testcase_and_implementation(jsonObject: object):
    testcases = ''
    implementations = ''
    for key in jsonObject["test2code"]:
        testcases += key["testcase"] + "\n"
        implementations += key["implementation"] + "\n"
    return testcases, implementations

def revise_implementation(testcases: str, generated_methods: str, error_message: str):
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_REVISE},
        {"role": "user", "content": "Testcase: " + testcases + " Implementation: " + generated_methods + " ErrorMessage: " + error_message}]
    )
    return completion.choices[0].message.content

generate_implementation(test)