import re
from fastapi import HTTPException
from typing import List, Dict, Tuple
import os

def parse_tool_file(file_content: str) -> Tuple[Dict[str, str], List[str]]:

    try:
        # Try to compile the code to check syntax
        compile(file_content, '<string>', 'exec')
        
        # Basic validation checks
        if 'class' not in file_content:
            raise HTTPException(status_code=400, detail="File must contain a tool class definition")
        
        imports = _fetch_imports(file_content)
        _install_imports(imports)
        tools = _fetch_tools(file_content)

        return tools, imports
        
    except SyntaxError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Python syntax in tool file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error validating tool file: {str(e)}"
        )

def _fetch_tools(file_content: str) -> Dict[str, str]:
    tool_pattern = re.compile(r'^\s*def\s+(\w+)\s*\((.*?)\)\s*(?:->\s*\w+\s*)?:$')
    tools = {}
    for line in file_content.split('\n'):
        match = tool_pattern.match(line)
        if match:
            # Get function name and start line number
            func_name = match.group(1).strip()
            lines = file_content.split('\n')
            for i, line in enumerate(lines):
                if match.string == line:
                    # Found the function definition line
                    # Collect lines until next def or end of file
                    indent = len(line) - len(line.lstrip())
                    # Remove (self, from the line if it exists
                    line = line.replace('(self, ', '(')
                    func_lines = [line[indent:]]  # Add current line with indent removed
                    j = i + 1
                    while j < len(lines) and not lines[j].lstrip().startswith('def '):
                        func_lines.append(lines[j][indent:])
                        j += 1
                    tools[func_name] = '\n'.join(func_lines)
                    break

    # Remove special methods and private methods
    tools = {k: v for k, v in tools.items() if not k.startswith('_')}
    return tools


def _fetch_imports(file_content: str) -> List[str]:
    import_pattern = re.compile(r'^\s*(from\s+[\w.]+\s+)?import\s+(?:[\w\s,]+|\*|\w+(?:\s+as\s+\w+)?(?:\s*,\s*\w+(?:\s+as\s+\w+)?)*)')
    imports = []
    for line in file_content.split('\n'):
        match = import_pattern.match(line)
        if match:
            imports.append(line)
    return imports


def _install_imports(imports: List[str]):
    import subprocess
    import sys
    import pkg_resources

    for import_str in imports:
        # Handle both 'import x' and 'from y import x' cases
        if 'from' in import_str:
            # For 'from y import x' format
            package, imports = import_str.split('import')
            package = package.replace('from', '').strip()
            import_parts = [package for p in imports.split(',')]
        else:
            # For 'import x' format
            _, imports = import_str.split('import')
            import_parts = [p.strip().split(' as ')[0] for p in imports.split(',')]
        for import_part in import_parts:
            import_part = import_part.strip()
            if import_part:
                try:
                    # Try importing first
                    exec(f"import {import_part}")
                except ImportError:
                    # If import fails, try installing with pip
                    print(f"Installing {import_part}...")
                    try:
                        try:
                            # Try installing with --user flag to avoid permission issues
                            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", import_part])
                        except (OSError, subprocess.CalledProcessError):
                            # If user install fails, check and create .local directory
                            local_dir = os.path.expanduser('~/.local')
                            if not os.path.exists(local_dir):
                                os.makedirs(local_dir, exist_ok=True)
                                os.chmod(local_dir, 0o700)  # Set proper permissions
                            try:
                                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", import_part])
                            except (OSError, subprocess.CalledProcessError):
                                print("Error: Failed to install package. Try manually installing with:")
                                print(f"pip install {import_part} --user")
                                raise ImportError(f"Failed to install package {import_part}")
                        # Try importing again after install
                        exec(f"import {import_part}")
                    except subprocess.CalledProcessError:
                        raise ImportError(f"Failed to install package {import_part}")