from fastapi import APIRouter
from app.api.routes.users import router as users_router
from app.api.routes.login import router as auth_router
from app.api.routes.intake import router as intake_router
from app.api.routes.price import router as price_router
from app.api.routes.slots import router as slots_router
from app.api.routes.booking import router as bookings_router
from app.api.routes.webhook import router as webhooks_router
from app.api.routes.utils import router as utils_router

api_router = APIRouter()
api_router.include_router(utils_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(intake_router)
api_router.include_router(price_router)
api_router.include_router(slots_router)
api_router.include_router(bookings_router)
api_router.include_router(webhooks_router)


# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)
