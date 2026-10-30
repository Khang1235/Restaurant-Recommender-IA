from restaurant import Restaurant

RATING_WEIGHT = 0.6
PREFERENCE_WEIGHT = 0.4
MIN_REVIEWS = 50


def score_restaurant(r, preferred_categories, dataset_mean):
    adjusted = r.adjusted_rating(dataset_mean, MIN_REVIEWS)
    normalized_rating = adjusted / 5.0

    if not preferred_categories:
        preference_score = 1.0
    else:
        preference_score = 1.0 if any(
            r.matches_preference(c) for c in preferred_categories
        ) else 0.0

    return (
        normalized_rating * RATING_WEIGHT
        + preference_score * PREFERENCE_WEIGHT
    )


def rank_restaurants(restaurants, preferred_categories, dataset_mean):
    """
    Sort by score, then adjusted rating, then review count, then lower price.
    This makes ties deterministic rather than relying on dataset order.
    """
    return sorted(
        restaurants,
        key=lambda r: (
            score_restaurant(r, preferred_categories, dataset_mean),
            r.adjusted_rating(dataset_mean, MIN_REVIEWS),
            r.review_count,
            -r.avg_price,
        ),
        reverse=True,
    )
