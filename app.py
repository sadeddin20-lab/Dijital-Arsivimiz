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
# Arka plan dosyasını okuyup base64 formatına çeviren fonksiyon
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        data = base64.b64encode(image_file.read()).decode()
    return data

# Arka plan görseli dosya adını (uzantısıyla birlikte, örn: arka_plan.jpg) buraya yazın:
BACKGROUND_IMAGE = "arka_plan.jpg" # Eğer dosya adınız farklıysa burayı güncelleyin reisim

if os.path.exists(BACKGROUND_IMAGE):
    bg_image_base64 = get_base64_image(BACKGROUND_IMAGE)
    
    # CSS ile arka planı uygulayan bölüm
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bg_image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #FFFFFF; /* Metin rengi, arka plana göre değiştirilebilir */
        }}
        h1, h3 {{
            text-align: center;
            color: #FFFFFF; /* Başlık renkleri */
        }}
        /* Dosya yükleme alanını daha belirgin hale getir */
        .stFileUploader > label {{
            color: #FFFFFF;
        }}
        .stFileUploader section {{
            background-color: rgba(255, 255, 255, 0.1); /* Hafif şeffaf arka plan */
            border-radius: 10px;
            padding: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    # Eğer dosya bulunamazsa eski koyu tema kullanılır
    st.markdown("""
        <style>
        .stApp {
            background-color: #121212;
            color: #FFFFFF;
            text-align: center;
        }
        h1, h3 {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    st.warning(f"⚠️ Dikkat reisim: '{BACKGROUND_IMAGE}' dosyası bulunamadı. Lütfen dosyanın 'app.py' ile aynı klasörde olduğundan emin olun.")

# --- ÇİFT DİLLİ KARŞILAMA METNİ ---
st.title("📸 Hoş geldiniz! / Benvinguts!")

# Türkçe Bölüm
st.markdown("""
### **Bu gecenin fotoğrafçısı biraz da sizsiniz.** 😄
Yakaladığınız en güzel, en komik ve en özel anları buraya yükleyin.

**Teşekkürler ❤️**
""")

st.write("---")

# Katalanca Bölüm
st.markdown("""
### **Aquesta nit, vosaltres també sou una mica els fotògrafs.** 😄
Pugeu aquí els moments més bonics, divertits i especials que captureu.

**Gràcies ❤️**
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
        # Zaman damgası ile dosya ismini benzersiz yap
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        success_count += 1
    
    # Çift dilli başarı mesajı
    st.success(f"🎉 {success_count} adet anı başarıyla yüklendi! / S'han pujat {success_count} records correctament!")
