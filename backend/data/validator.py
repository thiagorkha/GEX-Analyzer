"""
Data validation module for GEX Analyzer
Validates market data and input parameters
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates market data and parameters"""
    
    MIN_PRICE = 0.0001
    MAX_PRICE = 1000000.0
    MIN_VOLUME = 0
    MAX_VOLUME = 10**15
    
    @staticmethod
    def validate_ohlc_data(data: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate OHLC data structure and values
        
        Args:
            data: DataFrame with OHLC data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_columns = {'open', 'high', 'low', 'close', 'volume'}
        
        if not isinstance(data, pd.DataFrame):
            return False, "Data must be a pandas DataFrame"
        
        if data.empty:
            return False, "Data cannot be empty"
        
        # Check required columns
        missing_cols = required_columns - set(data.columns.str.lower())
        if missing_cols:
            return False, f"Missing columns: {missing_cols}"
        
        # Normalize column names
        data.columns = data.columns.str.lower()
        
        # Validate price relationships
        invalid_prices = (
            (data['high'] < data['low']).any() or
            (data['close'] > data['high']).any() or
            (data['close'] < data['low']).any() or
            (data['open'] > data['high']).any() or
            (data['open'] < data['low']).any()
        )
        
        if invalid_prices:
            return False, "Invalid price relationships (high < low or close out of range)"
        
        # Validate price ranges
        if (data['close'] < DataValidator.MIN_PRICE).any():
            return False, f"Prices below minimum {DataValidator.MIN_PRICE}"
        
        if (data['close'] > DataValidator.MAX_PRICE).any():
            return False, f"Prices above maximum {DataValidator.MAX_PRICE}"
        
        # Validate volume
        if (data['volume'] < DataValidator.MIN_VOLUME).any():
            return False, "Volume cannot be negative"
        
        if (data['volume'] > DataValidator.MAX_VOLUME).any():
            return False, "Volume exceeds maximum"
        
        return True, "Valid data"
    
    @staticmethod
    def validate_parameters(params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate analysis parameters
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(params, dict):
            return False, "Parameters must be a dictionary"
        
        # Validate required parameters
        required = {'symbol', 'timeframe'}
        missing = required - set(params.keys())
        if missing:
            return False, f"Missing parameters: {missing}"
        
        # Validate symbol
        symbol = params.get('symbol', '')
        if not isinstance(symbol, str) or len(symbol) == 0:
            return False, "Symbol must be a non-empty string"
        
        # Validate timeframe
        valid_timeframes = {'1m', '5m', '15m', '1h', '4h', '1d', '1w', '1M'}
        if params.get('timeframe') not in valid_timeframes:
            return False, f"Invalid timeframe. Must be one of {valid_timeframes}"
        
        return True, "Valid parameters"
    
    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize data
        
        Args:
            data: Raw data
            
        Returns:
            Cleaned data
        """
        # Normalize column names
        data.columns = data.columns.str.lower()
        
        # Remove duplicates
        data = data.drop_duplicates(subset=['open', 'high', 'low', 'close', 'volume'])
        
        # Handle missing values
        data = data.dropna(subset=['close'])
        
        # Sort by date/time if index exists
        if hasattr(data.index, 'name') and data.index.name:
            data = data.sort_index()
        
        return data
