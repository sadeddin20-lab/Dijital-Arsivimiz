import streamlit as st
import os
import base64
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# NOT: 4GB yükleme limiti için proje klasörünüzde ".streamlit/config.toml" oluşturup
# içine [server] maxUploadSize = 4096 yazmanız gerekmektedir.

st.set_page_config(page_title="Düğün Fotoğraf Havuzu", page_icon="📸", layout="centered")
DRIVE_FOLDER_ID = "1fI3VtB34YJnmeJXvVAlY5bcj4pdtc137"
LOCAL_TEMP_DIR = "temp_local"

def get_drive_service():
    try:
        oauth_info = st.secrets["textkey"]
        creds = Credentials(
            token=None, 
            refresh_token=oauth_info["refresh_token"], 
            client_id=oauth_info["client_id"], 
            client_secret=oauth_info["client_secret"], 
            token_uri="https://oauth2.googleapis.com/token"
        )
        if not creds.valid: 
            creds.refresh(Request())
        return build('drive', 'v3', credentials=creds)
    except Exception as e: 
        st.error(f"Drive Bağlantı Hatası: {e}")
        return None

def upload_to_drive(file_path, file_name):
    service = get_drive_service()
    if service:
        try:
            file_metadata = {'name': file_name, 'parents': [DRIVE_FOLDER_ID]}
            media = MediaFileUpload(file_path, chunksize=5*1024*1024, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return file.get('id')
        except Exception as e: 
            st.error(f"Dosya Drive'a Yüklenemedi ({file_name}): {e}")
            return None
    return None

# --- STİL VE MOBİL NİZAM ---
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
            background-size: 100% 100% !important; 
            background-position: center center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
            color: #FFFFFF;
        }}
        h1, h3, h2, p {{ text-align: center; color: #FFFFFF; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; margin-bottom: 5px !important; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important; }}
        .stFileUploader section {{ background-color: transparent !important; border: none !important; margin: 0px auto !important; width: 100% !important; }}
        .stFileUploader label {{ display: none !important; }}
        .stFileUploader button {{
            background-color: #FFFFFF !important; border: 2px solid #000000 !important;
            padding: 14px 20px !important; width: 100% !important; max-width: 450px !important; 
            border-radius: 12px !important; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.5) !important;
            margin-top: 45px !important; margin-bottom: 30px !important;
        }}
        .stFileUploader button p, .stFileUploader button span {{ color: #000000 !important; font-weight: 900 !important; font-size: 20px !important; }}
        .alt-talimat-yazisi {{ color: #FFFFFF !important; font-weight: bold !important; font-size: 14px !important; text-align: center; margin-top: 5px !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.9) !important; }}
        .admin-section {{ background-color: rgba(0, 0, 0, 0.85); padding: 20px; border-radius: 15px; border: 1px solid #ff4b4b; margin-top: 40px; }}
        </style>
    """, unsafe_allow_html=True)

# --- ANA SAYFA ---
# 🚨 BAŞTAKİ BOZUK YAZI SİLİNDİ, TERTEMİZ YAPILDI 🚨
st.markdown("""
    <div style="text-align: center; font-size: 36px; font-weight: bold; color: #C5A034; margin-top: 20px; text-shadow: 2px 2px 8px #000;">
        𝓜𝓪𝓻𝓲𝓪 ∞ 𝓒𝓪𝓷𝓫𝓮𝓻𝓴
    </div>
""", unsafe_allow_html=True)

# 🚨 BAŞLIKLAR MOBİLDE ÜST ÜSTE BİNMEMESİ İÇİN AYRILDI VE DÜZENLENDİ 🚨
st.markdown("<h1>📸 Hoş geldiniz!</h1>", unsafe_allow_html=True)
st.markdown("""
### **Bu gecenin fotoğrafçısı biraz da sizsiniz. 😄**
### **Yakaladığınız anları buraya yükleyin. Teşekkürler ❤️**
""")

st.markdown("<br>", unsafe_allow_html=True) # Araya hafif bir boşluk

st.markdown("<h1>📸 Benvinguts!</h1>", unsafe_allow_html=True)
st.markdown("""
### **Aquesta nit, vosaltres també sou els fotògrafs. 😄**
### **Pugeu aquí els vostres moments. Gràcies ❤️**
""")

if "uploader_key" not in st.session_state: 
    st.session_state["uploader_key"] = "uploader_first"

uploaded_files = st.file_uploader("", type=["jpg", "jpeg", "png", "heic", "mp4", "mov"], accept_multiple_files=True, key=st.session_state["uploader_key"])
st.markdown('<p class="alt-talimat-yazisi">Fotoğrafları/Videoları yükle / Selecciona fotos i vídeos</p>', unsafe_allow_html=True)

# --- YÜKLEME VE BAŞARI MESAJI AKIŞI ---
if uploaded_files:
    if not os.path.exists(LOCAL_TEMP_DIR): 
        os.makedirs(LOCAL_TEMP_DIR)
        
    success_count = 0
    with st.spinner('Medya yükleniyor, lütfen bekleyin... / Pujant media, si us plau espereu...'):
        for uploaded_file in uploaded_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}_{uploaded_file.name}"
            local_path = os.path.join(LOCAL_TEMP_DIR, file_name)
            
            # Yerel diske kayıt
            with open(local_path, "wb") as f: 
                f.write(uploaded_file.getbuffer())
            
            # Google Drive'a transfer
            drive_id = upload_to_drive(local_path, file_name)
            if drive_id:
                success_count += 1
        
    # Tüm medya başarıyla yüklendiyse mesaj ver ve beklet
    if success_count == len(uploaded_files):
        st.success("🎉 Başarıyla yüklendi! / Tot s'ha penjat correctament!")
        time.sleep(3)  # Misafir mesajı görsün diye 3 saniye ekran donar
    else:
        st.warning(f"⚠️ {success_count}/{len(uploaded_files)} dosya yüklenebildi.")
        time.sleep(4)
        
    # Sayfayı tazeleyerek uploader'ı sıfırla
    st.session_state["uploader_key"] = f"uploader_{datetime.now().strftime('%M%S')}"
    st.rerun()

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- YÖNETİCİ PANELİ ---
admin_password = st.text_input("Yönetici şifresi:", type="password", key="admin_pass_input")
if admin_password == "145348":
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)
    st.header("👑 Medya Yönetim")
    files = os.listdir(LOCAL_TEMP_DIR) if os.path.exists(LOCAL_TEMP_DIR) else []
    for media_file in sorted([f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.mp4', '.mov'))], reverse=True):
        local_file_path = os.path.join(LOCAL_TEMP_DIR, media_file)
        c1, c2 = st.columns([3, 1])
        with c1: st.caption(f"📄 {media_file}")
        with c2: 
            if st.button(f"❌ Sil", key=f"del_{media_file}"):
                if os.path.exists(local_file_path): 
                    os.remove(local_file_path)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
