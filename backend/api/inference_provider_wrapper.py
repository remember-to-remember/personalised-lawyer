""" Module for inference provider wrapper. """

from abc import ABC, abstractmethod


class InferenceProviderWrapper(ABC):
    """Class for inference provider wrapper."""

    @abstractmethod
    def request_for_inference(
        job_id: str,
        content_file_urls: list[str],
        prompt_text: str,
        output_blob_container: str = None,
        output_blob_paths: list[str] = [],
    ):
        """Request for inference."""
