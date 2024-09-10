import aiosqlite
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path='src/database/database.db'):
        self.db_path = db_path

    async def initialize(self):
        """
        Initialize the database and create tables if they don't exist.
        """
        async with aiosqlite.connect(self.db_path) as db:
            with open('src/database/schema.sql') as file:
                await db.executescript(file.read())
            await db.commit()

    async def execute(self, query, params=None):
        """
        Execute a query without returning results.
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params or ()) as cursor:
                await db.commit()

    async def fetchall(self, query, params=None):
        """Fetch all rows from a query."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params or ()) as cursor:
                return await cursor.fetchall()

    async def fetchone(self, query, params=None):
        """Fetch a single row from a query."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params or ()) as cursor:
                return await cursor.fetchone()

