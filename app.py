import streamlit as st
import json
import os

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
st.set_page_config(page_title="溫習 Quiz", page_icon="📝")

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
    st.balloons() # 放氣球特效
    st.success(f"測驗結束！")
    
    final_score = st.session_state.score
    total_q = len(quiz_data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("總分", f"{final_score} / {total_q}")
    col2.metric("準確率", f"{int((final_score/total_q)*100)}%")
    
    if st.button("再做一次"):
        # 重置所有變數
        st.session_state.current_q_index = 0
        st.session_state.score = 0
        st.session_state.quiz_finished = False
        st.session_state.answer_submitted = False
        st.rerun()

# 如果測驗還沒結束，顯示題目
else:
    question_data = quiz_data[st.session_state.current_q_index]
    
    st.subheader(f"Q{st.session_state.current_q_index + 1}: {question_data['question']}")
    
    # 如果還沒回答，顯示表單
    if not st.session_state.answer_submitted:
        with st.form(key='quiz_form'):
            user_choice = st.radio("請選擇答案：", question_data['options'], index=None)
            submit_btn = st.form_submit_button("提交答案")
            
            if submit_btn:
                if user_choice is None:
                    st.warning("請先選擇一個答案！")
                else:
                    st.session_state.answer_submitted = True
                    st.session_state.user_choice = user_choice
                    # 計算分數
                    if user_choice == question_data['answer']:
                        st.session_state.score += 1
                    st.rerun()
    
    # 如果已經回答，顯示結果和下一題按鈕
    else:
        # 顯示剛才的選擇 (禁用狀態)
        st.radio("請選擇答案：", question_data['options'], index=question_data['options'].index(st.session_state.user_choice), disabled=True)
        
        if st.session_state.user_choice == question_data['answer']:
            st.success("✅ 答對了！")
            # 這裡移除了原本的圖片代碼
        else:
            st.error(f"❌ 答錯了！")
            st.markdown(f"**正確答案是：** `{question_data['answer']}`")
        
        # 顯示解釋
        st.info(f"💡 解析：{question_data['explanation']}")
        
        st.write("---")
        if st.button("下一題 / 查看結果"):
            st.session_state.answer_submitted = False
            if st.session_state.current_q_index + 1 < len(quiz_data):
                st.session_state.current_q_index += 1
            else:
                st.session_state.quiz_finished = True
            st.rerun()

# 頁尾
st.divider()
st.text("Created with Streamlit & NotebookLM")
