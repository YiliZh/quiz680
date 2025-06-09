# Import base classes first
from app.models.base import Base, TimestampMixin

# Import models in dependency order
from app.models.user import User
from app.models.upload import Upload
from app.models.chapter import Chapter
from app.models.question import Question
from app.models.question_attempt import QuestionAttempt
from app.models.exam_session import ExamSession
from app.models.review_recommendation import ReviewRecommendation

# Export all models
__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Upload",
    "Chapter",
    "Question",
    "QuestionAttempt",
    "ExamSession",
    "ReviewRecommendation"
] 