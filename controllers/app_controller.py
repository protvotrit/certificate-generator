import os
import logging
from models.certificate_model import CertificateModel
from views.renderer import CertificateRenderer


class AppController:
    def __init__(self, data_path, template_path, font_path, output_dir, coords_mapping):
        self.model = CertificateModel(data_path)
        self.view = CertificateRenderer(template_path, font_path)
        self.output_dir = output_dir

        # Динамические координаты из GUI
        # Переводим из формата строки/кортежа StringVar в чистые числа
        self.elements = {
            'name': {'pos': self._parse_coord(coords_mapping['ФИО']), 'size': 140},
            'program': {'pos': self._parse_coord(coords_mapping['Программа']), 'size': 140},
            'reg_num': {'pos': self._parse_coord(coords_mapping['Рег. номер']), 'size': 90},
            'hours': {'pos': self._parse_coord(coords_mapping['Часы']), 'size': 100}
        }
        self.max_width = 1200

    def _parse_coord(self, val):
        """Безопасно извлекает кортеж (x, y) из переменной GUI"""
        try:
            # Если пришло как (100, 200) или строка "(100, 200)"
            if isinstance(val, (list, tuple)):
                return val
            return eval(str(val))
        except:
            return (0, 0)

    def generate_all(self):
        try:
            records = self.model.get_data()
            success_count = 0

            for record in records:
                mapping = {
                    'name': record.get('ФИО'),
                    'program': record.get('Название программы'),
                    'reg_num': record.get('Регистрационный номер'),
                    'hours': record.get('Часы')
                }

                img = self.view.render(mapping, self.elements, self.max_width)
                if img:
                    group = self.model.sanitize_name(record.get('Номер группы', 'NoGroup'))
                    name = self.model.sanitize_name(record.get('ФИО', 'Unknown'))

                    path_jpg = os.path.join(self.output_dir, group, 'JPG')
                    path_pdf = os.path.join(self.output_dir, group, 'PDF')
                    os.makedirs(path_jpg, exist_ok=True)
                    os.makedirs(path_pdf, exist_ok=True)

                    img.save(os.path.join(path_jpg, f"{name}.jpg"), "JPEG")
                    img.save(os.path.join(path_pdf, f"{name}.pdf"), "PDF")
                    success_count += 1

            return True, f"Готово! Создано сертификатов: {success_count}"
        except Exception as e:
            logging.error(f"Ошибка контроллера: {e}")
            return False, f"Ошибка: {e}"