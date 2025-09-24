"""
Currency utilities for analytics pipeline transformations.
Provides centralized currency symbol mapping and formatting helpers.
"""

from dzgroshared.db.enums import CountryCode


def get_currency_symbol(countrycode: CountryCode) -> str:
    """
    Get currency symbol based on country code.
    
    Args:
        countrycode: Country code
        
    Returns:
        Currency symbol string
    """
    currency_map = {
        CountryCode.INDIA: "₹",
        CountryCode.UNITED_STATES: "$",
        CountryCode.UNITED_KINGDOM: "£",
        CountryCode.CANADA: "C$",
        CountryCode.GERMANY: "€",
        CountryCode.FRANCE: "€",
        CountryCode.ITALY: "€",
        CountryCode.SPAIN: "€",
        CountryCode.NETHERLANDS: "€",
        CountryCode.BELGIUM: "€",
        CountryCode.POLAND: "zł",
        CountryCode.SWEDEN: "kr",
        CountryCode.JAPAN: "¥",
        CountryCode.AUSTRALIA: "A$",
        CountryCode.SINGAPORE: "S$",
        CountryCode.UNITED_ARAB_EMIRATES: "AED",
        CountryCode.SAUDI_ARABIA: "SR",
        CountryCode.MEXICO: "MX$",
        CountryCode.BRAZIL: "R$",
        CountryCode.TURKIYE: "₺",
        CountryCode.EGYPT: "E£",
        CountryCode.SOUTH_AFRICA: "R"
    }
    return currency_map.get(countrycode, "$")  # Default to $ if country not found


def format_currency_value(value: float, countrycode: CountryCode) -> str:
    """
    Format a numeric value as currency with appropriate symbol and magnitude suffixes.
    
    Args:
        value: Numeric value to format
        countrycode: Country code for currency symbol
        
    Returns:
        Formatted currency string (e.g., "₹1.25 Cr", "$1.5 M")
    """
    currency_symbol = get_currency_symbol(countrycode)
    abs_val = abs(value)
    
    if abs_val >= 1000000:
        if countrycode == CountryCode.INDIA and abs_val >= 10000000:
            base_string = f"{abs_val/10000000:.2f} Cr"
        elif countrycode == CountryCode.INDIA:
            base_string = f"{abs_val/100000:.2f} Lacs" if abs_val >= 100000 else f"{abs_val/1000:.2f} K"
        else:
            base_string = f"{abs_val/1000000:.2f} M"
    elif abs_val >= 1000:
        base_string = f"{abs_val/1000:.2f} K"
    else:
        base_string = f"{value:.1f}" if isinstance(value, float) else str(value)
    
    return f"{currency_symbol}{base_string}"


def format_number_value(value: float, countrycode: CountryCode) -> str:
    """
    Format a numeric value with appropriate magnitude suffixes (without currency symbol).
    
    Args:
        value: Numeric value to format
        countrycode: Country code for number formatting style
        
    Returns:
        Formatted number string (e.g., "1.25 Cr", "1.5 M")
    """
    abs_val = abs(value)
    
    if abs_val >= 1000000:
        if countrycode == CountryCode.INDIA and abs_val >= 10000000:
            return f"{abs_val/10000000:.2f} Cr"
        elif countrycode == CountryCode.INDIA:
            return f"{abs_val/100000:.2f} Lacs" if abs_val >= 100000 else f"{abs_val/1000:.2f} K"
        else:
            return f"{abs_val/1000000:.2f} M"
    elif abs_val >= 1000:
        return f"{abs_val/1000:.2f} K"
    else:
        return f"{value:.1f}" if isinstance(value, float) else str(value)


def format_percentage_value(value: float) -> str:
    """
    Format a numeric value as percentage.
    
    Args:
        value: Numeric value to format as percentage
        
    Returns:
        Formatted percentage string (e.g., "12.34%")
    """
    return f"{value:.2f}%"


def format_metric_value(value: float, is_percentage: bool, is_currency: bool, countrycode: CountryCode) -> str:
    """
    Format a metric value based on its type.
    
    Args:
        value: Numeric value to format
        is_percentage: Whether this is a percentage metric
        is_currency: Whether this is a currency metric
        countrycode: Country code for formatting
        
    Returns:
        Formatted value string
    """
    if is_percentage:
        return format_percentage_value(value)
    elif is_currency:
        return format_currency_value(value, countrycode)
    else:
        return format_number_value(value, countrycode)