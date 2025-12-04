"""
Validation Rules Engine
Main validation logic that applies all validation rules
"""
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import config
from .date_validator import DateValidator
from .numeric_validator import NumericValidator

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Main validation engine that applies all validation rules"""
    
    def __init__(self):
        """Initialize validation engine"""
        self.date_validator = DateValidator()
        self.numeric_validator = NumericValidator()
    
    def validate_required_fields(self, fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that all required fields are present
        
        Args:
            fields: Dictionary of extracted fields
            
        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        missing_fields = []
        
        for required_field in config.REQUIRED_FIELDS:
            if required_field not in fields or fields[required_field] is None or fields[required_field] == "":
                missing_fields.append(required_field)
        
        is_valid = len(missing_fields) == 0
        
        if not is_valid:
            logger.warning(f"Missing required fields: {missing_fields}")
        
        return (is_valid, missing_fields)
    
    def validate_date_format(self, date_str: Optional[str], field_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate date format
        
        Args:
            date_str: Date string to validate
            field_name: Name of the date field
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if date_str is None:
            return (True, None)  # Optional fields are allowed to be None
        
        if not self.date_validator.is_valid_date_format(date_str):
            error_msg = f"{field_name} must be in ISO format (YYYY-MM-DD), got: {date_str}"
            logger.warning(error_msg)
            return (False, error_msg)
        
        return (True, None)
    
    def validate_currency(self, currency: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate currency code
        
        Args:
            currency: Currency code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if currency is None:
            return (False, "Currency is required")
        
        valid_currencies = config.VALIDATION_RULES["valid_currencies"]
        
        if currency.upper() not in valid_currencies:
            error_msg = f"Invalid currency code: {currency}. Must be one of: {valid_currencies}"
            logger.warning(error_msg)
            return (False, error_msg)
        
        return (True, None)
    
    def validate_numeric_fields(self, fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate numeric fields
        
        Args:
            fields: Dictionary of extracted fields
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate total_amount
        total_amount = fields.get("total_amount")
        if not self.numeric_validator.is_valid_number(total_amount):
            errors.append("total_amount must be a valid number")
        elif not self.numeric_validator.is_positive(total_amount):
            errors.append(f"total_amount must be positive, got: {total_amount}")
        
        # Validate tax_amount (optional)
        tax_amount = fields.get("tax_amount")
        if tax_amount is not None:
            if not self.numeric_validator.is_valid_number(tax_amount):
                errors.append("tax_amount must be a valid number")
            elif not self.numeric_validator.is_non_negative(tax_amount):
                errors.append(f"tax_amount must be non-negative, got: {tax_amount}")
        
        # Validate total > tax
        if total_amount is not None and tax_amount is not None:
            is_valid, error_msg = self.numeric_validator.validate_total_greater_than_tax(
                total_amount, tax_amount
            )
            if not is_valid:
                errors.append(error_msg)
        
        # Flag negative values
        warnings = self.numeric_validator.flag_negative_values(total_amount, tax_amount)
        errors.extend(warnings)
        
        return (len(errors) == 0, errors)
    
    def validate_date_logic(self, fields: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate date-related business logic
        
        Args:
            fields: Dictionary of extracted fields
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        issue_date = fields.get("issue_date")
        due_date = fields.get("due_date")
        
        # Validate issue_date format
        if issue_date:
            is_valid, error_msg = self.validate_date_format(issue_date, "issue_date")
            if not is_valid:
                errors.append(error_msg)
        
        # Validate due_date format
        if due_date:
            is_valid, error_msg = self.validate_date_format(due_date, "due_date")
            if not is_valid:
                errors.append(error_msg)
        
        # Validate due_date > issue_date
        if issue_date and due_date:
            is_valid, error_msg = self.date_validator.validate_due_date_after_issue_date(
                issue_date, due_date
            )
            if not is_valid:
                errors.append(error_msg)
        
        return (len(errors) == 0, errors)
    
    def calculate_validation_score(self, fields: Dict[str, Any], validation_errors: List[str]) -> float:
        """
        Calculate validation confidence score (0.0 to 1.0)
        
        Args:
            fields: Dictionary of extracted fields
            validation_errors: List of validation errors
            
        Returns:
            Validation score between 0.0 and 1.0
        """
        total_fields = len(config.EXTRACTION_SCHEMA)
        filled_fields = len([v for v in fields.values() if v is not None and v != ""])
        
        # Base score based on filled fields
        field_completion_score = filled_fields / total_fields if total_fields > 0 else 0.0
        
        # Penalty for validation errors
        error_penalty = min(len(validation_errors) * 0.1, 0.5)  # Max 0.5 penalty
        
        # Penalty for missing required fields
        _, missing_required = self.validate_required_fields(fields)
        required_penalty = len(missing_required) * 0.2  # 0.2 per missing required field
        
        score = field_completion_score - error_penalty - required_penalty
        score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
        
        return round(score, 2)
    
    def determine_validation_status(self, score: float, missing_required: List[str], validation_errors: List[str]) -> str:
        """
        Determine validation status based on score and errors
        
        Args:
            score: Validation score
            missing_required: List of missing required fields
            validation_errors: List of validation errors
            
        Returns:
            Validation status: PASSED, PARTIAL, or FAILED
        """
        if len(missing_required) > 0:
            return config.VALIDATION_STATUS["FAILED"]
        
        if len(validation_errors) == 0 and score >= 0.8:
            return config.VALIDATION_STATUS["PASSED"]
        
        if score >= 0.5:
            return config.VALIDATION_STATUS["PARTIAL"]
        
        return config.VALIDATION_STATUS["FAILED"]
    
    def validate_all(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all validation rules on extracted fields
        
        Args:
            fields: Dictionary of extracted fields
            
        Returns:
            Dictionary with validation results
        """
        logger.info("Starting validation...")
        
        validation_results = {
            "validation_errors": [],
            "missing_fields": [],
            "validation_score": 0.0,
            "validation_status": config.VALIDATION_STATUS["FAILED"],
        }
        
        # Validate required fields
        required_valid, missing_required = self.validate_required_fields(fields)
        validation_results["missing_fields"] = missing_required
        
        # Validate date formats and logic
        date_valid, date_errors = self.validate_date_logic(fields)
        validation_results["validation_errors"].extend(date_errors)
        
        # Validate numeric fields
        numeric_valid, numeric_errors = self.validate_numeric_fields(fields)
        validation_results["validation_errors"].extend(numeric_errors)
        
        # Validate currency
        currency_valid, currency_error = self.validate_currency(fields.get("currency"))
        if not currency_valid:
            validation_results["validation_errors"].append(currency_error)
        
        # Calculate validation score
        all_errors = validation_results["validation_errors"]
        validation_results["validation_score"] = self.calculate_validation_score(fields, all_errors)
        
        # Determine validation status
        validation_results["validation_status"] = self.determine_validation_status(
            validation_results["validation_score"],
            missing_required,
            all_errors
        )
        
        logger.info(
            f"Validation completed. Status: {validation_results['validation_status']}, "
            f"Score: {validation_results['validation_score']}, "
            f"Errors: {len(all_errors)}"
        )
        
        return validation_results

