from dataclasses import dataclass, field


@dataclass
class Restaurant:
    id: int
    name: str
    location: str           
    price_range: str        
    avg_price: float       
    food_category: str      
    rating: float            
    review_count: int        
    special_features: list[str] = field(default_factory=list)

    def matches_preference(self, preferred_category: str) -> bool:
        """Check if this restaurant matches a user's preferred food category."""
        return self.food_category.lower() == preferred_category.lower()

    def is_within_budget(self, budget_per_meal: float) -> bool:
        """Check if this restaurant's average price fits within a per-meal budget."""
        return self.avg_price <= budget_per_meal

    def adjusted_rating(self, dataset_mean: float, min_reviews: int = 50) -> float:
    
        v = self.review_count
        m = min_reviews
        return (v / (v + m)) * self.rating + (m / (v + m)) * dataset_mean

    def __str__(self) -> str:
        return f"{self.name} ({self.location}) - {self.food_category}, {self.avg_price:,.0f}VND, {self.rating}/5 ({self.review_count} reviews)"
