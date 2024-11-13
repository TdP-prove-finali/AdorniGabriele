import decimal
from dataclasses import dataclass
@dataclass
class Food:
    ID: int
    food: str
    caloricValue: decimal.Decimal
    fats: decimal.Decimal
    saturatedFats: decimal.Decimal
    carbohydrates: decimal.Decimal
    sugars: decimal.Decimal
    proteins: decimal.Decimal
    fibers: decimal.Decimal
    cholesterol: decimal.Decimal
    sodium: decimal.Decimal
    vitaminA: decimal.Decimal
    vitaminB1: decimal.Decimal
    vitaminB12: decimal.Decimal
    vitaminB2: decimal.Decimal
    vitaminB3: decimal.Decimal
    vitaminB5: decimal.Decimal
    vitaminB6: decimal.Decimal
    vitaminC: decimal.Decimal
    vitaminD: decimal.Decimal
    vitaminE: decimal.Decimal
    vitaminK: decimal.Decimal
    calcium: decimal.Decimal
    iron: decimal.Decimal
    magnesium: decimal.Decimal
    potassium: decimal.Decimal
    nutritionDensity: decimal.Decimal



    def __str__(self):
        return str(f"ID: {self.ID}, {self.food}")

    def __hash__(self):
        return hash(self.ID)
