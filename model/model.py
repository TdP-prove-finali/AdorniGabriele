from database.DAO import DAO
from model.food import Food


class Model:

    def __init__(self):
        self.all_foods_list = None

        pass

    # Metodo per calcolare il bmr (Basal Metabolic Rate)
    def calculate_bmr(self, weight, height, age, gender):
        if gender == 'male':
            # Formula per gli uomini
            bmr = 10 * float(weight) + 6.25 * float(height) - 5 * float(age) + 5
        else:
            # Formula per le donne
            bmr = 10 * float(weight) + 6.25 * float(height) - 5 * float(age) - 161
        return bmr

    # Metodo per calcolare il TDEE (Total Daily Energy Expenditure) in base al livello di attività fisica

    def calculate_tdee(self, bmr, activity_level):

        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        if activity_level not in activity_multipliers:
            raise ValueError("Invalid activity level.")

        return round(bmr * activity_multipliers.get(activity_level), 2)

    # Metodo per personalizzare il TDEE in base all'obiettivo dell'utente (es. perdita di peso, mantenimento, aumento di massa)

    def adjust_for_goal(self, tdee, goal):
        if goal == 'weight_loss':
            return tdee - 500  # Riduzione calorica per perdere peso
        elif goal == 'weight_gain':
            return tdee + 500  # Aumento calorico per aumentare massa
        else:
            return tdee  # Mantenimento

    # prende dal DAO tutto il cibo
    def get_all_foods(self):
        self.all_foods_list = DAO.getAllFood()
        pass

    # prende dal DAO il cibo filtrato in base alle preferenze (toggle)
    def get_filtered_food(self, list_of_preferences):
        lista_temp = DAO.getFoodPers(list_of_preferences)
        self.filtered_food_list = lista_temp
        return lista_temp

    # calcola il fabbisogno di nutrienti in base ai parametri dell'utente presi in input
    @staticmethod
    def calculate_nutrients_requirement(tdee: float, userdata: dict):
        weight = float(userdata["weight"])
        requirements = {
            "Calories": tdee,
            "Fat": round(0.3 * tdee / 9, 2),  # 30% delle kcal dai grassi totali (g)
            "SaturatedFats": round(0.1 * tdee / 9, 2),  # 10% delle kcal da grassi saturi (g)
            "Carbohydrates": round(0.5 * tdee / 4, 2),  # 50% delle kcal dai carboidrati (g)
            "Protein": weight * (0.8 if userdata["gender"] == "Female" else 1.0),  # 0.8g/kg per donne, 1g/kg per uomini
            "Fiber": 25 if userdata["gender"] == "Female" else 30,  # Obiettivo giornaliero di fibre (g)
            "Sodium": 1500 if int(userdata["age"]) < 50 else 1300,  # mg, raccomandazioni per età
            "VitaminC": 75 if userdata["gender"] == "Female" else 90,  # mg
            "VitaminD": 15,  # mcg (valore generico)
            "Calcium": 1000,  # mg
            "Iron": 18 if userdata["gender"] == "Female" else 8,  # mg
            "Potassium": 3400 if userdata["gender"] == "Male" else 2600,  # mg
        }
        print(sum(requirements.values()))
        return requirements


    def generate_lists_recursive_v0_no_tolerance(self, tdee: float, userdata: dict, preferences: dict,  max_items: int = 10) -> list[Food]:
        """
        Genera una lista ottimizzata di cibi usando un approccio ricorsivo.
        :param tdee: Calorie totali giornaliere (kcal).
        :param userdata: Dizionario con i parametri dell'utente
        :param preferences: Dizionario con le preferenze dietetiche dell'utente
        :param max_items: Numero massimo di prodotti nella lista.
        :return: Lista ottimizzata di oggetti Food.
        """
        food_list = self.get_filtered_food(preferences)
        requirements = self.calculate_nutrients_requirement(tdee, userdata)
        best_list = []
        best_diff = float('inf')

        def helper(current_list, remaining_foods, current_fabbisogno, current_calories):
            nonlocal best_list, best_diff

            # Se abbiamo raggiunto il numero massimo di prodotti, valuta la soluzione
            if len(current_list) == max_items:
                if current_calories > tdee:  # Scarta combinazioni che superano le calorie
                    return

                # Calcola la differenza dai fabbisogni
                diff = sum(
                    abs(current_fabbisogno[key] - sum(float(getattr(food, key, 0)) for food in current_list))
                    for key in requirements
                )

                # Aggiorna la migliore soluzione se necessario
                if diff < best_diff:
                    best_diff = diff
                    best_list = list(current_list)
                return

            # Esplora le combinazioni aggiungendo un nuovo alimento
            for i, food in enumerate(remaining_foods):
                # Aggiungi il nuovo alimento, ma solo se non supera le calorie
                new_calories = current_calories + food.CaloricValue
                if new_calories <= tdee:
                    new_fabbisogno = {key: current_fabbisogno[key] - float(getattr(food, key, 0)) for key in requirements}
                    helper(current_list + [food], remaining_foods[i + 1:], new_fabbisogno, new_calories)

        # Avvio della ricorsione
        helper([], food_list, requirements, 0)
        print(list(food for food in best_list))
        return best_list

    def generate_lists_recursive(self, tdee: float, userdata: dict, preferences: dict, max_items: int = 20) -> list[
        Food]:
        """
        Genera una lista ottimizzata di cibi usando un approccio ricorsivo.
        :param tdee: Calorie totali giornaliere (kcal).
        :param userdata: Dizionario di dati dell'utente.
        :param preferences: Preferenze degli utenti riguardo la dieta.
        :param max_items: Numero massimo di prodotti nella lista.
        :return: Lista ottimizzata di oggetti Food.
        """
        food_list = self.get_filtered_food(preferences)
        requirements = self.calculate_nutrients_requirement(tdee, userdata)
        tolerance = 100.0  # Tolleranza sul TDEE in kcal

        best_list = []
        best_diff = float('inf')

        def _recursion(current_list, remaining_foods, current_fabbisogno, current_calories):
            nonlocal best_list, best_diff
            print(len(current_list))
            print(current_calories)


            # Condizione di uscita: il numero massimo di elementi è stato raggiunto
            if len(current_list) == max_items:
                # Controlla se le calorie sono entro il margine di tolleranza
                if abs(float(current_calories) - tdee) > tolerance:
                    return

                # Calcola la differenza totale rispetto ai fabbisogni
                diff = sum(
                    abs(current_fabbisogno[key] - sum(float(getattr(food, key, 0)) for food in current_list))
                    for key in requirements
                )
                print(diff)

                # Aggiorna la migliore soluzione trovata
                if diff < best_diff:
                    best_diff = diff
                    best_list = list(current_list)
                return

            # Esplora le combinazioni aggiungendo un nuovo alimento
            for i, food in enumerate(remaining_foods):
                # Controlla se il cibo supera lo spazio calorico rimanente
                if current_calories + food.CaloricValue > tdee + tolerance:
                    continue  # Salta questo alimento
                if food in current_list:
                    continue

                # Aggiorna i fabbisogni correnti sottraendo i valori del cibo scelto
                new_fabbisogno = {key: current_fabbisogno[key] - float(getattr(food, key, 0)) for key in requirements}

                # Ricorsione con la lista aggiornata
                _recursion(current_list + [food], remaining_foods, new_fabbisogno, current_calories + food.CaloricValue)

        # Avvio della ricorsione
        _recursion([], food_list, requirements, 0)
        return best_list









