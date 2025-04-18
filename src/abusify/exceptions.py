class AbusifyException(RuntimeError):
    """
    Raised when a lower‑level operation fails while processing a Spotify URL.

    Attributes
    ----------
    url : str
        The Spotify HTTPS URL whose processing failed.
    """

    def __init__(self, url: str, message: str):
        super().__init__(message)
        self.url = url
