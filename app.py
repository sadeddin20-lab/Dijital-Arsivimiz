import streamlit as st
import os
import base64
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- AYARLAR ---
st.config.set_option("server.maxUploadSize", 4096)
st.set_page_config(page_title="Düğün Fotoğraf Havuzu", page_icon="📸", layout="centered")
DRIVE_FOLDER_ID = "1fI3VtB34YJnmeJXvVAlY5bcj4pdtc137"

# --- GOOGLE DRIVE ---
def get_drive_service():
    try:
        oauth_info = st.secrets["textkey"]
        creds = Credentials(token=None, refresh_token=oauth_info["refresh_token"], client_id=oauth_info["client_id"], client_secret=oauth_info["client_secret"], token_uri="https://oauth2.googleapis.com/token")
        if not creds.valid: creds.refresh(Request())
        return build('drive', 'v3', credentials=creds)
    except Exception: return None

def upload_to_drive(file_path, file_name):
    service = get_drive_service()
    if service:
        try:
            file_metadata = {'name': file_name, 'parents': [DRIVE_FOLDER_ID]}
            media = MediaFileUpload(file_path, chunksize=5*1024*1024, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return file.get('id')
        except Exception: return None
    return None

# --- MOBİL İÇİN KESİN NİZAM ---
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

BACKGROUND_IMAGE = "arka_plan.jpg"
if os.path.exists(BACKGROUND_IMAGE):
    bg_image_base64 = get_base64_image(BACKGROUND_IMAGE)
    st.markdown(f"""
        <style>
        /* 🚨 MOBİL TELEFON İÇİN TAM EKRAN KİLİT NİZAMI 🚨 */
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpeg;base64,{bg_image_base64}");
            background-attachment: fixed;
            background-position: center center;
            background-repeat: no-repeat;
            background-size: cover; /* Resmi enine boyuna, boşluk kalmadan yayar */
            height: 100vh;
            width: 100vw;
        }}
        
        /* Arka planı sabitleyip içindeki içeriği kaydırılabilir yapmak için */
        [data-testid="stMainBlockContainer"] {{
            background: rgba(0, 0, 0, 0.4); /* Resim okunabilsin diye hafif karartma */
            padding: 20px;
            border-radius: 15px;
        }}
        
        .stApp {{ background: transparent !important; }}
        </style>
    """, unsafe_allow_html=True)

# --- ANA SAYFA ---
st.title("📸 Hoş geldiniz!")
st.markdown("### **Fotoğrafları buraya yükleyin.**")

uploaded_files = st.file_uploader("", type=["jpg", "jpeg", "png", "heic", "mp4", "mov"], accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{uploaded_file.name}"
        local_path = os.path.join("temp_local", file_name)
        if not os.path.exists("temp_local"): os.makedirs("temp_local")
        with open(local_path, "wb") as f: f.write(uploaded_file.getbuffer())
        upload_to_drive(local_path, file_name)
    st.success("Başarıyla yüklendi!")
    st.rerun()

# --- YÖNETİCİ PANELİ ---
st.markdown("<br><hr>", unsafe_allow_html=True)
admin_password = st.text_input("Yönetici şifresi:", type="password")
if admin_password == "145348":
    st.header("👑 Medya Yönetim")
    files = os.listdir("temp_local") if os.path.exists("temp_local") else []
    for media_file in sorted([f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.mp4', '.mov'))], reverse=True):
        if st.button(f"❌ Sil: {media_file}"):
            os.remove(os.path.join("temp_local", media_file))
            st.rerun()
