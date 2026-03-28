import logging
from PIL import Image, ImageDraw, ImageFont


class CertificateRenderer:
    def __init__(self, template_path, font_path):
        self.template_path = template_path
        self.font_path = font_path

    def _split_text_to_lines(self, draw, text, font, max_width):
        """Разбивает текст на строки, чтобы каждая была не шире max_width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            # Получаем ширину тестовой строки
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    def render(self, data, config_elements, max_width):
        try:
            img = Image.open(self.template_path).convert("RGB")
            draw = ImageDraw.Draw(img)

            for key, settings in config_elements.items():
                text = str(data.get(key, "")).strip()
                if not text or text.lower() == "nan":
                    continue

                # 1. Берем размер шрифта СТРОГО из твоих настроек в GUI
                current_size = int(settings['size'])
                font = ImageFont.truetype(self.font_path, current_size)

                # 2. Сначала пробуем разбить на строки с этим размером
                lines = self._split_text_to_lines(draw, text, font, max_width)

                # 3. Если даже после разбивки текст слишком огромный (одно длинное слово),
                # тогда чуть-чуть уменьшаем шрифт (опционально)
                while current_size > 20:
                    longest_line = max(lines, key=lambda l: draw.textbbox((0, 0), l, font=font)[2])
                    if (draw.textbbox((0, 0), longest_line, font=font)[2]) <= max_width:
                        break
                    current_size -= 5
                    font = ImageFont.truetype(self.font_path, current_size)
                    lines = self._split_text_to_lines(draw, text, font, max_width)

                # 4. Рисуем полученные строки
                self._draw_wrapped_text(draw, lines, font, settings['pos'])

            return img
        except Exception as e:
            logging.error(f"Ошибка рендеринга: {e}")
            return None

    def _draw_wrapped_text(self, draw, lines, font, position, fill='black'):
        """Рисует блок строк, центрируя его по вертикали и горизонтали"""
        ascent, descent = font.getmetrics()
        line_height = ascent + descent

        total_height = len(lines) * line_height
        # Центрируем блок по вертикали относительно Y
        current_y = position[1] - (total_height // 2)

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            # Центрируем строку по горизонтали относительно X
            draw.text(
                (position[0] - line_w // 2, current_y),
                line,
                font=font,
                fill=fill
            )
            current_y += line_height