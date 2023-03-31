import asyncio
from uuid import UUID
from aiortc import (
    RTCPeerConnection,
    RTCDataChannel,
    MediaStreamTrack,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaRecorder, MediaRelay

from logging import getLogger
from app.schemas.offer import OfferSchema

from app.utils.video_transform_track import VideoTransformTrack


class WebRTCService:

    _peer_connections: dict[UUID, RTCPeerConnection]

    def __init__(self, *, rec_path: str, logger=None) -> None:
        self._peer_connections = dict()
        self._logger = logger or getLogger(__name__)
        self._relay = MediaRelay()  # or create for each client individually?
        self._rec_path = rec_path

    async def add_peer_connection(
        self, peer_id: UUID, connection: RTCPeerConnection, params: OfferSchema
    ) -> OfferSchema:
        if peer_id not in self._peer_connections:
            offer = RTCSessionDescription(params.sdp, params.type)
            self._peer_connections[peer_id] = connection
            self._logger.info("peer %s is connected", peer_id)

            recorder = MediaRecorder(f"{self._rec_path}/{str(peer_id)}.mp4")

            @connection.on("datachannel")
            def on_datachannel(channel: RTCDataChannel):
                @channel.on("message")
                def on_message(message: str):
                    self._logger.info("MESSAGE %s: %s", peer_id, message)

            @connection.on("connectionstatechange")
            async def on_connection_state_change():
                self._logger.info("Connection state is %s", connection.connectionState)
                if connection.connectionState == "failed":
                    await connection.close()
                    del self._peer_connections[peer_id]

            @connection.on("track")
            def on_track(track: MediaStreamTrack):
                self._logger.info("%s: Track %s received", peer_id, track.kind)

                if track.kind == "audio":
                    recorder.addTrack(track)
                elif track.kind == "video":
                    _track = self._relay.subscribe(track)
                    _transform_track = VideoTransformTrack(
                        _track, params.video_transform
                    )
                    connection.addTrack(_transform_track)

                    recorder.addTrack(self._relay.subscribe(track))

                @track.on("ended")
                async def on_ended():
                    self._logger.info("%s: Track %s ended", peer_id, track.kind)
                    await recorder.stop()

            await connection.setRemoteDescription(offer)
            await recorder.start()

            answer = await connection.createAnswer()
            await connection.setLocalDescription(answer)

            return OfferSchema(
                sdp=connection.localDescription.sdp,
                type=connection.localDescription.type,
            )

        else:
            self._logger.error("peer %s is connected already!", peer_id)
            raise Exception

    async def close_all_connections(self):
        self._logger.info("closing all connections...")
        await asyncio.gather(
            *[self._peer_connections[key].close() for key in self._peer_connections]
        )
        self._peer_connections.clear()
