from uuid import UUID

from fastapi import APIRouter, Depends

from app.libs.auth import auth_required
from app.schemas.offer import OfferSchema
from app.services.webrtc import WebRTCService
from app.settings import settings

webrtc_router = APIRouter()

service = WebRTCService(rec_path=settings.rec_path)


@webrtc_router.post(path="/offer", summary="Offer WebRTC", response_model=OfferSchema)
async def offer_route(params: OfferSchema, user_id: UUID = Depends(auth_required)):
    return await service.add_peer_connection(user_id, params)


@webrtc_router.on_event("shutdown")
async def on_webrtc_router_shutdown():
    await service.close_all_connections()
