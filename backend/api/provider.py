""" Module for providers. """

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from structlog import get_logger

from backend.api import config
from backend.api.data_repositories.sqlite import SQLite
from backend.api.data_repository import DataRepository
from backend.api.enum import DataRepositoryType, InferenceProviderType
from backend.api.inference_provider_wrapper import InferenceProviderWrapper
from backend.api.inference_provider_wrappers.kubernetes_pod_wrapper import (
    KubernetesPodWrapper,
)
from backend.api.inference_provider_wrappers.runpod_serverless_api_wrapper import (
    RunpodServerlessAPIWrapper,
)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Providers:
    """Class for storing providers."""

    data_repository: DataRepository
    inference_provider_wrapper: InferenceProviderWrapper


PROVIDERS: Providers = None


def configure_providers() -> None:
    """Configure providers."""

    logger = get_logger().bind(
        DataRepositoryType=config.CONFIG.data_repository_type,
        InferenceProviderType=config.CONFIG.inference_provider_type,
    )
    logger.info("Starting configure providers")

    global PROVIDERS
    PROVIDERS = Providers(
        data_repository=_get_data_repository(config.CONFIG.data_repository_type),
        inference_provider_wrapper=_get_inference_provider_wrapper(
            config.CONFIG.inference_provider_type
        ),
    )

    logger.info("Completed configure providers")


def _get_data_repository(enum_type: DataRepositoryType) -> DataRepository:
    match enum_type:
        case DataRepositoryType.SQLITE:
            return SQLite()


def _get_inference_provider_wrapper(
    enum_type: InferenceProviderType,
) -> InferenceProviderWrapper:
    match enum_type:
        case InferenceProviderType.KUBERNETES_POD:
            return KubernetesPodWrapper()
        case InferenceProviderType.RUNPOD_SERVERLESS_API:
            return RunpodServerlessAPIWrapper()
