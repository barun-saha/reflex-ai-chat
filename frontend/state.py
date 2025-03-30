import uuid
from dataclasses import dataclass

import litellm
import reflex as rx
from dotenv import load_dotenv
from litellm.types.utils import ModelResponseStream

load_dotenv()


@dataclass
class MessageRole:
    """
    Define the roles of who generated the messages.
    """

    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'


class SettingsState(rx.State):
    # The accent color for the app
    color: str = 'violet'
    # The font family for the app
    font_family: str = 'Poppins'


class ChatState(rx.State):
    # The current question being asked
    question: str
    # Capture the streaming response
    streaming_content: str = ''
    # Whether the app is processing a question
    processing: bool = False
    # Keep track of the chat history
    chat_history: list[dict[str, str]] = []
    model: str = 'gemini/gemini-2.0-flash-lite'
    user_id: str = str(uuid.uuid4())

    async def answer(self):
        self.processing = True
        yield

        query = self.question
        self.question = ''
        yield

        try:
            self.chat_history.append({'role': MessageRole.USER, 'content': query})
            self.streaming_content = '' # Reset the streaming content
            async for chunk in await litellm.acompletion(
                    model=self.model,
                    messages=self.chat_history,
                    response_format=None,
                    temperature=0.01,
                    max_tokens=512,
                    stream=True,
                    metadata={'session_id': self.user_id},  # Set langfuse Session ID
            ):  # type: ModelResponseStream
                if 'choices' in chunk and chunk['choices'][0]['delta']:
                    delta_content = chunk['choices'][0]['delta'].content
                    if delta_content:
                        self.streaming_content += str(delta_content)
                        yield

            self.chat_history.append(
                {'role': MessageRole.ASSISTANT, 'content': self.streaming_content}
            )
            yield
            self.streaming_content = ''
        except Exception as e:
            self.streaming_content = f'An error occurred: {e}'
            yield
            self.chat_history.append(
                {'role': MessageRole.ASSISTANT, 'content': self.streaming_content}
            )
        finally:
            self.processing = False
            yield

    def get_history(self) -> list[dict[str, str]]:
        """
        Get the conversation history.

        Returns:
            A list of messages exchanged between the user and the LLM.
        """
        return self.chat_history

    def clear_chat_history(self):
        """
        Clear the chat history.
        """
        self.chat_history = []

    async def handle_key_down(self, key: str):
        if key == 'Enter':
            async for t in self.answer():
                yield t

            self.question = ''
            yield
