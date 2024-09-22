import os
import streamlit.components.v1 as components
import urllib.request as req
import json
from jose import jwt

_RELEASE = False
_RELEASE = True


if not _RELEASE:
    _login_button = components.declare_component(
        "auth0_login_button",
        url="http://localhost:8080/personalised-lawyer",  # vite dev server port
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _login_button = components.declare_component("auth0_login_button", path=build_dir)


class LoginButtonManager:
    def __init__(self, client_id, domain):
        self.client_id = client_id
        self.domain = domain
        self.audience = f"personalised-lawyer"

    def get_verified_sub(self, token):
        rsa_key = self.get_public_key(token)

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=self.audience,
                # issuer=domain + "/",
            )
        except jwt.ExpiredSignatureError:
            raise
        except jwt.JWTClaimsError:
            raise
        except Exception:
            raise

        return payload["sub"]

    def get_jwks(self):
        jwks_url = f"https://{self.domain}/.well-known/jwks.json"
        jwks = req.urlopen(jwks_url).read()
        jwks = json.loads(jwks)
        return jwks

    def get_public_key(self, token):
        jwks = self.get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        if "kid" not in unverified_header:
            raise ValueError("Authorization malformed.")
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        if rsa_key:
            return rsa_key
        raise ValueError("Public key not found.")

    def is_auth(self, response):
        return self.get_verified_sub(response["token"]) == response["sub"]


def login_button(clientId, domain, key=None, **kwargs):
    """Create a new instance of "login_button".
    Parameters
    ----------
    clientId: str
        client_id per auth0 config on your Applications / Settings page

    domain: str
        domain per auth0 config on your Applications / Settings page in the form dev-xxxx.us.auth0.com
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    Returns
    -------
    dict
        User info
    """
    manager = LoginButtonManager(client_id=clientId, domain=domain)
    user_info = _login_button(
        client_id=clientId, domain=domain, key=key, audience=manager.audience, default=0
    )

    if not user_info:
        return False
    elif manager.is_auth(response=user_info):
        return user_info
    else:
        print("Auth failed: invalid token")
        raise


if not _RELEASE:
    import streamlit as st
    from dotenv import load_dotenv
    import os

    load_dotenv()

    clientId = os.environ["clientId"]
    domain = os.environ["domain"]
    st.subheader("Login component")
    user_info = login_button(clientId, domain=domain)
    # user_info = login_button(clientId = "...", domain = "...")
    st.write("User info")
    st.write(user_info)
    if st.button("rerun"):
        st.experimental_rerun()
