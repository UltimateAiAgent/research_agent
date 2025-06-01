import streamlit as st
import fitz  # PyMuPDF
from agent.student import student_agent
from agent.professor import professor_agent
from agent.master import master_agent
from agent.llm import OpenAILLM
from agent.architect import architect_agent
import random
import re

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Read It For Me! ", layout="wide")
if "show_characters" not in st.session_state:
    st.session_state["show_characters"] = False
if "murloc_unlocked" not in st.session_state:
    st.session_state["murloc_unlocked"] = False
st.title("📚 Read It For Me!")
st.markdown("這是一個有著多位成員的魔法實驗室（半獸人、可怕的指導老師、魚人學弟、珍娜．普勞德摩爾） ✨")

uploaded_file = st.file_uploader("請上傳你想讀的論文或是文章，請使用 PDF 檔案！", type=["pdf"])
murloc_audio_files = ["doc/murloc1.mp3", "doc/murloc2.mp3","doc/murloc3.mp3"]

def _extract_from_pdf(stream) -> list[tuple[str, str]]:
    doc = fitz.open(stream=stream.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        text = page.get_text()
        full_text += text + "\n"
    doc.close()

    # 用較精準的方式抓常見章節
    section_names = [
        "abstract", "introduction", "related work", "background", "method", "methodology",
        "approach", "experiment", "experiments", "evaluation", "results", "discussion", 
        "conclusion", "future work", 
    ]
    pattern = re.compile(r"(?i)^({})\b.*".format("|".join(section_names)), flags=re.MULTILINE)
    matches = list(pattern.finditer(full_text))

    sections = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        title = matches[i].group().strip()
        content = full_text[start:end].strip()
        sections.append((title, content))

    # 若沒有偵測到標題，則切為單頁段落
    if not sections:
        page_lines = full_text.split("\n")
        avg_len = len(page_lines) // 5  # 分五段 fallback
        for i in range(5):
            start = i * avg_len
            end = (i + 1) * avg_len if i < 4 else len(page_lines)
            sections.append((f"Section {i+1}", "\n".join(page_lines[start:end]).strip()))

    # 合併過短的段落
    min_len = 500
    merged_sections = []
    i = 0
    while i < len(sections):
        title, content = sections[i]
        if len(content) < min_len:
            if i + 1 < len(sections):
                next_title, next_content = sections[i + 1]
                merged_sections.append((f"{title} + {next_title}", content + "\n" + next_content))
                i += 2
            elif merged_sections:
                prev_title, prev_content = merged_sections.pop()
                merged_sections.append((f"{prev_title} + {title}", prev_content + "\n" + content))
                i += 1
            else:
                merged_sections.append((title, content))
                i += 1
        else:
            merged_sections.append((title, content))
            i += 1
    

    return merged_sections


# def render_mermaid_and_save(graph_str: str, filename: str = "mermaid_diagram.png"):
#     # 編碼 Mermaid 為 base64 URL-safe 字串
#     graph_bytes = graph_str.encode("utf-8")
#     base64_bytes = base64.urlsafe_b64encode(graph_bytes)
#     base64_string = base64_bytes.decode("ascii")

#     # 向 mermaid.ink API 請求圖片
#     # response = requests.get('https://mermaid.ink/img/' + base64_string)
#     # if response.status_code != 200:
#     #     st.error("❌ 圖片生成失敗，Mermaid 圖形伺服器出錯")
#     #     return

#     # 顯示圖像與儲存
#     img = Image.open(io.BytesIO(response.content))
#     st.image(img, caption="📐 Mermaid 架構圖", use_column_width=True)

#     # 儲存圖檔
#     img.save(filename)
#     st.success(f"✅ 架構圖已儲存為：{filename}")

#     # 提供下載連結
#     buffered = io.BytesIO()
#     img.save(buffered, format="PNG")
#     st.download_button(
#         label="📥 下載架構圖 (PNG)",
#         data=buffered.getvalue(),
#         file_name=filename,
#         mime="image/png"
#     )


if uploaded_file is not None:
    
    user_instruction = st.text_area("請簡要地設下任務，讓魔法實驗室為你效勞！比如這篇文章的研究動機為何、主題是什麼...？") or ""
    paper_content = _extract_from_pdf(uploaded_file)
    st.success("已上傳論文囉～")

    # 讓使用者選擇章節段落
    section_titles = [title for title, _ in paper_content]
    selected_section_title = st.selectbox("📑 請選擇要處理的章節", section_titles)
    selected_section_text = next(content for title, content in paper_content if title == selected_section_title)
    
    st.text_area("📖 預覽內容", selected_section_text, height=300)
    # user_instruction = st.text_area("請簡要地設下任務，讓魔法實驗室為你效勞！比如這篇文章的研究動機為何、主題是什麼...？")

    # 初始化 agent
    llm = OpenAILLM(model="gpt-3.5-turbo")
    student = student_agent()
    professor = professor_agent()
    master = master_agent()

    # 全域儲存變數
    if 'student_output' not in st.session_state:
        st.session_state.student_output = ""
    if 'professor_output' not in st.session_state:
        st.session_state.professor_output = ""
    if 'master_output' not in st.session_state:
        st.session_state.master_output = ""
    if 'architect_output' not in st.session_state:
        st.session_state.architect_output = ""

    # ---------- 隱藏角色解鎖 ----------
    with st.expander("🌊 你聽到遠方傳來奇怪的咕嚕聲 … 想要查看嗎？"):
        if not st.session_state["murloc_unlocked"]:
            if st.button("在黑暗中呼喊『Mrglgrlgrl!』🔓  (點我解鎖神祕角色)"):
                st.session_state["murloc_unlocked"] = True
                st.success("魚人學弟從水裡跳了出來！🫧")
        else:
            st.info("魚人學弟已加入隊伍 🐟")

    # ---------- 角色圖示與觸發對話 ----------
    # 新增大按鈕
    if st.button("🧠 召喚你的論文夥伴們（點我！）", use_container_width=True):
        st.session_state["show_characters"] = True

    character_map = {
        "orc": {
            "name": "半獸魚學長",
            "image": "doc/半獸人學長2.png",
            "state_key": "orc_output",
            "function": lambda _, text, user_instruction: student_agent().summarize_and_questions(paper_text=text, user_query=user_instruction),
        },
        "undead": {
            "name": "💀 可怕的指導教授",
            "image": "doc/可怕的老師卡德加.png",
            "state_key": "undead_output",
            "function": lambda _, text, user_instruction: professor_agent().critique(student_output=text, user_query=user_instruction),
        },
        "jaina": {
            "name": "🧙‍♀️ 珍娜法師學姊",
            "image": "doc/珍娜.png",
            "state_key": "jaina_output",
            "function": lambda _, text, user_instruction: master_agent().review(*text, user_instruction),
        },
        "architect": {
            "name": "瘋狂畫家",
            "image": "doc/architect.png",
            "state_key": "architect_output",
            "function": lambda _, text, __: architect_agent().generate_diagram(text),
        }
    }
    if st.session_state["murloc_unlocked"]:
        character_map["murloc"] = {
            "name": "魚人學弟",
            "image": "doc/就是隻魚人.png",
            "state_key": "murloc_output",
        }

    for key in character_map:
        if character_map[key]["state_key"] not in st.session_state:
            st.session_state[character_map[key]["state_key"]] = ""

    # 只在 show_characters 為 True 時顯示角色
    if st.session_state.get("show_characters", False):
        st.markdown("## 🧙‍♂️ 召喚你的論文夥伴們")
        
        cols = st.columns(5)
        for i, (key, char) in enumerate(character_map.items()):
            with cols[i]:
                st.image(char["image"])
                if st.button(f"與 {char['name']} 對話", key=key):
                    with st.spinner(f"{char['name']} 正在思考..."):
                        llm = OpenAILLM(model="gpt-3.5-turbo")

                        if key == "orc":
                            input_text = selected_section_text
                            response = char["function"](llm, input_text, user_instruction)
                        elif key == "undead":
                            prev = st.session_state["orc_output"]
                            if not prev:
                                st.warning("請先呼叫半獸人學長")
                                continue
                            response = char["function"](llm, prev, user_instruction)
                        elif key == "murloc":
                            # 固定台詞與音效
                            st.session_state[char["state_key"]] = "@#/!@$%^&%^*%$&tfsgwe"
                            st.subheader("@#/!@$%^&%^*%$&tfsgwe！")
                            selected_audio = random.choice(murloc_audio_files)
                            st.audio(selected_audio)
                            continue
                        elif key == "jaina":
                            if not st.session_state["orc_output"] or not st.session_state["undead_output"]:
                                st.warning("你和教授談過了嗎？沒有的話就快去！")
                                continue
                            full_text = selected_section_text
                            # 讀 Orc 和 Khadgar
                            response = char["function"](llm, (st.session_state["orc_output"], st.session_state["undead_output"], full_text), user_instruction)
                        elif key == "architect":
                            input_text = selected_section_text
                            response = char["function"](llm, input_text, user_instruction)
                            st.markdown("### 📊 Mermaid 原始語法")
                            st.code(response, language="mermaid")
                            st.markdown("[開啟 Mermaid 編輯器](https://mermaid.live/edit)（功能尚未完成：請自行貼上圖表）")
                            # render_mermaid_and_save(response)

                        else:
                            response = ""

                        st.session_state[char["state_key"]] = response
                        if key != "murloc" and key != "architect":
                            st.subheader(f"{char['name']} 的回應")
                            st.markdown(response)
        st.markdown("## 💬 角色回應區")
        for key, char in character_map.items():
            output = st.session_state.get(char["state_key"], "")
            if output:
                if char['name'] == "魚人學弟":
                    if st.session_state.get("murloc_unlocked", False):
                        st.subheader("魚人學弟的回應 (請聆聽音效)")
                elif char['name'] == "瘋狂畫家":
                    st.markdown(f"### 🎨 瘋狂畫家的作畫")
                    st.markdown("```mermaid\n" + output + "\n```")
                else:
                    st.markdown(f"**{char['name']} 的回應：**")
                    st.markdown(output)
   
else:
    st.info("請先上傳 PDF 並描述你的目的，Chaotic 小隊會和你一起想方法～")
