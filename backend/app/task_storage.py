import os
import json
from typing import Dict, Any
import logging

logger = logging.getLogger("job_search_app.task_storage")

class TaskStorage:
    """
    A simple class for storing and retrieving tasks in memory with optional persistence to disk
    """
    
    def __init__(self, storage_file: str = "./task_storage.json"):
        """
        Initialize the TaskStorage
        
        Args:
            storage_file: Optional path to a JSON file for persisting tasks
        """
        self.tasks = {}
        self.storage_file = storage_file
        
        # Try to load existing tasks if the storage file exists
        self._load_from_disk()
        
        logger.info(f"TaskStorage initialized with {len(self.tasks)} tasks")
    
    def _load_from_disk(self) -> None:
        """Load tasks from disk if the storage file exists"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    self.tasks = json.load(f)
                logger.info(f"Loaded {len(self.tasks)} tasks from {self.storage_file}")
        except Exception as e:
            logger.error(f"Error loading tasks from disk: {str(e)}")
    
    def _save_to_disk(self) -> None:
        """Save tasks to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.storage_file)), exist_ok=True)
            
            # Save tasks to file
            with open(self.storage_file, 'w') as f:
                json.dump(self.tasks, f)
            logger.info(f"Saved {len(self.tasks)} tasks to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving tasks to disk: {str(e)}")
    
    def get(self, task_id: str) -> Dict[str, Any]:
        """
        Get a task by ID
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            The task dictionary or an empty dict if not found
        """
        return self.tasks.get(task_id, {})
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all tasks
        
        Returns:
            Dictionary of all tasks
        """
        return self.tasks
    
    def add(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """
        Add or update a task
        
        Args:
            task_id: The ID of the task
            task_data: The task data
        """
        self.tasks[task_id] = task_data
        self._save_to_disk()
        
    def update(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Update an existing task
        
        Args:
            task_id: The ID of the task to update
            task_data: The new task data
            
        Returns:
            True if the task was updated, False if not found
        """
        if task_id in self.tasks:
            self.tasks[task_id] = task_data
            self._save_to_disk()
            return True
        return False
    
    def delete(self, task_id: str) -> bool:
        """
        Delete a task
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            True if the task was deleted, False if not found
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_to_disk()
            return True
        return False
