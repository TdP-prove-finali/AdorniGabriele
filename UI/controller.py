import flet as ft


class Controller:
    def __init__(self, view, model):
        # view
        self._view = view
        # model
        self._model = model
        # dict per memorizzare i dati dell'utente che saranno inseriti in input
        self._userData = {'weight': None,
                          'height': None,
                          'age': None,
                          'gender': None,
                          'activity_level': None,
                          'goal': None}
        self._tdee = None
        # dict per memorizzare le preferenze dell'utente selezionate tramite gli switches
        self._switches_state = {}
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

    def handle_toggle_changes(self, toggle_name, new_value):
        # Salva dinamicamente lo stato dell'interruttore
        self._switches_state[toggle_name] = new_value
        # print(f"{toggle_name}: {'Attivo' if new_value else 'Non attivo'}")

    # Metodo per ottenere lo stato di un toggle specifico
    def get_toggle_state(self, toggle_name):
        return self._switches_state.get(toggle_name, False)

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

        self._tdee = tdee

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

    def handle_display_all_foods(self, e):
        """
        Alla pressione del bottone corrispondente, la funzione mostra la lista di tutti i cibi presenti nel database.
        (opt.: filtraggio lista con ricerche o categorie...)
        :param e:
        :return:
        """
        self._model.get_all_foods()
        pass


    def handle_generate_lists(self, e):
        """
        Alla pressione del bottone corrispondente, la funzione mostra una lista della spesa ottimizzata per soddisfare
        i parametri di valori nutrizionali calcolati precedentemente, tenendo anche conto delle preferenze inserite
        dall'utente (toggles).
        L'algoritmo terra in una cache le migliori n combinazioni cosi da poterne proporre diverse su richiesta dell'utente
        :param e:
        :return:
        """
        # fisso i valori di self._switches_state, self._userData e self._tdee
        preferences = self._switches_state
        userdata = self._userData
        tdee = self._tdee

        lists = self._model.generate_lists_recursive(tdee, userdata, preferences)
        # list_best = lists[0]
        for food in lists:
            self._view.txt_result_2.controls.append(f"{food.food}")

        self._view.update_page()

        pass
