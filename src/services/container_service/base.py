# base.py

import docker
import tempfile
import os
import uuid
import time
import json
import tarfile
import io
from abc import ABC, abstractmethod
from typing import Dict, Any

import logging
from docker.errors import DockerException


class ContainerService(ABC):
    def __init__(self, version: str = None, logger=None):
        self.version = version
        self.logger = logger or logging.getLogger(__name__)
        try:
            self.docker_client = docker.from_env()
        except DockerException as e:
            self.logger.error(f"Error connecting to Docker: {str(e)}")
            raise ValueError(
                f"Error connecting to Docker (Docker running and configured correctly?): {str(e)}"
            )

    @abstractmethod
    def get_dockerfile_content(self, filename: str) -> str:
        pass

    @abstractmethod
    def get_run_command(self, filename: str) -> str:
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        pass

    def parse_test_results(self, json_content: str) -> Dict[str, Any]:
        data = json.loads(json_content)
        return {
            "summary": data["summary"],
            "tests": [
                {
                    "name": test["nodeid"],
                    "outcome": test["outcome"],
                    "duration": test["call"]["duration"],
                    "setup": test["setup"],
                    "call": test["call"],
                    "teardown": test["teardown"],
                }
                for test in data["tests"]
            ],
        }

    def run_code_in_container(self, code: str, test_code: str) -> Dict[str, Any]:
        self.logger.info(f"Running code in container, code length: {len(code)}, test_code length: {len(test_code)}")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                unique_filename = f"code_{uuid.uuid4().hex}"
                file_path = os.path.join(
                    temp_dir, f"{unique_filename}.{self.get_file_extension()}"
                )

                with open(file_path, "w") as file:
                    file.write(code)
                    if test_code:
                        file.write("\n\n")
                        file.write(test_code)

                dockerfile_content = self.get_dockerfile_content(unique_filename)
                dockerfile_path = os.path.join(temp_dir, "Dockerfile")

                with open(dockerfile_path, "w") as dockerfile:
                    dockerfile.write(dockerfile_content)

                build_start_time = time.time()
                image, _ = self.docker_client.images.build(
                    path=temp_dir, tag="code_test_image"
                )
                build_time = (time.time() - build_start_time) * 1000

                run_start_time = time.time()
                container = self.docker_client.containers.run(
                    image="code_test_image",
                    command=self.get_run_command(unique_filename),
                    detach=True,
                )
                container.wait()
                run_time = (time.time() - run_start_time) * 1000

                # Extract the JSON content from the tar archive
                bits, _ = container.get_archive("/app/test_results.json")
                tar_stream = io.BytesIO()
                for chunk in bits:
                    tar_stream.write(chunk)
                tar_stream.seek(0)

                with tarfile.open(fileobj=tar_stream) as tar:
                    json_file = tar.extractfile("test_results.json")
                    json_content = json_file.read().decode("utf-8")

                test_results = self.parse_test_results(json_content)

                container.remove()
                self.docker_client.images.remove(image.id, force=True)

                self.logger.info("Successfully ran code in container")
                return {
                    "test_results": test_results,
                    "build_time": build_time,
                    "run_time": run_time,
                    "total_time": build_time + run_time,
                }
        except Exception as e:
            self.logger.error(f"Error running code in container: {str(e)}")
            return {"error": str(e)}
