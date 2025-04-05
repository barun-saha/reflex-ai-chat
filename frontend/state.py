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


# To indicate that the streaming response has begun
STREAMING_MARKER = 'Just a moment...'
# The input text field
CHAT_TEXT_INPUT = 'input-query'
# Reference to the chat area component for scrolling
CHAT_SCROLL_ELEMENT = 'chat-scroll-area'


@dataclass
class MessageRole:
    """
    Define the roles of who generated the messages.
    """

    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'


class SettingsState(rx.State):
    """
    Display settings.
    """

    # The accent color for the app
    color: str = 'violet'
    # The font family for the app
    font_family: str = 'Poppins'


class ChatState(rx.State):
    """
    The LLM chat state with history.
    """

    # The current question being asked
    question: str
    # Whether the app is processing a question
    is_processing: bool = False
    # Keep track of the chat history
    chat_history: list[dict[str, str]] = []
    model: str = 'gemini/gemini-2.0-flash-lite'
    user_id: str = str(uuid.uuid4())

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

    async def handle_query_submission(self, form_data: dict):
        """
        Handle the Enter key press in the query form.

        Args:
            form_data: Data submitted via form.
        """

        query = form_data['input_query'].strip()

        if query:
            self.question = query
            yield

            self.is_processing = True
            yield

            try:
                self.chat_history.append({'role': MessageRole.USER, 'content': query})
                self.chat_history.append(
                    {'role': MessageRole.ASSISTANT, 'content': STREAMING_MARKER})
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
