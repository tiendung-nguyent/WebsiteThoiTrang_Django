from django import template

register = template.Library()

@register.filter
def vietnam_number(value):
    """
    Formats a number with '.' as the thousands separator.
    Example: 1000000 -> 1.000.000
    """
    try:
        if value is None:
            return "0"
        
        # Ensure value is numeric
        num = float(value)
        
        # Format with commas as thousands separators, then replace with dots
        # Using :.0f to remove decimals as requested by context (currency often doesn't show cents in VN)
        return "{:,.0f}".format(num).replace(",", ".")
    except (ValueError, TypeError):
        return value
