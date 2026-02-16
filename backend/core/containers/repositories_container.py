from dependency_injector import containers , providers
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.data_access.postgres.cv.award_repository import AwardRepository
from backend.data_access.postgres.cv.certification_repository import CertificationRepository
from backend.data_access.postgres.cv.education_repository import EducationRepository
from backend.data_access.postgres.cv.experience_repository import ExperienceRepository
from backend.data_access.postgres.cv.objective_repository import CVObjectiveRepository
from backend.data_access.postgres.cv.project_repository import ProjectRepository
from backend.data_access.postgres.cv.skill_language_repository import SkillsLanguagesRepository
from backend.data_access.postgres.cv.volunteering_repository import VolunteeringRepository
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository
from backend.data_access.postgres.hr.hr_user_repository import HRUserRepository
from backend.data_access.postgres.user_repository import UserRepository
from backend.data_access.mongo.home.home_stats_repository import HomeStatsRepository
from backend.data_access.mongo.home.interview_session_home_repository import InterviewSessionHomeRepository
from backend.data_access.mongo.interview.interview_repository import InterviewRepository
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.data_access.mongo.hr.hr_interview_evaluation_repository import HRInterviewEvaluationRepository
from backend.data_access.mongo.hr.hr_interview_gridfs_repository import HRGridFSStorageService
from backend.data_access.redis.code_redis_repository import CodeRedisRepository
from backend.data_access.redis.session_redis_repository import SessionRedisRepository
from backend.data_access.mongo.home.resume_gridfs_repository import ResumeGridFSRepository
from backend.data_access.mongo.home.gridfs_storage_repository import GridFSStorageService
from backend.data_access.mongo.task.tasks_repository import TasksRepository
from backend.data_access.mongo.hr.hr_summary_repository import HRSummaryRepository
from backend.data_access.postgres.cv.resume_repository import ResumeRepository


class RepositoriesContainer (containers.DeclarativeContainer):
    infra = providers.DependenciesContainer()

    header_repository_factory = providers.Factory(CVHeaderRepository)
    award_repository_factory = providers.Factory(AwardRepository)
    certification_repository_factory = providers.Factory(CertificationRepository)
    education_repository_factory = providers.Factory(EducationRepository)
    experience_repository_factory = providers.Factory(ExperienceRepository)
    objective_repository_factory = providers.Factory(CVObjectiveRepository)
    project_repository_factory = providers.Factory(ProjectRepository)
    resume_repository_factory = providers.Factory(ResumeRepository)
    skill_language_repository_factory = providers.Factory(SkillsLanguagesRepository)
    volunteering_repository_factory = providers.Factory(VolunteeringRepository)
    hr_auth_repository_factory = providers.Factory(HRRepository)
    hr_user_repository_factory = providers.Factory(HRUserRepository)
    user_repository_factory = providers.Factory(UserRepository)
    home_stats_repository_factory = providers.Factory(HomeStatsRepository)
    interview_session_home_repository_factory = providers.Factory(InterviewSessionHomeRepository)
    interview_repository_factory = providers.Factory(InterviewRepository)
    hr_interview_client_repository_factory = providers.Factory(HRAnswerRepository)
    hr_invitation_repository_factory = providers.Factory(HRInvitationRepository , db = infra.mongo_hr_db) ## editing 
    hr_interview_repository_factory = providers.Factory(HRInterviewRepository , db = infra.mongo_hr_db) ## editing 
    hr_interview_evaluation_repository_factory = providers.Factory(HRInterviewEvaluationRepository , db = infra.hr_video_bucket)
    hr_gridfs_storage_repository_factory = providers.Factory(HRGridFSStorageService)
    hr_summary_repository_factory = providers.Factory(HRSummaryRepository , db=infra.mongo_hr_db)
    tasks_repository_factory = providers.Factory(TasksRepository)
    code_redis_repository_factory = providers.Factory(CodeRedisRepository)
    session_redis_repository_factory = providers.Factory(SessionRedisRepository)
    resume_gridfs_repository_factory = providers.Factory(ResumeGridFSRepository)
    gridfs_storage_repository_factory = providers.Factory(GridFSStorageService)
    resume_repository_factory = providers.Factory(ResumeRepository)

   





    




