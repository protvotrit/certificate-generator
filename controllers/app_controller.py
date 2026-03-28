import os
import logging
from models.certificate_model import CertificateModel
from views.renderer import CertificateRenderer


class AppController:
    def __init__(self, data_path, template_path, font_path, output_dir, coords_mapping, size_mapping):
        """
        Инициализация контроллера.
        Принимает пути к файлам и начальные настройки оформления.
        """
        self.model = CertificateModel(data_path)
        self.view = CertificateRenderer(template_path, font_path)
        self.output_dir = output_dir

        # Первичная настройка элементов
        self._update_elements(coords_mapping, size_mapping)

        # Лимит ширины текста (чтобы не уходил за края шаблона)
        self.max_width = 2200

    def _update_elements(self, coords_mapping, size_mapping):
        """Внутренний метод для обновления словаря элементов перед отрисовкой"""
        self.elements = {
            'name': {
                'pos': self._parse_coord(coords_mapping.get('ФИО', (0, 0))),
                'size': int(size_mapping.get('ФИО', 120))
            },
            'program': {
                'pos': self._parse_coord(coords_mapping.get('Программа', (0, 0))),
                'size': int(size_mapping.get('Программа', 80))
            },
            'reg_num': {
                'pos': self._parse_coord(coords_mapping.get('Рег. номер', (0, 0))),
                'size': int(size_mapping.get('Рег. номер', 60))
            },
            'hours': {
                'pos': self._parse_coord(coords_mapping.get('Часы', (0, 0))),
                'size': int(size_mapping.get('Часы', 60))
            }
        }

    def _parse_coord(self, val):
        """Превращает любые входные данные координат в чистый кортеж (int, int)"""
        try:
            if isinstance(val, (tuple, list)):
                return tuple(map(int, val))
            if isinstance(val, str):
                # Очистка строки от скобок и пробелов
                cleaned = val.replace('(', '').replace(')', '').replace(' ', '')
                if ',' in cleaned:
                    parts = cleaned.split(',')
                    return (int(parts[0]), int(parts[1]))
            return (0, 0)
        except Exception as e:
            logging.error(f"Ошибка парсинга координат {val}: {e}")
            return (0, 0)

    def generate_all(self, is_preview=False, current_coords=None, current_sizes=None):
        """
        Запуск процесса генерации.
        is_preview: если True, делает только 1 копию и открывает её.
        current_coords/current_sizes: свежие данные из GUI для мгновенного обновления.
        """
        try:
            # Обновляем настройки перед запуском, если они переданы из GUI
            if current_coords and current_sizes:
                self._update_elements(current_coords, current_sizes)

            # Получаем записи из Excel
            records = self.model.get_data()
            if not records:
                return False, "Ошибка: Excel-таблица пуста или не загружена."

            # Режим предпросмотра: берем только первую строку
            if is_preview:
                records = records[:1]
                target_base_dir = os.path.join(self.output_dir, "_PREVIEW_MODE")
            else:
                target_base_dir = self.output_dir

            success_count = 0
            last_saved_path = None

            for record in records:
                # Подготовка текстовых данных
                mapping = {
                    'name': str(record.get('ФИО', 'Имя не указано')),
                    'program': str(record.get('Название программы', '')),
                    'reg_num': str(record.get('Регистрационный номер', '')),
                    'hours': str(record.get('Часы', ''))
                }

                # Отрисовка
                img = self.view.render(mapping, self.elements, self.max_width)

                if img:
                    # 1. Очищаем имена от лишних пробелов в начале и конце
                    group = self.model.sanitize_name(str(record.get('Номер группы', 'Группа'))).strip()
                    file_name = self.model.sanitize_name(str(record.get('ФИО', 'Сертификат'))).strip()

                    # 2. Формируем пути
                    if is_preview:
                        path_jpg = target_base_dir
                        path_pdf = target_base_dir
                    else:
                        # Используем normpath, чтобы слеши были правильными
                        path_jpg = os.path.normpath(os.path.join(target_base_dir, group, 'JPG'))
                        path_pdf = os.path.normpath(os.path.join(target_base_dir, group, 'PDF'))

                    # 3. Создаем папки (exist_ok=True не даст ошибку, если папка уже есть)
                    os.makedirs(path_jpg, exist_ok=True)
                    os.makedirs(path_pdf, exist_ok=True)

                    # Сохранение файлов
                    img_path = os.path.join(path_jpg, f"{file_name}.jpg")
                    img.save(img_path, "JPEG", quality=95)
                    img.save(os.path.join(path_pdf, f"{file_name}.pdf"), "PDF")

                    last_saved_path = img_path
                    success_count += 1

            # Если это превью — автоматически открываем файл в Windows
            if is_preview and last_saved_path and os.path.exists(last_saved_path):
                os.startfile(last_saved_path)
                return True, "Предпросмотр открыт!"

            return True, f"Успешно создано документов: {success_count}"

        except Exception as e:
            logging.error(f"Критическая ошибка генерации: {e}")
            return False, f"Ошибка: {e}"