import math


def validate_budget(raw_budget):
    try:
        value = float(raw_budget.replace(",", "").strip())
    except (ValueError, AttributeError):
        return False, "Budget must be a number."
    if not math.isfinite(value):
        return False, "Budget must be a finite number."
    if value <= 0:
        return False, "Budget must be greater than zero."
    return True, ""


def validate_destination(raw_destination, known_locations):
    if not raw_destination.strip():
        return False, "Destination cannot be empty."
    if raw_destination.strip().lower() not in {
        location.lower() for location in known_locations
    }:
        return False, "Destination is not one of the available cities."
    return True, ""


def validate_num_meals(raw_num_meals):
    try:
        value = int(raw_num_meals.strip())
    except (ValueError, AttributeError):
        return False, "Number of meals must be a whole number."
    if not (1 <= value <= 10):
        return False, "Number of meals must be between 1 and 10."
    return True, ""
