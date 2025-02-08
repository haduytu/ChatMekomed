import streamlit as st
import sys
import openpyxl
st.write(f"Python version: {sys.version}")
st.write(f"OpenPyXL version: {openpyxl.__version__}")
from openai import OpenAI
import pandas as pd
from datetime import datetime

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

# Đọc file danh sách khách hàng
try:
    df_kh = pd.read_excel('data/khach_hang.xlsx', engine='openpyxl')
    df_kh.columns = df_kh.columns.str.strip()
    df_kh['MaKH'] = df_kh['MaKH'].astype(str)
except Exception as e:
    st.error("Không thể đọc file danh sách khách hàng: " + str(e))
    df_kh = pd.DataFrame()

def get_customer_title(ma_kh):
    if not ma_kh or pd.isna(ma_kh):
        return "Bạn"
    
    customer = df_kh[df_kh['MaKH'] == ma_kh.strip()]
    if customer.empty:
        return "Bạn"
    
    customer = customer.iloc[0]
    ho_ten = customer['HoTen'].strip()
    gioi_tinh = customer['GioiTinh'].strip().lower()
    nam_sinh = int(customer['NamSinh'])
    
    current_year = datetime.now().year
    tuoi = current_year - nam_sinh
    ten_goi = ho_ten.split()[-1]
    
    if tuoi < 18:
        return f"Em {ten_goi}"
    if gioi_tinh == 'nam':
        danh_xung = "Bác" if tuoi >= 50 else "Anh"
    elif gioi_tinh == 'nữ':
        danh_xung = "Cô" if tuoi >= 50 else "Chị"
    else:
        danh_xung = ""
    
    return f"{danh_xung} {ten_goi}"

ma_kh_input = st.text_input("Nhập mã khách hàng của bạn:")
if ma_kh_input:
    greeting = get_customer_title(ma_kh_input)
    st.session_state["customer_name"] = greeting
    st.write(f"Xin chào {greeting}!")
else:
    st.session_state["customer_name"] = "Bạn"
    st.write("Xin chào Bạn!")

# Lấy OpenAI API key từ st.secrets.
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# Tạo OpenAI client.
client = OpenAI(api_key=openai_api_key)

INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": rfile("01.system_trainning.txt"),
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

user_name = st.session_state.get("customer_name", "Bạn")

if prompt := st.chat_input(f"{user_name} nhập nội dung cần trao đổi ở đây nhé."):
    # Lưu trữ tin nhắn của người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Tạo phản hồi từ OpenAI
    response = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
    )

    # Lấy nội dung phản hồi từ API
    response_text = response.choices[0].text.strip()

    # Hiển thị phản hồi chatbot
    with st.chat_message("assistant"):
        st.markdown(response_text)

    # Lưu phản hồi vào session
    st.session_state.messages.append({"role": "assistant", "content": response_text})

