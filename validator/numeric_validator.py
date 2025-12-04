"""
Numeric Validation Module
Validates numeric fields and numeric-related logic
"""
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class NumericValidator:
    """Validates numeric fields and numeric-related business rules"""
    
    @staticmethod
    def is_valid_number(value: Optional[float]) -> bool:
        """
        Check if value is a valid number
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid number
        """
        if value is None:
            return False
        
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_positive(value: Optional[float]) -> bool:
        """
        Check if value is positive
        
        Args:
            value: Value to check
            
        Returns:
            True if positive
        """
        if not NumericValidator.is_valid_number(value):
            return False
        
        return float(value) > 0
    
    @staticmethod
    def is_non_negative(value: Optional[float]) -> bool:
        """
        Check if value is non-negative
        
        Args:
            value: Value to check
            
        Returns:
            True if non-negative
        """
        if not NumericValidator.is_valid_number(value):
            return False
        
        return float(value) >= 0
    
    @staticmethod
    def validate_total_greater_than_tax(total_amount: Optional[float], tax_amount: Optional[float]) -> Tuple[bool, Optional[str]]:
        """
        Validate that total amount is greater than tax amount
        
        Args:
            total_amount: Total amount value
            tax_amount: Tax amount value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not NumericValidator.is_valid_number(total_amount):
            return (False, "Total amount is not a valid number")
        
        if tax_amount is None:
            return (True, None)  # Tax is optional
        
        if not NumericValidator.is_valid_number(tax_amount):
            return (False, "Tax amount is not a valid number")
        
        if float(total_amount) <= float(tax_amount):
            return (False, f"Total amount ({total_amount}) must be greater than tax amount ({tax_amount})")
        
        return (True, None)
    
    @staticmethod
    def validate_amounts_positive(total_amount: Optional[float], tax_amount: Optional[float]) -> Tuple[bool, Optional[str]]:
        """
        Validate that amounts are positive
        
        Args:
            total_amount: Total amount value
            tax_amount: Tax amount value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not NumericValidator.is_positive(total_amount):
            return (False, f"Total amount must be positive, got: {total_amount}")
        
        if tax_amount is not None and not NumericValidator.is_non_negative(tax_amount):
            return (False, f"Tax amount must be non-negative, got: {tax_amount}")
        
        return (True, None)
    
    @staticmethod
    def is_within_range(value: Optional[float], min_val: float, max_val: float) -> bool:
        """
        Check if value is within specified range
        
        Args:
            value: Value to check
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            True if within range
        """
        if not NumericValidator.is_valid_number(value):
            return False
        
        val = float(value)
        return min_val <= val <= max_val
    
    @staticmethod
    def flag_negative_values(total_amount: Optional[float], tax_amount: Optional[float]) -> List[str]:
        """
        Flag negative values in amounts
        
        Args:
            total_amount: Total amount value
            tax_amount: Tax amount value
            
        Returns:
            List of warning messages for negative values
        """
        warnings = []
        
        if total_amount is not None and float(total_amount) < 0:
            warnings.append(f"Total amount is negative: {total_amount}")
        
        if tax_amount is not None and float(tax_amount) < 0:
            warnings.append(f"Tax amount is negative: {tax_amount}")
        
        return warnings

