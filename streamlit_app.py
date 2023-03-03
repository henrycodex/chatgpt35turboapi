import streamlit as st
import os
import json
import requests

#api_key = config.OPENAI_API_KEY

# Streaming endpoint
API_URL = "https://api.openai.com/v1/chat/completions"

# Testing with my Open AI Key
api_key = os.getenv("OPENAI_API_KEY")


def predict(inputs, top_p, temperature, chat_counter, chatbot=[], history=[]):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"{inputs}"}],
        "temperature": 1.0,
        "top_p": 1.0,
        "n": 1,
        "stream": True,
        "presence_penalty": 0,
        "frequency_penalty": 0,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    if chat_counter != 0:
        messages = []
        for data in chatbot:
            temp1 = {}
            temp1["role"] = "user"
            temp1["content"] = data[0]
            temp2 = {}
            temp2["role"] = "assistant"
            temp2["content"] = data[1]
            messages.append(temp1)
            messages.append(temp2)
        temp3 = {}
        temp3["role"] = "user"
        temp3["content"] = inputs
        messages.append(temp3)
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "n": 1,
            "stream": True,
            "presence_penalty": 0,
            "frequency_penalty": 0,
        }

    chat_counter += 1

    history.append(inputs)

    response = requests.post(API_URL, headers=headers, json=payload, stream=True)

    token_counter = 0
    partial_words = ""

    counter = 0
    for chunk in response.iter_lines():
        if counter == 0:
            counter += 1
            continue
        counter += 1
        if chunk:
            if len(json.loads(chunk.decode()[6:])['choices'][0]["delta"]) == 0:
                break
            partial_words = partial_words + json.loads(chunk.decode()[6:])['choices'][0]["delta"]["content"]
            if token_counter == 0:
                history.append(" " + partial_words)
            else:
                history[-1] = partial_words
            chat = [(history[i], history[i + 1]) for i in range(0, len(history) - 1, 2)]
            token_counter += 1
            return chat, history, chat_counter


def reset_textbox():
    return st.empty()


def main():
    st.markdown("<h2 style='text-align: center; color: #023047;'>🔥ChatGPT Turbo API 3.5🔥</h2>", unsafe_allow_html=True)
    st.markdown("<center><a href=''><img src='' alt=''></a></center>", unsafe_allow_html=True)

    chatbot = st.chatbot()
    inputs = st.text_input("ChatGPT 3.5 Turbo API", placeholder="Hello! You can speak to ChatGPT about anything that's on your mind.")
    state = st.session_state.get("state", [])
    b1 = st.button("Send")

    with st.beta_expander("Advanced Settings
