from app.api.cv_api import all_routers as cv_routers
from app.api.auth_api.auth import all_routers as auth_routers
from app.api.home_api import all_routers as home_routers
from app.api.interview_api import all_routers as interview_routers 

all_routers = [
    *cv_routers,
    *auth_routers,
    *home_routers,
    *interview_routers
]

