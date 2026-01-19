import streamlit as st
import json

# ==========================================
# 1. 這裡貼上 NotebookLM 生成的 JSON 數據
# ==========================================
# 範例數據 (你可以直接把 NotebookLM 的輸出取代這裡)
quiz_json = """
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

# 將 JSON 字串轉換為 Python list
try:
    quiz_data = json.loads(quiz_json)
except json.JSONDecodeError:
    st.error("JSON 格式錯誤，請檢查 NotebookLM 的輸出是否包含多餘文字。")
    st.stop()

# ==========================================
# 2. 初始化 Session State (用來記憶變數)
# ==========================================
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
st.caption("由 NotebookLM 生成題目 x Streamlit 呈現")

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
