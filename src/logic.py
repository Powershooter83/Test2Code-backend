import os

from services.container_service import get_container_service
from services.llm_service.llm_service import CodeGenerator


class CodeExecutionLogic:
    @staticmethod
    def get_supported_languages():
        return [
            "python",
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
    def handel_docker_response(docker_response: dict):
        failed_tests = []
        passed_tests = []
        tests = docker_response["test_results"]["tests"]
        for test in tests:
            test_info = {
                "name": test.split("::")[-1],
                "errorType": None,
                "errorMessage": None,
            }
            if test["outcome"] == "passed":
                passed_tests.append(test_info)
            elif test["outcome"] == "failed":
                test_info["errorType"] = test["call"]["traceback"]["message"]
                test_info["errorMessage"] = test["call"]["crash"]["message"]
                failed_tests.append(test_info)
        return failed_tests, passed_tests

    @staticmethod
    async def execute_testcases(testcases: str, lang: str, version: str):

        # check if lang and version are supported
        if lang.lower() not in CodeExecutionLogic.get_supported_languages():
            return {"error": "Language not supported"}
        if version not in CodeExecutionLogic.get_language_versions(lang)["versions"]:
            return {"error": "Version not supported"}

        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")

            code_generator = CodeGenerator(openai_api_key)

            llm_response_obj = code_generator.generate_implementation(testcases)
            if llm_response_obj["error"]["type"] != "noError":
                return llm_response_obj["error"]

            testcases, implementations = CodeExecutionLogic.parse_testcase_and_implementation(llm_response_obj)
            service = get_container_service(lang)

            result = service.run_code_in_container(implementations, testcases)

            # foo = CodeExecutionLogic.handel_docker_response(result)

            if result.get("test_results").get("passed") == result.get("test_results").get("total"):
                return implementations
            else:
                return result

        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
