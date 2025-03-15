from dotenv import load_dotenv

load_dotenv ()

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import argparse
from pathlib import Path
from openai import OpenAI
import logging
import sys
import re

# Настройка логирования
logging.basicConfig (
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler (sys.stdout)
    ]
)
logger = logging.getLogger (__name__)

# Конфигурация OpenRouter
OPENROUTER_API_KEY = os.environ.get ("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    logger.error ("Не задан ключ API OPENROUTER_API_KEY в переменных окружения")
    sys.exit (1)

# Настройки по умолчанию
# DEFAULT_MODEL = "mistralai/mistral-small-24b-instruct-2501"
DEFAULT_MODEL = "openai/gpt-4o-mini"
SITE_URL = "https://example.com"
SITE_NAME = "CodeFixer"


class CodeFixer:
    def __init__(self, api_key, model=DEFAULT_MODEL):
        """
        Инициализация класса для анализа и исправления кода

        Args:
            api_key (str): API ключ для OpenRouter
            model (str): Модель ИИ для использования
        """
        self.client = OpenAI (
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
        logger.info (f"Инициализирован CodeFixer с моделью {model}")

    def compare_code_segments(self, expected, actual):
        """
        Сравнивает сегменты кода с учетом различных вариантов форматирования

        Args:
            expected (str): Ожидаемый код
            actual (str): Фактический код

        Returns:
            bool: True, если сегменты эквивалентны
        """
        # Нормализация концов строк
        expected_normalized = expected.replace ('\r\n', '\n').rstrip ('\n')
        actual_normalized = actual.replace ('\r\n', '\n').rstrip ('\n')

        # Прямое сравнение
        if expected_normalized == actual_normalized:
            return True

        # Сравнение без учета пробелов в конце строк
        expected_lines = [line.rstrip () for line in expected_normalized.splitlines ()]
        actual_lines = [line.rstrip () for line in actual_normalized.splitlines ()]

        if expected_lines == actual_lines:
            return True

        # Дополнительно можно добавить более гибкие сравнения при необходимости

        return False

    def read_file(self, file_path):
        """
        Чтение содержимого файла

        Args:
            file_path (str): Путь к файлу

        Returns:
            str: Содержимое файла
        """
        try:
            with open (file_path, 'r', encoding='utf-8') as file:
                return file.read ()
        except Exception as e:
            logger.error (f"Ошибка при чтении файла {file_path}: {e}")
            raise

    def create_backup(self, file_path):
        """
        Создание резервной копии файла

        Args:
            file_path (str): Путь к файлу

        Returns:
            str: Путь к резервной копии
        """
        backup_path = f"{file_path}.bak.{int (time.time ())}"
        try:
            with open (file_path, 'r', encoding='utf-8') as source_file:
                with open (backup_path, 'w', encoding='utf-8') as backup_file:
                    backup_file.write (source_file.read ())
            logger.info (f"Создана резервная копия {backup_path}")
            return backup_path
        except Exception as e:
            logger.error (f"Ошибка при создании резервной копии: {e}")
            raise

    def generate_prompt(self, code):
        """
        Формирование промта для ИИ с инструкциями по использованию промпт-инструментов

        Args:
            code (str): Исходный код для анализа

        Returns:
            str: Промт для отправки ИИ
        """
        # Подготовка строк кода с нумерацией
        lines = code.splitlines ()
        numbered_code = "\n".join ([f"{i + 1}: {line}" for i, line in enumerate (lines)])

        prompt = """
### ЗАДАЧА ПРОВЕРКИ И ИСПРАВЛЕНИЯ КОДА ###

# ИНСТРУКЦИИ
Ты - эксперт по Python. Твоя задача - проверить код на наличие ошибок, проблем, неоптимальных решений и исправить их.
Необходимо найти и исправить:
1. Синтаксические ошибки
2. Логические ошибки
3. Проблемы с именованием переменных
4. Неэффективные алгоритмы или структуры данных
5. Нарушения стиля кодирования PEP 8
6. Потенциальные исключения, которые не обрабатываются
7. Проблемы безопасности или утечки ресурсов

# ИСХОДНЫЙ КОД
Код с номерами строк:
```
{0}
```

Код без номеров строк для анализа:
```python
{1}
```

# ИНСТРУКЦИИ ПО ФОРМАТУ ОТВЕТА
Ты должен использовать следующие функции для анализа и исправления кода:

ФОРМАТ ВЫЗОВА ФУНКЦИЙ: Когда тебе нужно вызвать функцию, используй строго следующий формат: 
[FUNCTION: имя_функции(параметр1="значение1", параметр2=значение2)]

ДОСТУПНЫЕ ФУНКЦИИ:

1. analyze_code()
   Описание: Анализирует предоставленный код и находит проблемы
   Пример вызова: [FUNCTION: analyze_code()]

2. suggest_fixes(issues)
   Описание: Предлагает исправления для найденных проблем
   Параметры:
   - issues (список): Список найденных проблем
   Пример вызова: [FUNCTION: suggest_fixes(issues=["проблема1", "проблема2"])]

3. format_changes(fixes)
   Описание: Форматирует предложенные исправления в структуру JSON
   Параметры:
   - fixes (список): Список исправлений
   Пример вызова: [FUNCTION: format_changes(fixes=[{{"тип": "замена", "строка": 10}}])]

Твой ответ должен содержать JSON в следующем формате:

{2}
  "has_issues": true/false,
  "changes": [
    {2}
      "type": "replace",
      "line_start": X,
      "line_end": Y,
      "old_code": "...",
      "new_code": "..."
    {3},
    {2}
      "type": "insert",
      "line": Z,
      "new_code": "..."
    {3},
    {2}
      "type": "delete",
      "line_start": A,
      "line_end": B,
      "old_code": "..."
    {3}
  ],
  "explanation": "Подробное объяснение найденных проблем и внесенных изменений"
{3}

# ВАЖНЫЕ ПРАВИЛА
1. ОЧЕНЬ ВАЖНО: Используй точные номера строк из первого блока кода с нумерацией!
2. Если проблем не обнаружено, верни {2}"has_issues": false, "changes": [], "explanation": "Код не содержит проблем"{3}
3. Используй только типы изменений "replace", "insert" или "delete"
4. Номера строк начинаются с 1 (не с 0)
5. Для операции "insert" указывай только "line" вместо "line_start" и "line_end"
6. Для операции "delete" и "replace" старый код (old_code) должен точно совпадать с исходным
7. Выделяй наименьший возможный фрагмент кода для изменения
8. Соблюдай отступы и форматирование при генерации нового кода
9. Сохраняй стиль именования переменных из исходного кода
10. Не добавляй и не удаляй пустые строки, если это не требуется для исправления проблемы

Возвращай только структуру JSON без дополнительного текста или markdown-форматирования.
"""
        # Используем .format с числовыми индексами и добавляем фигурные скобки как литералы
        return prompt.format (numbered_code, code, "{", "}")

    def analyze_code(self, code):
        """
        Отправка кода на анализ ИИ с использованием промпт-инструментов

        Args:
            code (str): Исходный код

        Returns:
            dict: Результат анализа в виде словаря
        """
        prompt = self.generate_prompt (code)

        try:
            logger.info ("Отправка запроса к ИИ...")
            completion = self.client.chat.completions.create (
                extra_headers={
                    "HTTP-Referer": SITE_URL,
                    "X-Title": SITE_NAME,
                },
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Низкая температура для более точного следования формату
                top_p=0.95,  # Слегка ограничиваем разнообразие
                max_tokens=2048  # Увеличиваем лимит токенов для полного ответа
            )

            response_text = completion.choices[0].message.content
            logger.info (f"Сырой ответ от ИИ: {response_text[:200]}...")

            # Обработка вызовов функций в ответе модели
            response_text = self.process_bot_response (response_text, code)

            # Извлечение JSON из ответа (на случай, если модель вернет лишний текст)
            json_match = re.search (r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group (1)
                logger.info ("Извлечен JSON из блока кода")
            else:
                # Если модель не использовала блок кода, попробуем найти JSON напрямую
                json_match = re.search (r'({[\s\S]*})', response_text)
                if json_match:
                    response_text = json_match.group (1)
                    logger.info ("Извлечен JSON из текста напрямую")
                else:
                    logger.warning ("Не удалось извлечь JSON в стандартном формате")

            logger.info ("Получен ответ от ИИ, попытка парсинга JSON")

            # Удалим возможные escape-символы, которые могут мешать парсингу
            response_text = response_text.strip ()

            try:
                response_json = json.loads (response_text)
                logger.info ("JSON успешно распарсен")
                return response_json
            except json.JSONDecodeError as e:
                logger.error (f"Ошибка декодирования JSON: {e}")
                logger.error (f"Полученный ответ для парсинга: {response_text}")

                # Попытка очистить и исправить JSON
                try:
                    # Иногда модели добавляют лишние символы или форматирование
                    cleaned_text = re.sub (r'[\n\r\t]', '', response_text)
                    cleaned_text = cleaned_text.replace ("'", '"')  # Замена одинарных кавычек на двойные
                    logger.info (f"Попытка исправления JSON: {cleaned_text[:200]}...")
                    response_json = json.loads (cleaned_text)
                    logger.info ("JSON успешно распарсен после очистки")
                    return response_json
                except json.JSONDecodeError:
                    # Если всё ещё не удаётся распарсить, создадим стандартную структуру
                    logger.error ("Не удалось распарсить JSON даже после очистки")
                    fallback_response = {
                        "has_issues": True,
                        "changes": [],
                        "explanation": "Не удалось распарсить ответ модели. Проверьте код вручную."
                    }
                    return fallback_response

        except Exception as e:
            logger.error (f"Ошибка при обращении к API: {e}")
            raise

    def process_bot_response(self, response, code):
        """
        Обрабатывает ответ бота, заменяя вызовы функций на их результаты.

        Args:
            response: Ответ бота
            code: Исходный код для анализа

        Returns:
            str: Обработанный ответ с результатами функций
        """
        # Шаблон для поиска вызовов функций
        function_pattern = r'\[FUNCTION: (\w+)\((.*?)\)\]'

        # Пока в ответе есть вызовы функций, обрабатываем их
        iteration = 0
        max_iterations = 10  # Защита от бесконечного цикла

        while re.search (function_pattern, response) and iteration < max_iterations:
            iteration += 1
            logger.info (f"Обработка вызова функции (итерация {iteration})")

            # Находим первый вызов функции
            match = re.search (function_pattern, response)
            if not match:
                break

            function_call = match.group (0)
            function_name = match.group (1)
            args_str = match.group (2)

            logger.info (f"Найден вызов функции: {function_call}")

            # Обрабатываем различные функции
            result = None
            if function_name == "analyze_code":
                # Выполняем базовый анализ кода
                issues = self.analyze_code_impl (code)
                result = {
                    "function": "analyze_code",
                    "issues": issues
                }
            elif function_name == "suggest_fixes":
                # Парсим аргументы функции
                args = self.parse_function_args (args_str)
                issues = args.get ("issues", [])

                # Получаем предложения по исправлениям
                fixes = self.suggest_fixes_impl (code, issues)
                result = {
                    "function": "suggest_fixes",
                    "fixes": fixes
                }
            elif function_name == "format_changes":
                # Парсим аргументы функции
                args = self.parse_function_args (args_str)
                fixes = args.get ("fixes", [])

                # Форматируем изменения в структуру JSON
                formatted_changes = self.format_changes_impl (fixes)
                result = {
                    "function": "format_changes",
                    "changes": formatted_changes
                }

            if result:
                # Форматируем результат
                formatted_result = self.format_function_result (result)

                # Заменяем вызов функции на результат
                response = response.replace (function_call, formatted_result, 1)
                logger.info (f"Функция {function_name} успешно выполнена и заменена")
            else:
                # Если функция не распознана, заменяем вызов на ошибку
                error_result = f"[RESULT: error]\nНе удалось выполнить функцию: {function_name}\n[/RESULT]"
                response = response.replace (function_call, error_result, 1)
                logger.info (f"Ошибка при выполнении функции {function_name}")

        # Проверяем, остались ли необработанные вызовы функций
        if re.search (function_pattern, response):
            logger.warning ("ВНИМАНИЕ: Остались необработанные вызовы функций!")

        return response

    def parse_function_args(self, args_str):
        """
        Парсит аргументы функций из строки.

        Args:
            args_str: Строка с аргументами

        Returns:
            dict: Словарь с разобранными аргументами
        """
        args = {}

        # Распознавание аргументов с учетом вложенных строк и экранирования
        import re

        # Шаблон для аргументов: имя=значение, где значение может быть строкой, числом или логическим
        pattern = r'(\w+)=(?:"((?:\\.|[^"])*?)"|\'((?:\\.|[^\'])*?)\'|(\d+\.\d+)|(\d+)|(true|false)|\[(.*?)\])'

        for match in re.finditer (pattern, args_str):
            arg_name = match.group (1)

            # Ищем первое непустое значение среди групп
            values = match.groups ()[1:]
            arg_value = next ((v for v in values if v is not None), None)

            # Проверяем на список
            if match.group (7):  # Это группа для содержимого списка
                try:
                    # Пытаемся распарсить как JSON
                    list_str = f"[{match.group (7)}]"
                    arg_value = json.loads (list_str)
                except json.JSONDecodeError:
                    # Если не получается, разбиваем по запятой
                    arg_value = [item.strip () for item in match.group (7).split (',')]

            # Преобразуем значение к правильному типу
            elif arg_value == "true":
                arg_value = True
            elif arg_value == "false":
                arg_value = False
            elif arg_value and arg_value.isdigit ():
                arg_value = int (arg_value)
            elif arg_value and re.match (r'^\d+\.\d+$', arg_value):
                arg_value = float (arg_value)

            # Обработка экранированных последовательностей в строках
            if isinstance (arg_value, str):
                # Заменяем экранированные спецсимволы
                arg_value = arg_value.replace ('\\n', '\n').replace ('\\t', '\t').replace ('\\"', '"')

                # Обрабатываем unicode последовательности
                arg_value = re.sub (r'\\u([0-9a-fA-F]{4})',
                                    lambda m: chr (int (m.group (1), 16)),
                                    arg_value)

            args[arg_name] = arg_value

        return args

    def format_function_result(self, result):
        """
        Форматирует результат выполнения функции.

        Args:
            result: Результат выполнения функции

        Returns:
            str: Форматированный результат
        """
        function_name = result.get ('function', 'unknown')

        if function_name == 'analyze_code':
            issues = result.get ('issues', [])
            issues_str = '\n'.join ([f"- {issue}" for issue in issues])

            if not issues:
                issues_str = "Проблем не обнаружено."

            return f"[RESULT: {function_name}]\n{issues_str}\n[/RESULT]"

        elif function_name == 'suggest_fixes':
            fixes = result.get ('fixes', [])
            fixes_str = json.dumps (fixes, indent=2, ensure_ascii=False)
            return f"[RESULT: {function_name}]\n{fixes_str}\n[/RESULT]"

        elif function_name == 'format_changes':
            changes = result.get ('changes', [])
            changes_str = json.dumps (changes, indent=2, ensure_ascii=False)
            return f"[RESULT: {function_name}]\n{changes_str}\n[/RESULT]"

        # Для неизвестных функций
        return f"[RESULT: {function_name}]\n{json.dumps (result, indent=2, ensure_ascii=False)}\n[/RESULT]"

    def analyze_code_impl(self, code):
        """
        Простая реализация анализа кода.

        Args:
            code: Исходный код для анализа

        Returns:
            list: Список найденных проблем
        """
        issues = []

        # Проверка на базовые проблемы
        lines = code.splitlines ()

        # Длинные строки
        for i, line in enumerate (lines):
            if len (line) > 100:
                issues.append (f"Строка {i + 1} превышает рекомендуемую длину в 100 символов")

        # Неиспользуемые импорты
        import_lines = [i for i, line in enumerate (lines) if re.match (r'^import\s+', line) or re.match (r'^from\s+.*\s+import\s+', line)]
        for i in import_lines:
            module = re.search (r'import\s+(\w+)', lines[i])
            if module:
                module_name = module.group (1)
                if not any (module_name in line for j, line in enumerate (lines) if j != i):
                    issues.append (f"Возможно неиспользуемый импорт в строке {i + 1}: {lines[i]}")

        # Переменные с пробелами вокруг скобок
        for i, line in enumerate (lines):
            if re.search (r'\(\s+', line) or re.search (r'\s+\)', line):
                issues.append (f"Лишние пробелы вокруг скобок в строке {i + 1}")

        # Непоследовательное использование кавычек
        single_quotes = sum (1 for line in lines if "'" in line)
        double_quotes = sum (1 for line in lines if '"' in line)
        if single_quotes > 0 and double_quotes > 0:
            issues.append ("Непоследовательное использование одинарных и двойных кавычек")

        return issues

    def suggest_fixes_impl(self, code, issues):
        """
        Генерирует предложения по исправлению проблем.

        Args:
            code: Исходный код
            issues: Список проблем

        Returns:
            list: Список предлагаемых исправлений
        """
        fixes = []
        lines = code.splitlines ()

        for issue in issues:
            # Поиск номера строки в сообщении о проблеме
            line_match = re.search (r'Строка (\d+)', issue)
            if line_match:
                line_num = int (line_match.group (1))

                # Проверяем тип проблемы и предлагаем исправление
                if "превышает рекомендуемую длину" in issue:
                    # Разбиваем длинную строку
                    original_line = lines[line_num - 1]
                    if "=" in original_line:
                        parts = original_line.split ("=", 1)
                        indentation = len (parts[0]) - len (parts[0].lstrip ())
                        fixed_line = parts[0] + "=\\\n" + " " * (indentation + 4) + parts[1].strip ()
                        fixes.append ({
                            "type": "replace",
                            "line": line_num,
                            "old": original_line,
                            "new": fixed_line
                        })

                elif "неиспользуемый импорт" in issue:
                    # Удаляем неиспользуемый импорт
                    fixes.append ({
                        "type": "delete",
                        "line": line_num,
                        "old": lines[line_num - 1]
                    })

                elif "Лишние пробелы вокруг скобок" in issue:
                    # Удаляем лишние пробелы
                    original_line = lines[line_num - 1]
                    fixed_line = re.sub (r'\(\s+', '(', original_line)
                    fixed_line = re.sub (r'\s+\)', ')', fixed_line)
                    fixes.append ({
                        "type": "replace",
                        "line": line_num,
                        "old": original_line,
                        "new": fixed_line
                    })

            elif "Непоследовательное использование" in issue:
                # Стандартизируем кавычки (выбираем двойные)
                for i, line in enumerate (lines):
                    if "'" in line and not '"' in line:  # Только одинарные кавычки
                        # Простая замена для демонстрации
                        original_line = line
                        fixed_line = line.replace ("'", '"')
                        fixes.append ({
                            "type": "replace",
                            "line": i + 1,
                            "old": original_line,
                            "new": fixed_line
                        })

        return fixes

    def format_changes_impl(self, fixes):
        """
        Преобразует предложенные исправления в формат изменений для CodeFixer.

        Args:
            fixes: Список предложенных исправлений

        Returns:
            list: Отформатированные изменения
        """
        changes = []

        for fix in fixes:
            if fix.get ("type") == "replace":
                changes.append ({
                    "type": "replace",
                    "line_start": fix.get ("line"),
                    "line_end": fix.get ("line"),
                    "old_code": fix.get ("old"),
                    "new_code": fix.get ("new")
                })
            elif fix.get ("type") == "delete":
                changes.append ({
                    "type": "delete",
                    "line_start": fix.get ("line"),
                    "line_end": fix.get ("line"),
                    "old_code": fix.get ("old")
                })
            elif fix.get ("type") == "insert":
                changes.append ({
                    "type": "insert",
                    "line": fix.get ("line"),
                    "new_code": fix.get ("new")
                })

        return changes


    def apply_changes(self, file_path, changes):
        """
        Применение изменений к файлу

        Args:
            file_path (str): Путь к файлу
            changes (list): Список изменений для применения

        Returns:
            bool: True, если изменения успешно применены
        """
        if not changes:
            logger.info ("Нет изменений для применения")
            return True

        # Чтение файла как список строк
        with open (file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines ()

        # Проверка всех изменений перед применением
        valid_changes = []
        invalid_changes = []

        for change in changes:
            change_type = change.get ('type')

            if change_type == "replace":
                start = change.get ('line_start', 0) - 1
                end = change.get ('line_end', 0) - 1

                # Проверка диапазона
                if start < 0 or end >= len (lines) or start > end:
                    logger.error (f"Неверный диапазон для замены: {start + 1}-{end + 1} (всего строк: {len (lines)})")
                    invalid_changes.append (change)
                    continue

                # Проверка соответствия старого кода
                old_code = change.get ('old_code', '').rstrip ('\n')
                actual_old_code = ''.join (lines[start:end + 1]).rstrip ('\n')

                if not self.compare_code_segments (old_code, actual_old_code):
                    logger.error (f"Несоответствие старого кода на строках {start + 1}-{end + 1}")
                    logger.debug (f"Ожидалось:\n{old_code}")
                    logger.debug (f"Фактически:\n{actual_old_code}")
                    invalid_changes.append (change)
                    continue

                valid_changes.append (change)

            elif change_type == "insert":
                position = change.get ('line', 0) - 1

                # Проверка позиции
                if position < 0 or position > len (lines):
                    logger.error (f"Неверная позиция для вставки: {position + 1} (всего строк: {len (lines)})")
                    invalid_changes.append (change)
                    continue

                valid_changes.append (change)

            elif change_type == "delete":
                start = change.get ('line_start', 0) - 1
                end = change.get ('line_end', 0) - 1

                # Проверка диапазона
                if start < 0 or end >= len (lines) or start > end:
                    logger.error (f"Неверный диапазон для удаления: {start + 1}-{end + 1} (всего строк: {len (lines)})")
                    invalid_changes.append (change)
                    continue

                # Проверка соответствия старого кода, если он предоставлен
                if 'old_code' in change:
                    old_code = change.get ('old_code', '').rstrip ('\n')
                    actual_old_code = ''.join (lines[start:end + 1]).rstrip ('\n')

                    if not self.compare_code_segments (old_code, actual_old_code):
                        logger.error (f"Несоответствие старого кода на строках {start + 1}-{end + 1}")
                        logger.debug (f"Ожидалось:\n{old_code}")
                        logger.debug (f"Фактически:\n{actual_old_code}")
                        invalid_changes.append (change)
                        continue

                valid_changes.append (change)

            else:
                logger.error (f"Неизвестный тип изменения: {change_type}")
                invalid_changes.append (change)

        # Выводим информацию о проверке изменений
        logger.info (f"Всего изменений: {len (changes)}")
        logger.info (f"Корректных изменений: {len (valid_changes)}")
        if invalid_changes:
            logger.info (f"Некорректных изменений: {len (invalid_changes)}")
            for i, change in enumerate (invalid_changes):
                logger.debug (f"Некорректное изменение #{i + 1}: {change}")

        if not valid_changes:
            logger.error ("Нет корректных изменений для применения")
            return False

        # Сортировка изменений в обратном порядке по номерам строк
        # для избежания смещения индексов при применении изменений
        sorted_changes = sorted (
            valid_changes,
            key=lambda x: x.get ('line_start', x.get ('line', 0)),
            reverse=True
        )

        # Применение изменений
        applied_changes = []
        for change in sorted_changes:
            change_type = change.get ('type')

            try:
                if change_type == "replace":
                    start = change['line_start'] - 1
                    end = change['line_end'] - 1

                    # Разбиваем новый код на строки
                    new_code_lines = change['new_code'].splitlines (True)

                    # Если последняя строка нового кода не имеет символа новой строки, но она не последняя в файле
                    if new_code_lines and not new_code_lines[-1].endswith ('\n') and end < len (lines) - 1:
                        new_code_lines[-1] += '\n'

                    # Заменяем строки
                    lines[start:end + 1] = new_code_lines
                    applied_changes.append (change)

                elif change_type == "insert":
                    position = change['line'] - 1

                    # Разбиваем новый код на строки
                    new_code_lines = change['new_code'].splitlines (True)

                    # Если последняя строка нового кода не имеет символа новой строки, но вставка не в конец файла
                    if new_code_lines and not new_code_lines[-1].endswith ('\n') and position < len (lines):
                        new_code_lines[-1] += '\n'

                    # Вставляем строки
                    if position == len (lines):
                        lines.extend (new_code_lines)
                    else:
                        for i, line in enumerate (new_code_lines):
                            lines.insert (position + i, line)

                    applied_changes.append (change)

                elif change_type == "delete":
                    start = change['line_start'] - 1
                    end = change['line_end'] - 1

                    # Удаляем строки
                    del lines[start:end + 1]
                    applied_changes.append (change)

            except Exception as e:
                logger.error (f"Ошибка при применении изменения {change_type}: {e}")
                # Продолжаем с другими изменениями

        logger.info (f"Применено {len (applied_changes)} из {len (valid_changes)} корректных изменений")

        # Запись изменений в файл только если были применены какие-либо изменения
        if applied_changes:
            with open (file_path, 'w', encoding='utf-8') as file:
                file.writelines (lines)

            logger.info (f"Изменения успешно записаны в файл {file_path}")
            return True
        else:
            logger.error ("Ни одно изменение не было применено")
            return False

    def fix_code(self, file_path):
        """
        Проверка и исправление кода в файле

        Args:
            file_path (str): Путь к файлу с кодом

        Returns:
            dict: Результат анализа и исправления
        """
        try:
            # Чтение исходного кода
            code = self.read_file (file_path)
            logger.info (f"Прочитан файл {file_path}, {len (code)} символов")

            # Анализ кода
            result = self.analyze_code (code)

            # Проверка структуры результата
            if not isinstance (result, dict):
                logger.error (f"Некорректный формат результата анализа: {type (result)}")
                logger.error (f"Содержимое: {result}")
                return {"has_issues": False, "changes": [], "explanation": "Ошибка анализа"}

            logger.info (f"Получен результат анализа: {result.keys ()}")

            # Если обнаружены проблемы
            has_issues = result.get ('has_issues', False)
            logger.info (f"Обнаружены проблемы: {has_issues}")

            if has_issues:
                logger.info (f"Создание резервной копии файла...")
                backup_path = self.create_backup (file_path)

                # Применение изменений
                changes = result.get ('changes', [])
                logger.info (f"Получено {len (changes)} изменений")

                if changes:
                    logger.info (f"Применение {len (changes)} изменений...")
                    success = self.apply_changes (file_path, changes)
                    if success:
                        logger.info ("Файл успешно исправлен")
                        logger.info (f"Резервная копия сохранена в {backup_path}")
                    else:
                        logger.warning ("Возникли проблемы при применении некоторых изменений")
                        logger.info (f"Резервная копия сохранена в {backup_path}")
                else:
                    logger.info ("Нет изменений для применения, хотя обнаружены проблемы")

            else:
                logger.info ("Проблем в коде не обнаружено")

            logger.info (f"Объяснение: {result.get ('explanation', 'Нет объяснения')}")
            return result

        except Exception as e:
            logger.error (f"Ошибка при исправлении кода: {e}")
            # Создаем дамп исключения для более подробной диагностики
            import traceback
            logger.error (f"Трассировка ошибки: {traceback.format_exc ()}")
            # Возвращаем базовый результат вместо выбрасывания исключения
            return {"has_issues": False, "changes": [], "explanation": f"Ошибка: {str (e)}"}


def main():
    parser = argparse.ArgumentParser (description='Проверка и исправление Python кода')
    parser.add_argument ('file', help='Путь к файлу для проверки')
    parser.add_argument ('--model', help='Модель ИИ для использования', default=DEFAULT_MODEL)
    parser.add_argument ('--debug', action='store_true', help='Включить режим отладки')
    args = parser.parse_args ()

    # Настройка уровня логирования
    if args.debug:
        logger.setLevel (logging.DEBUG)
        logger.debug ("Включен режим отладки")

    # Проверка API ключа
    if not OPENROUTER_API_KEY:
        logger.error ("API ключ OpenRouter не установлен. Установите переменную окружения OPENROUTER_API_KEY")
        sys.exit (1)

    # Проверка существования файла
    file_path = Path (args.file)
    if not file_path.exists ():
        logger.error (f"Файл {file_path} не существует")
        sys.exit (1)

    # Проверка расширения файла
    if file_path.suffix.lower () != '.py':
        logger.error (f"Файл {file_path} не является Python файлом")
        sys.exit (1)

    logger.info (f"Запуск проверки файла {file_path} с моделью {args.model}")

    # Инициализация CodeFixer
    fixer = CodeFixer (OPENROUTER_API_KEY, args.model)

    try:
        # Проверка и исправление кода
        result = fixer.fix_code (str (file_path))

        # Вывод результата
        if isinstance (result, dict):
            if result.get ('has_issues', False):
                changes_count = len (result.get ('changes', []))
                logger.info (f"Исправлено {changes_count} проблем в файле {file_path}")
                if 'explanation' in result:
                    logger.info (f"Объяснение: {result['explanation']}")
            else:
                logger.info (f"Файл {file_path} не содержит проблем")
        else:
            logger.error (f"Неожиданный формат результата: {type (result)}")

    except Exception as e:
        logger.error (f"Ошибка при выполнении программы: {e}")
        import traceback
        logger.debug (f"Трассировка стека: {traceback.format_exc ()}")
        sys.exit (1)

    logger.info ("Программа завершена")


if __name__ == "__main__":
    main ()