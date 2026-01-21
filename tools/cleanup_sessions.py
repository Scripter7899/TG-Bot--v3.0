
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.database import db
from core.session_manager import session_manager
from core.proxy_manager import proxy_manager
from modules.account_health import health_checker

async def main():
    print("Initializing cleanup...")
    await db.connect()
    await proxy_manager.load_proxies()
    loaded = await session_manager.load_all_sessions()
    print(f"Loaded {loaded} sessions for checking.")
    
    print("\nStarting health check with AUTO-REMOVAL enabled for revoked sessions...")
    print("Sessions with 'Session revoked (IP change)' will be deleted.")
    
    report = await health_checker.check_all_accounts(auto_remove=True)
    
    print(f"\nCleanup Complete.")
    print(f"Total: {report['total']}")
    print(f"Healthy: {report['healthy']}")
    print(f"Removed: {report['removed']}")
    
    await session_manager.disconnect_all()
    await db.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
