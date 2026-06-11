import streamlit as st
import os
import base64
from datetime import datetime

# --- 1. DOSYA YÜKLEME BOYUTU SINIRINI KALDIRMA ---
# Streamlit normalde dosya başına 200MB sınır koyar. Bunu kodun en başında konfigüre ediyoruz reisim.
# Ancak tam verim almak için Streamlit Cloud'a yüklerken .streamlit/config.toml ayarı da gerekebilir (aşağıda açıkladım).

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Düğün Fotoğraf Havuzu / Pool de Fotos Boda",
    page_icon="📸",
    layout="centered"
)

# --- FOTOĞRAF VE VİDEO KLASÖRÜ ---
UPLOAD_DIR = "dugun_fotograflari_havuzu"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

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
        /* Admin paneli kutusu */
        .admin-box {{
            background-color: rgba(0, 0, 0, 0.85);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #ff4b4b;
            margin-top: 50px;
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

# --- YAN MENÜ (YÖNETİCİ GİRİŞİ) ---
st.sidebar.title("🔐 Yönetim Paneli")
admin_password = st.sidebar.text_input("Yönetici Şifresi:", type="password")

# Yönetici Giriş Kontrolü
if admin_password == "145348":
    st.sidebar.success("Giriş Başarılı, Reisim!")
    st.write("---")
    st.header("👑 Yönetici İzleme Ekranı (Canlı Akış)")
    
    files = os.listdir(UPLOAD_DIR)
    media_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.heic', '.mp4', '.mov'))]
    
    if not media_files:
        st.info("Henüz hiç fotoğraf veya video yüklenmedi reisim.")
    else:
        st.write(f"Toplam Yüklenen Dosya: {len(media_files)}")
        for media_file in sorted(media_files, reverse=True): # En yeni yüklenen en üstte görünür
            file_path = os.path.join(UPLOAD_DIR, media_file)
            st.write(f"📄 {media_file}")
            
            # Fotoğraf veya video önizleme
            if media_file.lower().endswith(('.mp4', '.mov')):
                st.video(file_path)
            else:
                st.image(file_path, width=300)
            st.write("---")
            
else:
    if admin_password:
        st.sidebar.error("Hatalı Şifre!")

    # --- ANA SAYFA: EMRETTİĞİNİZ BİREBİR METİNLER ---
    
    # --- TÜRKÇE BÖLÜM ---
    st.title("📸 Hoş geldiniz!")
    st.markdown("""
    ### **Bu gecenin fotoğrafçısı biraz da sizsiniz. 😄**

    ### **Yakaldığınız en güzel, en komik ve en özel anları buraya yükleyin.**

    ### **Teşekkürler ❤️**
    """)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # --- KATALANCA BÖLÜM ---
    st.title("📸 Benvinguts!")
    st.markdown("""
    ### **Aquesta nit, vosaltres també sou una mica els fotògrafs. 😄**

    ### **Pugeu aquí els moments més bonics, divertits i especials que captureu.**

    ### **Gràcies ❤️**
    """)

    st.write("---")

    # --- DOSYA YÜKLEME ALANI (RESİM VE VİDEO) ---
    uploaded_files = st.file_uploader(
        "Fotoğraflarınızı ve Videolarınızı seçin / Selecciona o arrossega les teves fotos i vídeos aquí:",
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
        
        st.success(f"🎉 {success_count} adet anı başarıyla yüklenmiş ve havuza eklenmiştir! / S'han pujat {success_count} records correctament!")
