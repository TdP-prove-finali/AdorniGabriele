import flet as ft


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
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
        self._goal_input = None
        # --> buttons
        self._tdee_btn = None

    def load_interface(self):
        # title
        self._title = ft.Text("GROCERY SHOPPING LIST GENERATOR", color="orange", size=24)
        self._page.controls.append(self._title)
        self._page.controls.append(ft.Row(
            [ft.Text("Benvenuto nel tuo assistente alimentare, inserisci le informazioni richieste se vuoi ottenere dei suggerimenti\n per un piano alimentare bilanciato!")]))

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
        self._goal_input = ft.Dropdown(label="Obiettivo", options=[ft.dropdown.Option("Perdita di peso"),
                                                                   ft.dropdown.Option("Mantenimento"),
                                                                   ft.dropdown.Option("Incremento di peso")],
                                       width=200,
                                       on_change=self._controller.handle_dd_goal)
        self._page.controls.append(ft.Row([ft.Text("Compila con le informazioni sul tuo stile di vita e il tuo obiettivo in termini di peso:")]))
        row3 = ft.Row([self._activity_input, self._goal_input],
                      alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row3)

        # ROW 4
        self._tdee_btn = ft.ElevatedButton(text="CALCULATE TDEE",
                                           on_click=self._controller.calculate_caloric_needs,
                                           color='white', bgcolor='orange')

        row4 = ft.Row([self._tdee_btn], alignment=ft.MainAxisAlignment.CENTER)
        self._page.controls.append(row4)


        # List View where the reply is printed
        self.txt_result = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        self._page.controls.append(self.txt_result)
        self._page.update()


    # others View's functions
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
