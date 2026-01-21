from fastapi import APIRouter

from app.services.rewards_service import get_rewards_state, claim_reward
from app.db.database import get_connection
from app.services.daily_state_service import (
    get_system_day,
    assert_day_not_resolved,
    mark_day_resolved
)

router = APIRouter(prefix="/rewards")


@router.get("/")
def fetch_rewards():
    return get_rewards_state()


@router.post("/claim")
def claim(payload: dict):
    result = claim_reward(
        payload["reward_type"],
        payload["reward_key"]
    )
    return {
        "status": "OK",
        "message": result
    }
