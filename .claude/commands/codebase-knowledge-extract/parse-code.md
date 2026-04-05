# Parse Code

Extract code entities using AST-based Python analysis.

## What This Does

Analyzes all `.py` files in the target repository using Python's `ast` module to extract:
- **Modules**: Python files with metadata
- **Functions**: Signatures, parameters, return types, decorators, calls
- **Classes**: Inheritance, methods, attributes
- **Imports**: Module dependencies (stdlib vs external)
- **Complexity hints**: Branch/loop counts per function

## Run

```bash
cd tac-learning-system
python parser/code_parser.py
```

## Output

Saves to: `tac-learning-system/data/tac-2/code_entities.json`

## Expected Results

- Full AST parse of all Python files
- Function call chains mapped
- Import dependencies tracked
- Type annotations extracted
- Decorator patterns identified

## Example Output

```json
{
  "modules": [
    {
      "name": "server",
      "functions": [
        {
          "name": "upload_file",
          "parameters": [{"name": "file", "annotation": "UploadFile"}],
          "return_type": "FileUploadResponse",
          "decorators": ["app.post('/api/upload')"],
          "calls": ["convert_csv_to_sqlite", "HTTPException"],
          "complexity_hint": 2,
          "is_async": true
        }
      ],
      "classes": [...],
      "imports": [...]
    }
  ]
}
```

## Metadata Extracted

- Lines of code per module
- Function complexity (branch/loop count)
- Async function detection
- Method vs function classification
- Docstrings
