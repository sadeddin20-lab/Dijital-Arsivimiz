import streamlit as st
import os
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Düğün Fotoğraf Havuzu",
    page_icon="📸",
    layout="centered"
)

# --- KLASÖR AYARLARI ---
# Yüklenen fotoğrafların birikeceği klasör
UPLOAD_DIR = "dugun_fotograflari_havuzu"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- KULLANICI ARAYÜZÜ (GİRİŞ VE METİNLER) ---
st.title("📸 Hoş geldiniz!")

st.markdown("""
### **Bu gecenin fotoğrafçısı biraz da sizsiniz.** 😄

Yakaladığınız en güzel, en komik ve en özel anları buraya yükleyin.

**Teşekkürler ❤️**
""")

st.write("---")

# --- FOTOĞRAF YÜKLEME ALANI ---
uploaded_files = st.file_uploader(
    "Fotoğraflarınızı seçin veya buraya sürükleyin:",
    type=["jpg", "jpeg", "png", "heic"],
    accept_multiple_files=True
)

if uploaded_files:
    success_count = 0
    for uploaded_file in uploaded_files:
        # İsim çakışmasını önlemek için zaman damgası ekliyoruz reisim
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Dosyayı sunucuya/bilgisayara kaydetme
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        success_count += 1
    
    st.success(f"🎉 Harika! {success_count} adet anı başarıyla havuza eklendi. Katkınız için teşekkür ederiz!")

# --- ARKA PLAN TASARIMI (OPSİYONEL - ŞIK GÖRÜNÜM) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    h1, h3 {
        text-align: center;
    }
    div.stFileUploader {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)
