"""
Account Health Monitoring Module for FULL-TG v3.0
NEW FEATURE: Check account liveness and auto-remove dead accounts
"""

import asyncio
from datetime import datetime
from telethon.errors import (
    AuthKeyUnregisteredError, UserDeactivatedError,
    UserDeactivatedBanError, PhoneNumberBannedError,
    UnauthorizedError
)
import config
from core.session_manager import session_manager
from core.database import db
from core.logger import logger, log_removed_account
from ui.progress import ProgressBar, StatusIndicator

status = StatusIndicator()

class AccountHealthChecker:
    """Check and manage account health"""
    
    def __init__(self):
        self.health_report = {
            'total': 0,
            'healthy': 0,
            'removed': 0,
            'details': []
        }
    
    async def _should_auto_remove(self, reason):
        """Determine if account should be auto-removed based on reason"""
        # DNA (Do Not Auto-remove) list
        dna_reasons = [
            "Network/connection issues", 
            "Connection timeout",
            "Flood wait"
        ]
        
        for dna in dna_reasons:
            if dna in reason:
                return False
        return True

    async def check_all_accounts(self, auto_remove=True):
        """Check health of all accounts"""
        try:
            status.show_processing("Starting account health check")
            
            # Get all accounts from database
            accounts = await db.get_all_accounts()
            
            if not accounts:
                status.show_warning("No accounts found in database")
                return self.health_report
            
            self.health_report['total'] = len(accounts)
            progress = ProgressBar(len(accounts), prefix='Checking accounts:')
            
            # Use semaphore to limit concurrency (prevent database locking)
            semaphore = asyncio.Semaphore(10)
            
            async def check_wrapper(index, account):
                async with semaphore:
                    phone = account[1]
                    is_healthy, reason = await self._check_account(phone)
                    
                    if is_healthy:
                        self.health_report['healthy'] += 1
                        self.health_report['details'].append({
                            'phone': phone,
                            'status': 'HEALTHY',
                            'reason': reason
                        })
                        logger.success(f"✓ {phone}: {reason}")
                    else:
                        should_remove = False
                        status_label = 'DEAD'
                        
                        if auto_remove:
                            if await self._should_auto_remove(reason):
                                should_remove = True
                            else:
                                status_label = 'ERROR (SKIPPED REMOVAL)'
                        
                        self.health_report['details'].append({
                            'phone': phone,
                            'status': status_label,
                            'reason': reason
                        })
                        logger.error(f"✗ {phone}: {reason}")
                        
                        if should_remove:
                            await self._remove_account(phone, reason)
                            self.health_report['removed'] += 1
                    
                    progress.update(index + 1)

            tasks = [check_wrapper(i, acc) for i, acc in enumerate(accounts)]
            await asyncio.gather(*tasks)
            
            progress.finish()
            self._print_report()
            self._export_report()
            
            return self.health_report
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return self.health_report
    
    async def _check_account(self, phone):
        """Check individual account health"""
        try:
            # Try to load session
            client = await session_manager.get_client(phone)
            
            if not client:
                return False, "Failed to load session"
            
            # Try to get account info
            me = await client.get_me()
            
            if me:
                # Additional checks
                if me.deleted:
                    return False, "Account deleted"
                
                if me.restricted:
                    return False, "Account restricted"
                
                return True, "Account is healthy"
            else:
                return False, "Failed to get account info"
                
        except AuthKeyUnregisteredError:
            return False, "Session expired/invalid - Authorization key unregistered"
        except UserDeactivatedError:
            return False, "Account deleted by user"
        except UserDeactivatedBanError:
            return False, "Account banned by Telegram"
        except PhoneNumberBannedError:
            return False, "Phone number banned by Telegram"
        except UnauthorizedError:
            return False, "Authorization revoked - Session invalid"
        except ConnectionError:
            return False, "Network/connection issues"
        except TimeoutError:
            return False, "Connection timeout"
        except Exception as e:
            error_msg = str(e).lower()
            
            # Categorize errors
            if 'auth' in error_msg or 'unauthorized' in error_msg:
                return False, "Authorization error - Session invalid"
            elif 'banned' in error_msg:
                return False, "Account banned"
            elif 'deleted' in error_msg or 'deactivated' in error_msg:
                return False, "Account deleted/deactivated"
            elif 'phone' in error_msg and 'changed' in error_msg:
                return False, "Phone number changed"
            elif 'network' in error_msg or 'connection' in error_msg:
                return False, "Network/connection issues"
            else:
                return False, f"Unknown error: {str(e)[:50]}"
    
    async def _remove_account(self, phone, reason):
        """Remove dead account"""
        try:
            # Disconnect client if connected
            await session_manager.disconnect_client(phone)
            
            # Delete session file
            await session_manager.delete_session(phone)
            
            # Log removal
            log_removed_account(phone, reason)
            
            logger.warning(f"Removed account: {phone} - {reason}")
            
        except Exception as e:
            logger.error(f"Failed to remove account {phone}: {e}")
    
    def _print_report(self):
        """Print health check report"""
        print(f"\n{'='*70}")
        print(f"ACCOUNT HEALTH CHECK REPORT")
        print(f"{'='*70}")
        print(f"Total Accounts: {self.health_report['total']}")
        print(f"Healthy Accounts: {self.health_report['healthy']} ✓")
        print(f"Removed Accounts: {self.health_report['removed']} ✗")
        print(f"{'='*70}\n")
        
        if self.health_report['removed'] > 0:
            print(f"REMOVED ACCOUNTS DETAILS:")
            print(f"{'-'*70}")
            
            for detail in self.health_report['details']:
                if detail['status'] == 'DEAD':
                    print(f"✗ {detail['phone']}")
                    print(f"  Reason: {detail['reason']}\n")
            
            print(f"{'-'*70}\n")
    
    def _export_report(self):
        """Export report to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = config.LOGS_DIR / f"health_check_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("ACCOUNT HEALTH CHECK REPORT\n")
                f.write("="*70 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Accounts: {self.health_report['total']}\n")
                f.write(f"Healthy Accounts: {self.health_report['healthy']}\n")
                f.write(f"Removed Accounts: {self.health_report['removed']}\n")
                f.write("="*70 + "\n\n")
                
                f.write("DETAILED RESULTS:\n")
                f.write("-"*70 + "\n")
                
                for detail in self.health_report['details']:
                    status_icon = "✓" if detail['status'] == 'HEALTHY' else "✗"
                    f.write(f"{status_icon} {detail['phone']}\n")
                    f.write(f"  Status: {detail['status']}\n")
                    f.write(f"  Reason: {detail['reason']}\n\n")
            
            logger.success(f"Health report exported to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to export report: {e}")

# Global health checker
health_checker = AccountHealthChecker()

async def check_accounts_health():
    """Main function to check all accounts health"""
    try:
        print("\n" + "="*70)
        print("ACCOUNT HEALTH MONITORING")
        print("="*70 + "\n")
        
        auto_remove = input("Auto-remove dead accounts? (yes/no) [yes]: ").strip().lower()
        auto_remove = auto_remove != 'no'  # Default to yes
        
        if auto_remove:
            confirm = input("⚠️  This will permanently remove dead accounts. Continue? (yes/no): ").strip().lower()
            if confirm != 'yes':
                logger.info("Operation cancelled")
                return
        
        print()
        report = await health_checker.check_all_accounts(auto_remove=auto_remove)
        
        if report['removed'] > 0:
            print(f"\n{report['removed']} account(s) were removed.")
            print(f"Check {config.REMOVED_ACCOUNTS_LOG} for details.\n")
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")

async def view_removed_accounts_log():
    """View log of removed accounts"""
    try:
        if not config.REMOVED_ACCOUNTS_LOG.exists():
            status.show_warning("No removed accounts log found")
            return
        
        print(f"\n{'='*70}")
        print("REMOVED ACCOUNTS LOG")
        print(f"{'='*70}\n")
        
        with open(config.REMOVED_ACCOUNTS_LOG, 'r', encoding='utf-8') as f:
            content = f.read()
            if content:
                print(content)
            else:
                print("No accounts have been removed yet.\n")
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        logger.error(f"Failed to view log: {e}")

async def schedule_health_check():
    """Schedule automatic health checks"""
    try:
        print("\nScheduling automatic health checks...")
        print(f"Interval: Every {config.HEALTH_CHECK_INTERVAL} seconds ({config.HEALTH_CHECK_INTERVAL//3600} hours)")
        
        while True:
            await asyncio.sleep(config.HEALTH_CHECK_INTERVAL)
            logger.info("Running scheduled health check...")
            await health_checker.check_all_accounts(auto_remove=True)
            
    except Exception as e:
        logger.error(f"Scheduled health check error: {e}")
