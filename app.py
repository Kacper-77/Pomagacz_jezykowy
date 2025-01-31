import streamlit as st
import openai
from pydantic import BaseModel
import random
from io import BytesIO
from langfuse.decorators import observe
from dotenv import load_dotenv
from db import *

# Ustawienia Streamlit
st.set_page_config(page_title="Pomagacz językowy", layout="wide")


# Definicja klasy Translation
class Translation(BaseModel):
    translated_text: str
    language: str


load_dotenv()


@observe
# Funkcja do tłumaczenia tekstu za pomocą AI
def translate_text_with_openai(api_key, text, src_lang, dest_lang):
    openai.api_key = api_key
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jesteś profesjonalnym tłumaczem."},
            {
                "role": "user",
                "content": f"Przetłumacz ten tekst bez żadnych komentarzy z {src_lang} na {dest_lang}: {text}.",
            },
        ],
        max_tokens=500,
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


@observe
# Funkcja do uzyskiwania wskazówek gramatycznych od AI
def get_grammar_tips(api_key, src_text, translated_text, src_lang, dest_lang):
    openai.api_key = api_key
    messages = [
        {"role": "system", "content": "Jesteś ekspertem od gramatyki."},
        {
            "role": "user",
            "content": f"Podaj po krótce wskazówki gramatyczne dla następującego tłumaczenia:\n\nOryginał ({src_lang}): {src_text}\nPrzetłumaczone ({dest_lang}): {translated_text}\n\nWyjaśnij kluczowe różnice gramatyczne.",
        },
    ]
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        # max_tokens=500,
        stream=True,
    )
    return response


@observe
# Funkcja do sprawdzania umiejętności użytkownika
def analyze_user_text(api_key, user_text):
    try:
        openai.api_key = api_key
        messages = [
            {
                "role": "system",
                "content": "Znasz wszystkie języki świata i jesteś ekspertem od gramatyki, składni i poprawności językowej.",
            },
            {
                "role": "user",
                "content": f"Sprawdź poniższy tekst pod kątem błędów gramatycznych, składniowych oraz udziel po krótce sugestii. Oto tekst: {user_text}",
            },
        ]
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        feedback = response.choices[0].message.content.strip()
        return feedback
    except openai.AuthenticationError:
        return None


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
    try:
        prompt = f"Wygeneruj {num_words} losowych słów w języku {dest_lang} i je ponumeruj oraz podaj tłumaczenie dla każdego słowa w języku polskim."
        response = openai.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}], max_tokens=50
        )
        return response.choices[0].message.content.strip().split(", ")
    except openai.OpenAIError:
        return []


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
        "Japoński 🇯🇵": "ja",
    }
    with st.sidebar:
        # Słówka do zapamiętania
        st.subheader("Słówka do zapamiętania 📝")
        # Formularz dodawania nowego słowa
        col1, col2, col3 = st.columns(3)
        with col1:
            new_word = st.text_input("Nowe słowo", key="new_word_input")
        with col2:
            new_translation = st.text_input("Tłumaczenie", key="new_translation_input")
        with col3:
            new_lang = st.selectbox(
                "Język", list(lang_mapping3.keys()), key="new_lang_select"
            )

        if st.button("Dodaj słowo"):
            if new_word and new_translation:
                insert_vocabulary(new_word, new_translation, new_lang)
                st.success(f"'{new_word}' dodano do słówek do zapamiętania.")
                st.rerun()
            else:
                st.warning("Proszę wypełnić wszystkie pola.")

        # Wyświetlanie słówek do zapamiętania
        vocabulary = get_vocabulary()
        for idx, word_data in enumerate(vocabulary):
            word, translation, lang = word_data[1], word_data[2], word_data[3]
            st.write(f"{word} -> {translation} ({lang})")
            if st.button(
                f"Usuń {word} -> {translation}", key=f"vocab_{word_data[0]}_{idx}"
            ):
                delete_vocabulary(word_data[0])
                st.success(f"'{word}' zostało usunięte.")
                st.rerun()

        st.header(":red[Historia tłumaczeń]")
        # Historia tłumaczeń
        history = get_translation_history()
        for translation in history:
            original_text, translated_text, src_lang, dest_lang = (
                translation[1],
                translation[2],
                translation[3],
                translation[4],
            )
            st.write(
                f"{original_text} -> {translated_text} ({src_lang} -> {dest_lang})"
            )
            if st.button(
                f"Usuń {original_text} -> {translated_text}", key=translation[0]
            ):
                delete_translation(translation[0])
                st.rerun()

    st.header(":blue[Pomagacz językowy] 🤓")
    # Zakładki i kolumny
    tab1, tab2 = st.tabs(["Tłumaczenie", "Interaktywne Ćwiczenia"])

    # Sprawdzenie, czy w session_state istnieją potrzebne zmienne
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""
    if "audio" not in st.session_state:
        st.session_state.audio = None
    if "grammar_tips" not in st.session_state:
        st.session_state["grammar_tips"] = ""

    with tab1:
        with st.expander("Informacje dotyczące korzystania z aplikacji"):
            st.markdown(
                "## Witaj, niezmiernie nam miło, że zdecydowaleś/aś się skorzystać z naszej aplikacji 🥰"
            )
            st.markdown(
                "## Cenimy sobie ludzi którzy lubią się kształcić oraz rozwijać i dlatego dokładamy wszelkich starań aby umożliwić im korzystanie z jak najlepszych narzędzi."
            )
            st.markdown(
                "### Krótka instrukcja obsługi jak korzystać z naszej aplikacji:"
            )
            st.markdown(
                "#### 1. podaj swój klucz API OpenAI w polu do tego przeznaczonym"
            )
            st.markdown("#### 2. baw się dobrze podczas nauki z naszą aplikacją")
            st.markdown(
                "#### Tak, to już naprawdę wszystko jesteśmy przystępni dla każdego 😁"
            )

        # Pobranie klucza API OpenAI
        api_key = st.text_input(
            "Wprowadź swój klucz API OpenAI aby móc korzystać z aplikacji:",
            type="password",
        )

        # Wybór języka
        c1, c2 = st.columns(2)
        with c1:
            src_lang = st.selectbox("Język źródłowy", list(lang_mapping.keys()))
        with c2:
            dest_lang = st.selectbox("Język docelowy", list(lang_mapping2.keys()))

        # Tłumaczenie

        ### INFO
        # st.write("""Jeśli chodzi o tłumaczenie i audio koszty wyglądają w następujący sposób
        #             tłumaczenie: 'gpt-4o-mini' 0.150 dolara za milion input tokenów oraz 0.600 doloara za milion output tokenów
        #             co to oznacza? Otóż tutaj został użyty tani aczkolwiek wystarczający i bardzo szybki model.
        #             Input tokeny to ciągi znaków/sylaby ktore AI sobie nalicza w swój sposób.
        #             Jedno krótkie słowo to 1-1.5 tokena. Ceny są w tym przypadku bardzo przystępne.""")
        # st.write("""
        #             Jeśli zaś chodzi o audio wygląda to tak: 'tts-1' 15.000 dolarów za milion znaków (milion znaków nie tokenów)
        #             Cena w tym przypadku jest również przystępna i możliwe jest dobranie
        #             sobie różnych głosów w zależności od gustu.""")
        
        # st.write("""Poniżej tam gdzie znajdują się wskazówki gramatyczne został również użyty model gpt-4o-mini
        #          tak samo jak przy tłumaczeniu. Quiz gramatyczny jest darmowy z możliwością rozwoju jest to swego
        #          rodzaju eksperyment.""")

        text = st.text_area("Wprowadź tekst do przetłumaczenia", max_chars=300)
        column1, column2, _ = st.columns([1, 1, 5])
        with column1:
            if st.button("Tłumacz"):
                if not api_key:
                    st.info("Najpierw wprowadź klucz API")
                elif not text:
                    st.info("Najpierw wprowadź tekst do przetłumaczenia")
                else:
                    translation = translate_text_with_openai(
                        api_key, text, src_lang, dest_lang
                    )
                    st.session_state.translated_text = translation.translated_text

                    # Zapisywanie tłumaczenia w bazie danych
                    insert_translation(
                        text, st.session_state.translated_text, src_lang, dest_lang
                    )

                    # Generowanie audio z przetłumaczonego tekstu
                    st.session_state.audio = text_to_speech_tts1(
                        st.session_state.translated_text
                    )

        # Wyświetlanie tłumaczenia, audio i wskazówek
        if st.session_state.translated_text:
            st.subheader(":red[Przetłumaczony tekst]")
            st.write(st.session_state.translated_text)

        if st.session_state.audio:
            st.audio(st.session_state.audio)

        if api_key and st.session_state.translated_text:
            st.subheader(":red[Wskazówki gramatyczne]")
            if st.button("Pokaż wskazówki gramatyczne"):
                if api_key and st.session_state.translated_text:
                    tips = get_grammar_tips(
                        api_key,
                        text,
                        st.session_state.translated_text,
                        src_lang,
                        dest_lang,
                    )
                    response = st.write_stream(tips)
                    st.session_state["grammar_tips"] = response
                    st.rerun()

        if st.session_state["grammar_tips"]:
            st.write(st.session_state["grammar_tips"])

        # Quiz gramatyczny
        if api_key and st.session_state.translated_text:
            st.subheader(":violet[Quiz gramatyczny] 🤔")
            if st.session_state.translated_text:
                if st.button("Generuj quiz"):
                    quiz = generate_grammar_quiz(st.session_state.translated_text)
                    for q in quiz:
                        st.write(q)

    with tab2:

        # ### INFO
        # st.write("""Tutaj AI zostało wykorzystane do generownia losowych słow oraz oceny tekstu
        #          użytkownika jeśli chodzi o ocenę tekstu to ponownie został użyty szybki i skuteczny
        #          model 'gpt-4o-mini' także ceny bez zmian. W tym miejscu można dodać jeszcze strumieniowanie
        #          tekstu na żywo tak jak w przypadku wskazówek gramatycznych.
        #          """)
        
        # st.write("""Odnośnie generowania losowych słów tutaj tanie modele nie radziły sobie zbyt dobrze
        #          i został użyty model 'gpt-4' a jego ceny wyglądają w następujący sposób: 
        #          30.00 dolarów za milion input tokenów oraz 60.00 dolarów za milion output tokenów. Ceny tu już są zauważalnie wyższe
        #          aczkolwiek generowane są tylko trzy słowa i input tokenów to tu prawie nie ma więc koszty
        #          nie powinny być duże. Z biegiem czasu modele będą tanieć i wtedy będzie można eksperymentować.""")
        
        # st.write("""Ta część aplikacji ma naprawdę duży potencjał na nawiązanie więzi z użytkownikiem
        #          i może być stale rozwijana.""")

        st.header(":red[Sprawdź swoje umiejętności]")
        # Generowanie losowych słów i odzew AI
        dest_lang = st.selectbox("Wybierz język docelowy", list(lang_mapping3.keys()))

        # Sprawdzenie, czy losowe słowa zostały już wygenerowane
        if "random_words" not in st.session_state:
            st.session_state.random_words = generate_random_words(dest_lang)

        st.write(
            "Użyj poniższych słów, aby ułożyć sensowne zdanie (:blue[możesz użyć dowolnej formy tych słów i nie musisz używać wszystkich]):"
        )
        st.write(", ".join(st.session_state.random_words))

        if st.button("Losuj 🎲"):
            # Losowe słowa
            if api_key:
                st.session_state.random_words = generate_random_words(dest_lang)
                st.rerun()
            else:
                st.info("Najpierw wprowadź klucz API")

        user_sentence = st.text_input("Twoje zdanie:", key="user_sentence_input")

        if st.button("Sprawdź zdanie"):
            # Analiza zdania przez AI
            if user_sentence.strip():
                feedback = analyze_user_text(api_key, user_sentence)
                st.subheader("Analiza tekstu")
                st.write(feedback)
            else:
                st.warning("Proszę wprowadzić zdanie.")

        # Konwersacje z chatbotem
        st.subheader(
            "Asystent językowy 🤖"
        )
        # st.markdown("""Jest to ekspert językowy można się go zapytać w czym może pomóc.
        #             Tutaj również został użyty model 'gpt-4o-mini'.""")
        user_input = st.text_input(
            "Wprowadź wiadomość do chatbota:", key="chatbot_input"
        )
        if api_key:
            if user_input and st.button("Wyślij"):
                conversation_messages = [
                    {
                        "role": "system",
                        "content": "Jesteś ekspertem do spraw językowych znasz wszystkie języki świata i udzielasz kompleksowych porad oraz odpowiedzi na pytania użytkownika",
                    },
                    {"role": "user", "content": user_input},
                ]
                response = openai.chat.completions.create(
                    model="gpt-4o-mini", messages=conversation_messages, max_tokens=300
                )
                chatbot_reply = response.choices[0].message.content.strip()
                st.write(chatbot_reply)


# Uruchomienie aplikacji
if __name__ == "__main__":
    main()
