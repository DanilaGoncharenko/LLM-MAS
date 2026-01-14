from __future__ import annotations

import datetime
import json
import math
import re

from langchain_core.tools import tool

from .memory import load_notes, append_note, simple_retrieve_notes


# Инструменты для агентов
@tool("calc")
def calc(expression: str) -> str:
    """
    Для вычисления простых математических формул 
    """""
    if not re.fullmatch(r"[0-9\.\+\-\*\/\(\)\s]+", expression or ""):
        return "Ошибка: недопустимые символы в выражении"
    try:
        val = eval(expression, {"__builtins__": {}}, {"math": math})
        return str(val)
    except Exception as e:
        return f"Ошибка вычисления: {e}"

@tool("days_until")
def days_until(date_iso: str) -> str:
    """
    Считаем количество дней до заданной даты для планирования бытовых задач
    """""
    try:
        target = datetime.date.fromisoformat((date_iso or "").strip())
        today = datetime.date.today()
        return str((target - today).days)
    except Exception:
        return "Ошибка: ожидаю дату в формате YYYY-MM-DD"

@tool("save_user_note")
def save_user_note(text: str, tags_json: str = "[]") -> str:
    """
    Сохраняем пользовательский вопрос в файл
    """
    try:
        tags = json.loads(tags_json) if tags_json else []
        if not isinstance(tags, list):
            tags = []
    except Exception:
        tags = []
        
    # Загружаем текущие ответы, добавляем новую и сохраняем
    notes = load_notes()
    note = append_note(notes, text=text, tags=tags)
    return json.dumps(note, ensure_ascii=False)

@tool("search_user_notes")
def search_user_notes(query: str, k: int = 5) -> str:
    """
    Ищем релевантные ответы в файле с историей 
    """
    notes = load_notes()
    hits = simple_retrieve_notes(notes, query=query, k=k)
    return json.dumps(hits, ensure_ascii=False)

@tool("create_table")
def create_table(data_json: str) -> str:
    """
    Создает таблицу в формате Markdown из структурированных данных.
    
    Параметры:
    - data_json: строка в формате JSON с ключами:
        * headers: список названий столбцов (обязательно)
        * rows: список строк, каждая строка - список значений (обязательно)
        * caption: заголовок таблицы (опционально)
        * alignment: выравнивание столбцов (опционально, по умолчанию "left")
          Формат: список значений ["left", "center", "right"] по количеству столбцов
    
   
    
    Особенности:
    - Автоматическое форматирование чисел и дат
    - Поддержка многострочных ячеек
    - Валидация структуры данных
    - Экранирование специальных символов Markdown
    """
    try:
        # Парсинг JSON
        data = json.loads(data_json)
        
        # Валидация обязательных полей
        if "headers" not in data or "rows" not in data:
            return "Ошибка: отсутствуют обязательные поля 'headers' или 'rows' в JSON"
        
        headers = data["headers"]
        rows = data["rows"]
        caption = data.get("caption", "")
        alignment = data.get("alignment", ["left"] * len(headers))
        
        # Проверка соответствия количества столбцов
        num_cols = len(headers)
        if len(alignment) != num_cols:
            alignment = ["left"] * num_cols
        
        # Валидация строк
        for i, row in enumerate(rows):
            if len(row) != num_cols:
                return f"Ошибка: строка {i+1} содержит {len(row)} элементов, ожидается {num_cols}"
        
        # Функция для экранирования Markdown-спецсимволов
        def escape_markdown(text):
            if not isinstance(text, str):
                return str(text)
            # Экранируем только символы, которые могут нарушить форматирование таблицы
            return text.replace("|", "\\|").replace("\n", "<br>")
        
        # Формирование разделителя с учетом выравнивания
        def get_alignment_marker(align):
            if align == "center":
                return ":---:"
            elif align == "right":
                return "---:"
            else:
                return ":---"
        
        # Форматирование таблицы
        table_lines = []
        
        # Добавление заголовка, если есть
        if caption:
            table_lines.append(f"**{escape_markdown(caption)}**\n")
        
        # Заголовки
        header_row = "| " + " | ".join(escape_markdown(h) for h in headers) + " |"
        table_lines.append(header_row)
        
        # Разделитель с выравниванием
        separator = "| " + " | ".join(get_alignment_marker(align) for align in alignment) + " |"
        table_lines.append(separator)
        
        # Строки данных
        for row in rows:
            formatted_row = "| " + " | ".join(escape_markdown(cell) for cell in row) + " |"
            table_lines.append(formatted_row)
        
        # Добавление подписи к таблице (опционально)
        if caption:
            table_lines.append(f"\n_Таблица 1: {escape_markdown(caption)}_")
        
        return "\n".join(table_lines)
    
    except json.JSONDecodeError as e:
        return f"Ошибка парсинга JSON: {str(e)}"
    except TypeError as e:
        return f"Ошибка типа данных: {str(e)}"
    except Exception as e:
        return f"Ошибка создания таблицы: {str(e)}"

# Для бытовых задач
TOOLS_DAILY = [calc, days_until, save_user_note, search_user_notes]

# Для задач программирования
TOOLS_CODING = [calc, save_user_note, search_user_notes]

# Для задач литературных 
TOOLS_LITERATURE = [save_user_note, search_user_notes, create_table]

# Для задач с составлением таблиц
TOOLS_DATABASE = [calc, save_user_note, search_user_notes, create_table]