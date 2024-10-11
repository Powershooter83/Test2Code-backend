from openai import OpenAI
from .llm_prompt import SYSTEM_PROMPT_GENERATION, SYSTEM_PROMPT_REVISE
import json

class CodeGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_implementation(self, testcases: str):
        """
        Generate implementation code based on the given testcases
        :param testcases: the testcases that the implementation should pass
        :return: the generated implementation code
        """
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_GENERATION},
                {"role": "user", "content": "Input: " + testcases}
            ]
        )
        
        parsed_result = json.loads(completion.choices[0].message.content)
        return parsed_result

    def revise_implementation(self, testcases: str, generated_methods: str, error_message: str):
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_REVISE},
                {"role": "user", "content": "Testcase: " + testcases + 
                                            " Implementation: " + generated_methods + 
                                            " ErrorMessage: " + error_message}
            ]
        )
        parsed_result = json.loads(completion.choices[0].message.content)
        return parsed_result
