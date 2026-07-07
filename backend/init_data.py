import asyncio
from app.database import engine, async_session, Base
from app.models import User, Warehouse
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

WAREHOUSES = [
    "101D", "1800", "101G", "102H", "1200",
    "1050", "1400", "1450", "1600", "CA12",
    "101A", "101B", "102B", "1070", "CA11", "GA11",
]


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        for code in WAREHOUSES:
            existing = await session.execute(
                Warehouse.__table__.select().where(Warehouse.code == code)
            )
            if not existing.first():
                session.add(Warehouse(code=code, name=code))

        admin = await session.execute(
            User.__table__.select().where(User.username == settings.INITIAL_ADMIN_USERNAME)
        )
        if not admin.first():
            session.add(User(
                username=settings.INITIAL_ADMIN_USERNAME,
                password_hash=pwd_context.hash(settings.INITIAL_ADMIN_PASSWORD),
                role="admin",
            ))

        await session.commit()

    print(f"Init complete: {len(WAREHOUSES)} warehouses + admin user")


if __name__ == "__main__":
    asyncio.run(init())
