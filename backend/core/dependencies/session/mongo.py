from dependency_injector.wiring import Provide, inject
from backend.core.containers.application_container import ApplicationContainer
## mongo_hr_db , mongo_resumes_db , hr_video_bucket , resumes_bucket



@inject
def provide_cv_snapshot_mongo_db(
    db = Provide[ApplicationContainer.infra.mongo_snapshot_db]
):
    return db



@inject
def provide_hr_interview_mongo_db(
    db = Provide[ApplicationContainer.infra.mongo_hr_db],
):
    return db


@inject
def provide_interview_mongo_db(
    db = Provide[ApplicationContainer.infra.mongo_interview_db],
):
    return db


@inject
def provide_resume_gridfs_bucket(
    bucket = Provide[ApplicationContainer.infra.resumes_bucket],
):
    return bucket


@inject
def provide_hr_video_bucket(
    bucket = Provide[ApplicationContainer.infra.hr_video_bucket],
):
    return bucket



