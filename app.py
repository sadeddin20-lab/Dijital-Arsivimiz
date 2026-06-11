import streamlit as st
import os
import base64
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- 4 GB YÜKLEME LİMİTİ AYARI ---
st.config.set_option("server.maxUploadSize", 4096)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Düğün Fotoğraf Havuzu", page_icon="📸", layout="centered")

# --- GOOGLE DRIVE BAĞLANTI AYARLARI ---
DRIVE_FOLDER_ID = "1fI3VtB34YJnmeJXvVAlY5bcj4pdtc137"

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
            media = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return file.get('id')
        except Exception: return None
    return None

# --- ARKA PLAN VE STİL ---
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

BACKGROUND_IMAGE = "arka_plan.jpg" 
if os.path.exists(BACKGROUND_IMAGE):
    bg_image_base64 = get_base64_image(BACKGROUND_IMAGE)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_image_base64}");
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            color: #FFFFFF;
        }}
        h1, h3, p {{ text-align: center; color: #FFFFFF; text-shadow: 2px 2px 5px #000; }}
        .stFileUploader section {{ background-color: transparent !important; }}
        .admin-section {{ background-color: rgba(0, 0, 0, 0.8); padding: 15px; border-radius: 12px; margin-top: 20px; }}
        </style>
    """, unsafe_allow_html=True)

# --- ANA SAYFA ---
st.title("📸 Hoş geldiniz!")
st.markdown("### **Bu gecenin fotoğrafçısı sizsiniz.**")
st.markdown("### **Fotoğrafları buraya yükleyin. Teşekkürler ❤️**")

if "uploader_key" not in st.session_state: st.session_state["uploader_key"] = "uploader_first"
uploaded_files = st.file_uploader("", type=["jpg", "jpeg", "png", "heic", "mp4", "mov"], accept_multiple_files=True, key=st.session_state["uploader_key"])

LOCAL_DIR = "temp_local"
if not os.path.exists(LOCAL_DIR): os.makedirs(LOCAL_DIR)

if uploaded_files:
    for uploaded_file in uploaded_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{uploaded_file.name}"
        local_path = os.path.join(LOCAL_DIR, file_name)
        with open(local_path, "wb") as f: f.write(uploaded_file.getbuffer())
        upload_to_drive(local_path, file_name)
    st.success("Başarıyla yüklendi!")
    st.session_state["uploader_key"] = f"uploader_{datetime.now().strftime('%M%S')}"
    st.rerun()

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- YÖNETİCİ PANELİ ---
admin_password = st.text_input("Yönetici şifresi:", type="password", key="admin_pass_input")
if admin_password == "145348":
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)
    st.header("👑 Medya Yönetim")
    files = os.listdir(LOCAL_DIR)
    for media_file in sorted([f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.mp4', '.mov'))], reverse=True):
        local_file_path = os.path.join(LOCAL_DIR, media_file)
        c1, c2 = st.columns([3, 1])
        with c1: st.caption(f"📄 {media_file}")
        with c2: 
            if st.button(f"❌ Sil", key=f"del_{media_file}"):
                if os.path.exists(local_file_path): os.remove(local_file_path)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
elif admin_password: st.error("Hatalı Şifre!")
