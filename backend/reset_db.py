

# from app.models import Base
# from app.dependencies import postgres_engine
# import asyncio

# async def recreate_tables():
#     async with postgres_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     print("Tables recreated successfully!")

# asyncio.run(recreate_tables())

# if __name__ == "__main__":
#     asyncio.run(recreate_tables())