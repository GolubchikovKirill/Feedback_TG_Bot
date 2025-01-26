from sqlalchemy import create_engine, Column, Integer, String, Text, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from contextlib import contextmanager
from typing import  Dict
import logging
from config import DATABASE_URL

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

Base = declarative_base()


class FeedbackModel(Base):
    """Модель для хранения отзывов в базе данных"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    feedback_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    chat_id = Column(BigInteger, nullable=True)
    user_id = Column(Integer, nullable=True)
    feedback_text = Column(Text(500), nullable=True)

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, type={self.feedback_type}, user_id={self.user_id})>"


class DatabaseManager:
    """Класс для управления подключением к базе данных и операциями с ней"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._drop_and_create_tables()

    def _drop_and_create_tables(self) -> None:
        """Удаление и создание таблиц в базе данных"""
        # Base.metadata.drop_all(bind=self.engine)  # Удаляем все таблицы
        Base.metadata.create_all(bind=self.engine)  # Создаем таблицы заново
        logger.info("Database tables dropped and created successfully")

    @contextmanager
    def get_session(self) -> Session:
        """Контекстный менеджер для работы с сессией базы данных"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


class FeedbackRepository:
    """Репозиторий для работы с отзывами"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_feedback(self, user_id: int, feedback_type: str, feedback_text: str) -> bool:
        """Сохранение нового отзыва"""
        try:
            with self.db_manager.get_session() as session:
                logger.info(f"Сохранение отзыва от пользователя {user_id}")
                feedback = FeedbackModel(
                    user_id=user_id,
                    feedback_type=feedback_type,
                    feedback_text=feedback_text,
                    # Убираем ссылку на 'content', так как этого поля больше нет в таблице
                )
                session.add(feedback)
                logger.info(f"Отзыв от пользователя {user_id} успешно сохранен")
                return True
        except IntegrityError as e:
            logger.error(f"Ошибка целостности данных при сохранении отзыва: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при сохранении отзыва: {str(e)}")
            raise

    def get_feedback_stats(self) -> Dict[str, int]:
        """Получение статистики по отзывам"""
        try:
            with self.db_manager.get_session() as session:
                total_feedback = session.query(FeedbackModel).count()
                likes = session.query(FeedbackModel).filter_by(feedback_type="Понравилось").count()
                improvements = session.query(FeedbackModel).filter_by(feedback_type="Добавить").count()

                return {
                    "total": total_feedback,
                    "likes": likes,
                    "improvements": improvements
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {str(e)}")
            raise

    def get_user_feedback(self, user_id: int) -> list[FeedbackModel]:
        """Получение всех отзывов пользователя"""
        try:
            with self.db_manager.get_session() as session:
                return session.query(FeedbackModel).filter_by(user_id=user_id).all()
        except Exception as e:
            logger.error(f"Ошибка при получении отзывов пользователя {user_id}: {str(e)}")
            raise


# Создаем глобальные экземпляры для использования в приложении
db_manager = DatabaseManager(DATABASE_URL)
feedback_repository = FeedbackRepository(db_manager)