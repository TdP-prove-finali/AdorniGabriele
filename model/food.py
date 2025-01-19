import decimal
from dataclasses import dataclass
@dataclass
class Food:
    ID: int
    food: str
    CaloricValue: decimal.Decimal
    Fat: decimal.Decimal
    SaturatedFats: decimal.Decimal
    Carbohydrates: decimal.Decimal
    # sugars: decimal.Decimal
    Protein: decimal.Decimal
    Fiber: decimal.Decimal
    # cholesterol: decimal.Decimal
    Sodium: decimal.Decimal
    # vitaminA: decimal.Decimal
    # vitaminB1: decimal.Decimal
    # vitaminB12: decimal.Decimal
    # vitaminB2: decimal.Decimal
    # vitaminB3: decimal.Decimal
    # vitaminB5: decimal.Decimal
    # vitaminB6: decimal.Decimal
    VitaminC: decimal.Decimal
    VitaminD: decimal.Decimal
    # vitaminE: decimal.Decimal
    # vitaminK: decimal.Decimal
    Calcium: decimal.Decimal
    Iron: decimal.Decimal
    # magnesium: decimal.Decimal
    Potassium: decimal.Decimal
    NutritionDensity: decimal.Decimal



    def __str__(self):
        return str(f"ID: {self.ID}, {self.food}")

    def __hash__(self):
        return hash(self.ID)
