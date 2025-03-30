import reflex as rx
from frontend.state import ChatState
from frontend.components.hint import hint


def reset() -> rx.Component:
    return hint(
        text='New Chat',
        content=rx.box(
            rx.icon(
                tag='square-pen',
                size=22,
                stroke_width='1.5',
                class_name='!text-slate-10',
            ),
            class_name='hover:bg-slate-3 p-2 rounded-xl transition-colors cursor-pointer',
            on_click=ChatState.clear_chat_history,
        ),
        side='bottom',
    )
