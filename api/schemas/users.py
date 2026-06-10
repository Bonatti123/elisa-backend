from pydantic import BaseModel


class CollaboratorResponse(BaseModel):
    id: int
    cupe: str
    first_name: str
    last_name: str
    role_name: str | None = None
    city: str
    is_active: bool
