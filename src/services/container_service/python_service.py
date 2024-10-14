# python_service.py

import re
import ast
from typing import Dict, Any, Tuple
from .base import ContainerService

class PythonContainerService(ContainerService):
    SUPPORTED_VERSIONS = ["3.6", "3.7", "3.8", "3.9", "3.10", "3.11"]

    def __init__(self, version: str = "3.11"):
        super().__init__(version)
        if not self.version:
            self.version = "3.11"  # default to 3.11 if version is None

        if self.version not in self.SUPPORTED_VERSIONS:
            raise ValueError(
                f"Unsupported Python version: {self.version}. Supported versions are: {', '.join(self.SUPPORTED_VERSIONS)}"
            )

    @classmethod
    def get_supported_versions(cls):
        return cls.SUPPORTED_VERSIONS

    def get_dockerfile_content(self, filename: str) -> str:
        """
        Get the content of the Dockerfile for Python code
        :param filename: Filename of the Python file
        :return: Content of the Dockerfile
        """
        python_version = self.version

        return f"""
        FROM python:{python_version}
        WORKDIR /app
        COPY {filename}.py /app/{filename}.py
        RUN pip install pytest pytest-json-report
        """

    def get_run_command(self, filename: str) -> str:
        """
        Get the command to run the Python code in a Docker container
        :param filename: Filename of the Python code
        :return: Command to run the Python code
        """
        return f"pytest /app/{filename}.py -v -k test_ --json-report --json-report-file=/app/test_results.json"

    def get_file_extension(self) -> str:
        """
        Get file extension for Python code
        :return: File extension
        """
        return "py"

    @staticmethod
    def validate_code(code: str) -> Tuple[bool, str]:
        """
        Validate Python code for syntax errors
        :param code: Python code
        :return: Tuple of boolean and error message
        """
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

    def validate_test_code(self, test_code: str) -> Tuple[bool, str]:
        """
        Validate Python test code and check if there's at least one test function which starts with "test_"
        :param test_code: Python test code
        :return: Tuple of boolean and error message
        """
        # First, check for syntax errors
        is_valid, error_msg = self.validate_code(test_code)
        if not is_valid:
            return False, error_msg

        # Check if there's at least one function that starts with "test_"
        test_function_pattern = r'\bdef\s+test_\w+\s*\('
        if not re.search(test_function_pattern, test_code):
            return False, "No test functions found. Test functions must start with 'test_'."

        return True, ""

    def run_code_in_container(self, code: str, test_code: str) -> Dict[str, Any]:
        """
        Run Python code in a Docker container
        :param code: Python code
        :param test_code: Python test code
        :return: Dictionary containing test results, build time, run time, and total time
        """
        # Validate main code
        is_valid, error_msg = self.validate_code(code)
        if not is_valid:
            return {"error": f"Invalid main code. {error_msg}"}

        # Validate test code if provided
        if test_code:
            is_valid, error_msg = self.validate_test_code(test_code)
            if not is_valid:
                return {"error": f"Invalid test code. {error_msg}"}

        return super().run_code_in_container(code, test_code)
