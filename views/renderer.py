import logging
from PIL import Image, ImageDraw, ImageFont


class CertificateRenderer:
    def __init__(self, template_path, font_path):
        self.template_path = template_path
        self.font_path = font_path

    def _get_optimal_font(self, text, draw, max_width, initial_size, min_size=15):
        """Уменьшает шрифт, если текст не влезает в max_width"""
        size = initial_size
        font = ImageFont.truetype(self.font_path, size)

        # Пока ширина текста больше max_width и размер шрифта больше минимального
        while draw.textbbox((0, 0), text, font=font)[2] > max_width and size > min_size:
            size -= 2
            font = ImageFont.truetype(self.font_path, size)
        return font

    def render(self, data, config_elements, max_width):
        try:
            img = Image.open(self.template_path).convert("RGB")
            draw = ImageDraw.Draw(img)

            for key, settings in config_elements.items():
                text = str(data.get(key, ""))
                if not text or text == "nan":  # Пропуск пустых значений
                    continue

                # Подбираем оптимальный шрифт
                font = self._get_optimal_font(text, draw, max_width, settings['size'])

                # Отрисовываем текст
                self._draw_centered_text(draw, text, font, settings['pos'], max_width)
            return img
        except Exception as e:
            logging.error(f"Ошибка при отрисовке сертификата для {data.get('name', 'Неизвестно')}: {e}")
            return None

    def _draw_centered_text(self, draw, text, font, position, max_width=None, fill='black'):
        """
        Отрисовывает центрированный текст, при необходимости переносит его на новую строку,
        если ширина текста превышает max_width.
        """

        # Вспомогательная функция для получения ширины текста
        def get_text_width(t):
            bbox = draw.textbbox((0, 0), t, font=font)
            return bbox[2] - bbox[0]

        if max_width and get_text_width(text) > max_width:
            # Разбиваем текст, если он слишком длинный
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if get_text_width(test_line) <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
        else:
            lines = [text]

        # Если текст длинный и не был разбит (и max_width не задан), делим на две строки
        if max_width is None and len(lines[0].split()) > 4:
            words = lines[0].split()
            split_point = len(words) // 2
            lines = [" ".join(words[:split_point]), " ".join(words[split_point:])]

        # Вычисляем высоту строки на основе тестовых символов (учитывая выносные элементы)
        tg_bbox = draw.textbbox((0, 0), "Tg", font=font)
        line_height = tg_bbox[3] - tg_bbox[1]

        total_height = len(lines) * line_height
        start_y = position[1] - total_height // 2

        # Отрисовка каждой строки
        for i, line in enumerate(lines):
            line_width = get_text_width(line)
            draw.text(
                (position[0] - line_width // 2, start_y + i * line_height),
                line,
                font=font,
                fill=fill,
            )