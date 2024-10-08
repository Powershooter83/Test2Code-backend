from .base import ContainerService
from .python_service import PythonContainerService

def get_container_service(language: str) -> ContainerService:
    if language.lower() == 'python':
        return PythonContainerService()
    # Add more languages in the future here
    else:
        raise ValueError(f"Unsupported language: {language}")