class Model:

    def __init__(self):
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

        return bmr * activity_multipliers.get(activity_level)

    # Metodo per personalizzare il TDEE in base all'obiettivo dell'utente (es. perdita di peso, mantenimento, aumento di massa)

    def adjust_for_goal(self, tdee, goal):
        if goal == 'weight_loss':
            return tdee - 500  # Riduzione calorica per perdere peso
        elif goal == 'weight_gain':
            return tdee + 500  # Aumento calorico per aumentare massa
        else:
            return tdee  # Mantenimento


    # prende dal DAO tutto il cibo
    def get_all_food(self):
        pass

    # prende dal DAO il cibo filtrato in base alle preferenze (toggle)
    def filter_food(self, list_of_preferences):
        pass


    # calcola il fabbisogno di macronutrienti in base a input utente
    def calculate_macronutrients(self):


        pass

    # calcola il fabbisogno di micronutrienti in base a input utente e tenendo conto delle RDA (Recommended Daily Allowance)
    def calculate_micronutrients(self):
        pass








