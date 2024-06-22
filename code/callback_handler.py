import json
from langchain.callbacks import StreamingStdOutCallbackHandler


class ChatOpsStreamingHandler(StreamingStdOutCallbackHandler):

    def __init__(self) -> None:
        self.tokens = []

    def on_llm_start(
            self, serialized, prompts, **kwargs) -> None:
        print("Prompts", prompts)
        print("Serialized", serialized)

        """Run when LLM starts running."""

    def on_chat_model_start(self, serialized, messages, **kwargs):
        """Run when LLM starts running."""
        print("LLM started")

    def on_llm_new_token(self, token: str, **kwargs):
        try:
            """Run on new LLM token. Only available when streaming is enabled."""
            self.tokens.extend(token)
        except Exception as e:
            print(str(e))

    def on_llm_end(self, response, **kwargs) -> None:
        """Run when LLM ends running."""
        print("LLM ended")
