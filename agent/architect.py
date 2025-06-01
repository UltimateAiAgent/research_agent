class architect_agent:
    PROMPT_TEMPLATE = """
    You are a scholarly architecture designer. Your task is to read a section of an academic paper or article and generate a high-level conceptual structure or logical flow based on its content.

    Format your response strictly using Mermaid syntax. Do NOT include code block delimiters like ```mermaid or ``` — just output the raw Mermaid code directly, starting with `graph TD` or `graph LR`.

    The Mermaid diagram should represent the structure, pipeline, methodology, or theoretical framework of the described section.

    Be concise, clear, and avoid unnecessary complexity. Prefer `graph TD` for flowcharts unless another type is more suitable. Do not explain the diagram—just return the Mermaid code block.

    The academic section is as follows:
    ---
    {paper_section}
    """

    def __init__(self):
        from agent.llm import OpenAILLM
        self.llm = OpenAILLM(model="gpt-4o")

    def generate_diagram(self, paper_section: str) -> str:
        prompt = self.PROMPT_TEMPLATE.format(paper_section=paper_section[:16000])
        return self.llm.complete(prompt)
