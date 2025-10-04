from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class AddChannelForm(BaseModel):
    username: str