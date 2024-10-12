import streamlit as st
import openai
from pydantic import BaseModel
import random
from io import BytesIO
import sqlite3

# Ustawienia Streamlit
st.set_page_config(page_title="Pomagacz językowy", layout="wide")


# Definicja klasy Translation
class Translation(BaseModel):
    translated_text: str
    language: str


# Funkcje do zarządzania bazą danych
def create_connection():
    conn = sqlite3.connect("translations.db")
    return conn


def create_tables():
    conn = create_connection()
    with conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, original_text TEXT, translated_text TEXT, src_lang TEXT, dest_lang TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS vocabulary (id INTEGER PRIMARY KEY, word TEXT, translation TEXT, lang TEXT)"
        )


def insert_translation(original_text, translated_text, src_lang, dest_lang):
    conn = create_connection()
    with conn:
        conn.execute(
            "INSERT INTO history (original_text, translated_text, src_lang, dest_lang) VALUES (?, ?, ?, ?)",
            (original_text, translated_text, src_lang, dest_lang)
        )


def insert_vocabulary(word, translation, lang):
    conn = create_connection()
    with conn:
        conn.execute(
            "INSERT INTO vocabulary (word, translation, lang) VALUES (?, ?, ?)",
            (word, translation, lang)
        )


def get_translation_history():
    conn = create_connection()
    with conn:
        history = conn.execute("SELECT id, original_text, translated_text, src_lang, dest_lang FROM history").fetchall()
    return history


def get_vocabulary():
    conn = create_connection()
    with conn:
        vocabulary = conn.execute("SELECT id, word, translation, lang FROM vocabulary").fetchall()
    return vocabulary


def delete_translation(translation_id):
    conn = create_connection()
    with conn:
        conn.execute("DELETE FROM history WHERE id = ?", (translation_id,))


def delete_vocabulary(vocabulary_id):
    conn = create_connection()
    with conn:
        conn.execute("DELETE FROM vocabulary WHERE id = ?", (vocabulary_id,))


# Funkcja do tłumaczenia tekstu za pomocą Ai
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


def text_to_speech_tts1(text):
    response = openai.audio.speech.create(
        model="tts-1",
        input=text,
        voice="alloy",
    )
    audio_content = response.content
    audio = BytesIO(audio_content)
    audio.seek(0)

    return audio


# Funkcja do uzyskiwania wskazówek gramatycznych od AI
def get_grammar_tips(api_key, src_text, translated_text, src_lang, dest_lang):
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": "Jesteś ekspertem od gramatyki."},
        {"role": "user", "content": f"Podaj wskazówki gramatyczne dla następującego tłumaczenia:\n\nOryginał ({src_lang}): {src_text}\nPrzetłumaczone ({dest_lang}): {translated_text}\n\nWyjaśnij kluczowe różnice gramatyczne."}
    ]
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()


# Funkcja do sprawdzania umiejętności użytkownika
def analyze_user_text(api_key, user_text):
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": "Znasz wszystkie języki świata i jesteś ekspertem od gramatyki, składni i poprawności językowej."},
        {"role": "user", "content": f"Sprawdź poniższy tekst pod kątem błędów gramatycznych, składniowych oraz udziel sugestii. Oto tekst: {user_text}"}
    ]  
     
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=300
    )  

    feedback = response.choices[0].message.content.strip()
    return feedback


# Funkcja do quizu gramatycznego
def generate_grammar_quiz(translated_text):
    quiz = []
    words = translated_text.split()
    for _ in range(3):
        random_word = random.choice(words)
        quiz.append(f"Jaką rolę gramatyczną pełni słowo '{random_word}' w tym zdaniu?")
    return quiz


# Funkcja do generowania losowych słów
def generate_random_words(dest_lang, num_words=3):
    prompt = f"Wygeneruj {num_words} losowych słów w języku {dest_lang} i je ponumeruj oraz podaj tłumaczenie dla każdego słowa w języku polskim."
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )
    return response.choices[0].message.content.strip().split(", ")


# Główna część aplikacji
def main():
    # Inicjalizacja bazy danych
    create_tables()

    # Mapowanie języków
    lang_mapping = {
        "Polski 🇵🇱": "pl",
        "Angielski 🇬🇧": "en",
        "Francuski 🇫🇷": "fr",
        "Niemiecki 🇩🇪": "de",
        "Hiszpański 🇪🇸": "es",
        "Włoski 🇮🇹": "it",
        "Rosyjski 🇷🇺": "ru",  
        "Chiński 🇨🇳": "zh",   
        "Arabski 🇸🇦": "ar",
        "Japoński 🇯🇵": "ja",
    }

    lang_mapping2 = {
        "Angielski 🇬🇧": "en",
        "Polski 🇵🇱": "pl",
        "Francuski 🇫🇷": "fr",
        "Niemiecki 🇩🇪": "de",
        "Hiszpański 🇪🇸": "es",
        "Włoski 🇮🇹": "it",
        "Rosyjski 🇷🇺": "ru",  
        "Chiński 🇨🇳": "zh",   
        "Arabski 🇸🇦": "ar",   
        "Japoński 🇯🇵": "ja",
    }

    lang_mapping3 = {
        "Angielski 🇬🇧": "en",
        "Francuski 🇫🇷": "fr",
        "Niemiecki 🇩🇪": "de",
        "Hiszpański 🇪🇸": "es",
        "Włoski 🇮🇹": "it",
        "Rosyjski 🇷🇺": "ru",  
        "Chiński 🇨🇳": "zh",   
        "Arabski 🇸🇦": "ar",
        "Japoński 🇯🇵": "ja"
    }

    st.header(":blue[Pomagacz językowy] 🤓")
    # Zakładki i kolumny
    tab1, tab2, tab3 = st.tabs(["Tłumaczenie", "Interaktywne Ćwiczenia", "Historia i Słówka"])
    c1, c2 = st.columns(2)

    # Sprawdzenie, czy w session_state istnieją potrzebne zmienne
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""
    if "audio" not in st.session_state:
        st.session_state.audio = None
    if "grammar_tips" not in st.session_state:
        st.session_state.grammar_tips = ""

    with tab1:
        # Pobranie klucza API OpenAI
        api_key = st.text_input("Wprowadź swój klucz API OpenAI aby móc korzystać z aplikacji:", type="password")
        # Wybór języka
        c1, c2 = st.columns(2)
        with c1:
            src_lang = st.selectbox("Język źródłowy", list(lang_mapping.keys()))
        with c2:
            dest_lang = st.selectbox("Język docelowy", list(lang_mapping2.keys()))

        # Tłumaczenie
        text = st.text_area("Wprowadź tekst do przetłumaczenia")

        if st.button("Tłumacz"):
            if not api_key:
                st.info("Najpierw wprowadź klucz API")
            else:        
                translation = translate_text_with_openai(api_key, text, src_lang, dest_lang)
                st.session_state.translated_text = translation.translated_text
                st.subheader(":red[Przetłumaczony tekst]")
                st.write(st.session_state.translated_text)

                # Zapisywanie tłumaczenia w bazie danych
                insert_translation(text, st.session_state.translated_text, src_lang, dest_lang)

                # Generowanie audio z przetłumaczonego tekstu
                st.session_state.audio = text_to_speech_tts1(st.session_state.translated_text)
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

        st.header(":red[Sprawdź swoje umiejętności]")

        # Generowanie losowych słów i odzew AI
        if st.session_state.translated_text:
            dest_lang = st.selectbox("Wybierz język docelowy", list(lang_mapping3.keys()))

            # Sprawdzenie, czy losowe słowa zostały już wygenerowane
            if "random_words" not in st.session_state:
                st.session_state.random_words = generate_random_words(dest_lang)

            st.write("Użyj poniższych słów, aby ułożyć sensowne zdanie (:blue[możesz użyć dowolnej formy tych słów i nie musisz używać wszystkich]):")
            st.write(", ".join(st.session_state.random_words))

            if st.button("Losuj 🎲"):
                # Losowanie nowych słów
                st.session_state.random_words = generate_random_words(dest_lang)

            user_sentence = st.text_input("Twoje zdanie:")

            if st.button("Sprawdź zdanie"):
                # Analiza zdania przez AI
                if user_sentence.strip():
                    feedback = analyze_user_text(api_key, user_sentence)
                    st.subheader("Analiza tekstu")
                    st.write(feedback)
                else:
                    st.warning("Proszę wprowadzić zdanie.")

        # Konwersacje z chatbotem
        st.subheader("Asystent 🤖")
        if api_key:
            user_input = st.text_input("Wprowadź wiadomość do chatbota:")
            if user_input and st.button("Wyślij"):
                conversation_messages = [
                    {"role": "system", "content": "Jesteś ekspertem do spraw językowych znasz wszystkie języki świata i udzielasz kompleksowych porad oraz odpowiedzi na pytania użytkownika"},
                    {"role": "user", "content": user_input}
                ]
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=conversation_messages,
                    max_tokens=300
                )
                chatbot_reply = response.choices[0].message.content.strip()
                st.write(chatbot_reply)

    with tab3:
        st.header(":red[Historia tłumaczeń]")       
        # Historia tłumaczeń
        history = get_translation_history()
        for translation in history:
            original_text, translated_text, src_lang, dest_lang = translation[1], translation[2], translation[3], translation[4]
            st.write(f"{original_text} -> {translated_text} ({src_lang} -> {dest_lang})")
            if st.button(f"Usuń {original_text} -> {translated_text}", key=translation[0]):
                delete_translation(translation[0])
                st.rerun()

        # Słówka do zapamiętania
        st.subheader("Słówka do zapamiętania 📝")       
        # Formularz dodawania nowego słowa
        col1, col2, col3 = st.columns(3)
        with col1:
            new_word = st.text_input("Nowe słowo")
        with col2:
            new_translation = st.text_input("Tłumaczenie")
        with col3:
            new_lang = st.selectbox("Język", list(lang_mapping3.keys()))

        if st.button("Dodaj słowo"):
            if new_word and new_translation:
                insert_vocabulary(new_word, new_translation, new_lang)
                st.success(f"'{new_word}' dodano do słówek do zapamiętania.")
                st.rerun()
            else:
                st.warning("Proszę wypełnić wszystkie pola.")

        # Wyświetlanie słówek do zapamiętania
        vocabulary = get_vocabulary()
        for word_data in vocabulary:
            word, translation, lang = word_data[1], word_data[2], word_data[3]
            st.write(f"{word} -> {translation} ({lang})")
            if st.button(f"Usuń {word} -> {translation}", key=word_data[0]):
                delete_vocabulary(word_data[0])
                st.success(f"'{word}' zostało usunięte.")
                st.rerun()


# Uruchomienie aplikacji
if __name__ == "__main__":
    main()
