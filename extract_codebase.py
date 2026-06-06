import ast
import json
import logging
from pathlib import Path
from typing import Iterator, Dict, Optional, Any, Union
from tqdm import tqdm

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

class CodeExtractor(ast.NodeVisitor):
    """
    A custom AST visitor that tracks class hierarchy to extract context-rich 
    method names (e.g., 'ClassName.method_name') alongside standalone functions.
    """
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.pairs: list[Dict[str, str]] = []
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Track the class context before diving into its methods
        prev_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        # Restore context after exiting the class
        self.current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node)
        self.generic_visit(node)

    def _process_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> None:
        name = getattr(node, "name", "")
        
        # Skip private/internal methods, but keep __init__
        if name.startswith("_") and name != "__init__":
            return

        # ast.get_docstring handles dedenting and basic cleanup
        docstring = ast.get_docstring(node, clean=True)
        if not docstring:
            return

        # Extract only the primary summary (first logical block)
        clean_docstring = docstring.split("\n\n")[0].strip()
        
        # Stricter filter: Ignore trivial or overly short docstrings
        if len(clean_docstring) < 15:  
            return

        try:
            # Extract the raw source code
            code_snippet = ast.get_source_segment(self.source_code, node)
            if not code_snippet:
                return

            # Prepend class name if the function is a method
            full_name = f"{self.current_class}.{name}" if self.current_class else name

            self.pairs.append({
                "function_name": full_name,
                "docstring": clean_docstring,
                "code": code_snippet.strip()
            })
        except Exception as e:
            # Catch segment extraction failures without breaking the whole file
            logger.debug(f"Failed to extract source for {name}: {e}")


def process_file(file_path: Path) -> Iterator[Dict[str, str]]:
    """Reads a file and yields extracted code pairs efficiently."""
    try:
        # errors="replace" ensures strict UTF-8 doesn't crash on bad bytes
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        
        extractor = CodeExtractor(source)
        extractor.visit(tree)
        
        yield from extractor.pairs
        
    except SyntaxError:
        logger.debug(f"Syntax error skipped in: {file_path}")
    except Exception as e:
        logger.warning(f"Unexpected error processing {file_path}: {e}")


def main(repo_dir: str, output_file: str) -> None:
    repo_path = Path(repo_dir)
    out_path = Path(output_file)

    if not repo_path.exists() or not repo_path.is_dir():
        logger.error(f"Repository directory '{repo_dir}' not found.")
        return

    exclude_dirs = {"tests", "benchmarks", "docs", ".git", "build", "scripts"}

    logger.info(f"Scanning {repo_dir} for Python files...")
    
    # Efficient path traversal filtering out unwanted directories
    python_files = [
        p for p in repo_path.rglob("*.py") 
        if not any(part in exclude_dirs for part in p.parts)
    ]

    logger.info(f"Found {len(python_files)} target Python files. Starting extraction...")

    # Ensure output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total_extracted = 0
    
    # Stream writes directly to disk to minimize RAM usage
    with out_path.open("w", encoding="utf-8") as f:
        for file_path in tqdm(python_files, desc="Parsing ASTs"):
            for pair in process_file(file_path):
                f.write(json.dumps(pair) + "\n")
                total_extracted += 1

    logger.info(f"Successfully extracted {total_extracted} code-docstring pairs to {output_file}")


if __name__ == "__main__":
    # Point this to your cloned pandas directory
    main(repo_dir="./pandas", output_file="pandas_dataset.jsonl")