import streamlit as st
import json
import os

# ==========================================
# 0. 頁面設定 & CSS 樣式 (必須放最前面)
# ==========================================
st.set_page_config(page_title="溫習 Quiz", page_icon="📝")

# 自訂 CSS (NotebookLM 風格)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

/* 全域設定 */
html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
    color: #202124;
    background-color: #ffffff;
}

/* 移除 Streamlit 預設 padding，讓畫面更像 App */
.block-container {
    padding-top: 2rem;
    padding-bottom: 5rem;
    max-width: 800px;
}

/* 隱藏 Radio Button 的圓圈，改成卡片式 */
div[role="radiogroup"] > label > div:first-child {
    display: none;
}

div[role="radiogroup"] > label {
    background-color: #f1f3f4;
    padding: 16px 20px;
    border-radius: 12px;
    margin-bottom: 12px;
    border: none;
    transition: background-color 0.2s;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    color: #3c4043;
    display: flex; /* 確保內容對齊 */
    width: 100%;
}

div[role="radiogroup"] > label:hover {
    background-color: #e8eaed;
}

/* 被選中的樣式 (Streamlit 內部標記) - 我們稍後用 Python 邏輯切換 View，這裡主要處理選取瞬間 */
div[role="radiogroup"] > label[data-baseweb="radio"] {
    background-color: #e8f0fe !important;
    color: #1a73e8 !important;
}

/* 題目文字 */
.question-text {
    font-size: 22px;
    font-weight: 500;
    color: #202124;
    margin-bottom: 24px;
    line-height: 1.5;
}

.question-header {
    font-size: 14px;
    color: #5f6368;
    margin-bottom: 8px;
    font-weight: 500;
}

/* 結果卡片 (HTML Render) */
.result-card {
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 12px;
    font-size: 16px;
    font-weight: 500;
}

.result-correct {
    background-color: #e6f4ea; /* NotebookLM Green */
    color: #137333;
}

.result-wrong {
    background-color: #fce8e6; /* NotebookLM Red */
    color: #c5221f;
}

.explanation-text {
    margin-top: 12px;
    font-size: 14px;
    font-weight: 400;
    color: #3c4043;
    line-height: 1.6;
}

/* 按鈕通用設定 */
.stButton button {
    border-radius: 24px !important;
    padding: 8px 24px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    border: 1px solid transparent !important;
    transition: all 0.2s;
}

/* Secondary Button (Previous / Explain) - 預設按鈕 */
button[data-testid="baseButton-secondary"] {
    background-color: transparent !important;
    color: #1a73e8 !important;
    border: 1px solid #dadce0 !important;
}

button[data-testid="baseButton-secondary"]:hover {
    background-color: #f6fafe !important;
    border-color: #1a73e8 !important;
}

/* Primary Button (Next / Finish / Restart) - 覆寫 */
button[data-testid="baseButton-primary"] {
    background-color: #1a73e8 !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}

button[data-testid="baseButton-primary"]:hover {
    background-color: #174ea6 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

/* 進度條 */
.stProgress > div > div > div > div {
    background-color: #1a73e8;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. 題目來源設定 (Sidebar)
# ==========================================
st.sidebar.header("題目設定")

# 初始化題庫 (如果沒有的話)
if 'quiz_library' not in st.session_state:
    st.session_state.quiz_library = {}

# 自動載入 quizzes/ 資料夾中的題目 (Persistent Library)
quizzes_dir = "quizzes"
if os.path.exists(quizzes_dir):
    for filename in os.listdir(quizzes_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(quizzes_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f: # 指定 utf-8 以防亂碼
                    data = json.load(f)
                    # 簡單格式檢查
                    if isinstance(data, list) and len(data) > 0 and "question" in data[0]:
                        st.session_state.quiz_library[filename] = data
            except Exception as e:
                # 這裡不特別顯示錯誤在 UI，以免干擾，僅在後端紀錄
                print(f"Error loading {filename}: {e}")

# 預設題目數據
default_quiz_json = """
[
  {
    "question": "植物進行光合作用主要的場所是哪裡？",
    "options": ["根部", "葉綠體", "花瓣", "樹幹"],
    "answer": "葉綠體",
    "explanation": "葉綠體含有葉綠素，是吸收光能並進行光合作用的主要場所。"
  },
  {
    "question": "吉伊卡哇 (Chiikawa) 最喜歡做什麼？",
    "options": ["打排球", "除草和討伐", "寫 Python", "睡覺"],
    "answer": "除草和討伐",
    "explanation": "在故事設定中，吉伊卡哇和朋友們主要透過除草和討伐怪物來賺取收入。"
  }
]
"""

# 確保預設題目在庫中
if "預設題目" not in st.session_state.quiz_library:
    try:
        st.session_state.quiz_library["預設題目"] = json.loads(default_quiz_json)
    except:
        pass

# 上傳區塊
uploaded_files = st.sidebar.file_uploader("上傳 .json 檔案 (可多選)", type=["json"], accept_multiple_files=True)

if uploaded_files:
    # 儲存按鈕
    save_btn = st.sidebar.button("📥 儲存到暫存區 (Server)")
    if save_btn:
        if not os.path.exists(quizzes_dir):
            os.makedirs(quizzes_dir)
        
        saved_count = 0
        for uploaded_file in uploaded_files:
            try:
                uploaded_file.seek(0)
                with open(os.path.join(quizzes_dir, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_count += 1
            except Exception as e:
                st.sidebar.error(f"儲存失敗 {uploaded_file.name}: {e}")
        
        if saved_count > 0:
            st.sidebar.success(f"已儲存 {saved_count} 份測驗到伺服器！")
            st.sidebar.info("注意：在 Streamlit Cloud 上，這些檔案會在重啟後消失。若要永久保存，請將檔案上傳至 GitHub。")
            st.rerun()

    for uploaded_file in uploaded_files:
        uploaded_file.seek(0) # 確保讀取位置正確
        # 使用檔名作為 key
        file_name = uploaded_file.name
        if file_name not in st.session_state.quiz_library:
            try:
                data = json.load(uploaded_file)
                # 簡單格式檢查
                if isinstance(data, list) and len(data) > 0 and "question" in data[0]:
                     st.session_state.quiz_library[file_name] = data
                else:
                    st.sidebar.warning(f"{file_name} 格式不正確，已略過。")
            except Exception as e:
                st.sidebar.error(f"讀取 {file_name} 失敗: {e}")

# 選擇目前要做的題目
if st.session_state.quiz_library:
    # 讓使用者選擇
    selected_quiz_name = st.sidebar.selectbox("選擇測驗主題", list(st.session_state.quiz_library.keys()))
    
    # 載入選中的題目
    quiz_data = st.session_state.quiz_library[selected_quiz_name]
    
    # 如果切換了題目，重置進度 (但如果是因為 rerun 導致的重跑則不重置)
    if 'current_quiz_name' not in st.session_state:
        st.session_state.current_quiz_name = selected_quiz_name
        
    if st.session_state.current_quiz_name != selected_quiz_name:
        st.session_state.current_quiz_name = selected_quiz_name
        st.session_state.current_q_index = 0
        st.session_state.score = 0
        st.session_state.quiz_finished = False
        st.session_state.answer_submitted = False
        st.rerun()

else:
    st.error("目前沒有任何題目，請上傳 JSON。")
    st.stop()
    
# 額外功能：貼上代碼 (保留作為備用)
with st.sidebar.expander("或者：直接貼上 JSON 代碼"):
    user_input = st.text_area("貼上 NotebookLM 生成的 JSON", height=100)
    if st.button("載入貼上的題目"):
        try:
            pasted_data = json.loads(user_input)
            if isinstance(pasted_data, list):
                st.session_state.quiz_library["(貼上的題目)"] = pasted_data
                st.session_state.current_quiz_name = "(貼上的題目)" # 強制切換
                st.rerun()
        except Exception as e:
             st.error(f"JSON 格式錯誤: {e}")

# 重置按鈕
if st.sidebar.button("🔄 重置目前測驗"):
    st.session_state.current_q_index = 0
    st.session_state.score = 0
    st.session_state.quiz_finished = False
    st.session_state.answer_submitted = False
    st.rerun()

# 顯示目前題庫數量
st.sidebar.markdown(f"--- \n *目前題庫中有 {len(st.session_state.quiz_library)} 份測驗*")


# ==========================================
# 2. 初始化 Session State (用來記憶變數)
# ==========================================
# 為了避免換題目時 index 超出範圍，這裡做個檢查
if 'current_q_index' in st.session_state and st.session_state.current_q_index >= len(quiz_data):
    st.session_state.current_q_index = 0
    st.session_state.score = 0
    st.session_state.quiz_finished = False

if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_finished' not in st.session_state:
    st.session_state.quiz_finished = False
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if 'user_choice' not in st.session_state:
    st.session_state.user_choice = None

# ==========================================
# 3. 介面設計
# ==========================================


# 標題
st.title("📝 輕鬆溫習 Time")
st.caption(f"目前測驗：{st.session_state.get('current_quiz_name', '預設題目')}")

# 顯示進度條
if not st.session_state.quiz_finished:
    progress = st.session_state.current_q_index / len(quiz_data)
    st.progress(progress)

# ==========================================
# 4. 主要邏輯
# ==========================================

# 如果測驗結束，顯示成績單
if st.session_state.quiz_finished:
    st.balloons() 
    
    # 成績單頁面也做簡單的美化
    st.markdown(f"""
    <div style="text-align: center; padding: 40px;">
        <h1 style="color: #1a73e8;">Quiz Complete!</h1>
        <p style="color: #5f6368;">Great job practicing.</p>
    </div>
    """, unsafe_allow_html=True)
    
    final_score = st.session_state.score
    total_q = len(quiz_data)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.metric("Total Score", f"{final_score} / {total_q}")
        st.metric("Accuracy", f"{int((final_score/total_q)*100)}%")
    
    st.write("") # Spacer
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("Start Over", key="restart_btn", type="primary"):
            st.session_state.current_q_index = 0
            st.session_state.score = 0
            st.session_state.quiz_finished = False
            st.session_state.answer_submitted = False
            st.session_state.user_choice = None
            st.rerun()

# 如果測驗還沒結束，顯示題目
else:
    question_data = quiz_data[st.session_state.current_q_index]
    
    # 題頭：進度
    st.markdown(f"""
    <div class="question-header">{st.session_state.current_q_index + 1} / {len(quiz_data)}</div>
    <div class="question-text">{question_data['question']}</div>
    """, unsafe_allow_html=True)
    
    # 邏輯：檢查是否已回答
    # 如果還沒回答 -> 顯示 Radio Button 選項
    if not st.session_state.answer_submitted:
        # 加上 A. B. C. D. 前綴 (如果原本沒有)
        display_options = []
        for i, opt in enumerate(question_data['options']):
            prefix = chr(65 + i) + ". " # A., B., ...
            display_options.append(f"{prefix}{opt}")
            
        choice = st.radio(
            "Options", 
            display_options, 
            index=None, 
            label_visibility="collapsed",
            key=f"q_{st.session_state.current_q_index}" # Unique key per question
        )
        
        # 監聽選擇，一旦選了就觸發提交
        if choice:
            # 去除前綴找回原始答案文字 (比較用)
            # 假設 user 選了 "A. 答案內容" -> 我們要比對 "答案內容"
            # 但小心如果原始選項就有 A. B. ...
            
            # 最穩的方法：透過 index
            choice_index = display_options.index(choice)
            original_choice_value = question_data['options'][choice_index]
            
            st.session_state.user_choice = original_choice_value
            st.session_state.answer_submitted = True
            
            if original_choice_value == question_data['answer']:
                st.session_state.score += 1
            st.rerun()

    # 如果已經回答 -> 顯示結果卡片 (不顯示 Radio)
    else:
        # 顯示正確/錯誤卡片
        user_val = st.session_state.user_choice
        correct_val = question_data['answer']
        explanation = question_data.get('explanation', '')
        
        is_correct = (user_val == correct_val)
        
        # 1. 如果答對：顯示綠色卡片
        if is_correct:
            st.markdown(f"""
            <div class="result-card result-correct">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span>✓</span> <strong>That's right!</strong>
                </div>
                <div class="explanation-text">{user_val}</div>
                <div class="explanation-text" style="font-style:italic;">{explanation}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # 2. 如果答錯：先顯示錯的紅色卡片，再顯示正確答案的灰色/綠色卡片? 
        # NotebookLM 通常是選錯的變紅，然後顯示正確答案。
        else:
            # 你的選擇 (紅)
            st.markdown(f"""
            <div class="result-card result-wrong">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span>✕</span> <strong>{user_val}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 正確答案 (綠/灰)
            st.markdown(f"""
            <div class="result-card" style="background-color: #f1f3f4; color: #5f6368;">
                <div style="font-size: 14px; margin-bottom: 4px;">Correct answer:</div>
                <div style="color: #202124; font-weight: 500;">{correct_val}</div>
                <div class="explanation-text">{explanation}</div>
            </div>
            """, unsafe_allow_html=True)

        # 底部按鈕區 (Next / Prev)
        st.write("")
        st.write("")
        col_prev, col_spacer, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if st.session_state.current_q_index > 0:
                if st.button("Previous"):
                    st.session_state.current_q_index -= 1
                    # 回到上一題時，狀態視為「已回答」還是「未回答」？
                    # 簡單起見，回到上一題我們會希望能重看，保留已回答狀態
                    # 但因為上一題的 user_choice 可能沒存到 (session_state.user_choice 只有一個變數)
                    # 為了簡單，我們先重置回答狀態，讓它可以重做
                    st.session_state.answer_submitted = False
                    st.session_state.user_choice = None
                    st.rerun()
                    
                    
        with col_next:
            # 最後一題顯示 "Finish"
            if st.session_state.current_q_index == len(quiz_data) - 1:
                btn_text = "Finish"
            else:
                btn_text = "Next"
                
                
            # 使用 type="primary" 來觸發 CSS 樣式
            if st.button(btn_text, key="next_btn", type="primary"):
                if st.session_state.current_q_index < len(quiz_data) - 1:
                    st.session_state.current_q_index += 1
                    st.session_state.answer_submitted = False
                    st.session_state.user_choice = None
                else:
                    st.session_state.quiz_finished = True
                st.rerun()
                st.rerun()

# 頁尾
st.divider()
st.text("Created with Streamlit & NotebookLM")
