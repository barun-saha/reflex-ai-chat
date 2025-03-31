"""
The chat area view module.

This module defines the chat interface for an AI chat application. It includes components
to display chat bubbles, manage the chat area, and an action bar for user inputs.
"""

import reflex as rx
from frontend.components.badge import made_with_reflex
from frontend.state import ChatState, MessageRole


# Shared style for the chat bubbles to dynamically adjust to their content
CHAT_BUBBLE_STYLE = {
    'display': 'inline-block',  # Dynamically adjust to content width
    'max-width': '80%',  # Prevent bubbles from becoming too wide
    'min-width': '10%',  # Set a minimum width for aesthetic consistency
    'word-wrap': 'break-word',  # Ensure long words break properly
}


def message_display(message: dict) -> rx.Component:
    """
    Display a single chat message as a bubble.

    Args:
        message (dict): A dictionary containing the message content and role (user or assistant).

    Returns:
        rx.Component: A Reflex component representing the chat bubble for the message.
    """
    def user_message():
        """
        Create a user message bubble aligned to the right.

        Returns:
            rx.Component: The user message bubble with left-aligned text.
        """
        return rx.box(
            rx.markdown(
                message['content'],
                class_name='[&>p]:!my-2.5 text-left',  # Text aligns to the left
            ),
            class_name=(
                'relative bg-slate-3 px-5 py-2 rounded-3xl text-slate-12 self-end'
            ),
            style=CHAT_BUBBLE_STYLE,
        )

    def assistant_message():
        """
        Create an assistant message bubble aligned to the left.

        Returns:
            rx.Component: The assistant message bubble with left-aligned text.
        """
        return rx.box(
            rx.image(
                src='llama.svg',
                class_name='h-6' + rx.cond(ChatState.is_processing, ' animate-pulse', ''),
            ),
            rx.box(
                rx.markdown(
                    message['content'],
                    class_name='[&>p]:!my-2.5 text-left',  # Text aligns to the left
                ),
                class_name=(
                    'relative bg-accent-4 px-5 py-2 rounded-3xl text-slate-12 self-start'
                ),
                style=CHAT_BUBBLE_STYLE,
            ),
            class_name='flex flex-row gap-6',
        )

    return rx.box(
        rx.cond(
            message['role'] == MessageRole.USER,
            user_message(),
            assistant_message(),
        ),
        class_name='flex flex-col gap-8 pb-10 group',
    )


def chat() -> rx.Component:
    """
    Create the chat area component.

    This component displays the chat history in a scrollable area.

    Returns:
        rx.Component: The scrollable chat area containing all chat bubbles.
    """
    return rx.scroll_area(
        rx.vstack(
            rx.foreach(
                ChatState.chat_history,
                lambda message: message_display(message),
            ),
            class_name='w-full flex flex-col items-stretch',  # Allows full-width flexibility
        ),
        scrollbars='vertical',
        class_name='w-full h-full',  # Ensures proper scrolling behavior
    )


def action_bar() -> rx.Component:
    """
    Create the action bar component.

    This component includes an input field for user queries and a send button to submit them.

    Returns:
        rx.Component: The action bar for user interactions.
    """
    return rx.box(
        rx.box(
            rx.el.input(
                placeholder='Ask me anything',
                on_blur=ChatState.set_question,
                on_key_down=ChatState.handle_key_down,
                id='input1',
                class_name='box-border bg-slate-3 px-4 py-2 pr-14 rounded-full w-full outline-none focus:outline-accent-10 h-[48px] text-slate-12 placeholder:text-slate-9',
            ),
            rx.el.button(
                rx.cond(
                    ChatState.is_processing,
                    rx.icon(
                        tag='loader-circle',
                        size=19,
                        color='white',
                        class_name='animate-spin',
                    ),
                    rx.icon(tag='arrow-up', size=19, color='white'),
                ),
                on_click=[ChatState.answer, rx.set_value('input1', '')],
                class_name='top-1/2 right-4 absolute bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default',
                disabled=rx.cond(
                    ChatState.is_processing | (ChatState.question == ''), True, False
                ),
            ),
            class_name='relative w-full',
        ),
        # Made with Reflex link
        made_with_reflex(),
        class_name='flex flex-col justify-center items-center gap-6 w-full',
    )
