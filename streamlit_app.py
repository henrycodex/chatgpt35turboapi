import streamlit as st
import os 
import json 
import requests

#api_key = config.OPENAI_API_KEY

#Streaming endpoint
API_URL = "https://api.openai.com/v1/chat/completions" 

#Testing with my Open AI Key 
api_key = os.getenv("OPENAI_API_KEY") 

def predict(inputs, top_p, temperature, chat_counter, chatbot=[], history=[]):  #repetition_penalty, top_k

    payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": f"{inputs}"}],
    "temperature" : 1.0,
    "top_p":1.0,
    "n" : 1,
    "stream": True,
    "presence_penalty":0,
    "frequency_penalty":0,
    }

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    print(f"chat_counter - {chat_counter}")
    if chat_counter != 0 :
        messages=[]
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
        #messages
        payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages, #[{"role": "user", "content": f"{inputs}"}],
        "temperature" : temperature, #1.0,
        "top_p": top_p, #1.0,
        "n" : 1,
        "stream": True,
        "presence_penalty":0,
        "frequency_penalty":0,
        }

    chat_counter+=1

    history.append(inputs)
    print(f"payload is - {payload}")
    # make a POST request to the API endpoint using the requests.post method, passing in stream=True
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    #response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    token_counter = 0 
    partial_words = "" 

    counter=0
    for chunk in response.iter_lines():
        if counter == 0:
          counter+=1
          continue
        counter+=1
        # check whether each line is non-empty
        if chunk :
          # decode each line as response data is in bytes
          if len(json.loads(chunk.decode()[6:])['choices'][0]["delta"]) == 0:
            break
          #print(json.loads(chunk.decode()[6:])['choices'][0]["delta"]["content"])
          partial_words = partial_words + json.loads(chunk.decode()[6:])['choices'][0]["delta"]["content"]
          if token_counter == 0:
            history.append(" " + partial_words)
          else:
            history[-1] = partial_words
          chat = [(history[i], history[i + 1]) for i in range(0, len(history) - 1, 2) ]  # convert to tuples of list
          token_counter+=1
          yield chat, history, chat_counter  # resembles {chatbot: chat, state

def train_chats(chatbot, conversations):
    token_counter = 0
    chat_counter = 0
    for conversation in conversations:
        history = []
        for message in conversation:
            text = message.text
            history.append(text)
            if len(history) > 1:
                chat = [(history[i], history[i + 1]) for i in range(0, len(history) - 1, 2) ]  # convert to tuples of list
                token_counter += 1
                yield chat, history, chat_counter  # resembles {chatbot: chat, state}
                chat_counter += 1

chatbot = st.chatbot()
inputs = st.text_input("ChatGPT 3.5 Turbo API", value="Hello! You can speak to ChatGPT about anything thats on your mind.")
state = []
top_p = st.slider("Top-p (nucleus sampling)", min_value=0.1, max_value=1.0, step=0.1)

