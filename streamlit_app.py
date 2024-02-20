import datetime
from datetime import date
import os
import time
import streamlit as st
import json
import random
import extra_streamlit_components as stx



start_time = time.time()
timeout = 0.1  # Preset timeout time

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

def get_manager():
    return stx.CookieManager()

def load_cookies():
  
    cookie_manager = get_manager()
    st.session_state.cookies = cookie_manager.get_all()
    
    # Wait for the cookies to be available
    for i in range(0, 10):
        time.sleep(timeout)
        if len(st.session_state.cookies) > 0:
            break

    # Check if the cookies are available
    if 'user_data' in st.session_state.cookies:
        # Copy the cookies to the session state
        st.session_state.user_data = st.session_state.cookies['user_data']
        st.success("Vorhergehende Lernsession geladen.")
        

def save_cookies():
    cookie_manager = get_manager()
    cookie_manager.set('user_data', st.session_state.user_data, key="0", expires_at=add_years(datetime.datetime.now(),1))
    time.sleep(5*timeout)

def reset_cookies():
    cookie_manager = get_manager()
    if 'cookies' in st.session_state:
        if 'user_data' in st.session_state.cookies:
            cookie_manager.delete('user_data')
    pass

def get_next_question(data):

    # Reset the flags
    st.session_state.flg_correct = 0
    st.session_state.flg_wrong = 0

    # Select a random index, make sure it's not the same as it has not been asked
    st.session_state.qindex = random.randint(0, len(data) - 1)

    if len(st.session_state.user_data['correct']) == len(data):
        st.warning("Alle Fragen wurden abgefragt.")
        return
    else:
        # Repeat until a new question is found
        while st.session_state.qindex in st.session_state.user_data['asked']:
            st.session_state.qindex = random.randint(0, len(data) - 1)

    # Retrieve the item
    st.session_state.random_entry = data[st.session_state.qindex]

# Streamlit app
def quiz_app(data: list):

    # Check if the session state is already initialized
    if 'random_entry' not in st.session_state:
        #needed for the first time

        st.session_state.user_data = {}
        st.session_state.user_data['asked'] = []
        st.session_state.user_data['wrong'] = []
        st.session_state.user_data['correct'] = []

        # Load cookies
        load_cookies()

        # Select a random index and retrieve the item
        get_next_question(data)

    if 'reset_session' in st.session_state:
            st.session_state.user_data['asked'] = []
            st.session_state.user_data['wrong'] = []
            st.session_state.user_data['correct'] = []
            st.success("Session zurückgesetzt.")
            del st.session_state['reset_session']
    

    # Display the question
    random_entry = st.session_state.random_entry

    # Sidebar
    with st.sidebar:
        st.header("Übungen zur Heilpraktikerprüfung für Psychotherapie")

        col1, col2, col3 = st.columns(3)
        st.metric("Gesamt", len(data))
        st.metric("Abgefragt", len(st.session_state.user_data["asked"]))
        st.metric("Richtig", len(st.session_state.user_data["correct"]))
        st.metric("Falsch", len(st.session_state.user_data["wrong"]))
    
        if st.button('Lernsession zurücksetzen'):
            reset_cookies()
            st.session_state.reset_session = 1 

        # if st.button('Speichern'):
        #     save_cookies()
        #     time.sleep(0.5)
            
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
        
        # update the counters
        if (st.session_state.flg_wrong == 0 and st.session_state.flg_correct == 1):
            st.session_state.user_data["correct"].append(st.session_state.qindex)

        if (st.session_state.flg_wrong == 1 and st.session_state.flg_correct == 0):
            st.session_state.user_data["wrong"].append(st.session_state.qindex)

        if (st.session_state.flg_wrong == 1 and st.session_state.flg_correct == 1):
            st.session_state.user_data["wrong"].append(st.session_state.qindex)

        st.session_state.user_data['asked'].append(st.session_state.qindex)

        get_next_question(data)

        # save cookies
        save_cookies()

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
    