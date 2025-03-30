import reflex as rx

from frontend.style import create_colors_dict


config = rx.Config(
    app_name='frontend',
    backend_port=9000,
    tailwind={
        'darkMode': 'class',
        'theme': {
            'colors': {
                **create_colors_dict(),
            },
        },
    },
)
