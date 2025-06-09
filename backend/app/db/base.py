# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.upload import Upload  # noqa
from app.models.chapter import Chapter  # noqa
from app.models.question import Question  # noqa
from app.models.question_attempt import QuestionAttempt  # noqa
from app.models.exam_session import ExamSession  # noqa
from app.models.review_recommendation import ReviewRecommendation  # noqa 