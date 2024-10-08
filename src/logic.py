from services.container_service import get_container_service
import services.llm_service  # import generate_code if needed
from fastapi import APIRouter, Request
import services.llm_service



class CodeExecutionLogic:
    @staticmethod
    def get_supported_languages():
        return [
            "Python",
            # "Java",
        ]

    @staticmethod
    def get_language_versions(lang: str):
        if lang == "Python":
            return {"language": lang, "versions": ["3.11"]}
        # if lang == "Java":
        #     return {"language": lang, "versions": ["11"]}
        return {"error": "Language not found"}

    @staticmethod
    async def execute_testcases(testcases: str, lang: str, version: str, simulate: bool = False):
        if simulate:
            return {
                "id": "chatcmpl-AFohtniAprarbO6GWW57oPoQSZMQ9",
                "object": "chat.completion",
                "created": 1728333201,
                "model": "gpt-4o-mini-2024-07-18",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "This is a test! How can I assist you further?",
                            "refusal": "null"
                        },
                        "logprobs": "null",
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 13,
                    "completion_tokens": 12,
                    "total_tokens": 25,
                    "prompt_tokens_details": {
                        "cached_tokens": 0
                    },
                    "completion_tokens_details": {
                        "reasoning_tokens": 0
                    }
                },
                "system_fingerprint": "fp_f85bea6784"}

        pseudo_code = """
def add(a, b):
    return a + b
"""

        pseudo_test_code = """
def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
"""
        try:
            service = get_container_service(lang)
            result = service.run_code_in_container(pseudo_code, pseudo_test_code)
            return result

        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
