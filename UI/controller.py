import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

        self._userData = {'weight': None,
                          'height': None,
                          'age': None,
                          'gender': None,
                          'activity_level': None,
                          'goal': None}

        pass

    def get_user_input(self):
        try:
            self._userData["weight"] = self._view._weight_input.value
            self._userData["height"] = self._view._height_input.value
        except ValueError:
            self._view.create_alert('Please, insert valid numeric values for weight and height...')
            return None

        return self._userData

    def handle_dd_age(self, e):
        print("Activity level selected:", e.control.value)
        if e.control.value is None:
            self._userData['age'] = None
        else:
            self._userData['age'] = e.control.value

    def handle_dd_gender(self, e):
        if e.control.value is None:
            self._userData['gender'] = None
        else:
            self._userData['gender'] = e.control.value
        pass

    def handle_dd_activity(self, e):
        if e.control.value is None:
            self._userData['activity_level'] = None
        else:
            self._userData['activity_level'] = e.control.value
        pass

    def handle_dd_goal(self, e):
        if e.control.value is None:
            self._userData['goal'] = None
        else:
            self._userData['goal'] = e.control.value
        pass

    def calculate_caloric_needs(self, e):
        # Ottieni i dati dall'utente
        user_data = self.get_user_input()
        print(user_data)

        # Calcola il BMR
        bmr = self._model.calculate_bmr(
            weight=user_data['weight'],
            height=user_data['height'],
            age=user_data['age'],
            gender=user_data['gender']
        )

        # Calcola il TDEE in base al livello di attività fisica
        tdee = self._model.calculate_tdee(bmr, user_data['activity_level'])

        # Personalizzazione in base all'obiettivo e alle preferenze (toggle)
        # if user_data['goal'] == 'weight_loss':
        #     tdee -= user_data['calorie_deficit']
        # elif user_data['goal'] == 'weight_gain':
        #     tdee += user_data['calorie_surplus']

        # Mostra il risultato all'utente
        self._view.txt_result.controls.append(
            ft.Text(f"Calcolato il tdee (total daily energy expenditure): {tdee} kCal"))
        self._view.update_page()
        pass

    def display_all_foods(self, e):
        self._model.get_all_foods()
        pass
