from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class ReplyKeyboardManager:
    """Класс для управления reply-клавиатурами"""
    
    def __init__(self):
        self._feedback_button = KeyboardButton(text="Обратная связь")
        self._help_button = KeyboardButton(text="Помощь")
        self._recommendations_button = KeyboardButton(text="Цифровые ресурсы")

    def get_main_keyboard(self) -> ReplyKeyboardMarkup:
        """Создает и возвращает основную клавиатуру"""
        return ReplyKeyboardMarkup(
            keyboard=[
                [self._feedback_button],
                [self._help_button, self._recommendations_button]
            ],
            resize_keyboard=True,
            input_field_placeholder="Выберите действие"
        )
