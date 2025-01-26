from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class InlineKeyboardManager:
    """Класс для управления inline-клавиатурами"""
    
    def __init__(self):
        self._like_button = InlineKeyboardButton(
            text="Что понравилось",
            callback_data="like"
        )
        self._improve_button = InlineKeyboardButton(
            text="Что можно добавить",
            callback_data="improve"
        )

    def get_feedback_keyboard(self) -> InlineKeyboardMarkup:
        """Создает и возвращает клавиатуру для выбора типа отзыва"""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [self._like_button],
                [self._improve_button]
            ]
        )
