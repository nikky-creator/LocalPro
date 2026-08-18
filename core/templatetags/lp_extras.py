from django import template

register = template.Library()


@register.filter
def star_range(rating):
    """Turns a 0-5 numeric rating into ['full','full','half','empty','empty']."""
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0
    stars = []
    for i in range(1, 6):
        if rating >= i:
            stars.append('full')
        elif rating >= i - 0.5:
            stars.append('half')
        else:
            stars.append('empty')
    return stars


@register.filter
def percent_of_five(rating):
    """Converts a 0-5 rating to a 0-100 percentage, for progress-bar widths."""
    try:
        return round((float(rating) / 5) * 100)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0


@register.filter
def initials(name):
    """First letters of the first two words of any name/business string."""
    if not name:
        return '?'
    parts = [p for p in str(name).split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    elif parts:
        return parts[0][:2].upper()
    return '?'


@register.filter
def get_item(dictionary, key):
    """Dict lookup that also works when the template loop var is a string
    but the dict (e.g. rating_breakdown) uses integer keys, or vice versa."""
    if dictionary is None:
        return None
    if key in dictionary:
        return dictionary[key]
    try:
        return dictionary.get(int(key))
    except (TypeError, ValueError):
        return None
