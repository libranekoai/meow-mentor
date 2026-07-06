# 🐾 Meow-Mentor

An AI-powered rescue mentor that guides everyday people through stray cat emergencies — step by step, in real time, in their own language.

## The Problem

When someone stumbles across a stray or injured cat, they usually don't know what to do next: Is this urgent? Should I bring it to a vet? Where's the nearest shelter? That hesitation costs time the animal may not have.

Meow-Mentor closes that gap. It's a conversational AI agent that assesses the situation and proactively finds relevant help — without the user needing to know what to ask for.

## What It Does

- **Understands free-form situations** — describe what you found in plain language (English or Malay), optionally with a photo
- **Assesses urgency automatically** — the agent detects symptoms/injury keywords and evaluates whether the cat needs immediate care
- **Finds nearby help automatically** — mentioning a location triggers a shelter/vet lookup, with no extra steps from the user
- **Fully bilingual** — responds naturally in colloquial Malaysian Malay or English, matching the user's choice
- **Runs as an agent, not a scripted flow** — the AI decides *when* to use its tools based on conversation context, not hardcoded if/else logic

## How It Works (Architecture)

Meow-Mentor is built on **Google Gemini 2.5 Flash** with **function calling (tool use)**, wrapped in a **Streamlit** interface.

```
User input (text + optional photo)
        │
        ▼
Gemini 2.5 Flash (system-instructed agent)
        │
        ├─ Detects location mention → calls cari_shelter_berdekatan()
        ├─ Detects symptom/injury mention → calls nilai_tahap_urgensi()
        │
        ▼
Tool results fed back to Gemini
        │
        ▼
Final natural-language response (bilingual)
```

### Tools (Agent Capabilities)

| Tool | Purpose |
|---|---|
| `cari_shelter_berdekatan(lokasi, bahasa)` | Looks up nearby shelters/vets for a given location |
| `nilai_tahap_urgensi(simptom, bahasa)` | Classifies a cat's condition as stable or critical based on described symptoms |

> **Note:** Tool data is currently mocked (`cari_shelter_berdekatan` returns simulated shelter listings) for demo purposes. The architecture is designed to swap in a real database/API (e.g. a Malaysian SPCA/shelter directory) without changing the agent logic.

### Key Design Decision: Manual Function-Calling Control

We explicitly **disable Gemini's Automatic Function Calling** (`automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)`) and handle tool execution manually. This was a deliberate choice, not an oversight — automatic mode resolves tool calls before our code can inject the user's selected language into the function arguments, which broke bilingual consistency during development. Manual control guarantees the `bahasa` parameter is always correctly passed through.

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** Google Gemini 2.5 Flash (via `google-genai` SDK)
- **Image handling:** Pillow (PIL)
- **Language:** Python

## Setup & Running Locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/libranekoai/meow-mentor.git
   cd meow-mentor
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. **Add your Gemini API key**

   Create a file at `.streamlit/secrets.toml` in the project root:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```
   Get a free API key at [Google AI Studio](https://aistudio.google.com/).

4. **Run the app**
   ```bash
   streamlit run source/app.py
   ```

5. Open the local URL Streamlit gives you (usually `http://localhost:8501`).

## ⚠️ Important Note: API Rate Limit

This project runs on the **Google Gemini API free tier**, which caps requests at **20 per day** for the `gemini-2.5-flash` model.

If you encounter a `429 RESOURCE_EXHAUSTED` error while testing the live demo, this means the daily quota has been reached — it is not an application bug. The app's error handling catches this gracefully and displays a readable message rather than crashing. Quota resets on a rolling 24-hour basis; you can also monitor usage at [ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits).

For a production deployment, this would be resolved by upgrading to a paid Gemini API tier to support concurrent users.

## Security Considerations

- **API key handling:** The Gemini API key is never hardcoded. It's loaded via `st.secrets`, and `.streamlit/secrets.toml` is git-ignored so it's never committed to version control.
- **`.gitignore` coverage:** Virtual environment (`.venv/`), Python cache files, and secrets are all excluded from the repository.
- **Error handling:** API failures (e.g. rate limits, connectivity issues) are caught and shown as a user-facing message rather than raw stack traces, though the underlying exception is still logged in the message for debugging during development.
- **No user data persistence:** Chat history and uploaded images exist only in the Streamlit session state — nothing is written to disk or an external database, so no personal data outlives the session.
- **Known limitation:** As this is a hackathon prototype, there is no rate-limiting or abuse protection on the API key itself, and the free-tier quota (20 requests/day) can be exhausted quickly during testing/demos — see the note above. In a production version, this would need request throttling, a backend proxy, and a paid API tier to protect the key and support real usage volume.

## Edge Cases Handled

- Uploading a photo without typing a message no longer results in silent inaction — a dedicated "Analyze Photo" button appears and disappears appropriately as photos are uploaded/reused
- A previously uploaded photo doesn't "stick" to unrelated follow-up messages once it's been processed
- Queries that trigger multiple tools at once (e.g. mentioning both a symptom *and* a location) are handled in a single coherent turn rather than requiring separate messages

## Future Improvements

- Replace mock shelter data with a real Malaysian shelter/vet directory (e.g. sourced from SPCA branches or `data.gov.my`)
- Add basic analytics (e.g. tracking urgency distribution of reported cases) to better understand real-world usage patterns
- Rate limiting / abuse protection for production deployment
