import requests
import streamlit as st
from streamlit_auth0_component import login_button

from frontend.app import config

user_info = login_button(
    config.CONFIG.auth0_client_id,
    domain=config.CONFIG.auth0_domain,
    audience="personal-ai-assistant",
)
st.write(user_info)

if user_info:
    st.title("Secure API Client")

    api_url = st.text_input("API URL", value="https://api.remember2.co:8001/chat")
    query_text = st.text_input("Query Text", value="Hello, how are you?")

    def call_api(api_url, token, query_text):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json={"caller_chat_text": f"{query_text}"},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            return {"error": str(err)}

    if st.button("Call API"):
        if not api_url or not user_info:
            st.error("API URL and Bearer Token are required")
        else:
            token = user_info.get("token", "")
            result = call_api(api_url, token, query_text)
            st.write(result)
