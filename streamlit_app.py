import time
import streamlit as st
import json
import random


# Streamlit app
def quiz_app(data: list):

    # Check if the session state is already initialized
    if 'random_entry' not in st.session_state:
        #needed for the first time
        st.session_state.random_entry = random.choice(data)
        st.session_state.flg_correct = 0
        st.session_state.flg_wrong = 0
        st.session_state.cnt_correct = 0
        st.session_state.cnt_wrong = 0
        st.session_state.cnt_total = 0
        st.session_state.questions_asked = []

    # Display the question
    random_entry = st.session_state.random_entry

    # Sidebar
    with st.sidebar:
        st.header("Übungen zur Heilpraktikerprüfung für Psychotherapie")

        col1, col2, col3 = st.columns(3)
        st.metric("Gesamt", len(data))
        st.metric("Abgefragt", st.session_state.cnt_total)
        st.metric("Richtig", st.session_state.cnt_correct)
        st.metric("Falsch", st.session_state.cnt_wrong)
    
    


    st.title(f'Frage {random_entry["number"]} vom {random_entry["date"]}')
    st.write(random_entry["text"])
    
    # Display options
    options = random_entry["options"]
    with st.form("my_form"):
        for option, description in options.items():
            st.checkbox(f'{option}: {description}', key=option)
        st.form_submit_button('Antwort prüfen')

    # Check answers
    selected_options = [option for option in options if st.session_state[option]]
    if len(selected_options) == 0:
        st.stop()
    if sorted(selected_options) == sorted(random_entry["solution"]):
        st.success("Richtig! Ihre Auswahl ist korrekt.")
        st.session_state.flg_correct = 1
    else:
        st.error("Falsch! Bitte versuchen Sie es erneut.")
        st.session_state.flg_wrong = 1

    if st.button('Nächste Frage'):
        # get a new random entry
        st.session_state.random_entry = random.choice(data)

        # update the counters
        if (st.session_state.flg_wrong == 0 and st.session_state.flg_correct == 1):
            st.session_state.cnt_correct += 1
        if (st.session_state.flg_wrong == 1 and st.session_state.flg_correct == 0):
            st.session_state.cnt_wrong += 1
        if (st.session_state.flg_wrong == 1 and st.session_state.flg_correct == 1):
            st.session_state.cnt_wrong += 1

        # always update the total count
        st.session_state.cnt_total += 1

        # rerun app, unclear why needed
        st.rerun()
        
if __name__ == "__main__":
    # Specify the file path
    file_path = "data/HPP_QandA.json"

    # Load JSON data from the file
    with open(file_path, "r") as file:
        data = json.load(file)

    # Now you can use the 'data' variable to access the loaded JSON data
    # Loop until user cancels
    
    quiz_app(data)
    