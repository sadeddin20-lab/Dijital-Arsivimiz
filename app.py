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
st.set_page_config(
    page_title="Düğün Fotoğraf Havuzu / Pool de Fotos Boda",
    page_icon="📸",
    layout="centered"
)

# --- GOOGLE DRIVE BAĞLANTI AYARLARI ---
DRIVE_FOLDER_ID = "1fI3VtB34YJnmeJXvVAlY5bcj4pdtc137"

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
        st.error(f"Google Drive kimlik doğrulama hatası: {e}")
        return None

def upload_to_drive(file_path, file_name):
    service = get_drive_service()
    if service:
        try:
            file_metadata = {
                'name': file_name,
                'parents': [DRIVE_FOLDER_ID]
            }
            media = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return file.get('id')
        except Exception as e:
            st.error(f"Google Drive'a dosya yazma hatası! Detay: {e}")
            return None
    return None

def delete_from_drive(file_name):
    service = get_drive_service()
    if service:
        try:
            query = f"'{DRIVE_FOLDER_ID}' in parents and name = '{file_name}' and trashed = false"
            results = service.files().list(q=query, fields="files(id, name)").execute()
            items = results.get('files', [])
            
            if items:
                for item in items:
                    service.files().delete(fileId=item['id']).execute()
                return True
        except Exception as e:
            st.error(f"Google Drive'dan silme hatası: {e}")
    return False

# --- ÖZEL ARKA PLAN VE MESAFELİ BUTON TASARIMI ---
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
    return data

BACKGROUND_IMAGE = "arka_plan.jpg" 

if os.path.exists(BACKGROUND_IMAGE):
    bg_image_base64 = get_base64_image(BACKGROUND_IMAGE)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #FFFFFF;
        }}
        h1, h3, h2, p {{
            text-align: center;
            color: #FFFFFF;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            margin-bottom: 5px !important;
            padding-bottom: 5px !important;
        }}
        
        /* DOSYA YÜKLEYİCİ ALANI */
        .stFileUploader section {{
            background-color: transparent !important;
            border: none !important;
            padding: 0px !important;
            margin: 0px auto !important;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            max-width: 500px;
        }}
        
        .stFileUploader label {{
            display: none !important;
        }}
        
        /* 🚨 REİSİM, DİĞER YAZILARLA ARASINA BOŞLUK EKLEDİĞİMİZ UZUN BUTON 🚨 */
        .stFileUploader button {{
            background-color: #FFFFFF !important;
            border: 2px solid #000000 !important;
            padding: 14px 0px !important;
            width: 100% !important;
            max-width: 450px !important;
            border-radius: 12px !important;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.3s ease;
            order: 1 !important;
            
            /* Üstteki hoş geldiniz ve alttaki talimat yazısıyla mesafesini açtık */
            margin-top: 45px !important; /* Üstteki yazılardan aşağıya ittik */
            margin-bottom: 30px !important; /* Alttaki yazıdan yukarıya açtık */
            display: block !important;
        }}
        
        /* Butonun içindeki iri ve kalın harfler */
        .stFileUploader button p, .stFileUploader button div, .stFileUploader button span {{
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 22px !important;
            text-align: center !important;
            width: 100% !important;
        }}
        
        /* Butonun üzerine gelince parlaması */
        .stFileUploader button:hover {{
            background-color: #ff4b4b !important;
            border-color: #FFFFFF !important;
            transform: scale(1.02);
        }}
        .stFileUploader button:hover p {{
            color: #FFFFFF !important;
        }}
        
        .stFileUploader [data-testid="stFileUploadDropzone"] {{
            background-color: transparent !important;
            border: none !important;
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100% !important;
        }}
        
        .stFileUploader svg, .stFileUploader data-testid="stFileUploadDropzone" > div:dir(ltr) {{
            display: none !important;
        }}
        
        /* BUTONUN ALTINDAKİ TALİMAT YAZISI */
        .alt-talimat-yazisi {{
            color: #FFFFFF !important;
            font-weight: bold !important;
            font-size: 16px !important;
            text-align: center;
            margin-top: 5px !important; /* Butonun kendi margin değeriyle birleşerek nizamlı duracak */
            display: block;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
        }}
        
        .admin-section {{
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #ff4b4b;
            margin-top: 40px; /* Yönetici panelini de biraz aşağı kaydırıp ferahlattık */
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #121212; color: #FFFFFF; text-align: center; }
        h1, h3 { text-align: center; }
        </style>
    """, unsafe_allow_html=True)

# =======================================================
# ANA SAYFA: MISAFIR YÜKLEME ALANI (HERKESE AÇIK)
# =======================================================

# Türkçe Karşılama
st.title("📸 Hoş geldiniz!")
st.markdown("""
### **Bu gecenin fotoğrafçısı biraz da sizsiniz. 😄**
### **Yakaladığınız en güzel, en komik ve en özel anları buraya yükleyin. Teşekkürler ❤️**
""")

# Katalanca Karşılama
st.title("📸 Benvinguts!")
st.markdown("""
### **Aquesta nit, vosaltres també sou una mica els fotògrafs. 😄**
### **Pugeu aquí els moments més bonics, divertits i especials que captureu. Gràcies ❤️**
""")

uploaded_files = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png", "heic", "mp4", "mov"],
    accept_multiple_files=True,
    key=st.session_state["uploader_key"] if "uploader_key" in st.session_state else "uploader_first"
)

# Yazı butonun altında dengeli bir boşlukla duruyor
st.markdown('<p class="alt-talimat-yazisi">Fotoğraflarınızı ve Videolarınızı seçin (Maks: 4GB) / Selecciona o arrossega fotos i vídeos (Màx: 4GB)</p>', unsafe_allow_html=True)

LOCAL_DIR = "temp_local"
if not os.path.exists(LOCAL_DIR):
    os.makedirs(LOCAL_DIR)

if uploaded_files:
    success_count = 0
    for uploaded_file in uploaded_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{uploaded_file.name}"
        local_path = os.path.join(LOCAL_DIR, file_name)
        
        with open(local_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        drive_id = upload_to_drive(local_path, file_name)
        
        if drive_id:
            success_count += 1
            
    if success_count > 0:
        st.success(f"🎉 {success_count} adet anı başarıyla yüklendi! / S'han pujat {success_count} records correctament!")
        st.session_state["uploader_key"] = f"uploader_{datetime.now().strftime('%M%S')}"
        st.rerun()

st.markdown("<br><br><br><br><br><hr>", unsafe_allow_html=True)

# =======================================================
# YÖNETİCİ PANELİ (GİRİŞ VEYA SİLME ALANI)
# =======================================================
admin_password = st.text_input("Yönetici şifresini giriniz:", type="password", key="admin_pass_input")

if admin_password == "145348":
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)
    st.success("Giriş Başarılı! Yönetim Paneli Aktif.")
    st.write("---")
    st.header("👑 Medya Yönetim ve Silme Ekranı")
    
    files = os.listdir(LOCAL_DIR)
    media_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.mp4', '.mov'))]
    
    if not media_files:
        st.info("Henüz havuzda yüklenmiş bir dosya bulunmuyor.")
    else:
        st.write(f"**Havuzdaki Toplam Dosya Sayısı:** {len(media_files)}")
        st.write("---")
        
        for media_file in sorted(media_files, reverse=True):
            local_file_path = os.path.join(LOCAL_DIR, media_file)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.caption(f"📄 Dosya Adı: {media_file}")
                if media_file.lower().endswith(('.mp4', '.mov')):
                    st.video(local_file_path)
                else:
                    st.image(local_file_path, width=250)
            
            with col2:
                st.write("<br><br>", unsafe_allow_html=True)
                if st.button(f"❌ Sil", key=f"del_{media_file}"):
                    delete_from_drive(media_file)
                    if os.path.exists(local_file_path):
                        os.remove(local_file_path)
                    st.error(f"Silindi: {media_file}")
                    st.rerun()
            st.write("------------------------------------")
    st.markdown('</div>', unsafe_allow_html=True)
            
elif admin_password:
    st.error("Hatalı Şifre girdiniz!")
