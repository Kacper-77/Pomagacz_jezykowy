import streamlit as st
import openai
from pydantic import BaseModel
import random
from gtts import gTTS
from io import BytesIO


# Definicja klasy Translation
class Translation(BaseModel):
    translated_text: str
    language: str


# Ustawienia Streamlit
st.set_page_config(page_title="Pomagacz językowy", layout="wide")


# Funkcja do tłumaczenia tekstu za pomocą modelu OpenAI
def translate_text_with_openai(api_key, text, src_lang, dest_lang):
    openai.api_key = api_key
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś profesjonalnym tłumaczem."},
            {"role": "user", "content": f"Przetłumacz ten tekst bez żadnych komentarzy z {src_lang} na {dest_lang}: {text}."}
        ],
        max_tokens=500
    )

    translated_text = response.choices[0].message.content.strip()
    return Translation(translated_text=translated_text, language=dest_lang)


# Funkcja do generowania pliku audio z tekstu za pomocą gTTS
def text_to_speech_gtts(text, lang):
    tts = gTTS(text=text, lang=lang)
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio


# Funkcja do uzyskiwania wskazówek gramatycznych od OpenAI
def get_grammar_tips(api_key, src_text, translated_text, src_lang, dest_lang):
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": "Jesteś ekspertem od gramatyki."},
        {"role": "user", "content": f"Podaj wskazówki gramatyczne dla następującego tłumaczenia:\n\nOryginał ({src_lang}): {src_text}\nPrzetłumaczone ({dest_lang}): {translated_text}\n\nWyjaśnij kluczowe różnice gramatyczne."}
    ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()


# Funkcja do quizu gramatycznego
def generate_grammar_quiz(translated_text):
    quiz = []
    words = translated_text.split()
    for _ in range(3):
        random_word = random.choice(words)
        quiz.append(f"Jaką rolę gramatyczną pełni słowo '{random_word}' w tym zdaniu?")
    return quiz


# Główna część aplikacji
def main():
    # Zakładki i kolumny
    tab1, tab2 = st.tabs(["Tłumaczenie", "Interaktywne Ćwiczenia"])

    # Sprawdzenie, czy w session_state istnieją potrzebne zmienne
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""
    if "audio" not in st.session_state:
        st.session_state.audio = None
    if "grammar_tips" not in st.session_state:
        st.session_state.grammar_tips = ""

    with tab1:
        st.header(":blue[Pomagacz językowy] 🤓")
        # Pobranie klucza API OpenAI
        api_key = st.text_input("Wprowadź swój klucz API OpenAI:", type="password")
        # Wybór języka 
        src_lang = st.selectbox("Język źródłowy", ["pl", "en", "fr", "de", "es", "it"])
        dest_lang = st.selectbox("Język docelowy", ["en", "pl", "fr", "de", "es", "it"])

        # Wprowadzenie tekstu do tłumaczenia
        text = st.text_area("Wprowadź tekst do przetłumaczenia")

        if st.button("Tłumacz"):
            # Tłumaczenie tekstu
            translation = translate_text_with_openai(api_key, text, src_lang, dest_lang)
            st.session_state.translated_text = translation.translated_text
            st.subheader(":red[Przetłumaczony tekst]")
            st.write(st.session_state.translated_text)

            # Generowanie audio z przetłumaczonego tekstu
            st.session_state.audio = text_to_speech_gtts(st.session_state.translated_text, lang=dest_lang)
            st.audio(st.session_state.audio)

            # Wskazówki gramatyczne
            if api_key and st.session_state.translated_text:
                st.session_state.grammar_tips = get_grammar_tips(api_key, text, st.session_state.translated_text, src_lang, dest_lang)
                st.subheader(":red[Wskazówki gramatyczne]")
                st.write(st.session_state.grammar_tips)
            elif not api_key:
                st.info("Wprowadź klucz API OpenAI, aby otrzymać wskazówki gramatyczne.")

    with tab2:
        st.header("Interaktywne Ćwiczenia")

        # Wyświetlanie przetłumaczonego tekstu i wskazówek gramatycznych
        if st.session_state.translated_text:
            st.subheader(":red[Przetłumaczony tekst]")
            st.write(st.session_state.translated_text)

            st.subheader(":red[Wskazówki gramatyczne]")
            st.write(st.session_state.grammar_tips)

            if st.session_state.audio:
                st.audio(st.session_state.audio)

        # Quizy gramatyczne
        st.subheader("Quiz gramatyczny")
        if st.session_state.translated_text:
            if st.button("Generuj quiz"):
                quiz = generate_grammar_quiz(st.session_state.translated_text)
                for q in quiz:
                    st.write(q)
        else:
            st.write(":green[Najpierw wykonaj tłumaczenie w zakładce 'Tłumaczenie']")

        # Konwersacje z chatbotem
        st.subheader("Asystent 🤖")
        if api_key:
            user_input = st.text_input("Wprowadź wiadomość do chatbota:")
            if user_input and st.button("Wyślij"):
                conversation_messages = [
                    {"role": "system", "content": "Prowadzisz rozmowę w języku docelowym."},
                    {"role": "user", "content": user_input}
                ]
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=conversation_messages,
                    max_tokens=300
                )
                chatbot_reply = response.choices[0].message.content.strip()
                st.write(chatbot_reply)

        # Tworzenie listy słówek
        st.subheader("Lista słówek")
        words_to_remember = st.text_area("Wprowadź słowa do zapamiętania:")
        if st.button("Dodaj do listy"):
            st.write(f"Słowa do zapamiętania: {words_to_remember}")


# Uruchomienie głównej funkcji
if __name__ == "__main__":
    main()
