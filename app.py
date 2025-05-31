import streamlit as st
import fitz  # PyMuPDF
import os
from pathlib import Path
from agent.student import student_agent
from agent.professor import professor_agent
from agent.master import master_agent
from agent.llm import OpenAILLM
import tempfile
import re

# ---------- Streamlit UI ----------
st.set_page_config(page_title="AI 共讀室：論文自爆機", layout="wide")
st.title("📚 論文自爆機：AI 模擬讀書會")
st.markdown("這是一個結合多位 AI 角色（學生、教授、預言者）的論文共讀系統 ✨")

uploaded_file = st.file_uploader("請上傳你想讀的 PDF 論文", type=["pdf"])
user_instruction = st.text_area("請簡要描述你想從這篇論文獲得什麼，例如研究動機、主題、模型？")

def _extract_from_pdf(stream) -> str:
    doc = fitz.open(stream=stream.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        text = page.get_text()
        if text:
            full_text += text + "\n"
    doc.close()
    full_text.strip()
    pattern = re.compile(r'\n?References\b.*', flags=re.IGNORECASE | re.DOTALL)
    cleaned_text = re.sub(pattern, '', full_text)
    return cleaned_text

def pipeline(paper_content: str) -> tuple:
    llm = OpenAILLM(model="gpt-4o")
    student = student_agent(llm)
    professor = professor_agent(llm)
    master = master_agent(llm)

    student_output = student.summarize_and_questions(paper_content)
    professor_output = professor.critique(student_output)
    master_output = master.review(student_output, professor_output, paper_content)

    return student_output, professor_output, master_output

# ---------- 啟動流程 ----------
if uploaded_file is not None:
    st.success("已上傳論文，開始解析...")
    paper_content = _extract_from_pdf(uploaded_file)
    st.text_area("📖 預覽全文內容", paper_content[:3000], height=300)

    # 初始化 agent
    llm = OpenAILLM(model="gpt-4o")
    student = student_agent(llm)
    professor = professor_agent(llm)
    master = master_agent(llm)

    # 全域儲存變數
    if 'student_output' not in st.session_state:
        st.session_state.student_output = ""
    if 'professor_output' not in st.session_state:
        st.session_state.professor_output = ""
    if 'master_output' not in st.session_state:
        st.session_state.master_output = ""

    # 個別按鈕觸發代理人
    if st.button("👦 Freshie_AI 開始摘要"):
        with st.spinner("Freshie_AI 正在閱讀與摘要中..."):
            st.session_state.student_output = student.summarize_and_questions(paper_content)
            st.subheader("🧑‍🎓 Freshie_AI：我的摘要與疑問")
            st.markdown(st.session_state.student_output)

    if st.button("🧓 ProfSnark_AI 開始批評"):
        if not st.session_state.student_output:
            st.warning("請先執行 Freshie_AI 摘要")
        else:
            with st.spinner("ProfSnark_AI 正在批評..."):
                st.session_state.professor_output = professor.critique(st.session_state.student_output)
                st.subheader("🧓 ProfSnark_AI：批評與建議")
                st.markdown(st.session_state.professor_output)

    if st.button("🔮 Oracle_AI 給出展望"):
        if not st.session_state.student_output or not st.session_state.professor_output:
            st.warning("請先執行前兩位代理人")
        else:
            with st.spinner("Oracle_AI 正在預測未來研究方向..."):
                st.session_state.master_output = master.review(
                    st.session_state.student_output,
                    st.session_state.professor_output,
                    paper_content
                )
                st.subheader("🔮 Oracle_AI：未來研究展望")
                st.markdown(st.session_state.master_output)

            # 儲存報告
            output_path = Path("outputs/summary.md")
            output_path.parent.mkdir(exist_ok=True, parents=True)
            output_path.write_text("\n\n".join([
                "# AI Paper Review Report",
                "## Student Summary & Questions", st.session_state.student_output,
                "## Professor's Perspective", st.session_state.professor_output,
                "## Master's Perspective", st.session_state.master_output
            ]), encoding="utf-8")
            st.success(f"🎉 共讀完成！報告已儲存於：{output_path.resolve()}")
else:
    st.info("請先上傳 PDF 並描述你的研究目的，我們的 AI 小隊將啟動共讀！")

