import decimal

from database.DB_connect import DBConnect
from model.food import Food
class DAO():
    def __init__(self):
        pass
    @staticmethod
    def getAllFood():
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
                SELECT f.ID, f.food, f.`Caloric Value` AS CaloricValue, f.Fat, f.`Saturated Fats` AS SaturatedFats, 
                f.Carbohydrates, f.Protein, f.`Dietary Fiber` AS Fiber, f.Sodium, 
                f.`Vitamin C` AS VitaminC, f.`Vitamin D` AS VitaminD, f.Calcium, f.Iron, f.Potassium, 
                f.`Nutrition Density` AS NutritionDensity
                FROM food_nutrients AS f
                """
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(Food(**row))
        cursor.close()
        cnx.close()
        return result

    @staticmethod
    def getFoodPers(switches_state: dict) -> list[Food]:
        """
        Recupera gli alimenti filtrati in base alle preferenze degli switch indicanti le preferenze alimentari.
        :param switches_state: Dizionario che contiene lo stato degli switch (es. Vegano: True/False).
        :return: Lista di oggetti Food filtrata.
        """
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary=True)
        result = []
        query = """
            SELECT 
                f.ID, f.food, f.`Caloric Value` AS CaloricValue, f.Fat, f.`Saturated Fats` AS SaturatedFats, 
                f.Carbohydrates, f.Protein, f.`Dietary Fiber` AS Fiber, f.Sodium, 
                f.`Vitamin C` AS VitaminC, f.`Vitamin D` AS VitaminD, f.Calcium, f.Iron, f.Potassium, 
                f.`Nutrition Density` AS NutritionDensity
            FROM food_nutrients AS f
            INNER JOIN food_params AS p ON f.ID = p.ID
            WHERE 1=1
        """
        conditions = []
        for toggle_name, is_active in switches_state.items():
            if is_active:
                conditions.append(f"p.{toggle_name} = 1")

        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query)
        for row in cursor:
            result.append(Food(**row))
        cursor.close()
        cnx.close()

        return result

    @staticmethod
    def getFoodByNutrient(nutrient):
        allowed_nutrients = {"Vitamin C", "Vitamin D", "Calcium", "Iron", "Potassium","Vitamin A", "Vitamin B1",
                             "Vitamin B12", "Vitamin B2", "Vitamin B3", "Vitamin B5", "Vitamin B6", "Vitamin E",
                             "Vitamin K", "Magnesium", "Phosphorus", "Selenium", "Zinc"}
        if nutrient not in allowed_nutrients:
            raise ValueError("Micronutriente non valido")

        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = f"""
            SELECT food, `{nutrient}` AS nutrient_value
            FROM food_nutrients
            WHERE `{nutrient}` IS NOT NULL
            AND `{nutrient}` <> 0
            ORDER BY `{nutrient}` DESC;
        """

        cursor.execute(query)
        result = []
        for row in cursor:
            result.append((row["food"], row["nutrient_value"]))

        cursor.close()
        cnx.close()
        return result






