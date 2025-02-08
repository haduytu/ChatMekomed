import streamlit as st
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
        st.image("logo.png", use_container_width=True)  # Thay use_column_width bằng use_container_width
except Exception as e:
    pass

# Tùy chỉnh nội dung tiêu đề
title_content = rfile("00.xinchao.txt")

# Hiển thị tiêu đề với nội dung tùy chỉnh
st.markdown(
    f"""
    <h1 style="text-align: center; font-size: 24px;">{title_content}</h1>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# XỬ LÝ DANH SÁCH KHÁCH HÀNG
# -------------------------------

# Đọc file danh sách khách hàng (ví dụ: khach_hang.csv nằm cùng thư mục hoặc trong thư mục con 'data')
try:
    df_kh = pd.read_excel('data/khach_hang.xlsx')
except Exception as e:
    st.error("Không thể đọc file danh sách khách hàng: " + str(e))
    df_kh = pd.DataFrame()  # Nếu không đọc được file thì tạo DataFrame rỗng

def get_customer_title(ma_kh):
    """
    Tra cứu thông tin khách hàng theo MaKH.
    - Nếu không có MaKH hoặc không tìm thấy trong danh sách, trả về "Bạn".
    - Nếu tìm thấy, dựa vào tuổi và giới tính:
        + Nếu tuổi < 18: gọi là "Em {tên}".
        + Nếu >= 18:
            - Với khách hàng nam: gọi là "Bác {tên}" nếu từ 50 tuổi trở lên, ngược lại gọi là "Anh {tên}".
            - Với khách hàng nữ: gọi là "Cô {tên}" nếu từ 50 tuổi trở lên, ngược lại gọi là "Chị {tên}".
    """
    if not ma_kh or pd.isna(ma_kh):
        return "Bạn"
    
    customer = df_kh[df_kh['MaKH'] == ma_kh.strip()]
    if customer.empty:
        return "Bạn"
    
    customer = customer.iloc[0]
    ho_ten = customer['HoTen'].strip()
    gioi_tinh = customer['GioiTinh'].strip().lower()  # Giả sử dữ liệu chỉ có "nam" hoặc "nữ"
    nam_sinh = int(customer['NamSinh'])
    
    current_year = datetime.now().year
    tuoi = current_year - nam_sinh
    # Lấy tên gọi (ví dụ: phần tử cuối cùng của họ tên)
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

# Nhập mã khách hàng và hiển thị lời chào cá nhân hóa
ma_kh_input = st.text_input("Nhập mã khách hàng của bạn:")
if ma_kh_input:
    greeting = get_customer_title(ma_kh_input)
    st.write(f"Xin chào {greeting}!")
else:
    st.write("Xin chào Bạn!")

# -------------------------------
# PHẦN XỬ LÝ CHATBOT VỚI OPENAI
# -------------------------------

# Lấy OpenAI API key từ st.secrets.
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# Tạo OpenAI client.
client = OpenAI(api_key=openai_api_key)

# Khởi tạo lời nhắn "system" để định hình hành vi mô hình.
INITIAL_SYSTEM_MESSAGE = {
    "role": "system",
    "content": rfile("01.system_trainning.txt"),
}

# Khởi tạo lời nhắn ví dụ từ vai trò "assistant".
INITIAL_ASSISTANT_MESSAGE = {
    "role": "assistant",
    "content": rfile("02.assistant.txt"),
}

# Tạo một biến trạng thái session để lưu trữ các tin nhắn nếu chưa tồn tại.
if "messages" not in st.session_state:
    st.session_state.messages = [INITIAL_SYSTEM_MESSAGE, INITIAL_ASSISTANT_MESSAGE]

# Loại bỏ INITIAL_SYSTEM_MESSAGE khỏi giao diện hiển thị.
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Tạo ô nhập liệu cho người dùng.
if prompt := st.chat_input("Bạn nhập nội dung cần trao đổi ở đây nhé."):
    # Lưu trữ và hiển thị tin nhắn của người dùng.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Tạo phản hồi từ API OpenAI.
    stream = client.chat.completions.create(
        model=rfile("module_chatgpt.txt").strip(),
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        stream=True,
    )
    
    # Hiển thị và lưu phản hồi của trợ lý.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
