
import asyncio
from core.database import db

async def count():
    await db.connect()
    accounts = await db.get_all_accounts()
    print(f"Total Accounts in DB: {len(accounts)}")
    await db.close()

if __name__ == "__main__":
    asyncio.run(count())
