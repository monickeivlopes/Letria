from fastapi import File
from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):
    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        return dict(filter(lambda x: x[1] is not None, data.items()) or {})


class IdentModel(BaseModel):
    id: int = File(...)
