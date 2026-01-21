"""
Background Task Manager
Manages recurring background tasks like auto-posting
"""

import asyncio
from datetime import datetime
from core.logger import logger

class BackgroundTaskManager:
    """Manages background tasks that run independently"""
    
    def __init__(self):
        self.tasks = {}
        self.stop_flags = {}
    
    def start_task(self, task_name, coroutine):
        """Start a background task"""
        if task_name in self.tasks and not self.tasks[task_name].done():
            logger.warning(f"Task '{task_name}' is already running")
            return False
        
        # Create stop flag
        self.stop_flags[task_name] = False
        
        # Start task
        task = asyncio.create_task(coroutine)
        self.tasks[task_name] = task
        
        logger.info(f"Started background task: {task_name}")
        return True
    
    def stop_task(self, task_name):
        """Stop a background task"""
        if task_name not in self.tasks:
            logger.warning(f"Task '{task_name}' not found")
            return False
        
        # Set stop flag
        self.stop_flags[task_name] = True
        
        # Cancel task
        if not self.tasks[task_name].done():
            self.tasks[task_name].cancel()
        
        logger.info(f"Stopped background task: {task_name}")
        return True
    
    def is_running(self, task_name):
        """Check if a task is running"""
        if task_name not in self.tasks:
            return False
        return not self.tasks[task_name].done()
    
    def should_stop(self, task_name):
        """Check if task should stop"""
        return self.stop_flags.get(task_name, False)
    
    def list_tasks(self):
        """List all tasks and their status"""
        result = []
        for name, task in self.tasks.items():
            status = "Running" if not task.done() else "Stopped"
            result.append(f"{name}: {status}")
        return result
    
    async def stop_all(self):
        """Stop all background tasks"""
        for task_name in list(self.tasks.keys()):
            self.stop_task(task_name)
        
        # Wait for all tasks to complete
        for task in self.tasks.values():
            if not task.done():
                try:
                    await asyncio.wait_for(task, timeout=5.0)
                except:
                    pass

# Global instance
background_tasks = BackgroundTaskManager()
