""" Module for kubernetes pod wrapper. """

from backend.api.inference_provider_wrapper import InferenceProviderWrapper


class KubernetesPodWrapper(InferenceProviderWrapper):
    """Class for kubernetes pod wrapper."""

    def request_for_inference(
        self,
        job_id: str,
        content_file_urls: list[str],
        prompt_text: str,
        output_blob_container: str = None,
        output_blob_paths: list[str] = [],
    ):
        """Request for inference."""
