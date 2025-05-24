import fitz
import re
import argparse
from pathlib import Path
from agent.student import student_agent
from agent.professor import professor_agent
from agent.master import master_agent
from agent.llm import OpenAILLM

def _extract_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    full_text = ""
    for page in doc:
        text = page.get_text()
        if text:
            full_text += text + "\n"
    doc.close()
    full_text.strip()
    # truncate references 
    pattern = re.compile(r'\n?References\b.*', flags=re.IGNORECASE | re.DOTALL)
    cleaned_text = re.sub(pattern, '', full_text)

    return cleaned_text

def pipeline(path: str):
    paper_content = _extract_from_pdf(path)
    llm = OpenAILLM(model="gpt-4o")

    student = student_agent(llm)
    professor = professor_agent(llm)
    master = master_agent(llm)

    student_output = student.summarize_and_questions(paper_content)
    professor_output = professor.critique(student_output)
    master_output = master.review(student_output, professor_output, paper_content)

    summary_md = "\n\n".join([
        "# AI Paper Review Report",
        "## Student Summary & Questions",
        student_output,
        "## Professor's Perspective",
        professor_output,
        "## Master's Perspective",
        master_output,
    ])
    output_path = Path("outputs/summary1.md")
    output_path.parent.mkdir(exist_ok=True, parents=True)
    output_path.write_text(summary_md, encoding="utf-8")

    print(f"你的報告已經完成了！在以下路徑： {output_path.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="請輸入你想了解的論文路徑！")
    parser.add_argument("--input", required=True, help="Path to PDF paper")
    args = parser.parse_args()
    pipeline(args.input)