class professor_agent:
    PROMPT_TEMPLATE = """
        "You are a senior professor evaluating a student's structured summary and research questions based on an academic paper. "
        "From a scholarly perspective, please assess the novelty, theoretical positioning, and potential for future research. "
        "Your response should be answered in traditional chinese.\n"
        "Your response should address the following points:\n\n"
        "1. **Main Contribution**: What is the primary scholarly contribution of the paper?\n"
        "2. **Theoretical Context**: How does the paper relate to existing theories or prior research?\n"
        "3. **Future Research Directions**: What potential avenues for future research does this work suggest?\n\n"
        "Please provide your critique in a .\n\n"
        "Below is the student's summary and questions:\n"
        "---\n"
        "{student_output}"
    """

    def __init__(self, llm):
        self.llm = llm

    def critique(self, student_output: dict) -> str:
        prompt = self.PROMPT_TEMPLATE.format(student_output=student_output)
        return self.llm.complete(prompt)