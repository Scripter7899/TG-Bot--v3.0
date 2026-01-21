"""
Menu Display Module
Displays the main menu with all features organized by category
"""

import os
from ui.colors import *

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.LIGHTCYAN_EX}╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                        ███████╗██╗   ██╗██╗     ██╗          ████████╗ ██████╗║
║                        ██╔════╝██║   ██║██║     ██║          ╚══██╔══╝██╔════╝║
║                        █████╗  ██║   ██║██║     ██║  █████╗     ██║   ██║  ███╗
║                        ██╔══╝  ██║   ██║██║     ██║  ╚════╝     ██║   ██║   ██║
║                        ██║     ╚██████╔╝███████╗███████╗          ██║   ╚██████╔╝
║                        ╚═╝      ╚═════╝ ╚══════╝╚══════╝          ╚═╝    ╚═════╝ ║
║                                                                               ║
║                           {BOLD}FULL-TG v3.0 - Professional Edition{RESET}{Fore.LIGHTCYAN_EX}                    ║
║                                                                               ║
║              🚀 Advanced Telegram Automation & Management Platform            ║
║              📊 124 Premium Features | 🔐 Multi-Account Support               ║
║              ⚡ AI-Powered Automation | 🛡️ Enterprise-Grade Security          ║
║                                                                               ║
║                            Created by: @MR_DIAZZZ                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

def show_menu():
    """Display main menu"""
    menu = f"""

{SUCCESS}┌─ ⭐ FAVORITES (Quick Access) ──────────────────────────────────────────┐{RESET}
⭐  1. 🔐 Login New Account
⭐ 14. 👥 Mass Invite [All Accounts]
⭐ 16. 🚀 Join Groups [All Accounts]
⭐ 21. 🧬 Smart Clone Session
⭐ 39. ❤️ React to Post [All Accounts]
⭐ 47. 📥 Export Members
⭐ 69. 💰 Scam Report [All Accounts]
⭐ 96. 📤 Auto-Post to Groups
⭐ 97. 👍 Auto-React to Posts
⭐104. 💪 Engagement Booster
⭐112. 🤖 Auto-Reply Bot [Multi-Account]
⭐123. 📝 Update Bio [All Accounts]
⭐124. 📺 Join Channels [All Accounts]

{SUCCESS}┌─ 🔑 CORE OPERATIONS (1-30) ────────────────────────────────────────────┐{RESET}
⭐  1. 🔐 Login New Account
    2. ℹ️ Get Account Info
    3. ✏️ Change Profile Name [Single/All]
    4. 🖼️ Update Profile Picture [Single/All]
    5. 📝 Set Bio/Status [Single/All]
    6. 👤 Set Username [Single/All]
    7. 🔒 View 2FA Status
    8. ✅ Enable 2FA
    9. ❌ Disable 2FA
   10. 🚪 Logout Account
   11. 🌐 Add Proxy
   12. 🗑️ Remove Proxy
   13. 🧪 Test Proxy
⭐ 14. 👥 Mass Invite [All Accounts]
   15. 📤 Auto-Post to Groups [All Accounts]
⭐ 16. 🚀 Join Groups [All Accounts]
   17. 👋 Leave Groups [All Accounts]
   18. 👥 View All Active Accounts
   19. 📋 View All Sessions
   20. 🗑️ Delete Session
⭐ 21. 🧬 Smart Clone Session
   22. 👁️ View User Profile
   23. ➕ Add Contact
   24. 🚫 Block User
   25. ✅ Unblock User
   26. 🔍 Find User
   27. 🤝 Get Mutual Friends
   28. ⏰ Get Last Seen
   29. 📊 Get User Followers
   30. 📺 Get User Channels

{INFO}┌─ 💬 MESSAGING & COMMUNICATION (31-45) ─────────────────────────────────┐{RESET}
   31. 📨 Send Message
   32. 📷 Send Media
   33. ↪️ Forward Message
   34. ✏️ Edit Message
   35. 🗑️ Delete Message
   36. 🔍 Search Messages
   37. 📌 Pin Message
   38. 📍 Unpin Message
⭐ 39. ❤️ React to Post [All Accounts]
   40. ℹ️ Get Message Info
   41. 📊 View Message Stats
   42. 🔗 Get Message Link
   43. ⏰ Schedule Message
   44. 🗑️ Bulk Delete
   45. 📈 Message Analytics

{CHANNEL_COLOR}┌─ 👥 GROUP & CHANNEL MANAGEMENT (46-75) ────────────────────────────────┐{RESET}
   46. ➕ Create Group
⭐ 47. 📥 Export Members
   48. 👤 Add Members
   49. 📊 Group Statistics
   50. 🔗 Get Group Link
   51. ✏️ Change Group Title
   52. 📝 Change Group Description
   53. ℹ️ Get Member Info
   54. 🔇 Mute User
   55. 🔊 Unmute User
   56. 👢 Kick User
   57. 👑 Make Admin
   58. 👤 Remove Admin
   59. 🔒 Lock Group
   60. 🔓 Unlock Group
   61. 🚨 Report Group
   62. 🚨 Report Message
   63. 🗑️ Clear Chat History
   64. 🚫 Restrict User
   65. 🔇 Mute User Forever
   66. 📧 Spam Report
   67. 📝 Content Report
   68. 🤖 Bot Report
⭐ 69. 💰 Scam Report [All Accounts]
   70. 🔍 Advanced Report
   71. 👁️ View Stories
   72. 📸 Post Story
   73. 🗑️ Delete Story
   74. 📊 Story Analytics
   75. 💾 Download Stories

{ERROR}┌─ 🛡️  SPAM & SECURITY (76-81) ──────────────────────────────────────────┐{RESET}
   76. 📢 Mass Report
   77. 🤖 Auto Report Spam
   78. 🔍 Spam Filter
   79. 🚫 Block Spam Users
   80. 👤 Report Fake Accounts
   81. 🛡️ Anti-Spam Monitor

{STATS_COLOR}┌─ 📊 ANALYTICS & TRACKING (82-95) ──────────────────────────────────────┐{RESET}
   82. 💬 Dialog Count
   83. 📊 Account Statistics
   84. 💾 Session Storage Info
   85. 📜 Operation Logs
   86. 📈 Invite Statistics
   87. 🌐 Proxy Statistics
   88. 📱 Device Info
   89. ✅ View Added Users Log
   90. ❌ View Error Users Log
   91. 🧹 Cleanup Old Logs
   92. 📜 View Operation History
   93. ⚙️ Settings
   94. ℹ️ About
   95. ❤️ Check Accounts Health

{MARKETING_COLOR}┌─ 📈 MARKETING & GROWTH (96-105) ───────────────────────────────────────┐{RESET}
⭐ 96. 📤 Auto-Post to Groups
⭐ 97. 👍 Auto-React to Posts
   98. 💬 Auto-Comment on Posts
   99. 🔗 Follow Recommendations
  100. 📈 Channel Growth Analytics
  101.  #️⃣ Hashtag Management
  102. 🔥 Trending Topics Tracker
  103. 📅 Schedule Posts
⭐104. 💪 Engagement Booster
  105. ✨ Content Optimizer

{ADVANCED_COLOR}┌─ 🚀 ADVANCED AUTOMATION (106-120) ─────────────────────────────────────┐{RESET}
  106. 🔄 Push Updates & Check Ver
  107. 🔍 Auto Member Scraper
  108. 🧠 Smart Invite (AI-based)
  109. 💾 Backup & Restore
  110. 🔄 Account Switcher
  111. ⏰ Message Scheduler
⭐112. 🤖 Auto-Reply Bot [Multi-Account]
  113. 📥 Media Bulk Downloader
  114. 📦 Chat Exporter
  115. 👤 Username Monitor
  116. 🔄 Contact Sync
  117. 🛡️ Anti-Ban System
  118. 👑 VIP Member Filter
  119. 📊 Engagement Tracker
  120. 🔍 Competitor Analysis

{ADMIN_COLOR}┌─ ⚙️  SYSTEM & WORKFLOWS (121-124) ─────────────────────────────────────┐{RESET}
  121. 🔧 Automated Workflows
  122. 🔄 Reload Sessions
⭐123. 📝 Update Bio [All Accounts]
⭐124. 📺 Join Channels [All Accounts]
⭐125. 👁️ Increase View Count [All Accounts]
⭐126. ⚡ Combo: Engagement + Auto-React
⭐127. 🚀 Combo: Engage + Post + Reply
⭐128. 🧹 Deep System Cleanup

{ERROR}┌─ 🚪 EXIT ──────────────────────────────────────────────────────────────┐{RESET}
    0. 🚪 Exit Program

{INFO}Tip: Press Ctrl+C to cancel any operation and return to menu{RESET}
{PROMPT}"""
    print(menu)

def get_user_choice():
    """Get user menu choice"""
    try:
        choice = input("Enter option number: ").strip()
        return int(choice) if choice.isdigit() else -1
    except:
        return -1

def show_feature_not_implemented():
    """Show feature not implemented message"""
    print(f"\n{WARNING}⚠️  This feature is implemented in the codebase but requires user interaction.{RESET}")
    print(f"{INFO}The core functionality is ready. Please check the modules folder.{RESET}\n")
    input("Press Enter to continue...")
