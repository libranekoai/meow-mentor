import streamlit as str
from google import genai
from google.genai import types
from PIL import Image

# 1. SETUP API KEY
try:
    client = genai.Client(api_key=str.secrets["GEMINI_API_KEY"])
except Exception:
    client = None

# 2. SETUP KONFIGURASI HALAMAN
str.set_page_config(page_title="Meow-Mentor", page_icon="🐾", layout="centered")

# 3. SETUP MEMORI SEMBANG
if "messages" not in str.session_state:
    str.session_state.messages = []
if "trigger_prompt" not in str.session_state:
    str.session_state.trigger_prompt = None

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

# Himpunkan fungsi ke dalam list untuk dibaca oleh Gemini
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
with str.sidebar:
    str.title("🐾 Meow-Mentor Settings")
    lang_choice = str.radio("Select Language / Pilih Bahasa:", ("Malay", "English"))
    
    str.divider()
    if str.button("Clear Chat / Padam Sembang"):
        str.session_state.messages = []
        str.session_state.trigger_prompt = None
        str.rerun()

# 7. PENYEDIAAN MICROCOPY (DWI-BAHASA)
if lang_choice == "English":
    title_text = "🐾 Meow-Mentor (Agentic)"
    subtitle_text = "Your AI Agent guide to rescuing stray cats. Intelligent, responsive, and action-ready!"
    text_label = "What is the cat's current situation?"
    text_upload = "📸 Upload a photo of the cat (Optional):"
    text_btn_label = "🚨 Confirm Situation"
    text_placeholder = "Ask Meow-Mentor anything or report a location/symptom..."
    text_typing = "Meow-Mentor Agent is analyzing..."
    options_cat = [
        "-- Choose a quick situation --",
        "Found an abandoned newborn kitten",
        "Cat is injured or bleeding",
        "Cat is trapped and scared",
        "Cat looks sick and lethargic"
    ]
else:
    title_text = "🐾 Meow-Mentor (Agentic)"
    subtitle_text = "Agen AI bimbingan kecemasan anda untuk selamatkan kucing jalanan. Bijak, tangkas, dan sedia bertindak!"
    text_label = "Apa situasi kucing itu sekarang?"
    text_upload = "📸 Muat naik gambar kucing (Jika perlu):"
    text_btn_label = "🚨 Sahkan Situasi"
    text_placeholder = "Tanya Meow-Mentor, beritahu lokasi, atau aduan sakit..."
    text_typing = "Ejen Meow-Mentor sedang menganalisis..."
    options_cat = [
        "-- Pilih situasi pantas --",
        "Jumpa anak kucing baru lahir ditinggalkan",
        "Kucing cedera atau berdarah",
        "Kucing tersekat dan ketakutan",
        "Kucing nampak sakit dan lemah"
    ]

# PAPARAN UTAMA ANTARAMUKA
str.title(title_text)
str.write(subtitle_text)
str.divider()

# INTERFAS SITUASI & GAMBAR
selected_situation = str.selectbox(text_label, options=options_cat)
uploaded_file = str.file_uploader(text_upload, type=["jpg", "jpeg", "png"])

if uploaded_file:
    image_preview = Image.open(uploaded_file)
    str.image(image_preview, caption="Cat Photo Preview", width=250)

    # Track file id supaya kita tahu ni gambar BARU ke gambar LAMA yang dah pernah proses
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if "last_processed_file" not in str.session_state:
        str.session_state.last_processed_file = None

    # Bagi button khas untuk analyze gambar SAHAJA (kalau user tak taip apa-apa)
    if file_id != str.session_state.last_processed_file:
        analyze_label = "🔍 Analyze Photo" if lang_choice == "English" else "🔍 Analisa Gambar Ni"
        if str.button(analyze_label):
            if lang_choice == "English":
                str.session_state.trigger_prompt = "I uploaded a photo of a cat. Please analyze it and guide me."
            else:
                str.session_state.trigger_prompt = "Saya upload gambar kucing. Tolong analisa dan bimbing saya."
            str.session_state.last_processed_file = file_id

if selected_situation and selected_situation != options_cat[0]:
    if str.button(text_btn_label):
        if lang_choice == "English":
            str.session_state.trigger_prompt = f"I found a cat. Situation: {selected_situation}. Please guide me and evaluate this."
        else:
            str.session_state.trigger_prompt = f"Saya terjumpa kucing. Situasi: {selected_situation}. Tolong bimbing saya dan buat penilaian."

str.divider()

# Paparkan sejarah sembang
for message in str.session_state.messages:
    with str.chat_message(message["role"]):
        str.write(message["text"])

# 8. PROSES INPUT
user_query = str.chat_input(text_placeholder)
final_query = None

if user_query:
    final_query = user_query
elif str.session_state.trigger_prompt:
    final_query = str.session_state.trigger_prompt
    str.session_state.trigger_prompt = None

# 9. PROSES AGENTIC HANTAR KE GEMINI
if final_query:
    str.session_state.messages.append({"role": "user", "text": final_query})
    with str.chat_message("user"):
        str.write(final_query)

    if client:
        try:
            with str.chat_message("assistant"):
                with str.spinner(text_typing):
                    
                    # FORMAT KANDUNGAN YANG BETUL MENGGUNAKAN types.Content (Wajib untuk google-genai)
                    formatted_contents = []
                    
                    for msg in str.session_state.messages:
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
                    
                    # Konfigurasi Ejen
                    config = types.GenerateContentConfig(
                        tools=my_tools,
                        system_instruction=system_instruction + f"\n\nCURRENT LANGUAGE PREFERENCE: {lang_choice}. You must reply using this language choice.",
                        temperature=0.7,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                    )
                    
                    # Panggilan pertama
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=formatted_contents,
                        config=config
                    )

                    # Jika Ejen mahu panggil fungsi Python kita
                    if response.function_calls:
                        formatted_contents.append(response.candidates[0].content)  # append SEKALI je, di luar loop

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

                        # SATU je call kedua, bukan berulang dalam loop
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=formatted_contents,
                            config=config
                        )

                    # Paparkan hasil akhir
                    if lang_choice == "English":
                        str.markdown(f"**Here's what I recommend:**\n\n{response.text}")
                    else:
                        str.markdown(f"**Ini apa yang saya cadangkan:**\n\n{response.text}")
                    
                    str.session_state.messages.append({"role": "assistant", "text": response.text})
                    str.session_state.last_processed_file = file_id if uploaded_file else None 

        except Exception as e:
            str.error(f"Something went wrong: {e}")
    else:
        str.error("AI Offline. Sila semak API Key.")