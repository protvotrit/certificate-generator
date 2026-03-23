import os
import logging
from models.certificate_model import CertificateModel
from views.renderer import CertificateRenderer


class AppController:
    def __init__(self, data_path, template_path, font_path, output_dir):
        self.model = CertificateModel(data_path)
        self.view = CertificateRenderer(template_path, font_path)
        self.output_dir = output_dir

        # Настройки элементов можно вынести в JSON или оставить здесь
        self.elements = {
            'name': {'pos': (2550, 825), 'size': 40},
            'program': {'pos': (2550, 1310), 'size': 35},
            'reg_num': {'pos': (1100, 1800), 'size': 45},
            'hours': {'pos': (2560, 1480), 'size': 45}
        }
        self.max_width = 1200

    def generate_all(self):
        try:
            records = self.model.get_data()
        except Exception as e:
            logging.error(f"Ошибка чтения базы данных Excel: {e}")
            return False, f"Ошибка чтения Excel: {e}"

        success_count = 0
        for record in records:
            mapping = {
                'name': record.get('ФИО'),
                'program': record.get('Название программы'),
                'reg_num': record.get('Регистрационный номер'),
                'hours': record.get('Часы')
            }

            image = self.view.render(mapping, self.elements, self.max_width)
            if image is None:
                continue  # Пропускаем, если была ошибка рендера (уже в логах)

            # Структура папок
            safe_group = self.model.sanitize_name(record.get('Номер группы', 'Без группы'))
            safe_name = self.model.sanitize_name(mapping['name'])

            group_folder = os.path.join(self.output_dir, safe_group)
            jpg_folder = os.path.join(group_folder, 'JPG')
            pdf_folder = os.path.join(group_folder, 'PDF')

            os.makedirs(jpg_folder, exist_ok=True)
            os.makedirs(pdf_folder, exist_ok=True)

            # Сохранение JPG
            jpg_path = os.path.join(jpg_folder, f"{safe_name}.jpg")
            image.save(jpg_path, "JPEG")

            # Сохранение PDF (Pillow отлично конвертирует RGB изображения в PDF)
            pdf_path = os.path.join(pdf_folder, f"{safe_name}.pdf")
            image.save(pdf_path, "PDF", resolution=100.0)

            success_count += 1
            logging.info(f"Успешно создан сертификат: {safe_name}")

        return True, f"Готово! Создано сертификатов: {success_count}"