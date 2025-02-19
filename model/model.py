import decimal
import random
import pulp
from decimal import Decimal, ROUND_HALF_UP
from database.DAO import DAO
from model.food import Food


class Model:

    def __init__(self):
        self.all_foods_list = None
        pass

    def calculate_bmr(self, weight, height, age, gender):
        """
        Il metodo calculate_bmr calcola il Basal Metabolic Rate (BMR), ovvero il metabolismo basale, utilizzando la
        formula Mifflin-St Jeor. In base al genere, la formula applicata è:
        Per gli uomini:
        BMR = 0 * peso(kg) + 6.25 * altezza(cm) − 5 * eta(anni) + 5
        Per le donne:
        BMR = 10 * peso(kg) + 6.25 * altezza(cm) − 5 * eta(anni) − 161
        Il metodo converte i parametri in float e restituisce il BMR, espresso in kilocalorie al giorno, che rappresenta
        l'energia minima necessaria per mantenere le funzioni vitali a riposo.
        :param weight:
        :param height:
        :param age:
        :param gender:
        :return:
        """
        if gender == 'male':
            # Formula per gli uomini
            bmr = 10 * float(weight) + 6.25 * float(height) - 5 * float(age) + 5
        else:
            # Formula per le donne
            bmr = 10 * float(weight) + 6.25 * float(height) - 5 * float(age) - 161
        return bmr

    # Metodo per calcolare il TDEE (Total Daily Energy Expenditure) in base al livello di attività fisica

    def calculate_tdee(self, bmr, activity_level):
        """
        Il metodo calculate_tdee calcola il Total Daily Energy Expenditure (TDEE), ovvero il fabbisogno energetico
        giornaliero totale, partendo dal BMR (Basal Metabolic Rate) e moltiplicandolo per un coefficiente di attività
        fisica. In sintesi uesta funzione fornisce una stima del consumo calorico giornaliero in base al metabolismo basale e
        all'intensità dell'attività fisica svolta.
        :param bmr: basal metabolic rate calcolato nell'apposito metodo
        :param activity_level: input dell'uitente tramite dropdown, corrispondono alle cinque chiavi del dizionario
        activity_multipliers
        :return: TDEE
        """

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

    def get_all_foods(self):
        self.all_foods_list = DAO.getAllFood()
        return self.all_foods_list

    # prende dal DAO il cibo filtrato in base alle preferenze (toggle)
    def get_filtered_food(self, list_of_preferences):
        lista_temp = DAO.getFoodPers(list_of_preferences)
        self.filtered_food_list = lista_temp
        return lista_temp


    @staticmethod
    def calculate_nutrients_requirement(tdee_input, userdata: dict) -> dict:
        """
        Calcola i fabbisogni nutrizionali a partire dal TDEE (Total Daily Energy Expenditure)
        e dai dati dell'utente, restituendo un dizionario con i nutrienti espressi come Decimal.

        :param tdee_input: Il TDEE (preferibilmente già un Decimal, altrimenti verrà convertito).
        :param userdata: Dizionario contenente i dati dell'utente, ad esempio "weight", "gender" e "age".
        :return: Dizionario dei requisiti nutrizionali.
        """
        tdee = tdee_input if isinstance(tdee_input, Decimal) else Decimal(str(tdee_input))
        weight = Decimal(str(userdata["weight"]))
        gender = userdata["gender"]
        age = int(userdata["age"])

        # arrotondamento a 2 cifre decimali
        # UNITA DI MISURA DEI VALORI:
        # g: Fat, SaturatedFats, Carbohydrates, Protein, Fiber, Sodium(essendo
        # mg: VitaminC, Calcium, Iron, Potassium
        # 'mu'g: VitaminD
        requirements = {
            "CaloricValue": tdee,
            "Fat": (Decimal('0.3') * tdee / Decimal('9')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            "SaturatedFats": (Decimal('0.1') * tdee / Decimal('9')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            "Carbohydrates": (Decimal('0.5') * tdee / Decimal('4')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            "Protein": (weight * (Decimal('0.8') if gender == "Female" else Decimal('1.0'))).quantize(Decimal('0.01'),
                                                                                                      rounding=ROUND_HALF_UP),
            "Fiber": Decimal('25') if gender == "Female" else Decimal('30'),
            "Sodium": Decimal('1500') if age < 50 else Decimal('1300'),
            "VitaminC": Decimal('75') if gender == "Female" else Decimal('90'),
            "VitaminD": Decimal('15'),
            "Calcium": Decimal('1000'),
            "Iron": Decimal('18') if gender == "Female" else Decimal('8'),
            "Potassium": Decimal('3400') if gender == "Male" else Decimal('2600'),
        }
        return requirements

    def milp_optimization(self, tdee: float, userdata: dict, preferences: dict):
        """
        Genera una lista della spesa ottimizzata utilizzando un modello MILP.

        Il modello si concentra su 5 nutrienti fondamentali:
          - CaloricValue, Protein, Carbohydrates, Fat e Fiber

        I target nutrizionali sono ottenuti dalla funzione calculate_nutrients_requirement,
        e vengono pesati in base all'impatto calorico:
          - Protein e Carbohydrates: 4 kcal/g
          - Fat: 9 kcal/g
          - CaloricValue: 1 (già in kcal)
          - Fiber: 0.5
        """
        foods = self.get_filtered_food(preferences)
        random.shuffle(foods)

        target = self.calculate_nutrients_requirement(tdee, userdata)
        nutrient_keys = ["CaloricValue", "Protein", "Carbohydrates", "Fat", "Fiber"]
        target_floats = {k: float(target[k]) for k in nutrient_keys}

        prob = pulp.LpProblem("GroceryOptimization", pulp.LpMinimize)

        # Definizione variabili decisionali per ogni alimento (numero di porzioni, intero)
        food_vars = {}
        for food in foods:
            food_vars[food.ID] = pulp.LpVariable(f"x_{food.ID}", lowBound=0, upBound=5, cat="Integer")

        # Variabili slack per misurare le deviazioni dai target
        d_plus = {}
        d_minus = {}
        for n in nutrient_keys:
            d_plus[n] = pulp.LpVariable(f"d_plus_{n}", lowBound=0, cat="Continuous")
            d_minus[n] = pulp.LpVariable(f"d_minus_{n}", lowBound=0, cat="Continuous")
        nutrient_weights = {
            "CaloricValue": 1.0,
            "Protein": 4.0,
            "Carbohydrates": 4.0,
            "Fat": 9.0,
            "Fiber": 0.5
        }

        # Funzione obiettivo: minimizzo la somma pesata delle deviazioni
        prob += pulp.lpSum([nutrient_weights[n] * (d_plus[n] + d_minus[n]) for n in nutrient_keys])

        # Vincoli per ciascun nutriente: somma_i (valore_i * x_i) + d_minus - d_plus = target
        for n in nutrient_keys:
            prob += (pulp.lpSum([float(getattr(food, n)) * food_vars[food.ID] for food in foods])
                     + d_minus[n] - d_plus[n] == target_floats[n]), f"constraint_{n}"

        # Vincolo sul numero totale di porzioni (ad es. tra 5 e 15)
        prob += pulp.lpSum([food_vars[food.ID] for food in foods]) >= 5, "min_servings"
        prob += pulp.lpSum([food_vars[food.ID] for food in foods]) <= 15, "max_servings"

        # limit e gapRel per accettare una soluzione sub-ottimale in pochi secondi
        prob.solve(pulp.PULP_CBC_CMD(timeLimit=5, gapRel=0.1, msg=True))
        solution = []
        for food in foods:
            qty = food_vars[food.ID].varValue
            if qty and qty > 0:
                solution.append((food, qty))
        objective_value = pulp.value(prob.objective)
        print(f"Optimal objective (sub-optimal accettata): {objective_value}")
        for n in nutrient_keys:
            print(f"{n}: d_plus = {d_plus[n].varValue}, d_minus = {d_minus[n].varValue}")

        return solution, objective_value

    def get_similar_products(self, food):
        """
        Restituisce una lista di alimenti simili a quello passato, basandosi sui valori dei nutrienti.
        Si considerano i nutrienti: Protein, Carbohydrates, Fat e Fiber.

        L'approccio è quello di verificare che la differenza relativa (in percentuale) per ogni nutriente
        sia inferiore a una soglia prestabilita (ad esempio, il 10%).

        Se il valore del nutriente del cibo di riferimento è 0, viene utilizzata una soglia fissa (ad esempio 0.1 unità).
        """
        # Soglia di differenza accettabile (10%)
        threshold = 0.10
        # Lista dei nutrienti da confrontare (escludiamo CaloricValue)
        nutrient_keys = ["Protein", "Carbohydrates", "Fat", "Fiber"]

        # Ottieni la lista completa dei cibi dal database
        food_list = self.get_all_foods()
        similar_food_list = []

        for f in food_list:
            if f.ID == food.ID:
                continue

            is_similar = True
            for nutrient in nutrient_keys:
                value_original = float(getattr(food, nutrient))
                value_candidate = float(getattr(f, nutrient))
                if value_original != 0:
                    relative_diff = abs(value_original - value_candidate) / value_original
                    if relative_diff > threshold:
                        is_similar = False
                        break
                else:
                    if abs(value_candidate) > 0.1:
                        is_similar = False
                        break
            if is_similar:
                similar_food_list.append(f)

        return similar_food_list

    def get_total_nutrients(self, list, nutrient_keys):
        nutrient_totals = {nutrient:0.0 for nutrient in nutrient_keys}
        for food, qty in list:
            for nutrient in nutrient_keys:
                nutrient_totals[nutrient] += float(getattr(food, nutrient)) * qty
        return nutrient_totals

    def get_foods_by_micronutrient(self, nutrient):
        food_list = DAO.getFoodByNutrient(nutrient)
        return food_list

