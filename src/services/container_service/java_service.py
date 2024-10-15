# java_service.py

import io
import os
import shutil
import tarfile
import tempfile
import time
import xml.etree.ElementTree as ET
from typing import Dict, Any

from .base import ContainerService


class JavaContainerService(ContainerService):
    SUPPORTED_VERSIONS = ["11", "17"]

    def __init__(self, version: str = "11", logger=None):
        super().__init__(version, logger)
        if not self.version:
            self.version = "11"  # default to 11 if version is None

        if self.version not in self.SUPPORTED_VERSIONS:
            self.logger.error(
                f"Unsupported Java version: {self.version}. Supported versions are: {', '.join(self.SUPPORTED_VERSIONS)}"
            )
            raise ValueError(
                f"Unsupported Java version: {self.version}. Supported versions are: {', '.join(self.SUPPORTED_VERSIONS)}"
            )

    @classmethod
    def get_supported_versions(cls):
        return cls.SUPPORTED_VERSIONS

    def get_dockerfile_content(self, filename: str) -> str:
        """
        Return Dockerfile content for Java with JUnit support for a specific Java version.
        This Dockerfile will use an OpenJDK base image for the specified Java version, install JUnit,
        copy the Java source code to the container, compile and run it.

        :param filename: The name of the Java source file (without extension).
        :return: Dockerfile content as a string.
        """

        if self.version == "11":
            pom_file = "java11pom.xml"
            image_version = "3.8.1-adoptopenjdk-11"
        elif self.version == "17":
            pom_file = "java17pom.xml"
            image_version = "3.8.1-openjdk-17-slim"
        else:
            raise ValueError(f"Unsupported Java version: {self.version}")

        return f"""
        FROM maven:{image_version}

        WORKDIR /app
        COPY {pom_file} /app/pom.xml

        RUN mkdir -p src/test/java/com/example

        COPY {filename}.java src/test/java/com/example/{filename}.java
        """

    def get_run_command(self) -> str:
        return "mvn clean test"

    def get_file_extension(self) -> str:
        """
        Return the file extension for Java files.
        """
        return "java"

    def format_junit_response(self, xml_content):
        root = ET.fromstring(xml_content)

        total_tests = int(root.attrib["tests"])
        failures = int(root.attrib["failures"])
        errors = int(root.attrib["errors"])

        passed = total_tests - (failures + errors)
        summary = {
            "total": total_tests,
            "passed": passed
        }

        tests = []

        for testcase in root.findall('testcase'):
            test_data = {
                "name": testcase.attrib["name"],
                "outcome": "failed" if testcase.find('failure') is not None else "passed",
                "duration": testcase.attrib["time"],
                "call": {
                    "longrepr": ""
                }
            }

            failure = testcase.find('failure')
            if failure is not None:
                test_data["call"]["longrepr"] = failure.text.strip()
                test_data["failure"] = {
                    "type": failure.attrib.get("type", ""),
                    "message": failure.text.split('\n')[0].strip(),
                    "details": "\n".join(failure.text.split('\n')[1:]).strip()
                }

            tests.append(test_data)

        return {
            "summary": summary,
            "tests": tests
        }

    def create_java_class(self, tests, productiveCode, className):
        """
        Add JUnit imports and wrap the provided test code in a proper JUnit test class.
        """
        return f"""
            import static org.junit.jupiter.api.Assertions.assertEquals;
            import org.junit.jupiter.api.Test;

            public class {className} {{
                {tests}

                {productiveCode}
            }}
"""

    def run_code_in_container(self, code: str, test_code: str) -> Dict[str, Any]:
        """
        Run Java code in a Docker container with optional JUnit test code.
        :param code: Java source code
        :param test_code: Java test code (optional)
        :return: Dictionary containing build time, run time, and test results (if any)
        """

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                java11_pom_path = os.path.join(os.path.dirname(__file__), 'java/java11pom.xml')
                java17_pom_path = os.path.join(os.path.dirname(__file__), 'java/java17pom.xml')

                shutil.copy(java11_pom_path, temp_dir)
                shutil.copy(java17_pom_path, temp_dir)

                filename = "TestClass"
                file_path = os.path.join(temp_dir, f"{filename}.{self.get_file_extension()}")

                javaClass = self.create_java_class(test_code, code, filename)

                with open(file_path, "w") as file:
                    file.write(javaClass)

                dockerfile_content = self.get_dockerfile_content(filename)
                dockerfile_path = os.path.join(temp_dir, "Dockerfile")
                with open(dockerfile_path, "w") as dockerfile:
                    dockerfile.write(dockerfile_content)

                build_start_time = time.time()
                image, _ = self.docker_client.images.build(path=temp_dir, tag="java_code_test_image")
                build_time = (time.time() - build_start_time) * 1000  # in milliseconds

                run_start_time = time.time()

                container = self.docker_client.containers.run(
                    image="java_code_test_image",
                    command=self.get_run_command(),
                    detach=True
                )
                container.wait()
                run_time = (time.time() - run_start_time) * 1000

                test_results = None
                if test_code:
                    bits, _ = container.get_archive("/app/target/test-classes/TEST-TestClass.xml")
                    tar_stream = io.BytesIO()
                    for chunk in bits:
                        tar_stream.write(chunk)
                    tar_stream.seek(0)

                    with tarfile.open(fileobj=tar_stream) as tar:
                        xml_file = tar.extractfile('TEST-TestClass.xml')
                        xml_content = xml_file.read().decode('utf-8')

                    test_results = self.format_junit_response(xml_content)

                container.remove()
                self.docker_client.images.remove(image.id, force=True)

                return {
                    "test_results": test_results,
                    "build_time": build_time,
                    "run_time": run_time,
                    "total_time": build_time + run_time
                }

        except Exception as e:
            return {"error": str(e)}


java_code = """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""

test_code = """
@Test
public void testAddition() {
    assertEquals(5 + 2, 7);
}
"""
