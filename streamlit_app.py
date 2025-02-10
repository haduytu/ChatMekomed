import streamlit as st
from openai import OpenAI

def rfile(name_file):
    with open(name_file, "r", encoding="utf-8") as file:
        content_sys = file.read()
    return content_sys

# Hiển thị logo ở trên cùng, căn giữa
try:
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.image("logo.png", use_container_width=True)
except Exception as e:
    pass

# Tùy chỉnh nội dung tiêu đề
title_content = rfile("00.xinchao.txt")

st.markdown(
    f"""
    <h1 style="text-align: center; font-size: 24px;">{title_content}</h1>
    """,
    unsafe_allow_html=True
)

# Lấy OpenAI API key từ st.secrets.
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# Tạo OpenAI client.
client = OpenAI(api_key=openai_api_key)

#user_name = st.session_state.get("customer_name", "Bạn")

INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": f"""
    {rfile("01.system_trainning.txt")}
    
    #📌 Trong cuộc trò chuyện này, khách hàng tên là từ thông tin khách hàng nhập vào. Hãy luôn xưng hô với họ theo quy tắc trên.
    #""",
}

INITIAL_ASSISTANT_MESSAGE = {
    "role": "assistant",
    "content": rfile("02.assistant.txt"),
}

if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if prompt := st.chat_input(f"Bạn nhập nội dung cần trao đổi ở đây nhé."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )
    
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
