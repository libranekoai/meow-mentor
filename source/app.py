import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# 1. SETUP API KEY
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    client = None

# 2. SETUP KONFIGURASI HALAMAN
st.set_page_config(page_title="Meow Mentor | Your AI Agent to Rescuing Stray Cats", page_icon="🐾", layout="centered")

def reset_chat():
    st.session_state.messages = []
    st.session_state.trigger_prompt = None

# 3. SETUP MEMORI SEMBANG
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trigger_prompt" not in st.session_state:
    st.session_state.trigger_prompt = None

# ============================================================
# SVG MASCOT — kucing illustration comel (bukan emoji)
# ============================================================

CAT_HERO_SVG = """
<svg width="130" height="130" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <path d="M34 46 Q28 20 46 34 Q40 40 40 50 Z" fill="#FF8C5A"/>
  <path d="M86 46 Q92 20 74 34 Q80 40 80 50 Z" fill="#FF8C5A"/>
  <path d="M38 44 Q35 28 46 36 Q42 40 42 47 Z" fill="#FFC5A3"/>
  <path d="M82 44 Q85 28 74 36 Q78 40 78 47 Z" fill="#FFC5A3"/>
  <circle cx="60" cy="66" r="34" fill="#FF9D6C"/>
  <ellipse cx="60" cy="72" rx="24" ry="20" fill="#FFF6EE"/>
  <circle cx="48" cy="64" r="6" fill="#4A4A68"/>
  <circle cx="72" cy="64" r="6" fill="#4A4A68"/>
  <circle cx="50" cy="62" r="1.8" fill="#FFF"/>
  <circle cx="74" cy="62" r="1.8" fill="#FFF"/>
  <ellipse cx="41" cy="74" rx="5" ry="3.2" fill="#FFB6A8" opacity="0.7"/>
  <ellipse cx="79" cy="74" rx="5" ry="3.2" fill="#FFB6A8" opacity="0.7"/>
  <path d="M55 74 Q60 78 65 74" stroke="#4A4A68" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  <ellipse cx="60" cy="70" rx="2.6" ry="2" fill="#FF6B6B"/>
</svg>
"""

CAT_STABLE_SVG = """
<svg width="46" height="46" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <path d="M38 46 Q33 26 48 36 Q43 41 43 48 Z" fill="#5EC9B3"/>
  <path d="M82 46 Q87 26 72 36 Q77 41 77 48 Z" fill="#5EC9B3"/>
  <circle cx="60" cy="66" r="32" fill="#7ED9C7"/>
  <ellipse cx="60" cy="72" rx="22" ry="18" fill="#F0FDF9"/>
  <path d="M46 64 Q50 59 54 64" stroke="#2F6F63" stroke-width="2.6" fill="none" stroke-linecap="round"/>
  <path d="M66 64 Q70 59 74 64" stroke="#2F6F63" stroke-width="2.6" fill="none" stroke-linecap="round"/>
  <path d="M53 74 Q60 79 67 74" stroke="#2F6F63" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  <ellipse cx="60" cy="70" rx="2.4" ry="1.8" fill="#FF9E9E"/>
</svg>
"""

CAT_CRITICAL_SVG = """
<svg width="46" height="46" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
  <path d="M38 46 Q33 26 48 36 Q43 41 43 48 Z" fill="#FF7A7A"/>
  <path d="M82 46 Q87 26 72 36 Q77 41 77 48 Z" fill="#FF7A7A"/>
  <circle cx="60" cy="66" r="32" fill="#FF8F8F"/>
  <ellipse cx="60" cy="72" rx="22" ry="18" fill="#FFF2F2"/>
  <circle cx="49" cy="66" r="5.5" fill="#7A1F1F"/>
  <circle cx="71" cy="66" r="5.5" fill="#7A1F1F"/>
  <path d="M52 80 Q60 73 68 80" stroke="#7A1F1F" stroke-width="2.6" fill="none" stroke-linecap="round"/>
</svg>
"""

PAW_DIVIDER_SVG = """
<svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <circle cx="7" cy="8" r="2.6" fill="#FFB088"/>
  <circle cx="17" cy="8" r="2.6" fill="#FFB088"/>
  <circle cx="4" cy="14" r="2.2" fill="#FFB088"/>
  <circle cx="20" cy="14" r="2.2" fill="#FFB088"/>
  <ellipse cx="12" cy="17" rx="6" ry="4.6" fill="#FFB088"/>
</svg>
"""

# ============================================================
# CUSTOM CSS — light warm theme
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito+Sans:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito Sans', sans-serif;
    font-size: 1.1rem !important; /* Besarkan sikit tulisan biasa */
}

h1, h2, h3 {
    font-family: 'Fredoka', sans-serif !important;
    color: #E8703A !important;
}

section[data-testid="stSidebar"] {
    border-right: 2px solid #FFE0CC;
}

.stButton > button {
    background: #FF8C5A;
    color: white;
    border: none;
    border-radius: 14px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    transition: all 0.15s ease;
    box-shadow: 0 2px 0 #D9662F;
}
.stButton > button:hover {
    background: #FF9E70;
    transform: translateY(-1px);
    box-shadow: 0 3px 0 #D9662F;
    color: white;
}
.stButton > button:active {
    transform: translateY(1px);
    box-shadow: 0 1px 0 #D9662F;
}

div[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 2px dashed #FFC9A8;
    border-radius: 16px;
    padding: 0.6rem;
}

div[data-baseweb="select"] {
    border-radius: 12px !important;
}

.stChatMessage {
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #FFE7D6;
}

[data-testid="stChatInput"] {
    border-radius: 16px;
    border: 2px solid #FFD8BB;
}

.hero-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 0.2rem;
}
.hero-title {
    font-family: 'Fredoka', sans-serif;
    font-size: 3.5rem !important; /* Saiz baru yang lebih besar */
    font-weight: 700;
    color: #E8703A;
    margin: 0;
    letter-spacing: -0.5px;
    line-height: 1.1;
    text-align: center;
}
.hero-subtitle {
    color: #8A7A72;
    font-size: 1.15rem; /* Besarkan dari 0.98rem */
    margin-top: 6px;
    text-align: center;
}

.urgency-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    border-radius: 16px;
    font-family: 'Fredoka', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    margin: 10px 0;
}
.badge-stable {
    background: #E3FBF5;
    border: 2px solid #7ED9C7;
    color: #2F6F63;
}
.badge-critical {
    background: #FFEAEA;
    border: 2px solid #FF8080;
    color: #B23A3A;
}

.section-divider {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 1.2rem 0;
    opacity: 0.6;
}
.section-divider hr {
    flex: 1;
    border: none;
    border-top: 2px solid #FFE0CC;
    margin: 0;
}
            /* Responsive untuk Skrin Telefon */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.2rem !important; /* Kecilkan sikit font tajuk */
        line-height: 1.1;
    }
}
</style>
""", unsafe_allow_html=True)

# Semak kalau chat masih kosong
is_chat_empty = len(st.session_state.messages) == 0

# Kalau kosong, kita kunci scroll (overflow: hidden)
if is_chat_empty:
    st.markdown("""
        <style>
            /* Kunci scroll untuk keseluruhan badan web */
            body, .stApp {
                overflow: hidden !important;
            }
        </style>
    """, unsafe_allow_html=True)

# 4. DEFINISI TOOLS (Fungsi Sebenar Python Untuk Agen)
def cari_shelter_berdekatan(lokasi: str, bahasa: str = "Malay") -> str:
    """Mencari senarai shelter kucing berdekatan berdasarkan lokasi yang diberikan."""
    if bahasa == "English":
        return f"Mock Data: Found 2 shelters near {lokasi}: 1. Happy Paws Hub (012-3456789), 2. Stray Rescue Centre (011-9876543)."
    else:
        return f"Data Simulasi: Jumpa 2 shelter berdekatan {lokasi}: 1. Pusat Jagaan Meow (012-3456789), 2. Rumah Kucing Jalanan (011-9876543)."

def nilai_tahap_urgensi(simptom: str, bahasa: str = "Malay") -> str:
    """Menilai tahap kecemasan kucing berdasarkan simptom atau kecederaan."""
    simptom_lower = simptom.lower()
    if "darah" in simptom_lower or "bleeding" in simptom_lower or "nyawa" in simptom_lower:
        return "CRITICAL" if bahasa == "English" else "KRITIKAL (Perlu bawa ke klinik veterinar dengan segera!)"
    return "STABLE" if bahasa == "English" else "STABIL (Boleh diberi rawatan awal di rumah)"

my_tools = [cari_shelter_berdekatan, nilai_tahap_urgensi]

# 5. SYSTEM INSTRUCTION (Ejen Tegas & Sensitif Bahasa Pasar)
system_instruction = (
    "You are Meow-Mentor, an expert, calm, and empathetic stray cat rescue mentor. "
    "Your goal is to guide kind-hearted rescuers step-by-step through cat rescue situations. "

    "CRITICAL TOOL USAGE REGULATION:\n"
    "1. Whenever the user mentions ANY location, state, or city (e.g., 'Shah Alam', 'KL', 'Kuala Lumpur', 'area sini'), "
    "you MUST IMMEDIATELY execute the 'cari_shelter_berdekatan' tool. Do not ask for confirmation.\n"
    "2. Whenever the user mentions any symptoms, injury, sickness, or words like 'sakit', 'darah', 'lemah', 'cedera', "
    "you MUST IMMEDIATELY execute the 'nilai_tahap_urgensi' tool to analyze the situation first.\n"

    "LANGUAGE CHOICE:\n"
    "Always look at the language preference. If the user chooses Malay, you MUST respond in natural, "
    "colloquial Malay (Malaysia) using 'saya' for yourself and 'awak' for the user. If English, match in English."
)

# 6. SIDEBAR & PILIHAN BAHASA
with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;">{PAW_DIVIDER_SVG}'
        f'<span style="font-family:Fredoka,sans-serif;font-weight:600;font-size:1.15rem;color:#E8703A;">Meow-Mentor Settings</span></div>',
        unsafe_allow_html=True
    )
    st.write("")
    lang_choice = st.radio(
        "Select Language / Pilih Bahasa:",
        ("English", "Bahasa Melayu"),
        on_change=reset_chat
    )

    st.divider()
    if st.button("🗑️ Clear Chat / Padam Mesej"):
        st.session_state.messages = []
        st.session_state.trigger_prompt = None
        st.rerun()
    
    # TAMBAH KOD ABOUT DI SINI (Pastikan indentasi sejajar dengan 'if st.button')
    st.write("") # Jarakkan sikit
    with st.expander("ℹ️ About Meow Mentor"):
        st.markdown("""
        **Meow-Mentor** is an AI agent designed to guide everyday people through stray cat emergencies.
        
        🛠️ **Tech:** Powered by Google Gemini 2.5 Flash & Streamlit with custom Agentic AI logic.
        
        🏆 **Built for:** HackTheKitty 2026.
        
        ⚠️ **Disclaimer:** This AI provides initial guidance only. Always consult a real veterinarian for medical emergencies.
        
        ---
        <div style="text-align: center; font-size: 0.8rem; color: #8A7A72;">
            &copy; 2026 Meow Mentor. All rights reserved.
        </div>
        """, unsafe_allow_html=True)

# 7. PENYEDIAAN MICROCOPY (DWI-BAHASA)
if lang_choice == "English":
    title_text = "MEOW MENTOR"
    subtitle_text = "Your AI Agent guide to rescuing stray cats. Intelligent, responsive, and action-ready!"
    text_label = "What is the cat's current situation?"
    text_upload = "📷 Upload a photo of the cat (Optional):"
    text_btn_label = "🚨 Confirm Situation"
    text_placeholder = "Ask Meow-Mentor anything or report a location/symptom..."
    text_typing = "Meow-Mentor Agent is analyzing..."
    label_stable = "STABLE — can be given basic care at home"
    label_critical = "CRITICAL — needs a vet immediately!"
    options_cat = [
        "-- Choose a quick situation --",
        "Found an abandoned newborn kitten",
        "Cat is injured or bleeding",
        "Cat is trapped and scared",
        "Cat looks sick and lethargic"
    ]
else:
    title_text = "MEOW MENTOR"
    subtitle_text = "Agen AI bimbingan anda untuk menyelamatkan kucing jalanan. Bijak, responsif, dan sedia membantu!"
    text_label = "Apakah situasi kucing itu sekarang?"
    text_upload = "📷 Muat naik gambar kucing (Jika perlu):"
    text_btn_label = "🚨 Sahkan Situasi"
    text_placeholder = "Tanya Meow-Mentor apa sahaja berkaitan seperti lokasi atau keadaan kucing"
    text_typing = "Agen Meow-Mentor sedang menganalisis..."
    label_stable = "STABIL — boleh diberi rawatan awal di rumah"
    label_critical = "KRITIKAL — perlu bawa ke klinik veterinar segera!"
    options_cat = [
        "-- Pilihan situasi segera--",
        "Jumpa anak kucing baru lahir ditinggalkan",
        "Kucing cedera atau berdarah",
        "Kucing tersekat dan ketakutan",
        "Kucing nampak sakit dan lemah"
    ]

# PAPARAN UTAMA ANTARAMUKA
st.markdown(
   f'<div class="hero-wrap" style="display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 15px;">{CAT_HERO_SVG}'
    f'<div><p class="hero-title">{title_text}</p>'
    f'<p class="hero-subtitle">{subtitle_text}</p></div></div>',
    unsafe_allow_html=True
)
st.write("")

# INTERFAS SITUASI & GAMBAR
selected_situation = st.selectbox(text_label, options=options_cat)

# Tambah divider kecil "AND / OR" supaya user tahu dorang ada pilihan
st.markdown("<div style='text-align: center; margin: -5px 0 15px 0; color: #8A7A72; font-size: 0.9rem; font-weight: 600;'>— AND / OR —</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(text_upload, type=["jpg", "jpeg", "png"])

# KITA DECLARE file_id KAT SINI (Ini yang tertinggal)
file_id = None

if uploaded_file:
    image_preview = Image.open(uploaded_file)
    st.image(image_preview, caption="Cat Photo Preview", width=250)
    
    # TAMBAH BALIK BARIS NI
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"

# LOGIK 1 BUTANG PINTAR (Unified Button)
has_situation = selected_situation and selected_situation != options_cat[0]
has_photo = uploaded_file is not None

if "last_processed_file" not in st.session_state:
    st.session_state.last_processed_file = None

# Butang hanya akan muncul jika user ada pilih situasi ATAU upload gambar
if has_situation or has_photo:
    btn_label = "🚨 Analyze Situation & Photo" if lang_choice == "English" else "🚨 Analisa Situasi & Gambar"
    
    if st.button(btn_label):
        # 1. Kalau user bagi dua-dua (Teks + Gambar)
        if has_photo and has_situation:
            if lang_choice == "English":
                st.session_state.trigger_prompt = f"I found a cat. Situation: {selected_situation}. I also uploaded a photo. Please analyze the photo and situation, then guide me."
            else:
                st.session_state.trigger_prompt = f"Saya terjumpa kucing. Situasi: {selected_situation}. Saya juga muat naik gambar. Tolong analisa kedua-duanya dan bimbing saya."
        
        # 2. Kalau user cuma bagi gambar
        elif has_photo:
            if lang_choice == "English":
                st.session_state.trigger_prompt = "I uploaded a photo of a cat. Please analyze it and guide me."
            else:
                st.session_state.trigger_prompt = "Saya muat naik gambar kucing tersebut. Tolong analisa situasi ini dan bimbing saya."
        
        # 3. Kalau user cuma pilih situasi (Teks)
        elif has_situation:
            if lang_choice == "English":
                st.session_state.trigger_prompt = f"I found a cat. Situation: {selected_situation}. Please guide me and evaluate this."
            else:
                st.session_state.trigger_prompt = f"Saya terjumpa kucing. Situasi: {selected_situation}. Tolong bimbing saya dan buat penilaian."

        if has_photo:
            st.session_state.last_processed_file = f"{uploaded_file.name}_{uploaded_file.size}"
            
        st.rerun()

st.markdown(
    f'<div class="section-divider">{PAW_DIVIDER_SVG}<hr></div>',
    unsafe_allow_html=True
)

# Paparkan sejarah sembang, dengan urgency badge visual bila relevan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        text = message["text"]
        if message["role"] == "assistant" and ("KRITIKAL" in text or "CRITICAL" in text):
            st.markdown(
                f'<div class="urgency-badge badge-critical">{CAT_CRITICAL_SVG}<span>{label_critical}</span></div>',
                unsafe_allow_html=True
            )
        elif message["role"] == "assistant" and ("STABIL" in text or "STABLE" in text):
            st.markdown(
                f'<div class="urgency-badge badge-stable">{CAT_STABLE_SVG}<span>{label_stable}</span></div>',
                unsafe_allow_html=True
            )
        st.write(text)

# 8. PROSES INPUT
user_query = st.chat_input(text_placeholder)
final_query = None

if user_query:
    final_query = user_query
elif st.session_state.trigger_prompt:
    final_query = st.session_state.trigger_prompt
    st.session_state.trigger_prompt = None

# 9. PROSES AGENTIC HANTAR KE GEMINI
if final_query:
    st.session_state.messages.append({"role": "user", "text": final_query})
    with st.chat_message("user"):
        st.write(final_query)

    if client:
        try:
            with st.chat_message("assistant"):
                with st.spinner(text_typing):

                    formatted_contents = []

                    for msg in st.session_state.messages:
                        role_name = "model" if msg["role"] == "assistant" else "user"

                        if msg["role"] == "user" and msg["text"] == final_query and uploaded_file is not None:
                            formatted_contents.append(
                                types.Content(
                                    role=role_name,
                                    parts=[types.Part.from_text(text=msg["text"]), types.Part.from_bytes(data=uploaded_file.getvalue(), mime_type=uploaded_file.type)]
                                )
                            )
                        else:
                            formatted_contents.append(
                                types.Content(
                                    role=role_name,
                                    parts=[types.Part.from_text(text=msg["text"])]
                                )
                            )

                    config = types.GenerateContentConfig(
                        tools=my_tools,
                        system_instruction=system_instruction + f"\n\nCURRENT LANGUAGE PREFERENCE: {lang_choice}. You must reply using this language choice.",
                        temperature=0.7,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                    )

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=formatted_contents,
                        config=config
                    )

                    if response.function_calls:
                        formatted_contents.append(response.candidates[0].content)

                        function_response_parts = []
                        for function_call in response.function_calls:
                            name = function_call.name
                            args = dict(function_call.args)
                            args['bahasa'] = lang_choice

                            try:
                                if name == "cari_shelter_berdekatan":
                                    tool_result = cari_shelter_berdekatan(**args)
                                elif name == "nilai_tahap_urgensi":
                                    tool_result = nilai_tahap_urgensi(**args)
                                else:
                                    tool_result = "Function not found."
                            except Exception as e:
                                tool_result = f"Error executing tool: {e}"

                            function_response_parts.append(
                                types.Part.from_function_response(name=name, response={"result": tool_result})
                            )

                        formatted_contents.append(types.Content(role="user", parts=function_response_parts))

                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=formatted_contents,
                            config=config
                        )

                    result_text = response.text

                    if "KRITIKAL" in result_text or "CRITICAL" in result_text:
                        st.markdown(
                            f'<div class="urgency-badge badge-critical">{CAT_CRITICAL_SVG}<span>{label_critical}</span></div>',
                            unsafe_allow_html=True
                        )
                    elif "STABIL" in result_text or "STABLE" in result_text:
                        st.markdown(
                            f'<div class="urgency-badge badge-stable">{CAT_STABLE_SVG}<span>{label_stable}</span></div>',
                            unsafe_allow_html=True
                        )

                    if lang_choice == "English":
                        st.markdown(f"**Here's what I recommend:**\n\n{result_text}")
                    else:
                        st.markdown(f"**Ini cadangan saya:**\n\n{result_text}")

                    st.session_state.messages.append({"role": "assistant", "text": result_text})
                    st.session_state.last_processed_file = file_id if uploaded_file else None

        except Exception as e:
            st.error(f"Something went wrong: {e}")
    else:
        st.error("AI Offline. Sila semak API Key.")
