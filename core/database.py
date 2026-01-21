"""
Database Management for FULL-TG v3.0
SQLite database for persistent storage
"""

import aiosqlite
import asyncio
from datetime import datetime
from pathlib import Path
import config
from core.logger import logger

class Database:
    """Database manager for FULL-TG"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.connection = None
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """Connect to database"""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            # Enable WAL mode for better concurrency
            await self.connection.execute("PRAGMA journal_mode=WAL")
            # Enable Foreign Keys
            await self.connection.execute("PRAGMA foreign_keys = ON")
            await self._create_tables()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
    
    async def _create_tables(self):
        """Create all necessary tables"""
        async with self.connection.cursor() as cursor:
            # Accounts table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT UNIQUE NOT NULL,
                    session_name TEXT NOT NULL,
                    api_id TEXT,
                    api_hash TEXT,
                    proxy_id INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    FOREIGN KEY (proxy_id) REFERENCES proxies(id)
                )
            """)
            
            
            # Proxies table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS proxies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proxy_type TEXT NOT NULL,
                    address TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    username TEXT,
                    password TEXT,
                    status TEXT DEFAULT 'active',
                    success_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Operations log table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS operations_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    operation_type TEXT NOT NULL,
                    target TEXT,
                    details TEXT,
                    status TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            """)
            
            # Statistics table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    stat_type TEXT NOT NULL,
                    stat_value INTEGER DEFAULT 0,
                    date DATE DEFAULT CURRENT_DATE,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            """)
            
            # Scraped users cache
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    source_group TEXT,
                    is_premium BOOLEAN DEFAULT 0,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Scheduled tasks
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_type TEXT NOT NULL,
                    account_id INTEGER,
                    target TEXT,
                    message TEXT,
                    scheduled_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            """)
            
            # Removed accounts log
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS removed_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    removed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Post history tracking (P0 improvement)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    account_phone TEXT NOT NULL,
                    group_id TEXT,
                    group_name TEXT,
                    content_type TEXT NOT NULL,
                    content_hash TEXT,
                    status TEXT DEFAULT 'success',
                    error_message TEXT
                )
            """)
            
            await self.connection.commit()
            
            # Create Indices for Optimization
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status)")
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_proxies_status ON proxies(status)")
            await self.connection.commit()
    
    # Account operations
    async def add_account(self, phone, session_name, api_id=None, api_hash=None, proxy_id=None):
        """Add new account to database"""
        try:
            async with self._lock:
                async with self.connection.cursor() as cursor:
                    await cursor.execute("""
                        INSERT INTO accounts (phone, session_name, api_id, api_hash, proxy_id, last_used)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (phone, session_name, api_id, api_hash, proxy_id, datetime.now()))
                    await self.connection.commit()
                    return cursor.lastrowid
        except aiosqlite.IntegrityError:
            logger.warning(f"Account {phone} already exists")
            return None
        except Exception as e:
            logger.error(f"Failed to add account: {e}")
            return None
    
    async def get_all_accounts(self, status='active'):
        """Get all accounts"""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM accounts WHERE status = ?", (status,)
            )
            return await cursor.fetchall()
    
    async def update_account_status(self, phone, status):
        """Update account status"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "UPDATE accounts SET status = ? WHERE phone = ?", (status, phone)
                )
                await self.connection.commit()
    
    async def remove_account(self, phone, reason):
        """Remove account and log reason"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                # Log removal
                await cursor.execute(
                    "INSERT INTO removed_accounts (phone, reason) VALUES (?, ?)",
                    (phone, reason)
                )
                # Delete account
                await cursor.execute("DELETE FROM accounts WHERE phone = ?", (phone,))
                await self.connection.commit()
    
    async def update_last_used(self, phone):
        """Update last used timestamp"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "UPDATE accounts SET last_used = ? WHERE phone = ?",
                    (datetime.now(), phone)
                )
                await self.connection.commit()
    

    # Proxy operations
    async def add_proxy(self, proxy_type, address, port, username=None, password=None):
        """Add new proxy"""
        try:
            async with self._lock:
                async with self.connection.cursor() as cursor:
                    await cursor.execute("""
                        INSERT INTO proxies (proxy_type, address, port, username, password)
                        VALUES (?, ?, ?, ?, ?)
                    """, (proxy_type, address, port, username, password))
                    await self.connection.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add proxy: {e}")
            return None
    
    async def get_all_proxies(self, status='active'):
        """Get all proxies"""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM proxies WHERE status = ?", (status,)
            )
            return await cursor.fetchall()
    
    async def update_proxy_stats(self, proxy_id, success=True):
        """Update proxy statistics"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                if success:
                    await cursor.execute(
                        "UPDATE proxies SET success_count = success_count + 1 WHERE id = ?",
                        (proxy_id,)
                    )
                else:
                    await cursor.execute(
                        "UPDATE proxies SET fail_count = fail_count + 1 WHERE id = ?",
                        (proxy_id,)
                    )
                await self.connection.commit()
    
    # Operations log
    async def log_operation(self, account_id, operation_type, target, details, status):
        """Log operation to database"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO operations_log (account_id, operation_type, target, details, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (account_id, operation_type, target, details, status))
                await self.connection.commit()
    
    async def get_operations_history(self, limit=100):
        """Get operations history"""
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM operations_log ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return await cursor.fetchall()
    
    # Statistics
    async def update_stat(self, account_id, stat_type, increment=1):
        """Update statistics"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                today = datetime.now().date()
                # Check if stat exists for today
                await cursor.execute("""
                    SELECT id, stat_value FROM statistics 
                    WHERE account_id = ? AND stat_type = ? AND date = ?
                """, (account_id, stat_type, today))
                
                result = await cursor.fetchone()
                if result:
                    # Update existing
                    await cursor.execute("""
                        UPDATE statistics SET stat_value = stat_value + ? 
                        WHERE id = ?
                    """, (increment, result[0]))
                else:
                    # Insert new
                    await cursor.execute("""
                        INSERT INTO statistics (account_id, stat_type, stat_value, date)
                        VALUES (?, ?, ?, ?)
                    """, (account_id, stat_type, increment, today))
                
                await self.connection.commit()
    
    async def get_stats(self, account_id=None, stat_type=None):
        """Get statistics"""
        async with self.connection.cursor() as cursor:
            query = "SELECT * FROM statistics WHERE 1=1"
            params = []
            
            if account_id:
                query += " AND account_id = ?"
                params.append(account_id)
            
            if stat_type:
                query += " AND stat_type = ?"
                params.append(stat_type)
            
            query += " ORDER BY date DESC"
            
            await cursor.execute(query, params)
            return await cursor.fetchall()
    
    # Scraped users
    async def add_scraped_user(self, user_id, username, first_name, last_name, phone, source_group, is_premium=False):
        """Add scraped user to cache"""
        try:
            async with self._lock:
                async with self.connection.cursor() as cursor:
                    await cursor.execute("""
                        INSERT INTO scraped_users 
                        (user_id, username, first_name, last_name, phone, source_group, is_premium)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, username, first_name, last_name, phone, source_group, is_premium))
                    await self.connection.commit()
        except aiosqlite.IntegrityError:
            pass  # User already exists
    
    async def get_scraped_users(self, source_group=None, is_premium=None, limit=None):
        """Get scraped users"""
        async with self.connection.cursor() as cursor:
            query = "SELECT * FROM scraped_users WHERE 1=1"
            params = []
            
            if source_group:
                query += " AND source_group = ?"
                params.append(source_group)
            
            if is_premium is not None:
                query += " AND is_premium = ?"
                params.append(is_premium)
            
            query += " ORDER BY scraped_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            await cursor.execute(query, params)
            return await cursor.fetchall()
    
    # Scheduled tasks
    async def add_scheduled_task(self, task_type, account_id, target, message, scheduled_time):
        """Add scheduled task"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO scheduled_tasks (task_type, account_id, target, message, scheduled_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (task_type, account_id, target, message, scheduled_time))
                await self.connection.commit()
                return cursor.lastrowid
    
    async def get_pending_tasks(self):
        """Get pending scheduled tasks"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM scheduled_tasks 
                WHERE status = 'pending' AND scheduled_time <= ?
                ORDER BY scheduled_time
            """, (datetime.now(),))
            return await cursor.fetchall()
    
    async def update_task_status(self, task_id, status):
        """Update task status"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute(
                    "UPDATE scheduled_tasks SET status = ? WHERE id = ?",
                    (status, task_id)
                )
                await self.connection.commit()
    
    # Post history tracking (P0 improvement)
    async def add_post_history(self, account_phone, group_id, group_name, content_type, content_hash, status='success', error_message=None):
        """Track posted content"""
        async with self._lock:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO post_history (account_phone, group_id, group_name, content_type, content_hash, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (account_phone, group_id, group_name, content_type, content_hash, status, error_message))
                await self.connection.commit()
    
    async def check_post_duplicate(self, group_id, content_hash, days=7):
        """Check if content was posted recently"""
        async with self.connection.cursor() as cursor:
            await cursor.execute("""
                SELECT COUNT(*) FROM post_history 
                WHERE group_id = ? AND content_hash = ? 
                AND timestamp > datetime('now', '-' || ? || ' days')
            """, (group_id, content_hash, days))
            result = await cursor.fetchone()
            return result[0] > 0
    
    async def get_post_stats(self, account_phone=None, days=30):
        """Get posting statistics"""
        async with self.connection.cursor() as cursor:
            query = """
                SELECT group_name, COUNT(*) as post_count, 
                       SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as success_count
                FROM post_history 
                WHERE timestamp > datetime('now', '-' || ? || ' days')
            """
            params = [days]
            
            if account_phone:
                query += " AND account_phone = ?"
                params.append(account_phone)
            
            query += " GROUP BY group_name ORDER BY post_count DESC"
            
            await cursor.execute(query, params)
            return await cursor.fetchall()

# Global database instance
db = Database()
