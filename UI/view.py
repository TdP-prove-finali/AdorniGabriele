import flet as ft


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        page.title = "Gestione Nutrienti"
        page.window_width = 1200  # Larghezza in pixel
        page.window_height = 800  # Altezza in pixel
        page.window_resizable = True  # Permette il ridimensionamento della finestra
        page.window_maximized = False  # Non avvia in modalità massimizzata
        page.expand = True
        page.scroll = True

        super().__init__()
        # page params
        self._page = page
        self._page.title = "Generatore di lista della spesa ottimizzata."
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT
        # controller (it is not initialized. Must be initialized in the main, after the controller is created)
        self._controller = None

    # graphical elements
        self._title = None

    # UI elements

        # --> user input
        self._weight_input = None
        self._height_input = None
        self._age_input = None
        self._gender_input = None
        self._activity_input = None
        # --> buttons
        self._tdee_btn = None
        self._plus100_btn = None
        self._minus100_btn = None
        self._generate_btn = None
        self._refresh_btn = None
        # --> GRAPH
        self._nutrient_chart = None

        # --> personalization section
        self.personalization_container = None
        self._confirm_changes_btn = None
        self.personalization_section = ft.Column(controls=[], spacing=10)
        self.personalization_controls = {}

        # --> micronutrient section
        self.nutrient_list_container = None
        self.micronutrient_info_container = None
        self.micronutrient_dropdown = None
        self.nutrient_fact_text = None


    def load_interface(self):
        # title
        self._title = ft.Text("GROCERY SHOPPING LIST GENERATOR", color="orange", size=24)
        self._page.controls.append(self._title)
        self._page.controls.append(ft.Row(
            [ft.Text("Benvenuto nel tuo assistente alimentare, "
                     "inserisci le informazioni richieste se vuoi ottenere dei suggerimenti\n "
                     "per un piano alimentare bilanciato!")]))

    # ROW 1
        self._weight_input = ft.TextField(label="Peso (kg)", width=200)
        self._height_input = ft.TextField(label="Altezza (cm)", width=200)

        self._page.controls.append(ft.Row(
            [ft.Text("Inserisci il tuo peso e la tua altezza:")]))
        row1 = ft.Row([self._weight_input, self._height_input],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row1)

    # ROW 2
        self._age_input = ft.Dropdown(label="Età",
                                      options=[ft.dropdown.Option(str(age)) for age in range(18,81)],
                                      on_change=self._controller.handle_dd_age,
                                      width=100)
        self._gender_input = ft.Dropdown(label="Genere",
                                         options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female")],
                                         width=200,
                                         on_change=self._controller.handle_dd_gender)

        self._page.controls.append(ft.Row(
            [ft.Text("Inserisci la tua età e il tuo genere biologico:")]))
        row2 = ft.Row([self._age_input, self._gender_input],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row2)

    # ROW 3
        self._activity_input = ft.Dropdown(label="Livello di attività",
                                           options=[ft.dropdown.Option("sedentary"),
                                                    ft.dropdown.Option("light"),
                                                    ft.dropdown.Option("moderate"),
                                                    ft.dropdown.Option("active"),
                                                    ft.dropdown.Option("very_active")],
                                           width=200,
                                           on_change=self._controller.handle_dd_activity)
        self._page.controls.append(ft.Row([ft.Text("Compila con le informazioni sul tuo stile di vita e il tuo "
                                                   "obiettivo in termini di peso:")]))
        row3 = ft.Row([self._activity_input],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row3)

    # ROW 4
        self._tdee_btn = ft.ElevatedButton(text="CALCULATE TDEE",
                                           on_click=self._controller.calculate_caloric_needs,
                                           color='white', bgcolor='orange')

        row4 = ft.Row([self._tdee_btn], alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row4)

        self.txt_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self._plus100_btn = ft.ElevatedButton(text="+ 100 kcal",
                                              width=120,
                                              bgcolor='orange',
                                              color='white',
                                              on_click=self._controller.handle_plus100_btn)
        self._minus100_btn = ft.ElevatedButton(text="- 100 kcal",
                                               width=120,
                                               bgcolor='orange',
                                               color='white',
                                               on_click=self._controller.handle_minus100_btn)

        row4_1 = ft.Row(controls=[self._minus100_btn, self.txt_result, self._plus100_btn],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(ft.Container(content=row4_1, bgcolor="#F0F0F0", border_radius=10))

    # ROW 5 personalizzazione ulteriore per scartare a priori alcune tipologie di cibo incompatibili con l'utente
        self._page.controls.append(ft.Row(
            [ft.Text("Perfavore, compila il form sottostante per una lista della spesa piu compatibile con le tue "
                     "preferenze alimentari...")]))

        # Funzione di callback per gli switch, chiamata da on_change
        def on_toggle_change(e, toggle_name):
            self._controller.handle_toggle_changes(toggle_name, e.control.value)

        categorie = [
            {
                'titolo': "PREFERENZE DIETA",
                'opzioni': [
                    {"nome": "Vegano", "switch": ft.Switch(
                        on_change=lambda e: on_toggle_change(e, "Vegano"))},
                    {"nome": "Vegetariana", "switch": ft.Switch(
                        on_change=lambda e: on_toggle_change(e, "Vegetariano"))},
                ]
            },
            {
                "titolo": "INTOLLERANZE",
                "opzioni": [
                    {"nome": "Lattosio", "switch": ft.Switch(
                        on_change=lambda e: on_toggle_change(e, "Lattosio"))},
                    {"nome": "Glutine", "switch": ft.Switch(
                        on_change=lambda e: on_toggle_change(e, "Glutine"))},
                ]
            },
            {
                "titolo": "ALLERGIE",
                "opzioni": [
                    {"nome": "Arachidi", "switch": ft.Switch(
                        on_change=lambda e: on_toggle_change(e, "Arachidi"))},
                    {"nome": "Frutta secca", "switch": ft.Switch(
                        on_change=lambda e: on_toggle_change(e, "Frutta secca"))},
                ]
            },
            {
                "titolo": "CONDIZIONI MEDICHE",
                "opzioni": [
                    {"nome": "Diabete", "switch": ft.Switch(
                        on_change=lambda e: on_toggle_change(e, "diabete"))},
                    {"nome": "Insufficienza renale", "switch": ft.Switch(
                        on_change=lambda e: on_toggle_change(e, "insufficienza_renale"))},
                ]
            }
        ]

        row5 = ft.Row([
            ft.Column(
                [
                    ft.Text(categoria["titolo"],),
                    *[
                        ft.Row([ft.Text(opzione["nome"]), opzione["switch"]])
                        for opzione in categoria["opzioni"]
                    ]
                ]
            ) for categoria in categorie
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self._page.controls.append(row5)

    # ROW 6
        self._generate_btn = ft.ElevatedButton(text="GENERATE LIST",
                                               on_click=self._controller.handle_generate_lists,
                                               color='white', bgcolor='orange')
        self._refresh_btn = ft.ElevatedButton(text='REFRESH',
                                              color='white',
                                              bgcolor='red',
                                              on_click=self._controller.handle_refresh_btn)
        row6 = ft.Row([self._generate_btn, self._refresh_btn],alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row6)

    # List View where the reply is printed (LISTA OTTIMIZZATA)
        self.txt_result_2 = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self._page.controls.append(ft.Container(content=self.txt_result_2,
                                                bgcolor="#F0F0F0",
                                                border_radius=10,
                                                height=200))

    # GRAPH
        self._page.controls.append(ft.Text("Distribuzione dei Nutrienti nella Lista Generata:"))
        self._nutrient_chart = ft.BarChart(
            bar_groups=[],
            bottom_axis=ft.ChartAxis(labels=[]),
            interactive=True,
            width=1000,
            height=600,
        )
        self._page.controls.append(ft.Container(content=self._nutrient_chart,
                                                bgcolor="#F0F0F0",
                                                border_radius=10,
                                                expand=True))



    # PERSONALIZATION
        self._page.controls.append(ft.Text("Personalizzazione della lista:"))
        self._confirm_changes_btn = ft.ElevatedButton(text="CONFIRM CHANGES", color='white', bgcolor='orange', on_click=self._controller.handle_confirm_changes)

        self.personalization_container = ft.Container(
            content=ft.Column(
                controls=[self.personalization_section, self._confirm_changes_btn],
                spacing=10
            ),
            padding=10,
            bgcolor="#F0F0F0",
            border_radius=10
        )

        self._page.controls.append(self.personalization_container)

    # CARENZE MICRONUTRIENTI
        self._page.controls.append(ft.Text("Informazioni su alcuni Micronutrienti contenuti negli alimenti:"))
        self.micronutrient_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(data="VitaminC", text="Vitamin C"),
                ft.dropdown.Option(data="VitaminD", text="Vitamin D"),
                ft.dropdown.Option(data="Calcium", text="Calcium"),
                ft.dropdown.Option(data="Iron", text="Iron"),
                ft.dropdown.Option(data="Potassium", text="Potassium"),
                ft.dropdown.Option(data="VitaminA", text="Vitamin A"),
                ft.dropdown.Option(data="VitaminB1", text="Vitamin B1"),
                ft.dropdown.Option(data="VitaminB12", text="Vitamin B12"),
                ft.dropdown.Option(data="VitaminB2", text="Vitamin B2"),
                ft.dropdown.Option(data="VitaminB3", text="Vitamin B3"),
                ft.dropdown.Option(data="VitaminB5", text="Vitamin B5"),
                ft.dropdown.Option(data="VitaminB6", text="Vitamin B6"),
                ft.dropdown.Option(data="VitaminE", text="Vitamin E"),
                ft.dropdown.Option(data="VitaminK", text="Vitamin K"),
                ft.dropdown.Option(data="Magnesium", text="Magnesium"),
                ft.dropdown.Option(data="Phosphorus", text="Phosphorus"),
                ft.dropdown.Option(data="Selenium", text="Selenium"),
                ft.dropdown.Option(data="Zinc", text="Zinc")
            ],
            label="Seleziona micronutriente",
            width=200,
            on_change=self._controller.handle_micronutrient_change
        )

        self.nutrient_fact_text = ft.Text(
            value="Nutrient fact: ...",
            size=14,
            color='GRAY'
        )
        # Container 1: Dropdown + nutrient fact
        self.micronutrient_info_container = ft.Container(
            content=ft.Row(
                controls=[self.micronutrient_dropdown, self.nutrient_fact_text],
                spacing=10,
                alignment=ft.MainAxisAlignment.START
            ),
            padding=10,
            bgcolor="#EFEFEF",
            border_radius=10
        )

        # Container 2: ListView per mostrare l'output della query
        self.micronutrient_listview = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        self.micronutrient_list_container = ft.Container(
            content=self.micronutrient_listview,
            padding=10,
            bgcolor="#F0F0F0",
            border_radius=10,
            height=300
        )

        # Aggiungi questi container alla pagina
        self._page.controls.append(self.micronutrient_info_container)
        self._page.controls.append(self.micronutrient_list_container)

        self._page.update()



    # others View's functions

    def create_personalization_section(self, optimization_solution):
        """
        Crea e visualizza la sezione di personalizzazione basata sulla soluzione ottimizzata.
        optimization_solution: lista di tuple (food, quantity)
        """

        self.personalization_section.controls.clear()
        self.personalization_controls.clear()

        for food, qty in optimization_solution:
            food_name_text = ft.Text(value=food.food, width=150)
            minus_btn = ft.IconButton(icon=ft.icons.REMOVE, tooltip="Riduci porzioni")
            qty_text = ft.Text(value=str(qty), width=40, text_align=ft.alignment.center)
            plus_btn = ft.IconButton(icon=ft.icons.ADD, tooltip="Aumenta porzioni")
            similar_dd = ft.Dropdown(options=[], visible=False, width=200)
            switch_btn = ft.ElevatedButton(text="Switch", visible=False)

            row = ft.Row(
                controls=[food_name_text, minus_btn, qty_text, plus_btn, similar_dd, switch_btn],
                alignment=ft.MainAxisAlignment.START,
                spacing=10
            )

            self.personalization_section.controls.append(row)

            self.personalization_controls[food.ID] = {
                "food": food,
                "food_name_text": food_name_text,
                "minus_btn": minus_btn,
                "qty_text": qty_text,
                "plus_btn": plus_btn,
                "similar_dd": similar_dd,
                "switch_btn": switch_btn,
                "current_qty": qty,
                "row": row,
            }
        self.update_page()

    def update_nutrient_chart(self, nutrient_totals: dict, target_nutrients: dict):
        """
        nutrient_totals: dizionario con i totali ottenuti dalla combinazione,
            ad esempio: {"Protein": 85, "Carbohydrates": 245, "Fat": 70, "Fiber": 28}
        target_nutrients: dizionario con i valori target,
            ad esempio: {"Protein": 90, "Carbohydrates": 250, "Fat": 66.67, "Fiber": 30}

        Visualizza sul grafico, per ogni nutriente (escluso "CaloricValue"),
        due barre: una per il valore ottenuto e una per il valore target.
        """

        chart_nutrients = ["Protein", "Carbohydrates", "Fat", "Fiber", "Sodium", "VitaminC", "VitaminD", "Calcium", "Iron", "Potassium"]

        bar_groups = []
        for i, nutrient in enumerate(chart_nutrients):
            if nutrient in ['Sodium', 'Calcium', 'Potassium', 'Iron', 'VitaminC', 'VitaminD']:
                obtained_value = float(nutrient_totals.get(nutrient, 0))/1000
                target_value = float(target_nutrients.get(nutrient, 0))/1000
            else:
                obtained_value = float(nutrient_totals.get(nutrient, 0))
                target_value = float(target_nutrients.get(nutrient, 0))

            obtained_rod = ft.BarChartRod(from_y=0, to_y=obtained_value, color='blue')
            target_rod = ft.BarChartRod(from_y=0, to_y=target_value, color='red')

            group = ft.BarChartGroup(x=i, bar_rods=[obtained_rod, target_rod])
            bar_groups.append(group)

        self._nutrient_chart.bar_groups = bar_groups

        labels = []
        for i, nutrient in enumerate(chart_nutrients):
            labels.append(ft.ChartAxisLabel(value=i, label=ft.Text(nutrient)))
        self._nutrient_chart.bottom_axis = ft.ChartAxis(labels=labels)

        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()
