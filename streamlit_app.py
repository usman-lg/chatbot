import streamlit as st
import requests
from openai import OpenAI

# 1) Session state for storing keys and chat messages
if "searchatlas_jwt" not in st.session_state:
    st.session_state["searchatlas_jwt"] = ""
if "start_chat" not in st.session_state:
    st.session_state["start_chat"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 2) Title and instructions
st.title("💬 AI Agent")

st.write(
    "This simple chatbot uses OpenAI's GPT-4o-mini model to generate responses. "
    "Please enter your OpenAI API key and your SearchAtlas JWT token, then click the 'Start Chatting' button."
)

# 3) Let the user enter tokens
st.session_state["searchatlas_jwt"] = st.text_input(
    "SearchAtlas JWT Token", 
    type="password", 
    value=st.session_state["searchatlas_jwt"]
)

# 4) Button to start chatting
if st.button("Start Chatting"):
    st.session_state.clear()
    if not st.session_state["searchatlas_jwt"]:
        st.warning("Please provide both your OpenAI API key and SearchAtlas JWT token.")
    else:
        st.session_state["start_chat"] = True

        # Restart the chat session using the specified endpoint
        headers = {
            "Authorization": f"Bearer {st.session_state['searchatlas_jwt']}",
            "Content-Type": "application/json",
        }
        restart_resp = requests.post(
            "https://agent.searchatlas.com/api/v1/restart/",
            headers=headers,
        )
        if restart_resp.status_code == 200:
            st.success("Chat session restarted successfully.")
        else:
            st.error(f"Failed to restart chat session: {restart_resp.text}")
            
        resp = requests.get(
            "https://agent.searchatlas.com/api/v1/preloaded-data/",
            headers=headers,
        )
    
        if resp.status_code == 200:
            django_data = resp.json()
            bot_message = django_data.get("response", "No response")
            message = {"role": "assistant", "content": bot_message[0]}
            st.session_state["messages"].append({"role": "assistant", "content": bot_message})
        else:
            bot_message = f"Error calling Django API: {resp.text}"	

# Display previous messages from session state
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5) Chat interface
if st.session_state["start_chat"]:
    searchatlas_jwt = st.session_state["searchatlas_jwt"]

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        message = {"role": "user", "content": prompt}
        st.session_state["messages"].append(message)
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

        # Call Django endpoint with JWT
        headers = {
            "Authorization": f"Bearer {searchatlas_jwt}",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            "https://agent.searchatlas.com/api/v1/chat/",
            json={"message": prompt},
            headers=headers,
        )
        if resp.status_code == 200:
            django_data = resp.json()
            bot_message = django_data.get("response", "No response")
            print(django_data)
            message = {"role": "assistant", "content": bot_message}
            st.session_state["messages"].append({"role": "assistant", "content": bot_message})
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        else:
            bot_message = f"Error calling Django API: {resp.text}"	
