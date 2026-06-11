import streamlit as st
import os
import base64
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Düğün Fotoğraf Havuzu / Pool de Fotos Boda",
    page_icon="📸",
    layout="centered"
)

# --- FOTOĞRAF KLASÖRÜ ---
UPLOAD_DIR = "dugun_fotograflari_havuzu"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- ÖZEL ARKA PLAN ENTEGRASYONU ---
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
    return data

# Arka plan dosya adı (Uzantısı .jpg, .png veya .jpeg ise burayı kontrol edin reisim)
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
        h1, h3 {{
            text-align: center;
            color: #FFFFFF;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }}
        .stFileUploader section {{
            background-color: rgba(0, 0, 0, 0.6) !important; /* Yazıların okunması için hafif koyu transparan panel */
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
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
    st.warning(f"⚠️ Dikkat reisim: '{BACKGROUND_IMAGE}' dosyası bulunamadı. Lütfen dosyanın 'app.py' ile aynı klasörde olduğundan emin olun.")

# --- EMRETTİĞİNİZ BİREBİR METİNLER (EMOJİLERİYLE BİRLİKTE) ---

# --- TÜRKÇE BÖLÜM ---
st.title("📸 Hoş geldiniz!")

st.markdown("""
### **Bu gecenin fotoğrafçısı biraz da sizsiniz. 😄**

### **Yakaldığınız en güzel, en komik ve en özel anları buraya yükleyin.**

### **Teşekkürler ❤️**
""")

st.markdown("<br><hr><br>", unsafe_allow_html=True) # İki dil arasına şık bir boşluk çizgisi reisim

# --- KATALANCA BÖLÜM ---
st.title("📸 Benvinguts!")

st.markdown("""
### **Aquesta nit, vosaltres també sou una mica els fotògrafs. 😄**

### **Pugeu aquí els moments més bonics, divertits i especials que captureu.**

### **Gràcies ❤️**
""")

st.write("---")

# --- DOSYA YÜKLEME ALANI ---
uploaded_files = st.file_uploader(
    "Fotoğraflarınızı seçin veya sürükleyin / Selecciona o arrossega les teves fotos aquí:",
    type=["jpg", "jpeg", "png", "heic", "mp4", "mov"],
    accept_multiple_files=True
)

if uploaded_files:
    success_count = 0
    for uploaded_file in uploaded_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        success_count += 1
    
    st.success(f"🎉 {success_count} adet anı başarıyla yüklendi! / S'han pujat {success_count} records correctament!")
