from app.database.session import async_db_session


async def get_db():
    async with async_db_session as db:
        yield await db()
