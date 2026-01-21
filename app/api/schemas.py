from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class DailyReportSchema(BaseModel):
    STR: Optional[int] = Field(None, ge=0, le=1)
    INT: Optional[int] = Field(None, ge=0, le=1)
    VIT: Optional[int] = Field(None, ge=0, le=1)
    AGI: Optional[int] = Field(None, ge=0, le=1)
    PER: Optional[int] = Field(None, ge=0, le=1)
    CON: Optional[int] = Field(None, ge=0, le=1)
    CHA: Optional[int] = Field(None, ge=0, le=1)
    NET: Optional[int] = Field(None, ge=0, le=1)
    LUST_BOSS: Optional[int] = Field(None, ge=0, le=1)

    # 🆕 REPORT-GATED PENALTY COMPLETION
    penalties: Optional[Dict[str, int]] = None


class PlayerStatusSchema(BaseModel):
    name: str
    level: int
    rank: str
    current_xp: int
    streak: int
    stabilization_days: int
    iron_mode: bool


class StatusResponseSchema(BaseModel):
    player: PlayerStatusSchema
    stats: Dict[str, int]
    penalties: Dict[str, List[dict]]
    authority: dict
