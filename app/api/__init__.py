from app.api.routes_experience_cv import router as experience_router
from app.api.routes_education_cv import router as education_router
from app.api.routes_volunteering_cv import router as volunteering_router
from app.api.routes_certification_cv import router as certification_router
from app.api.routes_award_cv import router as awards_router
from app.api.routes_objective_cv import router as objective_router
from app.api.routes_resum_cv import router as export_router
from app.api.routes_project_cv import router as project_router
from app.api.routes_skill_language_cv import router as skills_router
from app.api.routes_header_cv import router as header_router
from app.api.routes_home import router as home_router


all_routers = [
    experience_router,
    education_router,
    volunteering_router,
    certification_router,
    awards_router,
    objective_router,
    export_router,
    project_router,
    skills_router,
    header_router,
    home_router
]
