"""
AST-based Python code parser for robust entity extraction.

Extracts:
- Functions (definitions, calls, decorators)
- Classes (definitions, inheritance, methods)
- Imports (modules, dependencies)
- Variables (global assignments)
- Docstrings and type hints
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json


@dataclass
class FunctionEntity:
    """Represents a Python function"""
    name: str
    file_path: str
    line_start: int
    line_end: int
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    decorators: List[str]
    calls: List[str]  # Functions this function calls
    docstring: Optional[str]
    complexity_hint: int  # Number of branches/loops
    is_async: bool
    is_method: bool  # True if inside a class


@dataclass
class ClassEntity:
    """Represents a Python class"""
    name: str
    file_path: str
    line_start: int
    line_end: int
    base_classes: List[str]
    methods: List[str]  # Method names
    decorators: List[str]
    docstring: Optional[str]
    attributes: List[str]  # Class/instance variables


@dataclass
class ImportEntity:
    """Represents an import statement"""
    module: str
    imported_names: List[str]  # Empty for 'import x', filled for 'from x import y'
    alias: Optional[str]  # For 'import x as y'
    file_path: str
    line_number: int
    is_stdlib: bool  # Heuristic: stdlib vs external


@dataclass
class ModuleEntity:
    """Represents a Python module (file)"""
    name: str
    file_path: str
    docstring: Optional[str]
    functions: List[FunctionEntity]
    classes: List[ClassEntity]
    imports: List[ImportEntity]
    global_variables: List[Dict[str, Any]]
    lines_of_code: int


class CodeParser:
    """AST-based parser for Python code"""

    # Known standard library modules (partial list)
    STDLIB_MODULES = {
        'os', 'sys', 'json', 'pathlib', 'typing', 're', 'datetime',
        'collections', 'itertools', 'functools', 'dataclasses', 'enum',
        'logging', 'argparse', 'subprocess', 'asyncio', 'io', 'time'
    }

    def parse_file(self, file_path: Path) -> Optional[ModuleEntity]:
        """Parse a single Python file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))

            module = ModuleEntity(
                name=file_path.stem,
                file_path=str(file_path),
                docstring=ast.get_docstring(tree),
                functions=[],
                classes=[],
                imports=[],
                global_variables=[],
                lines_of_code=len(content.splitlines())
            )

            # Extract top-level entities
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Only top-level functions (not methods)
                    if self._is_top_level(node, tree):
                        func = self._parse_function(node, file_path, is_method=False)
                        module.functions.append(func)

                elif isinstance(node, ast.ClassDef):
                    cls = self._parse_class(node, file_path, tree)
                    module.classes.append(cls)

                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    imports = self._parse_import(node, file_path)
                    module.imports.extend(imports)

                elif isinstance(node, ast.Assign) and self._is_top_level(node, tree):
                    # Global variable assignments
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            module.global_variables.append({
                                'name': target.id,
                                'line': node.lineno
                            })

            return module

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _is_top_level(self, node: ast.AST, tree: ast.Module) -> bool:
        """Check if a node is at module level (not nested)"""
        return node in tree.body

    def _parse_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        is_method: bool = False
    ) -> FunctionEntity:
        """Parse a function definition"""

        # Extract parameters
        params = []
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'annotation': ast.unparse(arg.annotation) if arg.annotation else None
            }
            params.append(param)

        # Extract return type
        return_type = ast.unparse(node.returns) if node.returns else None

        # Extract decorators
        decorators = [ast.unparse(dec) for dec in node.decorator_list]

        # Extract function calls made within this function
        calls = self._extract_calls(node)

        # Complexity hint: count branches and loops
        complexity = sum(1 for _ in ast.walk(node) if isinstance(_, (ast.If, ast.For, ast.While, ast.With)))

        return FunctionEntity(
            name=node.name,
            file_path=str(file_path),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parameters=params,
            return_type=return_type,
            decorators=decorators,
            calls=calls,
            docstring=ast.get_docstring(node),
            complexity_hint=complexity,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_method=is_method
        )

    def _parse_class(self, node: ast.ClassDef, file_path: Path, tree: ast.Module) -> ClassEntity:
        """Parse a class definition"""

        # Extract base classes
        bases = [ast.unparse(base) for base in node.bases]

        # Extract decorators
        decorators = [ast.unparse(dec) for dec in node.decorator_list]

        # Extract methods (function definitions inside the class)
        methods = []
        attributes = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                # Class variables
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)

        return ClassEntity(
            name=node.name,
            file_path=str(file_path),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            base_classes=bases,
            methods=methods,
            decorators=decorators,
            docstring=ast.get_docstring(node),
            attributes=attributes
        )

    def _parse_import(self, node: ast.Import | ast.ImportFrom, file_path: Path) -> List[ImportEntity]:
        """Parse import statements"""
        imports = []

        if isinstance(node, ast.Import):
            # import x, y, z
            for alias in node.names:
                module = alias.name
                imports.append(ImportEntity(
                    module=module,
                    imported_names=[],
                    alias=alias.asname,
                    file_path=str(file_path),
                    line_number=node.lineno,
                    is_stdlib=self._is_stdlib(module)
                ))

        elif isinstance(node, ast.ImportFrom):
            # from x import y, z
            module = node.module or ''
            imported = [alias.name for alias in node.names]
            imports.append(ImportEntity(
                module=module,
                imported_names=imported,
                alias=None,
                file_path=str(file_path),
                line_number=node.lineno,
                is_stdlib=self._is_stdlib(module)
            ))

        return imports

    def _extract_calls(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
        """Extract all function calls within a function"""
        calls = []

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Try to get the function name
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # For method calls like obj.method()
                    calls.append(child.func.attr)

        return list(set(calls))  # Deduplicate

    def _is_stdlib(self, module: str) -> bool:
        """Heuristic to determine if a module is from the standard library"""
        root_module = module.split('.')[0]
        return root_module in self.STDLIB_MODULES


def parse_python_directory(root_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Parse all Python files in a directory.

    Args:
        root_path: Root directory to search
        output_dir: Where to save extracted data

    Returns:
        Dictionary with all parsed modules
    """
    parser = CodeParser()
    modules = []

    # Find all Python files
    python_files = list(root_path.rglob('*.py'))

    print(f"Found {len(python_files)} Python files")

    for py_file in python_files:
        print(f"Parsing: {py_file.relative_to(root_path)}")
        module = parser.parse_file(py_file)
        if module:
            modules.append(module)

    # Create catalog
    catalog = {
        "metadata": {
            "root_path": str(root_path),
            "total_modules": len(modules),
            "total_functions": sum(len(m.functions) for m in modules),
            "total_classes": sum(len(m.classes) for m in modules),
            "total_imports": sum(len(m.imports) for m in modules),
        },
        "modules": [
            {
                "name": m.name,
                "file_path": m.file_path,
                "docstring": m.docstring,
                "lines_of_code": m.lines_of_code,
                "functions": [
                    {
                        "name": f.name,
                        "line_start": f.line_start,
                        "line_end": f.line_end,
                        "parameters": f.parameters,
                        "return_type": f.return_type,
                        "decorators": f.decorators,
                        "calls": f.calls,
                        "docstring": f.docstring,
                        "complexity_hint": f.complexity_hint,
                        "is_async": f.is_async,
                        "is_method": f.is_method
                    }
                    for f in m.functions
                ],
                "classes": [
                    {
                        "name": c.name,
                        "line_start": c.line_start,
                        "line_end": c.line_end,
                        "base_classes": c.base_classes,
                        "methods": c.methods,
                        "decorators": c.decorators,
                        "docstring": c.docstring,
                        "attributes": c.attributes
                    }
                    for c in m.classes
                ],
                "imports": [
                    {
                        "module": i.module,
                        "imported_names": i.imported_names,
                        "alias": i.alias,
                        "line_number": i.line_number,
                        "is_stdlib": i.is_stdlib
                    }
                    for i in m.imports
                ],
                "global_variables": m.global_variables
            }
            for m in modules
        ]
    }

    # Save to file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "code_entities.json"
    output_file.write_text(json.dumps(catalog, indent=2))

    print(f"\n✅ Extracted {catalog['metadata']['total_functions']} functions")
    print(f"✅ Extracted {catalog['metadata']['total_classes']} classes")
    print(f"✅ Extracted {catalog['metadata']['total_imports']} imports")
    print(f"✅ Saved to: {output_file}")

    return catalog


if __name__ == "__main__":
    # Test on tac-2
    root = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\tac-2")
    output = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\data\tac-2")

    catalog = parse_python_directory(root, output)

    # Print summary
    print("\n" + "="*60)
    print("CODE PARSING SUMMARY")
    print("="*60)
    for module in catalog['modules']:
        print(f"\n📄 {module['name']}.py ({module['lines_of_code']} lines)")
        if module['functions']:
            print(f"  Functions: {', '.join(f['name'] for f in module['functions'])}")
        if module['classes']:
            print(f"  Classes: {', '.join(c['name'] for c in module['classes'])}")
        if module['imports']:
            external_imports = [i for i in module['imports'] if not i['is_stdlib']]
            if external_imports:
                print(f"  External deps: {', '.join(i['module'] for i in external_imports)}")
