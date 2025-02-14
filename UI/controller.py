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

    def handle_toggle_changes(self, toggle_name, new_value):
        self._switches_state[toggle_name] = new_value

    def get_toggle_state(self, toggle_name):
        return self._switches_state.get(toggle_name, False)

    def calculate_caloric_needs(self, e):
        user_data = self.get_user_input()
        bmr = self._model.calculate_bmr(
            weight=user_data['weight'],
            height=user_data['height'],
            age=user_data['age'],
            gender=user_data['gender']
        )

        tdee = self._model.calculate_tdee(bmr, user_data['activity_level'])
        self._tdee = tdee
        self._view.txt_result.controls.append(
            ft.Text(f"Calcolato il tdee (total daily energy expenditure): {tdee} kCal"))

        self._view.update_page()
        pass

    def handle_generate_lists(self, e):
        """
        Alla pressione del bottone, genera una lista della spesa ottimizzata utilizzando il modello MILP.
        I target nutrizionali sono calcolati a partire dal TDEE e dai dati utente, tenendo conto delle preferenze (toggles).
        Vengono mostrati sia i dettagli della soluzione (lista e obiettivo) sia un grafico interattivo che riassume i nutrienti totali.
        """
        preferences = self._switches_state
        userdata = self._userData
        tdee = self._tdee

        best_solution, best_objective = self._model.milp_optimization(tdee, userdata, preferences)

        self._view.txt_result_2.controls.clear()
        self._view.txt_result_2.controls.append(ft.Text(f"Optimal objective: {best_objective}"))
        self._view.txt_result_2.controls.append(ft.Text("Best solution:"))
        for food, qty in best_solution:
            self._view.txt_result_2.controls.append(ft.Text(f" - {food.food}: {qty} porzioni"))

        nutrient_keys = ["CaloricValue", "Protein", "Carbohydrates", "Fat", "Fiber", "Sodium", "VitaminC", "VitaminD", "Calcium", "Iron", "Potassium"]
        nutrient_totals = self._model.get_total_nutrients(best_solution, nutrient_keys)
        nutrient_target = self._model.calculate_nutrients_requirement(tdee, userdata)
        # Aggiornamento il grafico dei nutrienti nella view.
        self._view.update_nutrient_chart(nutrient_totals, nutrient_target)
        # Crea\ione della sezione di personalizzazione nella View, passando la soluzione ottenuta
        self._view.create_personalization_section(best_solution)
        self.setup_personalization_handlers()

        self._view.update_page()

    def setup_personalization_handlers(self):
        """
        Associa, per ciascuna riga della sezione di personalizzazione, i gestori degli eventi
        per i bottoni "MENO", "PIÙ" e "SWITCH". Si basa sul dizionario self._view.personalization_controls.
        """
        for food_id, controls in self._view.personalization_controls.items():
            # lambda per passare il food_id come argomento fisso alla callback
            controls["minus_btn"].on_click = lambda e, fid=food_id: self.handle_minus(fid, e)
            controls["plus_btn"].on_click = lambda e, fid=food_id: self.handle_plus(fid, e)
            controls["switch_btn"].on_click = lambda e, fid=food_id: self.handle_switch(fid, e)

    def handle_minus(self, food_id, e):
        """
        Quando l'utente preme il bottone "MENO", non si decrementa direttamente la quantità
        perché il numero totale di porzioni deve rimanere costante.

        - Se sono disponibili prodotti simili, attiva la modalità di sostituzione:
            * Popola il dropdown con le opzioni (convertendo gli oggetti Food in ft.dropdown.Option)
            * Rende visibili il dropdown e il bottone SWITCH.
        - Se non sono disponibili prodotti simili, mostra un alert e non esegue il decremento.
        """
        controls = self._view.personalization_controls.get(food_id)
        if controls is None:
            return
        similar_options = self._model.get_similar_products(controls["food"])
        if not similar_options:
            self._view.create_alert(
                "Non è possibile diminuire l'alimento perché non sono disponibili prodotti simili per la sostituzione.")
            return
        else:
            controls["similar_dd"].options = [
                ft.dropdown.Option(data=prod, text=prod.food)
                for prod in similar_options
            ]
            controls["similar_dd"].visible = True
            controls["switch_btn"].visible = True

        self._view.update_page()

    def handle_plus(self, food_id, e):
        """
        Aumenta di una porzione l'alimento corrispondente.
        Nasconde eventuali controlli per la sostituzione se erano visibili.
        """
        controls = self._view.personalization_controls.get(food_id)
        if controls is None:
            return
        controls["current_qty"] += 1
        controls["qty_text"].value = str(controls["current_qty"])

        controls["similar_dd"].visible = False
        controls["switch_btn"].visible = False
        self._view.update_page()

    def handle_switch(self, food_id, e):
        """
        Quando l'utente preme il bottone SWITCH:
          - Decrementa di una porzione l'alimento corrente.
          - Recupera l'alimento selezionato dal dropdown.
          - Se il nuovo alimento è già presente nella sezione, ne incrementa la quantità di 1.
          - Altrimenti, crea una nuova riga per il nuovo alimento con quantità iniziale pari a 1.
          - Nasconde il dropdown e il bottone SWITCH.
        """
        controls = self._view.personalization_controls.get(food_id)
        if controls is None:
            return

        if controls["similar_dd"].value is None:
            print("Nessun alimento selezionato per la sostituzione.")
            return

        try:
            new_food_id = int(controls["similar_dd"].value)
            new_food = self._model.get_food_by_id(new_food_id)
        except ValueError:
            selected_name = controls["similar_dd"].value.strip().lower()
            similar_products = self._model.get_similar_products(controls["food"])
            new_food = next((prod for prod in similar_products if prod.food.strip().lower() == selected_name), None)
            if new_food is None:
                print("Nessun alimento trovato per il nome:", selected_name)
                return

        if new_food is None:
            print("Alimento selezionato non trovato.")
            return

        if controls["current_qty"] > 0:
            controls["current_qty"] -= 1
            controls["qty_text"].value = str(controls["current_qty"])

        if controls["current_qty"] == 0:
            controls["minus_btn"].visible = False
            controls["plus_btn"].visible = False
            controls["qty_text"].value = "0"

        # Gestione la sostituzione:
        if new_food.ID in self._view.personalization_controls:
            new_controls = self._view.personalization_controls[new_food.ID]
            new_controls["current_qty"] += 1
            new_controls["qty_text"].value = str(new_controls["current_qty"])
        else:
            # Creazione nuovi controlli per il nuovo alimento
            food_name_text = ft.Text(value=new_food.food, width=150)
            minus_btn = ft.IconButton(icon=ft.icons.REMOVE, tooltip="Riduci porzioni")
            qty_text = ft.Text(value="1", width=40, text_align=ft.alignment.center)
            plus_btn = ft.IconButton(icon=ft.icons.ADD, tooltip="Aumenta porzioni")
            similar_dd = ft.Dropdown(options=[], visible=False, width=200)
            switch_btn = ft.ElevatedButton(text="Switch", visible=False)
            new_row = ft.Row(
                controls=[food_name_text, minus_btn, qty_text, plus_btn, similar_dd, switch_btn],
                alignment=ft.MainAxisAlignment.START,
                spacing=10
            )
            self._view.personalization_section.controls.append(new_row)
            new_controls = {
                "food": new_food,
                "food_name_text": food_name_text,
                "minus_btn": minus_btn,
                "qty_text": qty_text,
                "plus_btn": plus_btn,
                "similar_dd": similar_dd,
                "switch_btn": switch_btn,
                "current_qty": 1,
            }
            self._view.personalization_controls[new_food.ID] = new_controls
            # le callback per la nuova riga
            minus_btn.on_click = lambda e, fid=new_food.ID: self.handle_minus(fid, e)
            plus_btn.on_click = lambda e, fid=new_food.ID: self.handle_plus(fid, e)
            switch_btn.on_click = lambda e, fid=new_food.ID: self.handle_switch(fid, e)

        controls["similar_dd"].visible = False
        controls["switch_btn"].visible = False

        self._view.update_page()

    def handle_micronutrient_change(self, e):
        """
        Callback che viene chiamata quando l'utente cambia selezione nel dropdown dei micronutrienti.
        Aggiorna il Text del nutrition fact in base al micronutriente selezionato e, eventualmente,
        aggiorna anche la listview informativa con i cibi ordinati per quel micronutriente.
        """

        selected_nutrient = self._view.micronutrient_dropdown.value
        print(f'nutriente {selected_nutrient} selezionato')
        if not selected_nutrient:
            return

        nutrient_facts = {
            "VitaminC": "La Vitamina C è fondamentale per il sistema immunitario e l'assorbimento del ferro.",
            "VitaminD": "La Vitamina D favorisce l'assorbimento del calcio e supporta la salute delle ossa.",
            "Calcium": "Il Calcio è essenziale per ossa e denti forti.",
            "Iron": "Il Ferro è vitale per il trasporto dell'ossigeno nel sangue.",
            "Potassium": "Il Potassio aiuta a mantenere la pressione sanguigna e la funzione muscolare.",
            "VitaminA": "La Vitamina A è importante per la vista, la crescita e il sistema immunitario.",
            "VitaminB1": "La Vitamina B1 (tiamina) è essenziale per il metabolismo energetico e la funzione nervosa.",
            "VitaminB12": "La Vitamina B12 è cruciale per la formazione dei globuli rossi e la salute del sistema nervoso.",
            "VitaminB2": "La Vitamina B2 (riboflavina) supporta la produzione di energia e la salute della pelle.",
            "VitaminB3": "La Vitamina B3 (niacina) aiuta a mantenere la pelle sana e supporta il sistema nervoso.",
            "VitaminB5": "La Vitamina B5 (acido pantotenico) è importante per il metabolismo e la sintesi degli ormoni.",
            "VitaminB6": "La Vitamina B6 è necessaria per il metabolismo delle proteine e la funzione cerebrale.",
            "VitaminE": "La Vitamina E è un potente antiossidante che protegge le cellule dai danni.",
            "VitaminK": "La Vitamina K è fondamentale per la coagulazione del sangue e la salute ossea.",
            "Magnesium": "Il Magnesio è essenziale per centinaia di reazioni enzimatiche, inclusa la produzione di energia.",
            "Phosphorus": "Il Fosforo è fondamentale per la formazione di ossa e denti e il metabolismo energetico.",
            "Selenium": "Il Selenio agisce come antiossidante e supporta la funzione tiroidea.",
            "Zinc": "Lo Zinco è importante per il sistema immunitario e la guarigione delle ferite."
        }

        fact = nutrient_facts.get(selected_nutrient, "Informazioni sul micronutriente non disponibili.")
        self._view.nutrient_fact_text.value = fact

        sorted_foods = self._model.get_foods_by_micronutrient(selected_nutrient)
        self._view.micronutrient_listview.controls.clear()
        for food, qty in sorted_foods:
            self._view.micronutrient_listview.controls.append(
                ft.Text(f"{food} - {selected_nutrient}: {qty}")
            )

        self._view.update_page()

    def handle_confirm_changes(self, e):
        """
        Salva la lista personalizzata ottenuta dalla sezione di personalizzazione,
        la visualizza nell'area di output e aggiorna il grafico con i totali nutrizionali.
        Il totale delle porzioni resta costante; la soluzione personalizzata sostituisce l'output precedente.
        """
        personalized_solution = []
        for food_id, controls in self._view.personalization_controls.items():
            qty = controls["current_qty"]
            if qty > 0:
                personalized_solution.append((controls["food"], qty))

        # aggiorno l'area di output (txt_result_2) con la nuova lista personalizzata
        self._view.txt_result_2.controls.clear()
        self._view.txt_result_2.controls.append(ft.Text("Personalized list:"))
        for food, qty in personalized_solution:
            self._view.txt_result_2.controls.append(ft.Text(f"{food.food}: {qty} portions"))

        nutrient_keys = ["CaloricValue", "Protein", "Carbohydrates", "Fat", "Fiber", "Sodium", "VitaminC", "VitaminD", "Calcium", "Iron", "Potassium"]  # quelli usati nel grafico
        nutrient_totals = self._model.get_total_nutrients(personalized_solution, nutrient_keys)

        target = self._model.calculate_nutrients_requirement(self._tdee, self._userData)


        # Aggiornamento grafico usando la funzione update_nutrient_chart (che riceve sia i totali ottenuti che i target)
        self._view.update_nutrient_chart(nutrient_totals, target)

        self._view.create_alert("Modifiche confermate e grafico aggiornato.")
        self._view.update_page()

    def handle_plus100_btn(self, e):
        """
        Modifica il TDEE di delta (ad esempio, -100 o +100 kcal),
        aggiorna il display del TDEE e rigenera la soluzione MILP, aggiornando output, sezione personalizzazione e grafico.
        """
        self._tdee += 100
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"TDEE: {self._tdee} kcal"))
        self._view.update_page()
        pass

    def handle_minus100_btn(self, e):
        """
        Modifica il TDEE di delta (ad esempio, -100 o +100 kcal),
        aggiorna il display del TDEE e rigenera la soluzione MILP, aggiornando output, sezione personalizzazione e grafico.
        """
        self._tdee -= 100
        self._view.txt_result.controls.clear()
        self._view.txt_result.controls.append(ft.Text(f"TDEE: {self._tdee} kcal"))
        self._view.update_page()
        pass

    def handle_refresh_btn(self, e):
        """
        Quando l'utente preme il bottone "Refresh", genera una nuova soluzione MILP (diversa dalla precedente)
        e aggiorna l'output, la sezione personalizzazione e il grafico.
        """
        best_solution, best_objective = self._model.milp_optimization(self._tdee, self._userData, self._switches_state)

        self._view.txt_result_2.controls.clear()
        self._view.txt_result_2.controls.append(ft.Text(f"Optimal objective: {best_objective}"))
        self._view.txt_result_2.controls.append(ft.Text("Best solution:"))
        for food, qty in best_solution:
            self._view.txt_result_2.controls.append(ft.Text(f"{food.food}: {qty} porzioni"))

        self._view.create_personalization_section(best_solution)

        nutrient_keys = ["CaloricValue", "Protein", "Carbohydrates", "Fat", "Fiber", "Sodium", "VitaminC", "VitaminD",
                         "Calcium", "Iron", "Potassium"]
        nutrient_totals = self._model.get_total_nutrients(best_solution, nutrient_keys)
        target = self._model.calculate_nutrients_requirement(self._tdee, self._userData)
        self._view.update_nutrient_chart(nutrient_totals, target)

        self._view.update_page()





