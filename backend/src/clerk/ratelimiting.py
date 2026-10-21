from datetime import datetime
from fastapi import HTTPException, status

MAX_TOKENS = 30
REFILL_SECONDS = 60 * 2

roten = {}


def ratelimiter(user_id: int) -> int:
    now = datetime.now()

    if user_id not in roten:
        roten[user_id] = {
            "tokens": MAX_TOKENS,
            "lastRefilled": now,
        }

    time_elapsed = now - roten[user_id]["lastRefilled"]
    added_tokens = int(time_elapsed.total_seconds() // REFILL_SECONDS)

    if added_tokens > 0:
        roten[user_id]["tokens"] = min(
            MAX_TOKENS,
            roten[user_id]["tokens"] + added_tokens,
        )

        roten[user_id]["lastRefilled"] = now

    if roten[user_id]["tokens"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit reached",
        )

    roten[user_id]["tokens"] -= 1
    return user_id
