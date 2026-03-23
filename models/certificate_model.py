import pandas as pd
import re


class CertificateModel:
    def __init__(self, data_path):
        self.data_path = data_path

    def get_data(self):
        # Читаем данные из Excel
        df = pd.read_excel(self.data_path)
        # Превращаем таблицу в список словарей
        return df.to_dict('records')

    @staticmethod
    def sanitize_name(name):
        """Очищает строку от запрещенных в именах файлов символов"""
        if not name or str(name) == 'nan':
            return "Unknown"
        return re.sub(r'[\\/*?:"<>|]', '_', str(name))