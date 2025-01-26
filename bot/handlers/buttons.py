import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import feedback_repository

logger = logging.getLogger(__name__)

class FeedbackStates(StatesGroup):
    """Состояния для FSM при сборе обратной связи"""
    waiting_for_feedback_text = State()

class FeedbackValidator:
    """Класс для валидации отзывов"""
    MAX_FEEDBACK_LENGTH = 1000
    MIN_FEEDBACK_LENGTH = 5

    @classmethod
    def validate(cls, text: str) -> tuple[bool, str]:
        """Валидация текста отзыва"""
        if len(text) > cls.MAX_FEEDBACK_LENGTH:
            return False, f"Текст слишком длинный. Максимальная длина: {cls.MAX_FEEDBACK_LENGTH} символов"
        if len(text.strip()) < cls.MIN_FEEDBACK_LENGTH:
            return False, "Пожалуйста, напиши более развернуто."
        return True, ""

class ButtonHandler:
    """Класс для обработки кнопок бота"""
    def __init__(self):
        self.router = Router()
        self.validator = FeedbackValidator()
        self._setup_handlers()

    def _setup_handlers(self):
        """Настройка обработчиков кнопок"""
        self.router.callback_query.register(
            self.handle_like,
            lambda callback: callback.data == "like"
        )
        self.router.callback_query.register(
            self.handle_improve,
            lambda callback: callback.data == "improve"
        )
        self.router.message.register(
            self.feedback_text_received,
            FeedbackStates.waiting_for_feedback_text,
            F.text
        )
        self.router.message.register(
            self.handle_invalid_feedback,
            FeedbackStates.waiting_for_feedback_text
        )

    async def handle_like(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик кнопки 'Что понравилось'"""
        await callback.answer()
        await state.update_data(feedback_type="Понравилось")
        await callback.message.answer(
            "Напиши, что понравилось:",
            parse_mode="HTML"
        )
        await state.set_state(FeedbackStates.waiting_for_feedback_text)
        logger.info(f"Пользователь {callback.from_user.id} начал оставлять положительный отзыв")

    async def handle_improve(self, callback: CallbackQuery, state: FSMContext):
        """Обработчик кнопки 'Что можно улучшить'"""
        await callback.answer()
        await state.update_data(feedback_type="Добавить")
        await callback.message.answer(
            "Напиши, что можно добавить:",
            parse_mode="HTML"
        )
        await state.set_state(FeedbackStates.waiting_for_feedback_text)
        logger.info(f"Пользователь {callback.from_user.id} начал оставлять предложения по улучшению")

    async def feedback_text_received(self, msg: Message, state: FSMContext):
        """Обработчик получения текста отзыва"""
        data = await state.get_data()
        feedback_type = data.get("feedback_type")
        feedback_text = msg.text

        # Валидация текста отзыва
        is_valid, error_message = self.validator.validate(feedback_text)
        if not is_valid:
            await msg.answer(error_message)
            return

        try:
            feedback_repository.save_feedback(
                user_id=msg.from_user.id,
                feedback_type=feedback_type,
                feedback_text=feedback_text
            )
            await msg.answer("Благодарю за обратную связь!")
            logger.info(f"Пользователь {msg.from_user.id} успешно оставил отзыв типа {feedback_type}")
        except Exception as e:
            error_msg = "Произошла ошибка при сохранении отзыва. Пожалуйста, попробуйте позже."
            logger.error(f"Ошибка при сохранении отзыва от пользователя {msg.from_user.id}: {str(e)}")
            await msg.answer(error_msg)
        finally:
            await state.clear()

    async def handle_invalid_feedback(self, msg: Message):
        """Обработчик неверного формата отзыва"""
        await msg.answer(
            "Пожалуйста, отправьте текстовое сообщение.",
            parse_mode="HTML"
        )

# Создаем экземпляр обработчика кнопок
button_handler = ButtonHandler()
router = button_handler.router
