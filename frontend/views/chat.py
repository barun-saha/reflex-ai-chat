import reflex as rx

from frontend.components.badge import made_with_reflex
from frontend.state import ChatState


def message_display(message: dict) -> rx.Component:
    def user_message():
        return rx.box(
            rx.markdown(
                message['content'],
                class_name='[&>p]:!my-2.5',
            ),
            class_name='relative bg-slate-3 px-5 rounded-3xl max-w-[70%] text-slate-12 self-end',
        )

    def assistant_message():
        return rx.box(
            rx.box(
                rx.image(
                    src='llama.svg',
                    class_name='h-6' + rx.cond(ChatState.processing, ' animate-pulse', ''),
                ),
            ),
            rx.box(
                rx.markdown(
                    rx.cond(
                        ChatState.processing & (message == ChatState.chat_history[-1]),
                        ChatState.streaming_content,  # Show incremental streaming content
                        message['content'],  # Show finalized content
                    ),
                    class_name='[&>p]:!my-2.5',
                ),
                rx.box(
                    rx.el.button(
                        rx.icon(tag='copy', size=18),
                        class_name='p-1 text-slate-10 hover:text-slate-11 transform transition-colors cursor-pointer',
                        on_click=[rx.set_clipboard(message['content']), rx.toast('Copied!')],
                        title='Copy',
                    ),
                    class_name='-bottom-9 left-5 absolute opacity-0 group-hover:opacity-100 transition-opacity',
                ),
                class_name='relative bg-accent-4 px-5 rounded-3xl max-w-[70%] text-slate-12 self-start',
            ),
            class_name='flex flex-row gap-6',
        )

    return rx.box(
        rx.cond(
            message['role'] == 'user',
            user_message(),
            assistant_message(),
        ),
        class_name='flex flex-col gap-8 pb-10 group',
    )


def chat() -> rx.Component:
    return rx.scroll_area(
        rx.vstack(
            rx.foreach(
                ChatState.chat_history,
                lambda message: message_display(message),
            ),
        ),
        scrollbars='vertical',
        class_name='w-full',
    )


def action_bar() -> rx.Component:
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
                    ChatState.processing,
                    rx.icon(
                        tag='loader-circle',
                        size=19,
                        color='white',
                        class_name='animate-spin',
                    ),
                    rx.icon(tag='arrow-up', size=19, color='white'),
                ),
                on_click=[ChatState.answer, rx.set_value("input1", "")],
                class_name='top-1/2 right-4 absolute bg-accent-9 hover:bg-accent-10 disabled:hover:bg-accent-9 opacity-65 disabled:opacity-50 p-1.5 rounded-full transition-colors -translate-y-1/2 cursor-pointer disabled:cursor-default',
                disabled=rx.cond(
                    ChatState.processing | (ChatState.question == ''), True, False
                ),
            ),
            class_name='relative w-full',
        ),
        # Made with Reflex link
        made_with_reflex(),
        class_name='flex flex-col justify-center items-center gap-6 w-full',
    )
