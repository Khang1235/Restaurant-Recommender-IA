import sqlite3
import filters
import budget
import ranking
import course_generator
import validation
import database
from restaurant import Restaurant


def make_sample_restaurants():
    return [
        Restaurant(1, "Pho Thin", "Hanoi", "budget", 45000, "Vietnamese", 4.5, 1200, ["local specialty"]),
        Restaurant(2, "Sushi Hokkaido", "Hanoi", "expensive", 250000, "Asian", 4.7, 30, ["fresh seafood"]),
        Restaurant(3, "Bun Cha Huong Lien", "Hanoi", "budget", 50000, "Vietnamese", 4.6, 3400, []),
        Restaurant(4, "Highlands Coffee", "Ha Long", "mid-range", 60000, "Cafe", 4.0, 800, ["wifi"]),
    ]


def test_filter_by_location():
    result = filters.filter_by_location(make_sample_restaurants(), "Hanoi")
    assert len(result) == 3


def test_filter_by_budget():
    result = filters.filter_by_budget(make_sample_restaurants(), 100000)
    assert len(result) == 3


def test_apply_all_filters_does_not_hard_cap_price():
    result = filters.apply_all_filters(make_sample_restaurants(), "Hanoi", 100000, ["Asian"])
    assert [r.id for r in result] == [1, 2, 3]


def test_filter_by_preferences():
    result = filters.filter_by_preferences(make_sample_restaurants(), ["Vietnamese"])
    assert [r.id for r in result] == [1, 3]


def test_calculate_total():
    rs = make_sample_restaurants()
    assert budget.calculate_total([rs[0], rs[2]]) == 95000


def test_adjusted_rating_penalises_low_review_count():
    rs = make_sample_restaurants()
    mean = sum(r.rating for r in rs) / len(rs)
    assert rs[1].adjusted_rating(mean) < rs[2].adjusted_rating(mean)


def test_rank_restaurants_uses_preference_as_soft_signal():
    rs = make_sample_restaurants()[:3]
    mean = sum(r.rating for r in rs) / len(rs)
    ranked = ranking.rank_restaurants(rs, ["Vietnamese"], mean)
    assert ranked[0].food_category == "Vietnamese"


def test_generate_course_stays_within_budget():
    rs = make_sample_restaurants()
    ranked = ranking.rank_restaurants(rs[:3], [], 4.5)
    course = course_generator.generate_course(ranked, 2, 100000)
    assert len(course) == 2
    assert budget.calculate_total(course) <= 100000


def test_generate_course_can_use_expensive_meal_when_total_budget_allows():
    rs = [
        Restaurant(1, "Cheap", "Hanoi", "budget", 50000, "Vietnamese", 4.0, 1000, []),
        Restaurant(2, "Dinner", "Hanoi", "expensive", 250000, "Seafood", 4.9, 1000, []),
        Restaurant(3, "Cheap 2", "Hanoi", "budget", 50000, "Vietnamese", 4.0, 1000, []),
    ]
    ranked = ranking.rank_restaurants(rs, ["Seafood"], 4.5)
    course = course_generator.generate_course(ranked, 3, 350000)
    assert len(course) == 3
    assert any(r.id == 2 for r in course)
    assert budget.calculate_total(course) <= 350000


def test_generate_course_does_not_repeat_restaurants():
    rs = make_sample_restaurants()
    course = course_generator.generate_course(rs, 3, 180000)
    assert len({r.id for r in course}) == len(course)


def test_last_slot_does_not_reserve_extra_budget():
    r = make_sample_restaurants()[0]
    assert course_generator.fits_remaining_budget(r, [], 0, 1, 45000, [r])


def test_too_small_budget_returns_without_crashing():
    rs = make_sample_restaurants()
    assert course_generator.generate_course(rs, 2, 1000) == []


def test_validation():
    assert validation.validate_budget("100000")[0]
    assert not validation.validate_budget("-1")[0]
    assert validation.validate_destination("hanoi", ["Hanoi", "Sapa"])[0]
    assert not validation.validate_destination("Tokyo", ["Hanoi", "Sapa"])[0]
    assert validation.validate_num_meals("3")[0]
    assert not validation.validate_num_meals("11")[0]


def test_database_loader_loads_pending_with_neutral_prior(tmp_path):
    csv_path = tmp_path / "restaurants.csv"
    csv_path.write_text(
        "id,name,location,price_range,avg_price_vnd,food_category,purpose,rating,review_count,special_features\n"
        "1,A,Hanoi,budget,50000,Vietnamese,x,4.5,100,wifi;local\n"
        "2,B,Hanoi,budget,40000,Vietnamese,x,,,\n",
        encoding="utf8",
    )
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    database.create_table(conn)
    assert database.load_from_csv(conn, str(csv_path)) == 2
    rows = database.get_all(conn)
    assert rows[0].avg_price == 50000.0
    assert rows[0].special_features == ["wifi", "local"]
    assert rows[1].review_count == 0
    assert rows[1].adjusted_rating(database.get_mean_rating(conn)) == database.get_mean_rating(conn)


def test_edit_restaurant_whitelists_columns():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    database.create_table(conn)
    database.add_restaurant(conn, make_sample_restaurants()[0])
    assert database.edit_restaurant(conn, 1, avg_price=55000) == 1
    assert database.get_all(conn)[0].avg_price == 55000
    try:
        database.edit_restaurant(conn, 1, **{"bad_column": 1})
    except ValueError:
        pass
    else:
        assert False
