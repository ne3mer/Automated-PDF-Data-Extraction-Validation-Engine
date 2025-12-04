"""
Date Validation Module
Validates date fields and date-related logic
"""
import logging
from datetime import datetime
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class DateValidator:
    """Validates date fields and date-related business rules"""
    
    @staticmethod
    def is_valid_date_format(date_str: Optional[str]) -> bool:
        """
        Check if date string is in ISO format (YYYY-MM-DD)
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid ISO format
        """
        if not date_str:
            return False
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime object
        
        Args:
            date_str: Date string in ISO format
            
        Returns:
            datetime object or None
        """
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def is_date_after(date1_str: Optional[str], date2_str: Optional[str]) -> bool:
        """
        Check if date1 is after date2
        
        Args:
            date1_str: First date string
            date2_str: Second date string
            
        Returns:
            True if date1 > date2, False otherwise
        """
        if not date1_str or not date2_str:
            return False
        
        date1 = DateValidator.parse_date(date1_str)
        date2 = DateValidator.parse_date(date2_str)
        
        if not date1 or not date2:
            return False
        
        return date1 > date2
    
    @staticmethod
    def is_date_before(date1_str: Optional[str], date2_str: Optional[str]) -> bool:
        """
        Check if date1 is before date2
        
        Args:
            date1_str: First date string
            date2_str: Second date string
            
        Returns:
            True if date1 < date2, False otherwise
        """
        if not date1_str or not date2_str:
            return False
        
        date1 = DateValidator.parse_date(date1_str)
        date2 = DateValidator.parse_date(date2_str)
        
        if not date1 or not date2:
            return False
        
        return date1 < date2
    
    @staticmethod
    def validate_due_date_after_issue_date(issue_date: Optional[str], due_date: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate that due date is after issue date
        
        Args:
            issue_date: Issue date string
            due_date: Due date string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not issue_date or not due_date:
            return (True, None)  # Can't validate if dates are missing
        
        if not DateValidator.is_valid_date_format(issue_date):
            return (False, f"Invalid issue date format: {issue_date}")
        
        if not DateValidator.is_valid_date_format(due_date):
            return (False, f"Invalid due date format: {due_date}")
        
        if not DateValidator.is_date_after(due_date, issue_date):
            return (False, f"Due date ({due_date}) must be after issue date ({issue_date})")
        
        return (True, None)
    
    @staticmethod
    def is_date_in_future(date_str: Optional[str]) -> bool:
        """
        Check if date is in the future
        
        Args:
            date_str: Date string to check
            
        Returns:
            True if date is in the future
        """
        if not date_str:
            return False
        
        date = DateValidator.parse_date(date_str)
        if not date:
            return False
        
        return date > datetime.now()
    
    @staticmethod
    def is_date_in_past(date_str: Optional[str], days_threshold: int = 365) -> bool:
        """
        Check if date is more than N days in the past
        
        Args:
            date_str: Date string to check
            days_threshold: Number of days threshold
            
        Returns:
            True if date is more than threshold days in the past
        """
        if not date_str:
            return False
        
        date = DateValidator.parse_date(date_str)
        if not date:
            return False
        
        from datetime import timedelta
        threshold_date = datetime.now() - timedelta(days=days_threshold)
        
        return date < threshold_date

