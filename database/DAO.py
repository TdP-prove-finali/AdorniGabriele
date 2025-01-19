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
                SELECT *
                FROM final_combined_dataset f
                """

        cursor.execute(query)

        result = []

        for row in cursor:
            result.append(Food(
                food=row[0],
                caloricValue=decimal.Decimal(row[1]),
                fats=decimal.Decimal(row[2]),
                saturatedFats=decimal.Decimal(row[3]),
                carbohydrates=decimal.Decimal(row[4]),
                sugars=decimal.Decimal(row[5]),
                proteins=decimal.Decimal(row[6]),
                fibers=decimal.Decimal(row[7]),
                cholesterol=decimal.Decimal(row[8]),
                sodium=decimal.Decimal(row[9]),
                vitaminA=decimal.Decimal(row[10]),
                vitaminB1=decimal.Decimal(row[11]),
                vitaminB12=decimal.Decimal(row[12]),
                vitaminB2=decimal.Decimal(row[13]),
                vitaminB3=decimal.Decimal(row[14]),
                vitaminB5=decimal.Decimal(row[15]),
                vitaminB6=decimal.Decimal(row[16]),
                vitaminC=decimal.Decimal(row[17]),
                vitaminD=decimal.Decimal(row[18]),
                vitaminE=decimal.Decimal(row[19]),
                vitaminK=decimal.Decimal(row[20]),
                calcium=decimal.Decimal(row[21]),
                iron=decimal.Decimal(row[22]),
                magnesium=decimal.Decimal(row[23]),
                potassium=decimal.Decimal(row[24]),
                nutritionDensity=decimal.Decimal(row[25]),
                ID=row[26]
            ))

        cursor.close()
        cnx.close()
        return result

    @staticmethod
    def getFoodPer(toggles_dict):



        cnx = DBConnect.get_connection()

        cursor = cnx.cursor(dictionary=True)

        query = """
                   query che prende i cibi selezionando in base alle personalizzazioni
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
        Recupera gli alimenti filtrati in base alle preferenze degli switch.
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

        # Aggiungi filtri in base allo stato degli switch attivi
        conditions = []
        for toggle_name, is_active in switches_state.items():
            if is_active:  # Aggiungi filtro solo se l'interruttore è attivo
                conditions.append(f"p.{toggle_name} = 1")

        if conditions:
            query += " AND " + " AND ".join(conditions)

        # Esegui la query e restituisci i risultati come oggetti Food
        cursor.execute(query)
        for row in cursor:
            result.append(Food(**row))
        cursor.close()
        cnx.close()

        return result





