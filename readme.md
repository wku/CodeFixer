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
- `SITE_NAME` - your project name (for OpenRouter statistics)

## Contributing

We welcome contributions to the project! If you have suggestions for improvements or have found a bug:

1. Create an issue describing the problem or suggestion
2. Fork the repository and create a branch for your changes
3. Make changes and create a pull request

## License

This project is distributed under the MIT license. Detailed information can be found in the LICENSE file.