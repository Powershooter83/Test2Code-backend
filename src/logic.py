import os

from starlette.config import undefined

from services.container_service import get_container_service
from services.llm_service.llm_service import CodeGenerator


class CodeExecutionLogic:
    @staticmethod
    def get_supported_languages():
        return [
            "Python",
        ]

    @staticmethod
    def get_language_versions(lang: str):
        if lang.lower() == "python":
            return {"language": lang, "versions": ["3.11"]}
        return {"error": "Language not found"}

    @staticmethod
    def parse_testcase_and_implementation(jsonObject: object):
        testcases = ''
        implementations = ''
        for key in jsonObject["test2code"]:
            testcases += key["testcase"] + "\n"
            implementations += key["implementation"] + "\n"
        return testcases, implementations

    @staticmethod
    def retry_generating_implementation(llm_response_obj: object,
                                        code_generator: CodeGenerator,
                                        testcases: str,
                                        implementations: str):
        for tries in range(3):
            llm_response_obj = code_generator.revise_implementation(testcases,
                                                                    implementations,
                                                                    llm_response_obj["error"]["message"])
            if llm_response_obj["error"]["type"] == "":
                return llm_response_obj

        return llm_response_obj

    @staticmethod
    async def execute_testcases(testcases: str, lang: str, version: str):

        # check if lang and version are supported
        if lang not in CodeExecutionLogic.get_supported_languages():
            return {"error": "Language not supported"}
        if version not in CodeExecutionLogic.get_language_versions(lang)["versions"]:
            return {"error": "Version not supported"}

        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")

            code_generator = CodeGenerator(openai_api_key)

            llm_response_obj = code_generator.generate_implementation(testcases)

            testcases, implementations = CodeExecutionLogic.parse_testcase_and_implementation(llm_response_obj)

            if llm_response_obj["error"]["type"] != "":
                if llm_response_obj["error"]["source"] == "implementation":
                    llm_response_obj = CodeExecutionLogic.retry_generating_implementation(llm_response_obj,
                                                                                code_generator,
                                                                                testcases,
                                                                                implementations)
                else:
                    return llm_response_obj

            testcases, implementations = CodeExecutionLogic.parse_testcase_and_implementation(llm_response_obj)
            service = get_container_service(lang)

            result = service.run_code_in_container(implementations, testcases)

            if result.get("test_results").get("passed") == result.get("test_results").get("total"):
                return llm_response_obj
            else:
                return CodeExecutionLogic.retry_generating_implementation(llm_response_obj,
                                                                            code_generator,
                                                                            testcases,
                                                                            implementations)

        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
