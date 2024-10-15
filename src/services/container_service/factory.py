# factory.py

from .base import ContainerService
from .java_service import JavaContainerService
from .python_service import PythonContainerService

SERVICE_CLASSES = {
    'python': PythonContainerService,
    'java': JavaContainerService,
    # Add more languages here in the future
}


def get_container_service(language: str, version: str) -> ContainerService:
    service_class = SERVICE_CLASSES.get(language.lower())
    if service_class:
        return service_class(version)
    else:
        raise ValueError(f"Unsupported language: {language}")


def get_supported_languages():
    return list(SERVICE_CLASSES.keys())


def get_language_versions(language: str):
    service_class = SERVICE_CLASSES.get(language.lower())
    if service_class:
        return service_class.get_supported_versions()
    else:
        return None
