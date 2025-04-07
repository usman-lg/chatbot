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
    "Please enter your SearchAtlas JWT token, then click the 'Start Chatting' button."
)

# 3) Token input
st.session_state["searchatlas_jwt"] = st.text_input(
    "SearchAtlas JWT Token", 
    type="password", 
    value=st.session_state["searchatlas_jwt"]
)

# 4) Button to start chatting
if st.button("Start Chatting"):
    if not st.session_state["searchatlas_jwt"]:
        st.warning("Please provide your SearchAtlas JWT token.")
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['searchatlas_jwt']}",
            "Content-Type": "application/json",
        }

        # Restart chat session
        restart_resp = requests.post(
            "https://agent.searchatlas.com/api/v1/restart/",
            headers=headers,
        )

        if restart_resp.status_code == 200:
            st.success("Chat session restarted successfully.")

            # Reset session state for a clean chat
            st.session_state["messages"] = []
            st.session_state["start_chat"] = True

            # 🔥 Initial message
            initial_message = "Show me the analysis of the top 10 high-ranking site explorer websites and 10 low-ranking site explorer websites."

            response = requests.post(
                "https://agent.searchatlas.com/api/v1/chat/",
                json={"message": initial_message},
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                bot_reply = data.get("response", "No response received.")
                st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.markdown(bot_reply)
            else:
                error_msg = f"Error from /chat/: {response.text}"
                st.session_state["messages"].append({"role": "assistant", "content": error_msg})
                with st.chat_message("assistant"):
                    st.markdown(error_msg)
        else:
            st.error(f"Failed to restart chat session: {restart_resp.text}")

# 5) Display past messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6) Chat interface
if st.session_state["start_chat"]:
    searchatlas_jwt = st.session_state["searchatlas_jwt"]

    if prompt := st.chat_input("Ask me anything..."):
        message = {"role": "user", "content": prompt}
        st.session_state["messages"].append(message)
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

        # Send user prompt
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
            message = {"role": "assistant", "content": bot_message}
            st.session_state["messages"].append(message)
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        else:
            bot_message = f"Error calling Django API: {resp.text}"
            st.session_state["messages"].append({"role": "assistant", "content": bot_message})
            with st.chat_message("assistant"):
                st.markdown(bot_message)
