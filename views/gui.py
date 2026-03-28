import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, Canvas, Toplevel
from PIL import Image, ImageTk
import logging
import os
import json

# Импорт контроллера
from controllers.app_controller import AppController


class AppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройки масштабирования интерфейса
        ctk.set_widget_scaling(1.1)
        ctk.set_window_scaling(1.1)

        self.title("Certificate Generator Pro v3.5")
        self.geometry("1100x850")

        # Переменные путей
        self.data_path = ctk.StringVar()
        self.template_path = ctk.StringVar()
        self.font_path = ctk.StringVar()
        self.output_dir = ctk.StringVar()

        # Координаты и размеры шрифтов
        self.coords = {
            'ФИО': ctk.Variable(value=(2550, 825)),
            'Программа': ctk.Variable(value=(2550, 1310)),
            'Рег. номер': ctk.Variable(value=(1100, 1800)),
            'Часы': ctk.Variable(value=(2560, 1480))
        }

        self.font_sizes = {
            'ФИО': ctk.StringVar(value="120"),
            'Программа': ctk.StringVar(value="80"),
            'Рег. номер': ctk.StringVar(value="60"),
            'Часы': ctk.StringVar(value="60")
        }

        self.create_widgets()

        # Загружаем сохраненные настройки, если они есть
        self.load_settings()

    def create_widgets(self):
        # --- 1. СЕКЦИЯ ФАЙЛОВ ---
        ctk.CTkLabel(self, text="1. Настройка ресурсов", font=("Arial", 18, "bold")).pack(pady=10)
        f_frame = ctk.CTkFrame(self)
        f_frame.pack(fill="x", padx=30, pady=5)

        self._file_row(f_frame, "Таблица Excel:", self.data_path, True)
        self._file_row(f_frame, "Шаблон (JPG):", self.template_path, True)
        self._file_row(f_frame, "Шрифт (TTF):", self.font_path, True)
        self._file_row(f_frame, "Папка сохранения:", self.output_dir, False)

        # --- 2. СЕКЦИЯ НАСТРОЕК ТЕКСТА ---
        ctk.CTkLabel(self, text="2. Расположение и размеры", font=("Arial", 18, "bold")).pack(pady=10)

        c_frame = ctk.CTkFrame(self)
        c_frame.pack(fill="both", expand=True, padx=30, pady=5)

        for field in self.coords.keys():
            row = ctk.CTkFrame(c_frame)
            row.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(row, text=field, width=120, anchor="w", font=("Arial", 14, "bold")).pack(side="left", padx=10)

            # Настройка шрифта
            ctk.CTkButton(row, text="-", width=30, command=lambda f=field: self.change_font(f, -5)).pack(side="left")
            ctk.CTkEntry(row, textvariable=self.font_sizes[field], width=50).pack(side="left", padx=5)
            ctk.CTkButton(row, text="+", width=30, command=lambda f=field: self.change_font(f, 5)).pack(side="left")

            # Настройка координат (стрелочки)
            move_frame = ctk.CTkFrame(row, fg_color="transparent")
            move_frame.pack(side="left", padx=20)

            ctk.CTkButton(move_frame, text="←", width=35, command=lambda f=field: self.move_coord(f, -20, 0)).pack(
                side="left", padx=2)
            ctk.CTkButton(move_frame, text="↑", width=35, command=lambda f=field: self.move_coord(f, 0, -20)).pack(
                side="left", padx=2)

            ctk.CTkLabel(move_frame, textvariable=self.coords[field], width=110, fg_color="#333333",
                         corner_radius=5).pack(side="left", padx=5)

            ctk.CTkButton(move_frame, text="↓", width=35, command=lambda f=field: self.move_coord(f, 0, 20)).pack(
                side="left", padx=2)
            ctk.CTkButton(move_frame, text="→", width=35, command=lambda f=field: self.move_coord(f, 20, 0)).pack(
                side="left", padx=2)

            # Кнопка прицела
            ctk.CTkButton(row, text="🎯 Прицел", width=80, command=lambda f=field: self.pick_coordinate(f)).pack(
                side="right", padx=10)

        # --- 3. КНОПКИ ДЕЙСТВИЯ ---
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=20)

        self.btn_preview = ctk.CTkButton(btn_row, text="👁️ ПРЕДПРОСМОТР", width=180, height=45,
                                         fg_color="#E67E22", hover_color="#D35400", command=self.show_preview)
        self.btn_preview.pack(side="left", padx=10)

        self.btn_run = ctk.CTkButton(btn_row, text="🚀 ЗАПУСК ВСЕХ", width=180, height=45,
                                     fg_color="green", hover_color="darkgreen", command=self.start_generation)
        self.btn_run.pack(side="left", padx=10)

        self.btn_save = ctk.CTkButton(btn_row, text="💾 СОХРАНИТЬ", width=180, height=45,
                                      fg_color="#34495E", command=self.save_settings)
        self.btn_save.pack(side="left", padx=10)

        self.status = ctk.CTkLabel(self, text="Система готова", font=("Arial", 13))
        self.status.pack(pady=10)

    def _file_row(self, master, label, var, is_file):
        r = ctk.CTkFrame(master, fg_color="transparent")
        r.pack(fill="x", pady=2)
        ctk.CTkLabel(r, text=label, width=130, anchor="w").pack(side="left")
        ctk.CTkEntry(r, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)

        def b():
            p = filedialog.askopenfilename() if is_file else filedialog.askdirectory()
            if p: var.set(p)

        ctk.CTkButton(r, text="Обзор", width=70, command=b).pack(side="right")

    def change_font(self, field, delta):
        try:
            val = int(self.font_sizes[field].get())
            self.font_sizes[field].set(str(val + delta))
        except:
            self.font_sizes[field].set("80")

    def move_coord(self, field, dx, dy):
        try:
            val = self.coords[field].get()
            if isinstance(val, str):
                x, y = eval(val.replace(' ', ''))
            else:
                x, y = val
            self.coords[field].set((x + dx, y + dy))
        except:
            pass

    def pick_coordinate(self, field_name):
        if not self.template_path.get():
            self.status.configure(text="❌ Сначала выберите шаблон!", text_color="red")
            return

        pick_win = Toplevel(self)
        pick_win.title(f"Выбор для {field_name}")
        pick_win.attributes("-topmost", True)

        img = Image.open(self.template_path.get())
        w, h = img.size
        ratio = 1100 / w
        img_res = img.resize((1100, int(h * ratio)))
        tk_img = ImageTk.PhotoImage(img_res)

        canv = Canvas(pick_win, width=1100, height=int(h * ratio), cursor="crosshair")
        canv.pack()
        canv.create_image(0, 0, anchor="nw", image=tk_img)
        canv.image = tk_img

        def click(e):
            rx, ry = int(e.x / ratio), int(e.y / ratio)
            self.coords[field_name].set((rx, ry))
            self.status.configure(text=f"✅ {field_name} установлена", text_color="green")
            pick_win.destroy()

        canv.bind("<Button-1>", click)

    def save_settings(self):
        data = {
            "coords": {k: str(v.get()) for k, v in self.coords.items()},
            "sizes": {k: v.get() for k, v in self.font_sizes.items()},
            "paths": {
                "data": self.data_path.get(),
                "template": self.template_path.get(),
                "font": self.font_path.get(),
                "output": self.output_dir.get()
            }
        }
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.status.configure(text="💾 Настройки сохранены", text_color="green")

    def load_settings(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in data.get("coords", {}).items(): self.coords[k].set(v)
                for k, v in data.get("sizes", {}).items(): self.font_sizes[k].set(v)
                p = data.get("paths", {})
                self.data_path.set(p.get("data", ""))
                self.template_path.set(p.get("template", ""))
                self.font_path.set(p.get("font", ""))
                self.output_dir.set(p.get("output", ""))
                self.status.configure(text="✅ Настройки загружены")
            except:
                pass

    def show_preview(self):
        self.start_generation(is_preview=True)

    def start_generation(self, is_preview=False):
        if not all([self.data_path.get(), self.template_path.get()]):
            self.status.configure(text="⚠️ Выберите файлы!", text_color="red")
            return

        # Парсим размеры и координаты
        c_sizes = {k: int(v.get()) if v.get() else 60 for k, v in self.font_sizes.items()}
        c_coords = {k: v.get() for k, v in self.coords.items()}

        try:
            ctrl = AppController(
                self.data_path.get(), self.template_path.get(),
                self.font_path.get(), self.output_dir.get(),
                c_coords, c_sizes
            )

            # 3. Передаем эти данные в метод генерации
            ok, msg = ctrl.generate_all(
                is_preview=is_preview,
                current_coords=c_coords,
                current_sizes=c_sizes
            )
            self.status.configure(text=msg, text_color="green" if ok else "red")
        except Exception as e:
            self.status.configure(text=f"❌ Ошибка: {e}", text_color="red")


if __name__ == "__main__":
    app = AppGUI()
    app.mainloop()