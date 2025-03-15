# CodeFixer - Automated Python Code Repair Using LLM

## Project Overview

CodeFixer is a tool for automatic analysis and fixing of errors in Python code using Large Language Models (LLM) via the OpenRouter API. The tool identifies syntax and logical errors, coding style issues, and potential vulnerabilities, then suggests and applies corrections.

## Key Features

- Automatic detection and fixing of syntax errors
- Correction of logical errors and suboptimal solutions
- Improvement of coding style according to PEP 8
- Addition of exception handling in problematic areas
- Creation of file backups before making changes
- Support for various models through OpenRouter

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/codefixer.git
cd codefixer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your API key:
```
OPENROUTER_API_KEY=your_api_key
```

## Usage

To analyze and fix a file:

```bash
python main.py path_to_file.py
```

With additional parameters:

```bash
python main.py path_to_file.py --model="anthropic/claude-3-haiku-20240307" --debug
```

### Command Line Parameters

- `file` - path to the file to check (required parameter)
- `--model` - LLM model to use (default: mistralai/mistral-small-24b-instruct-2501)
- `--debug` - enable debug mode with detailed logging

## Technical Details

### System Architecture

CodeFixer employs an innovative approach to interacting with language models through prompt-tools. Instead of using the standard OpenAI functions API, it uses a prompt engineering system that allows:

1. Formulating requests to the model with instructions for code analysis
2. Processing model responses, extracting structured data
3. Applying suggested changes to files with validity checking

### Workflow

1. Reading the source code of the Python file
2. Creating a specialized prompt for the language model
3. Sending a request to the LLM via OpenRouter API
4. Processing the response and extracting JSON with suggested changes
5. Checking and filtering changes
6. Creating a backup of the original file
7. Applying changes to the file
8. Outputting a report on the fixes made

### Types of Corrections

CodeFixer supports three types of changes:

- `replace` - replacing a part of the code
- `insert` - inserting new code
- `delete` - removing a part of the code

## Prompt Tools

Starting from version 2.0, CodeFixer uses a prompt-tools system for more flexible interaction with LLM. This allows:

1. Breaking down complex tasks into sequential steps
2. Performing deeper code analysis
3. Supporting an interactive analysis process
4. Ensuring compatibility with various models

Prompt tools in CodeFixer include:

- `analyze_code()` - analyzes the provided code and finds issues
- `suggest_fixes()` - suggests fixes for the identified problems
- `format_changes()` - formats the suggested fixes into a JSON structure

## Limitations

- Accuracy of fixes depends on the model used
- Complex logical errors may require manual verification
- Some specific code features or non-standard libraries might not be recognized

## Configuration

You can configure the following parameters at the beginning of the `main.py` file:

- `DEFAULT_MODEL` - default model for code analysis
- `SITE_URL` - your site URL (for OpenRouter statistics)
- `SITE_NAME` - your project # CodeFixer - Автоматическое исправление Python-кода с помощью LLM

## Описание проекта

CodeFixer - это инструмент для автоматического анализа и исправления ошибок в Python-коде с использованием больших языковых моделей (LLM) через API OpenRouter. Инструмент находит синтаксические и логические ошибки, проблемы стиля кодирования и потенциальные уязвимости, затем предлагает и применяет исправления.

## Основные возможности

- Автоматическое обнаружение и исправление синтаксических ошибок
- Исправление логических ошибок и неоптимальных решений
- Улучшение стиля кодирования согласно PEP 8
- Добавление обработки исключений в проблемных местах
- Создание резервных копий файлов перед внесением изменений
- Поддержка различных моделей через OpenRouter

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/codefixer.git
cd codefixer
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта и добавьте в него ключ API:
```
OPENROUTER_API_KEY=ваш_ключ_api
```

## Использование

Для анализа и исправления файла:

```bash
python main.py путь_к_файлу.py
```

С дополнительными параметрами:

```bash
python main.py путь_к_файлу.py --model="anthropic/claude-3-haiku-20240307" --debug
```

### Параметры командной строки

- `file` - путь к файлу для проверки (обязательный параметр)
- `--model` - модель LLM для использования (по умолчанию: mistralai/mistral-small-24b-instruct-2501)
- `--debug` - включение режима отладки с подробным логированием

## Технические детали

### Архитектура системы

CodeFixer использует инновационный подход к взаимодействию с языковыми моделями через промпт-инструменты. Вместо стандартного API функций OpenAI используется система промпт-инжиниринга, которая позволяет:

1. Формировать запросы к модели с инструкциями по анализу кода
2. Обрабатывать ответы модели, извлекая структурированные данные
3. Применять предложенные изменения к файлам с проверкой валидности

### Процесс работы

1. Чтение исходного кода Python-файла
2. Формирование специального промпта для языковой модели
3. Отправка запроса к LLM через OpenRouter API
4. Обработка ответа и извлечение JSON с предложенными изменениями
5. Проверка и фильтрация изменений
6. Создание резервной копии исходного файла
7. Применение изменений к файлу
8. Вывод отчета о выполненных исправлениях

### Типы исправлений

CodeFixer поддерживает три типа изменений:

- `replace` - замена части кода
- `insert` - вставка нового кода
- `delete` - удаление части кода

## Промпт-инструменты

Начиная с версии 2.0, CodeFixer использует систему промпт-инструментов для более гибкого взаимодействия с LLM. Это позволяет:

1. Разбивать сложные задачи на последовательные шаги
2. Выполнять более глубокий анализ кода
3. Поддерживать интерактивный процесс анализа
4. Обеспечивать совместимость с различными моделями

Промпт-инструменты в CodeFixer включают:

- `analyze_code()` - анализирует предоставленный код и находит проблемы
- `suggest_fixes()` - предлагает исправления для найденных проблем
- `format_changes()` - форматирует предложенные исправления в структуру JSON

## Ограничения

- Точность исправлений зависит от используемой модели
- Для сложных логических ошибок может потребоваться ручная проверка
- Некоторые специфические особенности кода или нестандартные библиотеки могут быть не распознаны

## Настройка и конфигурация

Вы можете настроить следующие параметры в начале файла `main.py`:

- `DEFAULT_MODEL` - модель по умолчанию для анализа кода
- `SITE_URL` - URL вашего сайта (для статистики OpenRouter)
- `SITE_NAME` - название вашего проекта (для статистики OpenRouter)

## Вклад в проект

Мы приветствуем вклад в проект! Если у вас есть предложения по улучшению или вы нашли ошибку:

1. Создайте issue с описанием проблемы или предложения
2. Сделайте fork репозитория и создайте ветку для ваших изменений
3. Внесите изменения и создайте pull request

## Лицензия

Этот проект распространяется под лицензией MIT. Подробная информация в файле LICENSE.name (for OpenRouter statistics)

## Contributing

We welcome contributions to the project! If you have suggestions for improvements or have found a bug:

1. Create an issue describing the problem or suggestion
2. Fork the repository and create a branch for your changes
3. Make changes and create a pull request

## License

This project is distributed under the MIT license. Detailed information can be found in the LICENSE file.