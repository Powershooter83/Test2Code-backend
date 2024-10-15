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
    def get_supported_languages(logger):
        logger.info("Fetching supported languages")
        return get_supported_languages()

    @staticmethod
    def get_language_versions(lang: str, logger):
        logger.info(f"Fetching versions for language '{lang}'")
        versions = get_language_versions(lang)
        if versions:
            return {"language": lang, "versions": versions}
        else:
            logger.error(f"Language '{lang}' not found")
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
    def check_for_failing_tests(result: any):
        failed_message = ""
        for test in result.get("test_results").get("tests"):
            if test.get("outcome") == "failed":
                test_name = test.get("name").split("::")[-1]
                error_msg = test.get("call").get("longrepr")
                failed_message += f"Test {test_name}: {error_msg} "
        return failed_message

    @classmethod
    async def execute_testcases(cls, testcases: str, language: str, version: str, logger):
        # Log the received request
        logger.info(f"execute_testcases called with language='{language}', version='{version}', testcases length={len(testcases)}")

        language = language.lower()
        # Check if language and version are supported
        if language not in cls.get_supported_languages(logger):
            logger.error(f"Language '{language}' not supported")
            return {"error": "Language not supported"}
        if version not in cls.get_language_versions(language, logger)["versions"]:
            logger.error(f"Version '{version}' not supported for language '{language}'")
            return {"error": "Version not supported"}

        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            code_generator = CodeGenerator(openai_api_key, logger)

            logger.info("Generating implementation using OpenAI API")
            llm_response_obj = code_generator.generate_implementation(testcases)

            logger.info("Received implementation from OpenAI")
            testcases_str, implementations = cls.parse_testcase_and_implementation(llm_response_obj)
            logger.info("Parsed testcases and implementations")

            for tries in range(4):
                logger.info(f"Attempt {tries+1} to run code in container")
                if llm_response_obj["error"]["type"] == "":
                    service = get_container_service(language, version, logger)
                    result = service.run_code_in_container(implementations, testcases_str)

                    logger.info(f"Container run result: {result}")

                    if result.get("test_results").get("summary").get("passed") == result.get("test_results").get("summary").get("total"):
                        logger.info("All tests passed")
                        return llm_response_obj
                    else:
                        error_message = cls.check_for_failing_tests(result)
                        llm_response_obj["error"]["message"] = error_message
                        llm_response_obj["error"]["type"] = "failedDockerCheck"
                        llm_response_obj["error"]["source"] = "docker"

                if llm_response_obj["error"]["source"] in ["implementation", "docker"]:
                    logger.info("Revising implementation due to error")
                    llm_response_obj = code_generator.revise_implementation(
                        testcases_str,
                        implementations,
                        llm_response_obj["error"]["message"]
                    )

                testcases_str, implementations = cls.parse_testcase_and_implementation(llm_response_obj)
                logger.info("Parsed revised testcases and implementations")

            logger.info("Maximum retries reached, returning last response")
            return llm_response_obj

        except ValueError as e:
            logger.error(f"ValueError occurred: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}