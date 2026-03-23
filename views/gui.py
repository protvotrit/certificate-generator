import customtkinter as ctk
from tkinter import filedialog
from controllers.app_controller import AppController


class AppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Генератор сертификатов")
        self.geometry("500x400")

        self.data_path = ctk.StringVar()
        self.template_path = ctk.StringVar()
        self.font_path = ctk.StringVar()
        self.output_dir = ctk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        self._add_file_selector("Таблица Excel (.xlsx):", self.data_path, 0)
        self._add_file_selector("Шаблон (.jpg):", self.template_path, 1)
        self._add_file_selector("Шрифт (.otf/.ttf):", self.font_path, 2)
        self._add_dir_selector("Папка сохранения:", self.output_dir, 3)

        self.btn_generate = ctk.CTkButton(self, text="Сгенерировать", command=self.start_generation)
        self.btn_generate.grid(row=4, column=0, columnspan=3, pady=20)

        self.status_label = ctk.CTkLabel(self, text="Ожидание...")
        self.status_label.grid(row=5, column=0, columnspan=3)

    def _add_file_selector(self, label_text, string_var, row):
        ctk.CTkLabel(self, text=label_text).grid(row=row, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=string_var, width=200).grid(row=row, column=1, padx=10)
        ctk.CTkButton(self, text="Обзор", command=lambda: string_var.set(filedialog.askopenfilename())).grid(row=row,
                                                                                                             column=2,
                                                                                                             padx=10)

    def _add_dir_selector(self, label_text, string_var, row):
        ctk.CTkLabel(self, text=label_text).grid(row=row, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(self, textvariable=string_var, width=200).grid(row=row, column=1, padx=10)
        ctk.CTkButton(self, text="Обзор", command=lambda: string_var.set(filedialog.askdirectory())).grid(row=row,
                                                                                                          column=2,
                                                                                                          padx=10)

    def start_generation(self):
        # Проверка, что все пути указаны
        if not all([self.data_path.get(), self.template_path.get(), self.font_path.get(), self.output_dir.get()]):
            self.status_label.configure(text="Ошибка: Заполните все пути!", text_color="red")
            return

        self.status_label.configure(text="Генерация...", text_color="orange")
        self.update()  # Обновляем интерфейс

        controller = AppController(
            self.data_path.get(),
            self.template_path.get(),
            self.font_path.get(),
            self.output_dir.get()
        )

        success, message = controller.generate_all()

        color = "green" if success else "red"
        self.status_label.configure(text=message, text_color=color)