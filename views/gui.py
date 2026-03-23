import customtkinter as ctk
from tkinter import filedialog, Canvas, Toplevel
from PIL import Image, ImageTk
import logging
from controllers.app_controller import AppController

class AppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Генератор сертификатов Pro")
        self.geometry("800x600")

        # Хранение путей и координат
        self.data_path = ctk.StringVar()
        self.template_path = ctk.StringVar()
        self.font_path = ctk.StringVar()
        self.output_dir = ctk.StringVar()

        # Словарь координат (X, Y) для каждого поля
        self.coords = {
            'ФИО': ctk.Variable(value=(2550, 825)),
            'Программа': ctk.Variable(value=(2550, 1310)),
            'Рег. номер': ctk.Variable(value=(1100, 1800)),
            'Часы': ctk.Variable(value=(2560, 1480))
        }

        self.create_widgets()

    def create_widgets(self):
        # --- Секция файлов ---
        header_files = ctk.CTkLabel(self, text="1. Настройка файлов", font=("Arial", 16, "bold"))
        header_files.pack(pady=(10, 5))

        self._file_row("Таблица Excel:", self.data_path, is_file=True)
        self._file_row("Шаблон JPG:", self.template_path, is_file=True)
        self._file_row("Шрифт:", self.font_path, is_file=True)
        self._file_row("Папка сохранения:", self.output_dir, is_file=False)

        # --- Секция визуальной настройки координат ---
        header_coords = ctk.CTkLabel(self, text="2. Настройка расположения текста", font=("Arial", 16, "bold"))
        header_coords.pack(pady=(20, 5))

        coords_frame = ctk.CTkFrame(self)
        coords_frame.pack(fill="x", padx=20, pady=10)

        for label_text in self.coords.keys():
            row = ctk.CTkFrame(coords_frame)
            row.pack(fill="x", padx=5, pady=2)

            ctk.CTkLabel(row, text=label_text, width=150, anchor="w").pack(side="left", padx=10)

            # Поле для отображения текущих координат
            coord_label = ctk.CTkLabel(row, textvariable=self.coords[label_text], width=120)
            coord_label.pack(side="left", padx=10)

            # Кнопка "Прицелиться"
            btn = ctk.CTkButton(row, text="🎯 Прицелиться", width=100,
                                command=lambda l=label_text: self.pick_coordinate(l))
            btn.pack(side="right", padx=10)

        # --- Кнопка запуска ---
        self.btn_run = ctk.CTkButton(self, text="СГЕНЕРИРОВАТЬ ВСЁ", height=50,
                                     fg_color="green", hover_color="darkgreen",
                                     command=self.start_generation)
        self.btn_run.pack(pady=30)

        self.status = ctk.CTkLabel(self, text="Готов к работе")
        self.status.pack()

    def _file_row(self, label, var, is_file):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(frame, text=label, width=150, anchor="w").pack(side="left", padx=10)
        ctk.CTkEntry(frame, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)
        cmd = lambda: var.set(filedialog.askopenfilename() if is_file else filedialog.askdirectory())
        ctk.CTkButton(frame, text="Обзор", width=60, command=cmd).pack(side="right", padx=5)

    def pick_coordinate(self, field_name):
        if not self.template_path.get():
            self.status.configure(text="Сначала выберите шаблон!", text_color="red")
            return

        # Создаем окно выбора
        picker = Toplevel(self)
        picker.title(f"Выберите место для: {field_name}")

        img = Image.open(self.template_path.get())
        orig_w, orig_h = img.size

        # Масштабируем картинку под экран (макс ширина 1200)
        screen_w = 1200
        ratio = screen_w / orig_w
        screen_h = int(orig_h * ratio)
        img_resized = img.resize((screen_w, screen_h))
        tk_img = ImageTk.PhotoImage(img_resized)

        canvas = Canvas(picker, width=screen_w, height=screen_h, cursor="crosshair")
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=tk_img)
        canvas.image = tk_img

        # Линии перекрестия для удобства
        def on_mouse_move(event):
            canvas.delete("temp_line")
            canvas.create_line(event.x, 0, event.x, screen_h, fill="red", tags="temp_line")
            canvas.create_line(0, event.y, screen_w, event.y, fill="red", tags="temp_line")

        def on_click(event):
            real_x = int(event.x / ratio)
            real_y = int(event.y / ratio)
            self.coords[field_name].set((real_x, real_y))
            picker.destroy()
            self.status.configure(text=f"Обновлено: {field_name}", text_color="green")

        canvas.bind("<Motion>", on_mouse_move)
        canvas.bind("<Button-1>", on_click)

    def start_generation(self):
        # 1. Проверка заполнения путей
        paths = [self.data_path.get(), self.template_path.get(),
                 self.font_path.get(), self.output_dir.get()]
        if not all(paths):
            self.status.configure(text="Заполните все пути!", text_color="red")
            return

        self.status.configure(text="Запуск генерации...", text_color="orange")
        self.update()

        # 2. Собираем координаты из интерфейса
        current_coords = {label: var.get() for label, var in self.coords.items()}

        # 3. Создаем контроллер и запускаем
        ctrl = AppController(
            data_path=self.data_path.get(),
            template_path=self.template_path.get(),
            font_path=self.font_path.get(),
            output_dir=self.output_dir.get(),
            coords_mapping=current_coords
        )

        ok, msg = ctrl.generate_all()
        self.status.configure(text=msg, text_color="green" if ok else "red")