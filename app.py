import streamlit as st
from openai import OpenAI
import google.generativeai as genai
import requests
import os

# Sayfa Genişlik ve Tema Ayarları
st.set_page_config(page_title="AI SaaS Studio", page_icon="🚀", layout="wide")

# Oturum Durumlarını (Session State) Başlatma
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "api_keys" not in st.session_state:
    st.session_state.api_keys = {"openai": "", "gemini": "", "elevenlabs": ""}

# --- GİRİŞ EKRANI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>⚡ AI İçerik Fabrikası SaaS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>İçerik üretim süreçlerinizi bulutta otomatikleştirin.</p>", unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.info("SaaS demosu için Google ile Giriş Yap butonuna tıklayın.")
        # Gerçek OAuth entegrasyonu için Render paneli yerine buton simülasyonu yapıyoruz
        if st.button("🔴 Google ile Giriş Yap", type="primary"):
            st.session_state.logged_in = True
            st.session_state.user_email = "kullanici@gmail.com"
            st.rerun()
    st.stop()

# --- PANEL EKRANI (Giriş Yapıldıktan Sonra) ---

# Üst Bar / Navigasyon
top_col1, top_col2 = st.columns([8, 2])
with top_col1:
    st.title("🎛️ AI İçerik Yönetim Paneli")
with top_col2:
    st.write(f"👤 `{st.session_state.user_email}`")
    if st.button("Çıkış Yap", key="logout_btn"):
        st.session_state.logged_in = False
        st.rerun()

# Sekmeli (Tab) Menü Yapısı
tab_dashboard, tab_providers = st.tabs(["🤖 İçerik Üretim Merkezi", "⚙️ API Sağlayıcıları / Ayarlar"])

# ==========================================
# 1. SEKME: API SAĞLAYICILARI (AYARLAR)
# ==========================================
with tab_providers:
    st.subheader("🔑 Kendi Anahtarını Getir (BYOK)")
    st.write("Uygulamayı kullanabilmek için kullanmak istediğiniz yapay zeka modellerinin API anahtarlarını girin. Anahtarlarınız sunucuda saklanmaz, tarayıcı oturumunuzda güvende tutulur.")
    
    col_key1, col_key2 = st.columns(2)
    
    with col_key1:
        st.session_state.api_keys["openai"] = st.text_input(
            "OpenAI API Key (GPT-4o ve DALL-E için):",
            value=st.session_state.api_keys["openai"],
            type="password",
            placeholder="sk-..."
        )
        st.session_state.api_keys["gemini"] = st.text_input(
            "Google Gemini API Key (Ücretsiz Metin Alternatifi):",
            value=st.session_state.api_keys["gemini"],
            type="password",
            placeholder="AIzaSy..."
        )
        
    with col_key2:
        st.session_state.api_keys["elevenlabs"] = st.text_input(
            "ElevenLabs API Key (Seslendirme İçin):",
            value=st.session_state.api_keys["elevenlabs"],
            type="password",
            placeholder="Girmek zorunlu değildir..."
        )
    
    st.success("🔒 Değişiklikler tarayıcı oturumunuza güvenli bir şekilde uygulandı.")

# ==========================================
# 2. SEKME: İÇERİK ÜRETİM MERKEZİ
# ==========================================
with tab_dashboard:
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        st.markdown("### 📝 İçerik Parametreleri")
        topic = st.text_input("İçerik Konusu:", placeholder="Örn: Sağlıklı Yaşam ve Egzersiz")
        platform = st.selectbox("Format / Platform:", ["Shorts / Reels Videosu", "Detaylı YouTube Senaryosu", "Blog Yazısı"])
        
        # Dinamik Model Seçimi (Kullanıcının girdiği anahtarlara göre)
        available_models = []
        if st.session_state.api_keys["openai"]: available_models.append("OpenAI (GPT-4o-mini)")
        if st.session_state.api_keys["gemini"]: available_models.append("Google Gemini (1.5-Flash)")
        
        if not available_models:
            st.warning("⚠️ Lütfen içerik üretebilmek için önce 'API Sağlayıcıları' sekmesinden en az bir anahtar tanımlayın.")
            selected_model = None
        else:
            selected_model = st.selectbox("Kullanılacak Yapay Zeka Motoru:", available_models)
            
        style = st.selectbox("Görsel Tasarım Stili (DALL-E 3):", ["Fotoğraf Gerçekçi", "Cyberpunk Art", "Vektörel Çizim"])
        
        # TETİKLEYİCİ BUTON
        run_button = st.button("Uçtan Uca İçeriği İnşa Et 🚀", disabled=(selected_model is None))

    with col_output:
        st.markdown("### 🎬 Üretilen Dijital Varlıklar")
        
        if run_button and topic:
            with st.spinner("Yapay zeka motorları çalışıyor..."):
                script_text = ""
                image_url = None
                audio_data = None
                
                # --- METİN ÜRETİM ADIMI ---
                prompt = f"{topic} konusu hakkında, {platform} formatına uygun, ilgi çekici bir içerik metni üret."
                
                try:
                    if "OpenAI" in selected_model:
                        ai_client = OpenAI(api_key=st.session_state.api_keys["openai"])
                        response = ai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        script_text = response.choices[0].message.content
                    elif "Gemini" in selected_model:
                        genai.configure(api_key=st.session_state.api_keys["gemini"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(prompt)
                        script_text = response.text
                        
                    st.write("**📝 Metin / Senaryo:**")
                    st.info(script_text)
                    
                except Exception as e:
                    st.error(f"Metin üretilirken hata oluştu: {str(e)}")

                # --- GÖRSEL ÜRETİM ADIMI (OpenAI Key Varsa) ---
                if st.session_state.api_keys["openai"]:
                    try:
                        ai_client = OpenAI(api_key=st.session_state.api_keys["openai"])
                        img_res = ai_client.images.generate(
                            model="dall-e-3",
                            prompt=f"{topic}, {style}, professional content background, high quality.",
                            n=1, size="1024x1024"
                        )
                        image_url = img_res.data[0].url
                        st.image(image_url, caption="Üretilen AI Kapak Görseli")
                    except Exception as e:
                        st.caption("Görsel üretimi atlandı veya hata oluştu (DALL-E limitleri/bakiye sorunu).")

                # --- SES ÜRETİM ADIMI (ElevenLabs Key Varsa) ---
                if st.session_state.api_keys["elevenlabs"] and script_text:
                    try:
                        el_url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
                        headers = {"xi-api-key": st.session_state.api_keys["elevenlabs"], "Content-Type": "application/json"}
                        data = {"text": script_text[:500], "model_id": "eleven_multilingual_v2"}
                        el_res = requests.post(el_url, json=data, headers=headers)
                        if el_res.status_code == 200:
                            st.audio(el_res.content, format="audio/mp3")
                    except:
                        st.caption("Seslendirme oluşturulamadı.")
        else:
            st.write("Sol taraftan parametreleri girip butona bastığınızda sonuçlar burada listelenir.")
