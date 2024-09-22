/* global __DEV__ */
import { Streamlit } from "streamlit-component-lib";
import {
  AuthenticationError,
  Auth0Client,
  GetTokenSilentlyOptions,
  GetTokenWithPopupOptions,
  User,
  createAuth0Client,
  LogoutOptions,
} from "@auth0/auth0-spa-js";
import "toastify-js/src/toastify.css";
import "./style.css";

interface EventDetailAuth0Args {
  client_id: string;
  domain: string;
  audience: string;
}

interface StreamlitEventDetailAuth0Args extends CustomEvent {
  detail: {
    args: EventDetailAuth0Args;
  };
}

const div = document.body.appendChild(document.createElement("div"));
const button = div.appendChild(document.createElement("button"));
button.className = "log";
button.textContent = "Login";

div.style.display = "flex";
div.style.flexDirection = "column";
div.style.color = "rgb(104, 85, 224)";
div.style.fontWeight = "600";
div.style.margin = "0";
div.style.padding = "10px";

const errorNode = div.appendChild(document.createTextNode(""));

const debugOutput = document.createElement("pre");
document.body.appendChild(debugOutput);

let auth0: Auth0Client;
let auth0EventArgs: EventDetailAuth0Args;

if (__DEV__) {
  try {
    auth0EventArgs = {
      client_id: import.meta.env.VITE_APP_AUTH0_CLIENT_ID,
      domain: import.meta.env.VITE_APP_AUTH0_DOMAIN,
      audience: "",
    };
    auth0EventArgs.audience = `https://${auth0EventArgs.domain}/api/v2/`;
    console.log("SET ARGS from import.meta.env", { auth0EventArgs });
  } catch {}
}

const logout = async () => {
  // this was returning a type error for "returnTo"
  // const logoutResult = await auth0.logout({ returnTo: getOriginUrl() });
  const logoutResult = await auth0.logout({
    logoutParams: { returnTo: getOriginUrl() },
  });
  console.log({ logoutResult });
  button.textContent = "Login";
  button.removeEventListener("click", logout);
  button.addEventListener("click", login);
};

const login = async () => {
  const { domain, client_id, audience } = auth0EventArgs;
  button.textContent = "working...";
  console.log("Callback urls set to: ", getOriginUrl());
  auth0 = await createAuth0Client({
    domain: domain,
    clientId: client_id,
    authorizationParams: {
      redirect_uri: getOriginUrl(),
      audience,
    },
    cacheLocation: "localstorage",
    useRefreshTokens: true,
  });
  try {
    await auth0.loginWithPopup();
    errorNode.textContent = "";
  } catch (err) {
    console.error(err);
    errorNode.textContent =
      `Popup blocked, please try again or enable popups` +
      String.fromCharCode(160);
    return;
  }
  const user = await auth0.getUser();
  console.log({ user });
  let token = null;

  try {
    const options: GetTokenSilentlyOptions = {
      authorizationParams: {
        audience,
      },
    };
    token = await auth0.getTokenSilently(options);
  } catch (error) {
    console.error(error);
    if (error instanceof AuthenticationError) {
      if (
        error.error === "consent_required" ||
        error.error === "login_required"
      ) {
        console.log("asking user for permission to their profile");
        const options: GetTokenWithPopupOptions = {
          authorizationParams: {
            audience,
          },
        };
        token = await auth0.getTokenWithPopup(options);
      }
    }
  }

  let userCopy: User & { token?: string | null } = JSON.parse(
    JSON.stringify(user),
  );
  userCopy.token = token;
  console.log({ userCopy });
  Streamlit.setComponentValue(userCopy);
  button.textContent = "Logout";
  button.removeEventListener("click", login);
  button.addEventListener("click", logout);

  if (__DEV__) {
    debugOutput.textContent = JSON.stringify(userCopy, null, 2);
  }
};

button.onclick = login;

function onRender(event: StreamlitEventDetailAuth0Args | Event | null) {
  if (!isStreamlitEventDetailAuth0Args(event)) {
    throw new Error("Event is not of type StreamlitEventDetailAuth0Args");
  }
  auth0EventArgs = event.detail.args;

  console.log("args from python", { auth0EventArgs });

  Streamlit.setFrameHeight();
}

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();

const getOriginUrl = (): string => {
  if (window.parent !== window) {
    const currentIframeHref = new URL(document.location.href);
    const urlOrigin = currentIframeHref.origin;
    const urlFilePath = decodeURIComponent(currentIframeHref.pathname);
    return urlOrigin + urlFilePath;
  } else {
    return window.location.origin;
  }
};

function isStreamlitEventDetailAuth0Args(
  event: CustomEvent | Event | null,
): event is StreamlitEventDetailAuth0Args {
  return event !== null && "detail" in event && "args" in event.detail;
}
