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


    # async def execute_testcases2(self, testcases: str, lang: str, version: str):
    #
    #     # check if lang and version are supported
    #     if lang not in CodeExecutionLogic.get_supported_languages():
    #         return {"error": "Language not supported"}
    #     if version not in CodeExecutionLogic.get_language_versions(lang)["versions"]:
    #         return {"error": "Version not supported"}
    #
    #     try:
    #         openai_api_key = os.getenv("OPENAI_API_KEY")
    #
    #         code_generator = CodeGenerator(openai_api_key)
    #
    #         llm_response_obj = code_generator.generate_implementation(testcases)
    #
    #         testcases, implementations = CodeExecutionLogic.parse_testcase_and_implementation(llm_response_obj)
    #
    #         for tries in range(3):
    #             error = llm_response_obj["error"]
    #             if error["type"] != "":
    #                 if error["source"] in ["implementation", "docker"]:
    #                     llm_response_obj = CodeExecutionLogic.retry_generating_implementation(code_generator,
    #                                                                                 testcases,
    #                                                                                 implementations,
    #                                                                                 error["message"])
    #
    #
    #             testcases, implementations = CodeExecutionLogic.parse_testcase_and_implementation(llm_response_obj)
    #             service = get_container_service(lang)
    #
    #             result = service.run_code_in_container(implementations, testcases)
    #
    #             if result.get("test_results").get("passed") == result.get("test_results").get("total"):
    #                 return llm_response_obj
    #             else:
    #                 llm_response_obj["error"]["message"] = result.get("test_results").
    #                 llm_response_obj["error"]["type"] = "failedDockerCheck"
    #                 llm_response_obj["error"]["source"] = "docker"
    #
    #
    #         llm_response_obj["error"]["message"] = "Failed to generated a method"
    #         return llm_response_obj
    #
    #     except ValueError as e:
    #         return {"error": str(e)}
    #     except Exception as e:
    #         return {"error": f"An unexpected error occurred: {str(e)}"}
    #

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

            for tries in range(4):
                if llm_response_obj["error"]["type"] == "":
                    service = get_container_service(lang)
                    result = service.run_code_in_container(implementations, testcases)

                    if result.get("test_results").get("passed") == result.get("test_results").get("total"):
                        return llm_response_obj
                    else:
                        llm_response_obj["error"]["message"] = self.check_for_failing_tests(result)
                        llm_response_obj["error"]["type"] = "failedDockerCheck"
                        llm_response_obj["error"]["source"] = "docker"

                if llm_response_obj["error"]["source"] in ["implementation", "docker"]:
                    llm_response_obj = code_generator.revise_implementation(testcases,
                                                                          implementations,
                                                                          llm_response_obj["error"]["message"])

                testcases, implementations = CodeExecutionLogic.parse_testcase_and_implementation(llm_response_obj)

            return  llm_response_obj

        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}