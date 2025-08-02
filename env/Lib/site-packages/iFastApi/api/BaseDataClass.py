from dataclasses import dataclass, asdict


@dataclass
class BaseDataClass:
    @property
    def dict(self):
        return asdict(self)
