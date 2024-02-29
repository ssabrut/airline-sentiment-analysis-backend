from sentence_transformers import SentenceTransformer


class Embedding:
    """
    Embedding class to embed the text using the sentence transformer model

    Args:
    ----
    model_name: str
    """

    def __init__(self, model_name="intfloat/e5-small-v2"):
        self.embedder = SentenceTransformer(model_name)

    def encode(self, text: str):
        """
        Encode the text using the sentence transformer model

        Args:
        ----
        text: str

        Returns:
        ----
        list: list of float
        """

        return self.embedder.encode(text)
