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