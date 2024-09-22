""" Module for conversation api. """

from typing import Annotated

import uvicorn
from authlib.jose import JoseError, JsonWebKey, jwt
from authlib.jose.errors import ExpiredTokenError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from structlog import get_logger

from backend.api import config, main
from backend.api.entities import Caller, ChatInputModel

app = (
    FastAPI(
        title=f"Personalised Lawyer API",
    )
    if config.CONFIG
    else FastAPI()
)


@app.get("/")
async def get_root() -> dict[str, str]:
    """Get root path and check for required permission."""

    logger = get_logger()
    logger.info("Completed get root path - '/' from acceptor api")

    return {"msg": "Welcome to the Conversation API!"}


def decode_jwt(token: str, required_permission: str) -> str:
    """Decode JWT token."""

    try:
        payload = jwt.decode(
            token,
            JsonWebKey.import_key(config.CONFIG.auth0_public_key, {"kty": "RSA"}),
            claims_options={
                "iss": {"essential": True, "value": config.CONFIG.auth0_issuer},
                "aud": {"essential": True, "value": config.CONFIG.auth0_audience},
            },
        )
        payload.validate()

        permissions = payload.get("permissions", [])
        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        return payload.sub
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JoseError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {error}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_caller(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
) -> Caller:
    """Get caller from token."""

    idp_id = decode_jwt(token, "access:chat")
    caller = main.get_caller(idp_id)
    if caller:
        return caller

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.post("/chat")
async def post_chat(
    chat_input: ChatInputModel, caller: Annotated[Caller, Depends(get_caller)]
) -> str:
    """Post chat."""

    logger = get_logger()
    logger.info("Starting post chat - '/chat' from conversation api")

    chat_output = main.create_job(chat_input, caller)

    logger.info("Completed post chat - '/chat' from conversation api")
    return chat_output


# def create_job(job_request: JobRequestModel, caller: Caller) -> Job:
#     """Create job."""

#     logger = get_logger().bind(
#         job_request=(
#             job_request.model_dump(
#                 exclude=JobRequestModel.get_exclude_fields_for_logging(
#                     job_request.request_content_type
#                 )
#             )
#             if job_request
#             else None
#         ),
#         caller=(
#             {
#                 k: str(v)
#                 for k, v in caller.__dict__.items()
#                 if k not in Caller.get_exclude_fields_for_logging()
#             }
#             if caller
#             else None
#         ),
#     )
#     logger.info("Starting create job")

#     job = Job(**job_request.model_dump())
#     job.caller_id = caller.caller_id

#     # additional job fields set from configuration
#     job.inference_provider_type = config.CONFIG.inference_provider_type
#     job.inference_model_version = config.CONFIG.inference_model_version
#     job.inference_engine_version = config.CONFIG.inference_engine_version

#     provider.PROVIDERS.data_repository.save_job(job, caller=caller)

#     logger.info("Completed create job")
#     return job


def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from conversation api")

    main.init()

    # configure uvicorn logging formatters
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_default_formatter = uvicorn_log_config["formatters"]["default"]
    uvicorn_log_default_formatter["fmt"] = "%(asctime)s [%(levelprefix)s] %(message)s"
    uvicorn_log_access_formatter = uvicorn_log_config["formatters"]["access"]
    uvicorn_log_access_formatter["fmt"] = (
        '%(asctime)s [%(levelprefix)s] %(client_addr)s - "%(request_line)s" %(status_code)s'
    )
    uvicorn_log_access_formatter["datefmt"] = uvicorn_log_default_formatter[
        "datefmt"
    ] = "%Y-%m-%d %H:%M:%S"

    # run uvicorn
    uvicorn.run(
        "backend.api.conversation_api:app",
        host="localhost",
        port=config.CONFIG.conversation_api_port,
        reload=config.CONFIG.conversation_api_reload,
        log_level="debug" if config.CONFIG.debug_mode else "info",
    )

    logger.info("Completed init from conversation api")


if __name__ == "__main__":
    init()
