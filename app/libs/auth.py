from uuid import uuid4, UUID


async def auth_required(token: str = None) -> UUID:
    return uuid4()
