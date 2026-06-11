import streamlit as st
import os
import base64
from datetime import datetime
from google.oauth2 import service_account
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
        # Secrets panelindeki [textkey] tablosunu doğrudan sözlük (dict) olarak okuyoruz
        creds_dict = dict(st.secrets["textkey"])
        # JSON yapısındaki ters bölü (\n) işaretlerini sistemin doğru okuması için nizamlıyoruz
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
        creds = service_account.Credentials.from_service_account_info(creds_dict)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Google Drive bağlantı hatası: {e}")
        return None

def upload_to_drive(file_path, file_name):
    service = get_drive_service()
    if service:
        try:
            file_metadata = {
                'name': file_name,
                'parents': [DRIVE_FOLDER_ID]
            }
            # Kota aşımını engellemek için parça boyutunu optimize ediyoruz
            media = MediaFileUpload(file_path, chunksize=256*1024, resumable=True)
            
            # supportsAllDrives=True ekleyerek botun kota alanını genişletiyoruz ve yetkiyi zorluyoruz
            file = service.files().create(
                body=file_metadata, 
                media_body=media, 
                fields='id',
                supportsAllDrives=True
            ).execute()
            
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
            results = service.files().list(
                q=query, 
                fields="files(id, name)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            items = results.get('files', [])
            
            if items:
                for item in items:
                    service.files().delete(fileId=item['id'], supportsAllDrives=True).execute()
                return True
        except Exception as e:
            st.error(f"Google Drive'dan silme hatası: {e}")
    return False

# --- ÖZEL ARKA PLAN ENTEGRASYONU ---
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
        }}
        .stFileUploader section {{
            background-color: rgba(0, 0, 0, 0.6) !important;
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .admin-section {{
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #ff4b4b;
            margin-top: 60px;
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

st.title("📸 Hoş geldiniz!")
st.markdown("""
### **Bu gecenin fotoğrafçısı biraz da sizsiniz. 😄**

### **Yakaldığınız en güzel, en komik ve en özel anları buraya yükleyin.**

### **Teşekkürler ❤️**
""")

st.markdown("<br><hr><br>", unsafe_allow_html=True)

st.title("📸 Benvinguts!")
st.markdown("""
### **Aquesta nit, vosaltres també sou una mica els fotògrafs. 😄**

### **Pugeu aquí els moments més bonics, divertits i especials que captureu.**

### **Gràcies ❤️**
""")

st.write("---")

uploaded_files = st.file_uploader(
    "Fotoğraflarınızı ve Videolarınızı seçin (Maks: 4GB) / Selecciona o arrossega fotos i vídeos (Màx: 4GB):",
    type=["jpg", "jpeg", "png", "heic", "mp4", "mov"],
    accept_multiple_files=True
)

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

st.markdown("<br><br><br><br><br><hr>", unsafe_allow_html=True)

# =======================================================
# YÖNETİCİ PANELİ (GİRİŞ VEYA SİLME ALANI)
# =======================================================
st.markdown('<div class="admin-section">', unsafe_allow_html=True)
st.subheader("🔐 Yönetici Girişi")
admin_password = st.text_input("Yönetici şifresini giriniz:", type="password", key="admin_pass_input")

if admin_password == "145348":
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
            
elif admin_password:
    st.error("Hatalı Şifre girdiniz!")
st.markdown('</div>', unsafe_allow_html=True)
