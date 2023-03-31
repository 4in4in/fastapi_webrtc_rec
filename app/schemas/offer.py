from pydantic import BaseModel


class OfferSchema(BaseModel):
    sdp: str
    type: str
    video_transform: str | None
