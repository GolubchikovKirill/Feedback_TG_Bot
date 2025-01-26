import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.database import DatabaseManager, FeedbackRepository, FeedbackModel, Base

# Фикстура для тестовой базы данных
@pytest.fixture
def test_db():
    # Используем SQLite в памяти для тестов
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@pytest.fixture
def db_manager():
    return DatabaseManager('sqlite:///:memory:')

@pytest.fixture
def feedback_repo(db_manager):
    return FeedbackRepository(db_manager)

def test_save_feedback(feedback_repo):
    # Тест сохранения отзыва
    result = feedback_repo.save_feedback(
        user_id=123,
        feedback_type="Понравилось",
        feedback_text="Тестовый отзыв"
    )
    assert result == True

    # Проверяем, что отзыв сохранился
    with feedback_repo.db_manager.get_session() as session:
        feedback = session.query(FeedbackModel).first()
        assert feedback is not None
        assert feedback.user_id == 123
        assert feedback.feedback_type == "Понравилось"
        assert feedback.feedback_text == "Тестовый отзыв"

def test_get_feedback_stats(feedback_repo):
    # Добавляем тестовые данные
    feedback_repo.save_feedback(1, "Понравилось", "Тест 1")
    feedback_repo.save_feedback(2, "Понравилось", "Тест 2")
    feedback_repo.save_feedback(3, "Добавить", "Тест 3")

    # Получаем статистику
    stats = feedback_repo.get_feedback_stats()
    
    assert stats["total"] == 3
    assert stats["likes"] == 2
    assert stats["improvements"] == 1

def test_get_user_feedback(feedback_repo):
    # Добавляем отзывы для разных пользователей
    feedback_repo.save_feedback(1, "Понравилось", "Отзыв 1")
    feedback_repo.save_feedback(1, "Добавить", "Отзыв 2")
    feedback_repo.save_feedback(2, "Понравилось", "Отзыв 3")

    # Получаем отзывы пользователя
    feedback_list = feedback_repo.get_user_feedback(1)
    
    assert len(feedback_list) == 2
    assert all(f.user_id == 1 for f in feedback_list)
