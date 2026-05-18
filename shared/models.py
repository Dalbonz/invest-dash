from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class EngineOutput:
    engine: str
    version: str = "1.0"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "ok"
    data: dict = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> dict:
        return self.__dict__

@dataclass
class Holding:
    ticker: str
    name: str
    market: str
    quantity: float
    avg_price: float
    asset_type: str
    sector: str = ""
    currency: str = "KRW"