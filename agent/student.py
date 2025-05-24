class student_agent:
    PROMPT_TEMPLATE = """
    You are a graduate student tasked with summarizing the following academic paper. Please produce a structured summary with the following five sections:

    - **Background**: Briefly describe the broader context or problem area the paper addresses.
    - **Objective**: State the specific goal or research question of the study.
    - **Method**: Summarize the methodology or approach used by the authors.
    - **Results**: Highlight the key findings of the research.
    - **Conclusion**: Summarize the implications, conclusions, or potential future directions.

    Each section should be 2~5 sentences long. Use succinct, understandable English. Do not include bullet points or headings in the final summary.
    "Your response should be answered in traditional chinese.\n"
    Here is the full text of the paper:
    {paper_text}
    """

    def __init__(self, llm):
        self.llm = llm

    def summarize_and_questions(self, paper_text: str) -> dict:
        prompt = self.PROMPT_TEMPLATE.format(paper_text=paper_text[:16000])  # truncate if exceeds context
        response = self.llm.complete(prompt)
        return response
