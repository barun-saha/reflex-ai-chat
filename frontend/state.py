"""
AI chat state with streaming response.
"""
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


STREAMING_MARKER = 'Just a moment...'


class SettingsState(rx.State):
    # The accent color for the app
    color: str = 'violet'
    # The font family for the app
    font_family: str = 'Poppins'


class ChatState(rx.State):
    # The current question being asked
    question: str
    # Whether the app is processing a question
    is_processing: bool = False
    # Keep track of the chat history
    chat_history: list[dict[str, str]] = []
    model: str = 'gemini/gemini-2.0-flash-lite'
    user_id: str = str(uuid.uuid4())

    async def answer(self):
        self.is_processing = True
        yield

        query = self.question
        self.question = ''
        yield

        try:
            self.chat_history.append({'role': MessageRole.USER, 'content': query})
            self.chat_history.append({'role': MessageRole.ASSISTANT, 'content': STREAMING_MARKER})
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
                        if self.chat_history[-1]['content'] == STREAMING_MARKER:
                            self.chat_history[-1]['content'] = str(delta_content)
                        else:
                            self.chat_history[-1]['content'] += str(delta_content)

                        yield
        except Exception as e:
            self.chat_history[-1]['content'] = f'An error occurred: {e}'
            yield
        finally:
            self.is_processing = False
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
