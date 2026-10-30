from restaurant import Restaurant


def calculate_total(course: list[Restaurant]) -> float:
    """Sum the avg_price of every restaurant in a meal course."""
    return sum(r.avg_price for r in course)


def is_within_budget(course: list[Restaurant], total_budget: float) -> bool:
    """Check whether a full course stays within the user's total budget."""
    return calculate_total(course) <= total_budget


def remaining_budget(course: list[Restaurant], total_budget: float) -> float:
    """How much of the total budget is left after the current course."""
    return total_budget - calculate_total(course)
