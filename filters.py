from restaurant import Restaurant


def filter_by_location(restaurants, destination):
    return [r for r in restaurants if r.location.lower() == destination.lower()]


def filter_by_budget(restaurants, budget_per_meal):
    return [r for r in restaurants if r.is_within_budget(budget_per_meal)]


def filter_by_preferences(restaurants, preferred_categories):
    """Keep restaurants matching at least one preferred category."""
    if not preferred_categories:
        return restaurants
    return [
        r for r in restaurants
        if any(r.matches_preference(category) for category in preferred_categories)
    ]


def apply_all_filters(restaurants, destination, total_budget, preferred_categories):
    """Apply only the hard destination constraint.

    Total budget is enforced by course generation, not as a per-meal cap.
    Preferences remain a soft ranking signal so an expensive but relevant
    restaurant is not removed before ranking.
    """
    return filter_by_location(restaurants, destination)
