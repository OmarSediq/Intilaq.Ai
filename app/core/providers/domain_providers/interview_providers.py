
from app.domain_services.interview_services.session_service import InterviewSessionService
from app.domain_services.interview_services.question_service import InterviewQuestionService
from app.domain_services.interview_services.answer_service import InterviewAnswerService
from app.domain_services.interview_services.feedback_service import InterviewFeedbackService
from app.domain_services.interview_services.score_service import InterviewScoreService
from app.domain_services.interview_services.validator_service import InterviewValidatorService





# ========== interview  ==========

validator_instance = InterviewValidatorService()

def get_interview_session_service() -> InterviewSessionService:
    return InterviewSessionService(validator_instance)

def get_interview_question_service() -> InterviewQuestionService:
    return InterviewQuestionService(validator_instance)

def get_interview_answer_service() -> InterviewAnswerService:
    return InterviewAnswerService(validator_instance)

def get_interview_feedback_service() -> InterviewFeedbackService:
    return InterviewFeedbackService(validator_instance)

def get_interview_score_service() -> InterviewScoreService:
    return InterviewScoreService(validator_instance)

def get_validator_service() -> InterviewValidatorService:
    return validator_instance