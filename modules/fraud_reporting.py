"""
Fraud Reporting Module
Enhanced scam reporting with rotating templates
"""

import random
import asyncio
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import InputReportReasonSpam, InputReportReasonFake, InputReportReasonOther
from core.session_manager import session_manager
from core.database import db
from core.logger import logger
from ui.progress import StatusIndicator
from utils.delay_manager import DelayManager

status = StatusIndicator()

# Scam report templates (10 templates for rotation)
SCAM_TEMPLATES = [
    "This user is running a fraudulent scheme targeting innocent people",
    "Scammer attempting to steal money through fake investment opportunities",
    "Fake investment scam - promising unrealistic returns",
    "Phishing attempt detected - trying to steal personal information",
    "Impersonation and fraud - pretending to be someone else",
    "Cryptocurrency scam - fake trading platform",
    "Fake giveaway scam - requesting payment for prizes",
    "Romance scam / catfishing - building fake relationships for money",
    "Pyramid scheme promotion - illegal multi-level marketing",
    "Selling fake products/services - taking money without delivery"
]

template_index = 0

def get_next_template():
    """Get next template in rotation"""
    global template_index
    template = SCAM_TEMPLATES[template_index % len(SCAM_TEMPLATES)]
    template_index += 1
    return template

async def report_scam_user():
    """
    Feature 74 (ENHANCED): Report user as scammer with rotating templates
    """
    try:
        print(f"\n{'-'*70}")
        print("⭐ SCAM REPORT [ALL ACCOUNTS]")
        print(f"{'-'*70}\n")
        
        # Get target user
        target_user = input("Enter username/user ID to report: ").strip()
        
        # Choose report type
        print("\nReport Options:")
        print("1. Use rotating templates (automatic)")
        print("2. Write custom reason")
        
        report_choice = input("\nSelect option (1-2): ").strip()
        
        custom_reason = None
        if report_choice == '2':
            custom_reason = input("Enter custom reason: ").strip()
        
        # Get all accounts
        clients_dict = await session_manager.get_all_clients()
        
        if not clients_dict:
            status.show_error("No active accounts found")
            return
        
        print(f"\n{'-'*70}")
        print(f"Target: {target_user}")
        print(f"Accounts: {len(clients_dict)}")
        print(f"Templates: {'Rotating' if report_choice == '1' else 'Custom'}")
        print(f"{'-'*70}\n")
        
        confirm = input("Submit reports? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Operation cancelled")
            return
        
        # Start reporting
        total_reported = 0
        total_failed = 0
        
        for phone, client in clients_dict.items():
            try:
                # Get target entity
                target_entity = await client.get_entity(target_user)
                
                # Get reason
                if report_choice == '1':
                    reason_text = get_next_template()
                else:
                    reason_text = custom_reason
                
                # Report user
                await client(ReportPeerRequest(
                    peer=target_entity,
                    reason=InputReportReasonOther(),
                    message=reason_text
                ))
                
                logger.success(f"{phone} reported {target_user}")
                logger.info(f"Reason: {reason_text}")
                total_reported += 1
                
                # Delay between accounts (30-60 seconds)
                await DelayManager.wait('bio_update')
                
            except Exception as e:
                logger.error(f"{phone} failed to report: {e}")
                total_failed += 1
        
        print(f"\n{'-'*70}")
        print(f"SCAM REPORT COMPLETED")
        print(f"{'-'*70}")
        print(f"Total Reported: {total_reported}")
        print(f"Total Failed: {total_failed}")
        print(f"{'-'*70}\n")
        
        status.show_success(f"Reported from {total_reported} accounts")
        
    except Exception as e:
        logger.error(f"Scam report error: {e}")
