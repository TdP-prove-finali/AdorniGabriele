import flet as ft

# Costanti per la palette di colori
PRIMARY_COLOR = "orange"
SECONDARY_COLOR = "red"
BACKGROUND_COLOR = "#F0F0F0"
CONTAINER_BG = "#EFEFEF"
TEXT_COLOR = "white"
TITLE_COLOR = "orange"

class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        # Configurazione della finestra
        page.title = "Generatore di lista della spesa ottimizzata."
        page.window_width = 1200  # Larghezza in pixel
        page.window_height = 800  # Altezza in pixel
        page.window_resizable = True  # Permette il ridimensionamento della finestra
        page.window_maximized = False  # Non avvia in modalità massimizzata
        page.expand = True
        page.scroll = True

        super().__init__()
        self._page = page
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT

        # Controller (da impostare successivamente)
        self._controller = None

        # UI Elements
        self._title = None

        # User input elements
        self._weight_input = None
        self._height_input = None
        self._age_input = None
        self._gender_input = None
        self._activity_input = None

        # Buttons
        self._tdee_btn = None
        self._plus100_btn = None
        self._minus100_btn = None
        self._generate_btn = None
        self._refresh_btn = None

        # Graph
        self._nutrient_chart = None

        # Personalization section
        self.personalization_container = None
        self._confirm_changes_btn = None
        self.personalization_section = ft.Column(controls=[], spacing=10)
        self.personalization_controls = {}

        # Micronutrient section
        self.nutrient_list_container = None
        self.micronutrient_info_container = None
        self.micronutrient_dropdown = None
        self.nutrient_fact_text = None

    def load_interface(self):
        """Costruisce l'interfaccia utente."""
        # Title
        self._title = ft.Text("GROCERY SHOPPING LIST GENERATOR", color=TITLE_COLOR, size=24, weight="bold")
        self._page.controls.append(ft.Container(content=self._title, padding=10))
        self._page.controls.append(ft.Container(
            content=ft.Text(
                "Benvenuto nel tuo assistente alimentare. Inserisci le informazioni richieste per ottenere dei suggerimenti per un piano alimentare bilanciato!",
                size=16
            ),
            padding=10
        ))
        # Costruzione delle righe in metodi separati per maggiore chiarezza
        self._build_row_input_weight_height()
        self._build_row_input_age_gender()
        self._build_row_activity()
        self._build_row_tdee_buttons()
        self._build_row_preferences()
        self._build_row_generate_refresh()
        self._build_listview_result()
        self._build_nutrient_chart()
        self._build_personalization_section_ui()
        self._build_micronutrient_section()
        self._page.update()

    def _build_row_input_weight_height(self):
        """Crea la riga per l'inserimento di peso e altezza."""
        self._weight_input = ft.TextField(label="Peso (kg)", width=200)
        self._height_input = ft.TextField(label="Altezza (cm)", width=200)
        row = ft.Row(
            controls=[self._weight_input, self._height_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
        container = ft.Container(content=row, padding=10)
        self._page.controls.append(ft.Text("Inserisci il tuo peso e la tua altezza:"))
        self._page.controls.append(container)

    def _build_row_input_age_gender(self):
        """Crea la riga per l'inserimento di età e genere."""
        self._age_input = ft.Dropdown(
            label="Età",
            options=[ft.dropdown.Option(str(age)) for age in range(18, 81)],
            on_change=self._controller.handle_dd_age,
            width=100
        )
        self._gender_input = ft.Dropdown(
            label="Genere",
            options=[ft.dropdown.Option("Male"), ft.dropdown.Option("Female")],
            on_change=self._controller.handle_dd_gender,
            width=200
        )
        row = ft.Row(
            controls=[self._age_input, self._gender_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
        container = ft.Container(content=row, padding=10)
        self._page.controls.append(ft.Text("Inserisci la tua età e il tuo genere:"))
        self._page.controls.append(container)

    def _build_row_activity(self):
        """Crea la riga per la selezione del livello di attività."""
        self._activity_input = ft.Dropdown(
            label="Livello di attività",
            options=[
                ft.dropdown.Option("sedentary"),
                ft.dropdown.Option("light"),
                ft.dropdown.Option("moderate"),
                ft.dropdown.Option("active"),
                ft.dropdown.Option("very_active")
            ],
            on_change=self._controller.handle_dd_activity,
            width=200
        )
        row = ft.Row(
            controls=[self._activity_input],
            alignment=ft.MainAxisAlignment.CENTER
        )
        container = ft.Container(content=row, padding=10)
        self._page.controls.append(ft.Text("Inserisci le informazioni sul tuo stile di vita:"))
        self._page.controls.append(container)

    def _build_row_tdee_buttons(self):
        """Crea la riga dei pulsanti per il calcolo e la personalizzazione del TDEE."""
        self._tdee_btn = ft.ElevatedButton(
            text="CALCULATE TDEE",
            on_click=self._controller.calculate_caloric_needs,
            color="white",
            bgcolor=PRIMARY_COLOR
        )
        row_btn = ft.Row(controls=[self._tdee_btn], alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(ft.Container(content=row_btn, padding=10))

        self.txt_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self._plus100_btn = ft.ElevatedButton(
            text="+ 100 kcal",
            width=120,
            bgcolor=PRIMARY_COLOR,
            color="white",
            on_click=self._controller.handle_plus100_btn
        )
        self._minus100_btn = ft.ElevatedButton(
            text="- 100 kcal",
            width=120,
            bgcolor=PRIMARY_COLOR,
            color="white",
            on_click=self._controller.handle_minus100_btn
        )
        row_text = ft.Row(
            controls=[self._minus100_btn, self.txt_result, self._plus100_btn],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER
        )
        container = ft.Container(
            content=row_text,
            bgcolor=BACKGROUND_COLOR,
            border_radius=10,
            padding=10
        )
        self._page.controls.append(ft.Container(content=ft.Text(
            "Personalizza il tuo apporto calorico giornaliero incrementando o decrementando di 100 kcal il tuo TDEE."
        ), padding=10))
        self._page.controls.append(container)

    def _build_row_preferences(self):
        """Crea la riga per il filtraggio dei cibi in base alle preferenze alimentari."""
        self._page.controls.append(ft.Container(
            content=ft.Text("Compila il form sottostante per ottenere una lista della spesa più compatibile con le tue preferenze alimentari:"),
            padding=10
        ))

        def on_toggle_change(e, toggle_name):
            self._controller.handle_toggle_changes(toggle_name, e.control.value)

        categorie = [
            {
                'titolo': "PREFERENZE DIETA",
                'opzioni': [
                    {"nome": "Vegano", "switch": ft.Switch(on_change=lambda e: on_toggle_change(e, "Vegano"))},
                    {"nome": "Vegetariana", "switch": ft.Switch(on_change=lambda e: on_toggle_change(e, "Vegetariano"))},
                ]
            },
            {
                "titolo": "INTOLLERANZE",
                "opzioni": [
                    {"nome": "Lattosio", "switch": ft.Switch(on_change=lambda e: on_toggle_change(e, "Lattosio"))},
                    {"nome": "Glutine", "switch": ft.Switch(on_change=lambda e: on_toggle_change(e, "Glutine"))},
                ]
            },
            {
                "titolo": "ALLERGIE",
                "opzioni": [
                    {"nome": "Arachidi", "switch": ft.Switch(on_change=lambda e: on_toggle_change(e, "Arachidi"))},
                    {"nome": "Frutta secca", "switch": ft.Switch(on_change=lambda e: on_toggle_change(e, "`frutta secca`"))},
                ]
            }
        ]
        cols = []
        for categoria in categorie:
            col = ft.Column(
                controls=[
                    ft.Text(categoria["titolo"], weight="bold")
                ] + [ft.Row(controls=[ft.Text(opzione["nome"]), opzione["switch"]], spacing=5)
                     for opzione in categoria["opzioni"]],
                spacing=5,
                alignment=ft.MainAxisAlignment.START
            )
            cols.append(col)
        row = ft.Row(
            controls=cols,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=20
        )
        self._page.controls.append(ft.Container(content=row, padding=10))

    def _build_row_generate_refresh(self):
        """Crea la riga dei pulsanti per generare e aggiornare la lista ottimizzata."""
        self._generate_btn = ft.ElevatedButton(
            text="GENERATE LIST",
            on_click=self._controller.handle_generate_lists,
            color="white",
            bgcolor=PRIMARY_COLOR
        )
        self._refresh_btn = ft.ElevatedButton(
            text="REFRESH",
            color="white",
            bgcolor=SECONDARY_COLOR,
            on_click=self._controller.handle_refresh_btn,
            disabled=True
        )
        row = ft.Row(
            controls=[self._generate_btn, self._refresh_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
        self._page.controls.append(ft.Container(content=row, padding=10))

    def _build_listview_result(self):
        """Crea la ListView dove viene visualizzata la lista ottimizzata."""
        self.txt_result_2 = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        container = ft.Container(
            content=self.txt_result_2,
            bgcolor=BACKGROUND_COLOR,
            border_radius=10,
            height=500,
            padding=10
        )
        self._page.controls.append(container)

    def _build_nutrient_chart(self):
        """Crea il grafico per la visualizzazione della distribuzione dei nutrienti."""
        self._page.controls.append(ft.Container(
            content=ft.Text("Distribuzione dei Nutrienti nella Lista Generata:"),
            padding=10
        ))
        self._nutrient_chart = ft.BarChart(
            bar_groups=[],
            bottom_axis=ft.ChartAxis(labels=[]),
            interactive=True,
            width=1000,
            height=800,
        )
        container = ft.Container(
            content=self._nutrient_chart,
            bgcolor=BACKGROUND_COLOR,
            border_radius=10,
            expand=True,
            padding=10,
            clip_behavior=ft.ClipBehavior.NONE
        )
        self._page.controls.append(container)

    def _build_personalization_section_ui(self):
        """Costruisce l'interfaccia per la personalizzazione della lista."""
        self._page.controls.append(ft.Container(
            content=ft.Text("Personalizzazione della lista:"),
            padding=10
        ))
        self._confirm_changes_btn = ft.ElevatedButton(
            text="CONFIRM CHANGES",
            color="white",
            bgcolor=PRIMARY_COLOR,
            on_click=self._controller.handle_confirm_changes
        )
        self.personalization_container = ft.Container(
            content=ft.Column(
                controls=[self.personalization_section, self._confirm_changes_btn],
                spacing=10
            ),
            padding=10,
            bgcolor=BACKGROUND_COLOR,
            border_radius=10
        )
        self._page.controls.append(self.personalization_container)

    def _build_micronutrient_section(self):
        """Costruisce la sezione dedicata ai micronutrienti."""
        self._page.controls.append(ft.Container(
            content=ft.Text("Informazioni su alcuni Micronutrienti contenuti negli alimenti:"),
            padding=10
        ))
        self.micronutrient_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(data="VitaminC", text="Vitamin C (mg)"),
                ft.dropdown.Option(data="VitaminD", text="Vitamin D (µg)"),
                ft.dropdown.Option(data="Calcium", text="Calcium (mg)"),
                ft.dropdown.Option(data="Iron", text="Iron (mg)"),
                ft.dropdown.Option(data="Potassium", text="Potassium (mg)"),
                ft.dropdown.Option(data="VitaminA", text="Vitamin A (mg)"),
                ft.dropdown.Option(data="VitaminB1", text="Vitamin B1 (mg)"),
                ft.dropdown.Option(data="VitaminB12", text="Vitamin B12 (mg)"),
                ft.dropdown.Option(data="VitaminB2", text="Vitamin B2 (mg)"),
                ft.dropdown.Option(data="VitaminB3", text="Vitamin B3 (mg)"),
                ft.dropdown.Option(data="VitaminB5", text="Vitamin B5 (mg)"),
                ft.dropdown.Option(data="VitaminB6", text="Vitamin B6 (mg)"),
                ft.dropdown.Option(data="VitaminE", text="Vitamin E (mg)"),
                ft.dropdown.Option(data="VitaminK", text="Vitamin K (mg)"),
                ft.dropdown.Option(data="Magnesium", text="Magnesium (mg)"),
                ft.dropdown.Option(data="Phosphorus", text="Phosphorus (mg)"),
                ft.dropdown.Option(data="Selenium", text="Selenium (mg)"),
                ft.dropdown.Option(data="Zinc", text="Zinc (mg)")
            ],
            label="Seleziona micronutriente",
            width=200,
            on_change=self._controller.handle_micronutrient_change
        )
        self.nutrient_fact_text = ft.Text(
            value="Nutrient fact: ...",
            size=14,
            color="gray"
        )
        self.micronutrient_info_container = ft.Container(
            content=ft.Row(
                controls=[self.micronutrient_dropdown, self.nutrient_fact_text],
                spacing=10,
                alignment=ft.MainAxisAlignment.START
            ),
            padding=10,
            bgcolor=CONTAINER_BG,
            border_radius=10
        )
        self.micronutrient_listview = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        self.micronutrient_list_container = ft.Container(
            content=self.micronutrient_listview,
            padding=10,
            bgcolor=BACKGROUND_COLOR,
            border_radius=10,
            height=300
        )
        self._page.controls.append(self.micronutrient_info_container)
        self._page.controls.append(self.micronutrient_list_container)

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
            # Assegna i callback per i pulsanti direttamente qui per garantire il corretto funzionamento
            minus_btn.on_click = lambda e, fid=food.ID: self._controller.handle_minus(fid, e)
            plus_btn.on_click = lambda e, fid=food.ID: self._controller.handle_plus(fid, e)
            switch_btn.on_click = lambda e, fid=food.ID: self._controller.handle_switch(fid, e)
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
        Visualizza sul grafico, per ciascun nutriente, due barre: una per il valore ottenuto e una per il target.
        """
        chart_nutrients = ["Protein", "Carbohydrates", "Fat", "Fiber", "Sodium", "VitaminC", "VitaminD", "Calcium",
                           "Iron", "Potassium"]
        bar_groups = []
        for i, nutrient in enumerate(chart_nutrients):
            if nutrient in ['Sodium', 'Calcium', 'Potassium', 'Iron', 'VitaminC', 'VitaminD']:
                obtained_value = float(nutrient_totals.get(nutrient, 0)) / 1000
                target_value = float(target_nutrients.get(nutrient, 0)) / 1000
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

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

