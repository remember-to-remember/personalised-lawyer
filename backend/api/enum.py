""" Module for enumerations. """

from enum import StrEnum, auto


class DataRepositoryType(StrEnum):
    """Class for storing data repository type enumeration."""

    SQLITE = auto()


class InferenceProviderType(StrEnum):
    """Class for storing inference provider type enumeration."""

    KUBERNETES_POD = auto()
    RUNPOD_SERVERLESS_API = auto()


class AttachmentType(StrEnum):
    """Class for storing input/response related file type."""

    TEXT_FILE = auto()
    PDF_FILE = auto()
    AUDIO_FILE = auto()
