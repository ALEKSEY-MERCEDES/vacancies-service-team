import pytest
from infrastructure.db.models import User, Candidate


@pytest.mark.asyncio
async def test_create_user(async_session):
    user = User(
        telegram_id=111,
        username="test",
        role="candidate",
    )
    async_session.add(user)
    await async_session.commit()

    assert user.id is not None
    assert user.is_banned is False


@pytest.mark.asyncio
async def test_candidate_profile(async_session):
    user = User(
        telegram_id=222,
        username="cand",
        role="candidate",
    )
    candidate = Candidate(
        user=user,
        full_name="Ivan Ivanov",
        age=25,
        skills="Python, SQL",
    )

    async_session.add(candidate)
    await async_session.commit()

    assert candidate.id is not None
    assert candidate.user_id == user.id
