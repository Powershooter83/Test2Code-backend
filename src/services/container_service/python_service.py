# services/container_service/python_service.py

from .base import ContainerService

class PythonContainerService(ContainerService):
    def get_dockerfile_content(self, filename: str) -> str:
        return f"""
        FROM python:3.11
        WORKDIR /app
        COPY {filename}.py /app/{filename}.py
        RUN pip install pytest
        """

    def get_run_command(self, filename: str) -> str:
        return f"pytest /app/{filename}.py -v -k test_"

    def get_file_extension(self) -> str:
        return "py"