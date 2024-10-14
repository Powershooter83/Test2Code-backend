# logic.py

import os
from services.container_service.factory import (
    get_container_service,
    get_supported_languages,
    get_language_versions,
)
from services.llm_service.llm_service import CodeGenerator

class CodeExecutionLogic:
    @staticmethod
    def get_supported_languages():
        return get_supported_languages()

    @staticmethod
    def get_language_versions(lang: str):
        versions = get_language_versions(lang)
        if versions:
            return {"language": lang, "versions": versions}
        else:
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
    def retry_generating_implementation(code_generator: CodeGenerator,
                                        testcases: str,
                                        implementations: str,
                                        errorMessage: str):

        responseObject = code_generator.revise_implementation(testcases,
                                                              implementations,
                                                              errorMessage)
        return responseObject

    @staticmethod
    def check_for_failing_tests(result: any):
        failed_message = ""

        for test in result.get("test_results").get("tests"):
            if test.get("outcome") == "failed":
                test_name = test.get("name").split("::")[-1]
                error_msg = test.get("call").get("longrepr")
                failed_message += f"Test {test_name}: {error_msg} "

        return failed_message

    @classmethod
    async def execute_testcases(cls, testcases: str, language: str, version: str):
        language = language.lower()
        # Check if language and version are supported
        if language not in cls.get_supported_languages():
            return {"error": "Language not supported"}
        if version not in cls.get_language_versions(language)["versions"]:
            return {"error": "Version not supported"}

        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")

            code_generator = CodeGenerator(openai_api_key)

            llm_response_obj = code_generator.generate_implementation(testcases)

            testcases_str, implementations = cls.parse_testcase_and_implementation(llm_response_obj)

            for tries in range(4):
                if llm_response_obj["error"]["type"] == "":
                    service = get_container_service(language, version)
                    result = service.run_code_in_container(implementations, testcases_str)

                    if result.get("test_results").get("summary").get("passed") == result.get("test_results").get("summary").get("total"):
                        return llm_response_obj
                    else:
                        error_message = cls.check_for_failing_tests(result)
                        llm_response_obj["error"]["message"] = error_message
                        llm_response_obj["error"]["type"] = "failedDockerCheck"
                        llm_response_obj["error"]["source"] = "docker"

                if llm_response_obj["error"]["source"] in ["implementation", "docker"]:
                    llm_response_obj = code_generator.revise_implementation(
                        testcases_str,
                        implementations,
                        llm_response_obj["error"]["message"]
                    )

                testcases_str, implementations = cls.parse_testcase_and_implementation(llm_response_obj)

            return llm_response_obj

        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
