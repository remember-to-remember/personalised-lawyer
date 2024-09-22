import requests
import streamlit as st
from streamlit_auth0_component import login_button

clientId = "NfCNgfVVeXernMyRVcu6GOkoCBUpurxN"
domain = "remember-to-remember.au.auth0.com"

user_info = login_button(clientId, domain=domain, audience="personalised-lawyer")
st.write(user_info)

if user_info:
    st.title("Secure API Client")

    api_url = st.text_input("API URL", value="http://localhost:8001/chat")

    def call_api(api_url, token):
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post("http://localhost:8001/chat", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            return {"error": str(err)}

    if st.button("Call API"):
        if not api_url or not user_info:
            st.error("API URL and Bearer Token are required")
        else:
            result = call_api(api_url, user_info.get("token", {}))
            st.write(result)
