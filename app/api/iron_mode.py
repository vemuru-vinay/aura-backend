from fastapi import APIRouter
from app.db.database import get_connection

router = APIRouter(prefix="/iron-mode", tags=["Iron Mode"])


@router.post("/activate")
def activate_iron_mode():
    """
    Manually activates Iron Mode.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE player SET iron_mode = 1 WHERE id = 1;"
    )

    conn.commit()
    conn.close()

    return {
        "status": "IRON_MODE_ACTIVATED"
    }


@router.post("/deactivate")
def deactivate_iron_mode():
    """
    Manually deactivates Iron Mode.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE player SET iron_mode = 0 WHERE id = 1;"
    )

    conn.commit()
    conn.close()

    return {
        "status": "IRON_MODE_DEACTIVATED"
    }
