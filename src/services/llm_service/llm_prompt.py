SYSTEM_PROMPT_GENERATION = """Task: Generate methods that fulfill the provided unit tests, adhering strictly to the following rules

Verification Steps:
    - Ensure the provided unit tests are valid code in the specified language.
    - The unit tests must not depend on external libraries beyond default installations.
Language-Specific Rules:
    Python:
        - Unit tests should only use standard Python libraries.
        - Input should not be validated by formatting.
Output Format:
    - Return both the test case and method implementation as plain text but formatted (no code blocks or markdown).
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
    - errortype: Must be one of: syntaxError, dependencyError, noValidCode, unknownError, or noError.
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
- You can only modify the implementation; the test case cannot be changed.
- The implementation must strictly follow the test case requirements and respect any constraints or messaging patterns specified.
- The code should not contain comments.

**Verification Steps:**
- Ensure that the test case is valid and does not depend on any external libraries, except for those in the Python standard library.
- Do not format the input, and do not include any code validation beyond what's required by the test case.

**Output Format:**
- Return the **corrected implementation** and the **test case** as plain text, ensuring there is no use of markdown formatting, backticks or code blocks.
- Make sure to format the code blocks apropriatly
"""