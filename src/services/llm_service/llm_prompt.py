SYSTEM_PROMPT_GENERATION = """Generate  methods that satisfy the provided unit tests, ensuring that the methods strictly adhere to the specified constraints and messaging patterns without including any comments. Follow these guidelines:

Verification Steps:
- Ensure the provided unit tests are valid code in the appropriate language.
- Confirm that the unit tests do not rely on external dependencies or libraries beyond those included in the default language installation.

Language-Specific Rules:
- The unit tests must exclusively utilize modules available in the standard Python library.
- The input should not be validated by formatting.

Output Format:
- Output the methods that fulfill the unit tests as plain text, without any enclosing backticks, code blocks, or markdown formatting and do the same for the input testcase and make sure the input testcase is also formatted and returned as output.
- Ensure that the response does not contain any code block syntax.

Error Handling:
- If any of the conditions are not met, return a message in the following JSON structure:

{
    "type": "errortype",
    "message": "short precise error description"
}
The errortype must be one of the following:
syntaxError
dependencyError
noValidCode
unknownError"""

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