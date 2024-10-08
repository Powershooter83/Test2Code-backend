import docker
import tempfile
import os
import uuid
import time
from abc import ABC, abstractmethod
from typing import Dict, Any

class ContainerService(ABC):
    def __init__(self):
        self.docker_client = docker.from_env()

    @abstractmethod
    def get_dockerfile_content(self, filename: str) -> str:
        pass

    @abstractmethod
    def get_run_command(self, filename: str) -> str:
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        pass

    def run_code_in_container(self, code: str, test_code: str = None) -> Dict[str, Any]:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                unique_filename = f"code_{uuid.uuid4().hex}"
                file_path = os.path.join(temp_dir, f"{unique_filename}.{self.get_file_extension()}")

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
                image, _ = self.docker_client.images.build(path=temp_dir, tag="code_test_image")
                build_time = (time.time() - build_start_time) * 1000

                run_start_time = time.time()
                container = self.docker_client.containers.run(
                    image="code_test_image",
                    command=self.get_run_command(unique_filename),
                    detach=True
                )
                logs = container.logs(stream=True, follow=True)
                result_logs = "".join([log.decode('utf-8') for log in logs])
                run_time = (time.time() - run_start_time) * 1000

                container.wait()
                container.remove()
                self.docker_client.images.remove(image.id, force=True)

                return {
                    "logs": result_logs,
                    "build_time": build_time,
                    "run_time": run_time,
                    "total_time": build_time + run_time
                }
        except Exception as e:
            return {"error": str(e)}