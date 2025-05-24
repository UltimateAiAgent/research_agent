class master_agent:
    PROMPT_TEMPLATE = """
    You are a peer reviewer for an academic journal. Based on standard scholarly review criteria, please evaluate the following content.

    Your response should be written in **Traditional Chinese**, and follow the structured format below for each evaluation aspect:

    - A numerical score (if applicable)
    - Strengths
    - Weaknesses
    - Specific suggestions for improvement

    Please structure your response as follows:

    1. **Overall Rigor Score (1–5)**
    - Score:
    - Strengths:
    - Weaknesses:
    - Suggestions:

    2. **Methodology and Data Integrity**
    - Strengths:
    - Weaknesses:
    - Suggestions:

    3. **Experimental Design and Results Validity**
    - Strengths:
    - Weaknesses:
    - Suggestions:

    4. **Experimental Procedure and Design Details**
    - Strengths:
    - Weaknesses:
    - Suggestions:

    5. **Overall Suggestions for Improvement**
    - Strengths (if any):
    - Weaknesses:
    - Suggestions:

    Please base your evaluation on the following combined content:
    ---
    {full_analysis}

    (The full paper content is provided below for detailed reference regarding methods and experiments.)
    ---
    {paper_content}
    """


    def __init__(self, llm):
        self.llm = llm

    def review(self, student_output: dict, professor_output: str, paper_content: str) -> str:
        # student + professor output
        combined = student_output + "\n" + professor_output
        prompt = self.PROMPT_TEMPLATE.format(full_analysis=combined, paper_content=paper_content)
        return self.llm.complete(prompt)