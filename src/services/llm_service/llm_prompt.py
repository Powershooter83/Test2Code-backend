SYSTEM_PROMPT_GENERATION = """Task: Generate methods that fulfill the provided unit tests, adhering strictly to the following rules

Verification Steps:
    - You can only modify the implementation; the test case CANNOT, under no sercumstances, be changed but only the formattation.
    - Ensure the provided unit tests are valid code in the specified language.
    - The unit tests must not depend on external libraries beyond default installations.
Language-Specific Rules:
    Python:
        - Unit tests should only use standard Python libraries.
        - Input should not be validated by formatting.
Output Format:
    - Return both the test case and method implementation as plain text but formatted (no code blocks or markdown).
    - The implementation should contain comments with a precise code explanation on how the code works
    - Output as a JSON structure like this JSON structure:
        {
        "test2code": [
            {
            "testcase": "Enter the full testcase, ensure **'test_' is prefixed** to the name and the testcase is **FORMATTED**.",
            "implementation": "Enter the generated implementation"
            }
        ],
        "error": {
            "type": "errortype",
            "message": "If error occurs, include a short and percise error description."
        }
        }
Error Handling:
    - errortype: Must be one of: logicError, syntaxError, dependencyError, noValidCode, unknownError, or noError.
    - Append test cases sharing the same implementation to a single "test2code" object.

Example Output
    {
    "test2code": [
        {
        "testcase": "def test_add_numbers(self):\n    self.assertEqual(add_numbers(3, 3), 6) \n\n def test_add_numbers2(self):\n    self.assertEqual(add_numbers(2, 3), 5)",
        "implementation": "def add_numbers(a, b):\n    return a + b"
        },
        {
        "testcase": "def test_subtract_numbers(self):\n    self.assertEqual(sub_numbers(2, 3), -1)",
        "implementation": "def sub_numbers(a, b):\n    return a - b"
        }
    ],
    "error": {
        "type": "noError",
        "message": ""
    }
    }
"""

SYSTEM_PROMPT_REVISE = """
**Task:** Modify the provided implementation to fix the error so that the unit tests pass. You will receive:
- The **test case**
- The **current (faulty) implementation**
- The **error message**

**Rules:**
- Do user can't know that you corrected or modified anything
- You can only modify the implementation; the test case CANNOT, under no sercumstances, be changed but only the formattation.
- The implementation must strictly follow the test case requirements and respect any constraints or messaging patterns specified.
Verification Steps:
    - Ensure the provided unit tests are valid code in the specified language.
    - The unit tests must not depend on external libraries beyond default installations.
Language-Specific Rules:
    Python:
        - Unit tests should only use standard Python libraries.
        - Input should not be validated by formatting.

**Output Format:**
    - Return both the test case and method implementation as plain text but formatted (no code blocks or markdown).
- The implementation should contain comments with a precise code explanation on how the code works
- Output as a JSON structure like this JSON structure:
        {
        "test2code": [
            {
            "testcase": "Enter the full and testcase, ensure that the testcase is **FORMATTED** and  **'test_' is prefixed** to the name.",
            "implementation": "Enter the generated implementation"
            }
        ]
        }
"""