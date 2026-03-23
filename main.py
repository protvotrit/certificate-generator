import logging
import customtkinter as ctk
from views.gui import AppGUI
import sys
import os

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсам, работает и в dev, и в exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Настраиваем логирование
logging.basicConfig(
    filename='app_errors.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

if __name__ == "__main__":
    logging.info("Запуск приложения")
    # CustomTkinter настройки
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = AppGUI()
    app.mainloop()