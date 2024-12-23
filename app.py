import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI

openai_client = OpenAI(api_key="openai_api_key")
df = pd.read_csv("output_cleaned.csv", sep=";")
# Konwersja DataFrame do formatu CSV (do prompta)
data_csv = df.to_csv(index=False)

st.header('Jak wypadasz na tle kursantów z kursu "Pracuj w AI: Zostań Data Scientist od Zera"')
st.text('Aby skorzystać z aplikacji wprowadź wszystkie odpowiedzi. Nasz asystent przygotuje dla Ciebie, krótką analizę Ciebie oraz tego jak wypadasz na tle kursantów "Pracuj w AI: Zostań Data Scientist od Zera"')
st.text("Wprowadź swoje odpowiedzi:")

col1, col2, col3 = st.columns(3)
with col1:
    age = st.selectbox(
        ":see_no_evil: Przedział wiekowy:", 
        ['Wybierz', '<18', '18-24', '25-34', '35-44', '45-54', '55-64', '>=65', 'Inne']
    )
    edu_level = st.selectbox(
        ":school: Poziom wykształcenia:", 
        ['Wybierz', 'Podstawowe', 'Średnie', 'Wyższe']
    )
    fav_animals = st.selectbox(
        ":monkey: Ulubione zwierzę:", 
        ['Wybierz', 'Brak ulubionych', 'Psy', 'Koty', 'Koty i Psy', 'Inne']
    )

with col2:
    hobby_choice = st.selectbox(
        ":swimmer: Twoje hobby:",
        ['Wybierz', 'Sztuka', 'Książki', 'Filmy', 'Sport', 'Gry komputerowe', 'Inne']
    )
    # Mapowanie użytkownika na odpowiednie kolumny
    hobby_map = {
        'Wybierz': 'wybierz',
        'Sztuka': 'hobby_art',
        'Książki': 'hobby_books',
        'Filmy': 'hobby_movies',
        'Sport': 'hobby_sport',
        'Gry komputerowe': 'hobby_video_games',
        'Inne': 'hobby_other',

    }
    mapped_hobby = hobby_map[hobby_choice]  # Mapowanie wyboru użytkownika do odpowiedniej kolumny
    industry = st.selectbox(
        ":office_worker: Branża:",
        ['Wybierz', 'IT', 'Edukacja', 'Energetyka', 'Automotive', 'Automatyzacja',
         'Energetyka zawodowa', 'Zdrowie', 'Kadry (HR)', 'Marketing', 'Produkcja',
         'Wellness', 'Chemia', 'Nieruchomości', 'Poligrafia', 'Administracja publiczna', 'Inne']
    )
    fav_place = st.selectbox(
        ":beach_with_umbrella: Ulubione miejsce:", 
        ['Wybierz', 'Nad wodą', 'W lesie', 'W górach', 'Inne']
    )

with col3:
    motivation = st.selectbox(
        ":fire: Co Cię motywuje?",
        ['Wybierz', 'Kariera', 'Wyzwania', 'Kreatywność i innowacje', 'Finanse i praca', 
         'Rozwój osobisty', 'Praca zdalna']
    )
 
    sweet_or_salty = st.selectbox(
        ":bowl_with_spoon: Preferencja (słodkie czy słone):", 
        ['Wybierz', 'sweet', 'salty', 'Inne']
    )
    
    years_of_experience = st.selectbox(
        ":hourglass_flowing_sand: Lata doświadczenia:", 
        ['Wybierz', '0-2', '3-5', '6-10', '11-15', '>=16', 'Inne']
    )

# Funkcja do obliczania zgodności procentowej
def calculate_response_percentage(user_response, df):
    """
    Funkcja oblicza, jaki procent użytkowników z DataFrame wybrał odpowiedzi takie jak użytkownik.
    :param user_response: słownik z odpowiedziami użytkownika
    :param df: DataFrame z danymi użytkowników
    :return: słownik z procentową liczbą odpowiedzi zgodnych
    """
    response_percentage = {}
    
    for key, value in user_response.items():
        # Sprawdzamy, czy kolumna istnieje w DataFrame
        if key in df.columns:
            match_count = df[key].value_counts().get(value, 0)
            total_users = len(df)
            percentage = (match_count / total_users) * 100
        else:
            percentage = 0  # Jeśli klucz nie istnieje, zwracamy 0
        response_percentage[key] = percentage    
    return response_percentage

# Funkcja do sprawdzania czy wszystkie pola są wypełnione
def all_fields_filled():
    """
    Funkcja sprawdza, czy wszystkie select boxy mają wartości inne niż 'Wybierz'
    """
    return all([
        age != 'Wybierz',
        edu_level != 'Wybierz',
        fav_animals != 'Wybierz',
        hobby_choice != 'Wybierz',
        industry != 'Wybierz',
        fav_place != 'Wybierz',
        motivation != 'Wybierz',
        sweet_or_salty != 'Wybierz',
        years_of_experience != 'Wybierz'
    ])

# Dynamiczne sprawdzanie, czy wszystkie warunki są spełnione
is_form_filled = all_fields_filled()  # Sprawdzenie, czy formularz został uzupełniony

user_key = st.text_input("Klucz API", type="password")
if user_key:
    st.session_state["openai_api_key"] = user_key
    openai_client.api_key = user_key

# OpenAI API key protection
if not st.session_state.get("openai_api_key"):
    st.error("Dodaj swój klucz API OpenAI")
else:
    st.success("Klucz API OpenAI wprowadzony :thumbsup:")

# Dynamiczne sprawdzanie wypełnienia pól
if not all_fields_filled():
    st.error("Uzupełnij wszystkie pola formularza")
else:
    st.success("Wszystkie pola formularza wypełnione :thumbsup:")

# Ustawienie klucza API w kliencie OpenAI
if st.session_state.get("openai_api_key"):
    api_key = st.session_state["openai_api_key"]
else:
    st.stop()  # Zatrzymaj aplikację, jeśli klucz nie jest dostępny

# Warunek, aby aktywować przycisk tylko wtedy, gdy oba warunki są spełnione
if st.button("Kliknij mnie po wypełnieniu :)", disabled=not (is_form_filled)):
     st.success("Klik! Wszystko prawidłowo wypełnione :thumbsup:")
     with st.spinner("Proszę czekać, przetwarzam dane..."):

        # Funkcja generująca odpowiedź chatbota
        def get_chatbot_reply(user_prompt):
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """
                            Odpowiadaj zawsze w języku polskim.
                            Jesteś osobą, która ma zachęcić do zostania data scientist. 
                            Posiadasz ponad 15 letnie doświadczenie w branży data scientis oraz zawsze potrafisz idealnie wyciągać wnioski.
                            Wypowiadasz się w sposób humorystyczny, ale zawsze w sposób merytoryczny i w pełni profesjonalny.
                            Jak starasz się być zabawny, to podkreślaj to emotikonami.
                        """
                    },
                    {"role": "user", "content": user_prompt}
                ]
            )
            return {
                "role": "assistant",
                "content": response.choices[0].message.content,
            }

        # Inicjalizacja historii wiadomości
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        # Wyświetlanie historii wiadomości - pomijamy wiadomości z treścią static_prompt
        for message in st.session_state["messages"]:
            if message["role"] != "user":  # Pomijamy wiadomości użytkownika
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Stała treść zapytania
        static_prompt = (f"""
            Na początku wypowiedzi przywitaj się i podziękuj za korzystanie z niniejszej aplikacji.
            Na podstawie danych przedstaw w humorystyczny sposób opis osoby, która: 
            Jest w wieku: {age},
            Posiada wykształcenia na poziomie {edu_level},
            Jej ulubione zwierzę to {fav_animals},
            Jej ulubionym miejscem jest {fav_place},
            Posiada hobby {mapped_hobby},
            Branża w której pracuje w tej chwili(przed przebranżowieniem) {industry}, 
            Smak który lubi to {sweet_or_salty},
            Posiada {years_of_experience} lat doświadczenia zawodowego.
            Cały tekst ma być odniesieniu do tego osoba opisywana chciałaby zostać data scientist. Nawiązuj do danych o osobie oraz zachęć do nauki data scientist.
            Zwracaj się bezpośrednio do czytającego.
            Następnie powiedz, że bardzo dziękujesz za skorzystanie z aplikacji pod tytułem: "Jak wypadasz na tle kursantów z kursu "Pracuj w AI: Zostań Data Scientist od Zera" oraz 
            wykonaj analizę na podstawie danych z ankiety kursantów z kursu, które znajdują się w formacie CSV:{data_csv} oraz porównaj do odpowiedzi osoby do której teraz piszesz, która 
            dała następujące odpowiedzi: {age}, {edu_level}, {fav_animals}, {fav_place}, {mapped_hobby}, {industry}, {sweet_or_salty}, {years_of_experience}. Podaj 3 odpowiedzi, które
            najbardziej pokrywały się z pozostałymi kursantami oraz 3 odpowiedz, które najmniej pokrywały się. Wyciągnij wnioski oraz zachęć do zostania data scientist.
        """
        )

        # Pobranie odpowiedzi od chatbota
        chatbot_message = get_chatbot_reply(static_prompt)

        # Wyświetlanie odpowiedzi asystenta
        with st.chat_message("assistant"):
            st.markdown(chatbot_message["content"])

            # Pobranie odpowiedzi użytkownika jako słownik
        user_response = {
            "age": age,
            "edu_level": edu_level,
            "fav_animals": fav_animals,
            "fav_place": fav_place,
            mapped_hobby: 1,  # Dynamiczne przypisanie na podstawie mapowania
            "industry": industry,
            "motivation": motivation,   #motivation 
            "sweet_or_salty": sweet_or_salty,
            "years_of_experience": years_of_experience,
        }

        # Obliczenie procentów zgodności
        response_percentages = calculate_response_percentage(user_response, df)

        # Wyświetlanie średniej zgodności
        avg_percentage = np.mean(list(response_percentages.values()))
        st.success(f"Z Twoich odpowiedzi wynika że Twój średni procent zgodności z uczestnikami kursu wynosi: {avg_percentage:.2f}%")

        # Przygotowanie danych do wykresu
        categories = list(response_percentages.keys())
        percentages = list(response_percentages.values())

        # Rysowanie wykresu
        fig, ax = plt.subplots(figsize=(10, 6))

        # Gradient kolorów od czerwonego do zielonego
        colors = [plt.cm.RdYlGn(p / 100) for p in percentages]

        # Tworzenie wykresu słupkowego
        bars = ax.barh(categories, percentages, color=colors)

        # Dodawanie wartości liczbowych na słupkach
        for bar, percentage in zip(bars, percentages):
            ax.text(
                bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{percentage:.1f}%", va='center', fontsize=10
            )

        # Formatowanie osi
        ax.set_xlim(0, 100)
        ax.set_xlabel("Zgodność procentowa od 0 do 100 (%)", fontsize=20)
        ax.set_ylabel("Kategorie", fontsize=20)
        ax.set_title("Zgodność użytkownika z grupą", fontsize=30)
        ax.grid(axis='x', linestyle='--', alpha=0.7)

        # Wyświetlenie wykresu w Streamlit
        st.pyplot(fig)
