from uuid import uuid4

from aiortc import RTCConfiguration, RTCPeerConnection, RTCSessionDescription
from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.offer import OfferSchema

from app.services.webrtc import WebRTCService
from app.settings import settings

webrtc_router = APIRouter()

service = WebRTCService(rec_path=settings.rec_path)


@webrtc_router.post(
    path="/offer",
    summary="Offer WebRTC",
)
async def offer_route(params: OfferSchema):
    peer_connection = RTCPeerConnection()  # stun/turn can be passed here
    _client_id = uuid4()
    offer = await service.add_peer_connection(_client_id, peer_connection, params)

    return offer


webrtc_router.add_event_handler("shutdown", service.close_all_connections)
