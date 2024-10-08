
from services.container_service import get_container_service
import services.llm_service  # import generate_code if needed

class CodeExecutionLogic:
    @staticmethod
    def get_supported_languages():
        return ["Python"]

    @staticmethod
    def get_language_versions(lang: str):
        if lang == "Python":
            return {"language": lang, "versions": ["3.11"]}
        return {"error": "Language not found"}

    @staticmethod
    async def execute_testcases(testcases: str, lang: str, version: str):
        
        
        pseudo_code = """
def add(a, b):
    return a + b
"""
        
        pseudo_test_code = """
def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
"""     
        try:
            service = get_container_service(lang)
            result = service.run_code_in_container(pseudo_code, pseudo_test_code)
            return result
        
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}