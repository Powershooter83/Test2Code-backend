from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

test = '''def test_add_positive_numbers(self):self.assertEqual(add(2, 3), 5)'''
test2 = '''abdalkjflkasf'''

def generate_implementation(test: str):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an experienced programmer with plenty of knowledge in testing"},
        {"role": "user", "content": """"
        First check if the following input is code. 
        Then ckeck if the code is a valid testcase in the appropriate language. 
        Then check if the test has any syntax errors.
        If any of the 3 check are not the case return a short error message.

        After the checks, if its a valid testcase, create the method which will solve the testcase input.
        Return the generated method without any extra text

        Input: """ + test}]
    )
    return completion;

