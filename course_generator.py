from restaurant import Restaurant
from budget import calculate_total


def fits_remaining_budget(candidate, course_so_far, slot_index, num_meals, total_budget, ranked_restaurants=None):
    if num_meals <= 0 or slot_index < 0 or slot_index >= num_meals:
        return False

    new_total = calculate_total(course_so_far) + candidate.avg_price
    remaining_slots = num_meals - slot_index - 1
    if new_total > total_budget:
        return False
    if remaining_slots == 0:
        return True

    if ranked_restaurants is None:
        # Backward-compatible fallback for direct unit calls.
        return new_total + remaining_slots * (total_budget / num_meals) * 0.5 <= total_budget

    used_ids = {r.id for r in course_so_far}
    used_ids.add(candidate.id)
    cheapest = sorted(
        r.avg_price for r in ranked_restaurants if r.id not in used_ids
    )
    if len(cheapest) < remaining_slots:
        return False

    reserve_for_others = sum(cheapest[:remaining_slots])
    return new_total + reserve_for_others <= total_budget


def generate_course(ranked_restaurants, num_meals, total_budget):
    if num_meals <= 0 or total_budget <= 0:
        return []

    course = []
    used_ids = set()

    for slot_index in range(num_meals):
        chosen = None
        for r in ranked_restaurants:
            if r.id in used_ids:
                continue
            if fits_remaining_budget(
                r, course, slot_index, num_meals, total_budget, ranked_restaurants
            ):
                chosen = r
                break

        if chosen is None:
            break

        course.append(chosen)
        used_ids.add(chosen.id)

    return course
