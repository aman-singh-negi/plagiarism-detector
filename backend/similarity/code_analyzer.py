import ast
import javalang
import clang.cindex
from difflib import SequenceMatcher
import re
from collections import defaultdict

class CodeAnalyzer:
    def __init__(self):
        self.cpp_parser = self._init_cpp_parser()
    
    def _init_cpp_parser(self):
        try:
            # Try to auto-locate libclang or use system default
            try:
                clang.cindex.Config.set_library_file('libclang.so')
            except:
                # Common paths for different operating systems
                paths = [
                    '/usr/lib/llvm-10/lib/libclang.so',  # Ubuntu
                    '/usr/local/opt/llvm/lib/libclang.dylib',  # macOS Homebrew
                    'C:\\Program Files\\LLVM\\bin\\libclang.dll'  # Windows
                ]
                for path in paths:
                    try:
                        clang.cindex.Config.set_library_file(path)
                        break
                    except:
                        continue
            return clang.cindex.Index.create()
        except Exception as e:
            print(f"Warning: C++ parser not available - {str(e)}")
            return None
    
    def compare(self, code1, code2, language):
        if language == 'python':
            result = self._compare_python(code1, code2)
        elif language == 'java':
            result = self._compare_java(code1, code2)
        elif language == 'cpp':
            try:
                result = self._compare_cpp(code1, code2)
            except ValueError as e:
                return {
                    'error': 'C++ analysis is not available on this server. Please install LLVM/Clang and set the correct path to libclang.',
                    'score': 0.0,
                    'details': {},
                    'matches': []
                }
        else:
            raise ValueError(f"Unsupported language: {language}")
        # Convert all floats to native Python float
        for k, v in result.items():
            if isinstance(v, (float, int)):
                result[k] = float(v)
            elif isinstance(v, list):
                result[k] = [float(x) if isinstance(x, (float, int)) else x for x in v]
        return result
    
    def _compare_python(self, code1, code2):
        try:
            metrics = {
                'ast_similarity': float(self._compare_ast(ast.parse(code1), ast.parse(code2))),
                'function_similarity': float(self._compare_functions(code1, code2)),
                'logic_similarity': float(self._compare_logic(code1, code2)),
                'variable_similarity': float(self._compare_variables(ast.parse(code1), ast.parse(code2))),
            }
            return {
                'details': metrics,
                'score': float(self._calculate_python_score(code1, code2)),
                'matches': self._find_code_matches(code1, code2)
            }
        except SyntaxError as e:
            raise ValueError(f"Python syntax error: {str(e)}")
    
    def _compare_java(self, code1, code2):
        try:
            metrics = self._get_java_metrics(code1, code2)
            return {
                'details': metrics,
                'score': float(self._calculate_java_score(code1, code2)),
                'matches': self._find_code_matches(code1, code2)
            }
        except javalang.parser.JavaSyntaxError as e:
            raise ValueError(f"Java syntax error: {str(e)}")
    
    def _compare_cpp(self, code1, code2):
        # Always return a warning for C++ analysis
        return {
            'details': {},
            'score': 0.0,
            'matches': [],
            'warning': 'C++ support is under development. Sorry for the inconvenience.'
        }
    
    def _compare_ast(self, tree1, tree2):
        """Compare Python AST structures using tree edit distance approximation"""
        def ast_to_sequence(node):
            if isinstance(node, ast.AST):
                return [type(node).__name__] + [
                    ast_to_sequence(x) 
                    for x in ast.iter_child_nodes(node)
                ]
            elif isinstance(node, list):
                return [ast_to_sequence(x) for x in node]
            return str(node)
        
        seq1 = str(ast_to_sequence(tree1))
        seq2 = str(ast_to_sequence(tree2))
        
        return SequenceMatcher(None, seq1, seq2).ratio()
    
    def _compare_functions(self, code1, code2):
        """Compare function signatures and structures"""
        def get_functions(code):
            try:
                tree = ast.parse(code)
                return [
                    (node.name, len(node.args.args))
                    for node in ast.walk(tree) 
                    if isinstance(node, ast.FunctionDef)
                ]
            except:
                return []
        
        funcs1 = get_functions(code1)
        funcs2 = get_functions(code2)
        
        if not funcs1 and not funcs2:
            return 1.0
        if not funcs1 or not funcs2:
            return 0.0
            
        # Count matching function signatures
        matches = sum(1 for f1 in funcs1 if f1 in funcs2)
        return matches / max(len(funcs1), len(funcs2))
    
    def _compare_variables(self, tree1, tree2):
        """Compare variable usage patterns"""
        def get_vars(tree):
            vars = defaultdict(int)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    vars[node.id] += 1
            return vars
        
        vars1 = get_vars(tree1)
        vars2 = get_vars(tree2)
        
        common = set(vars1.keys()) & set(vars2.keys())
        total = set(vars1.keys()) | set(vars2.keys())
        
        return len(common) / len(total) if total else 0
    
    def _compare_logic(self, code1, code2):
        """Compare normalized code logic (ignoring variable names)"""
        def normalize(code):
            # Remove comments
            code = re.sub(r'#.*', '', code)
            # Normalize strings
            code = re.sub(r'"[^"]*"', '"STR"', code)
            code = re.sub(r"'[^']*'", "'STR'", code)
            # Normalize numbers
            code = re.sub(r'\b\d+\b', '0', code)
            # Normalize variable names
            vars = {}
            counter = 1
            for match in re.finditer(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code):
                var = match.group()
                if var not in vars and var not in ('True', 'False', 'None', 'if', 'else', 'for', 'while'):
                    vars[var] = f'VAR{counter}'
                    counter += 1
            for var, replacement in vars.items():
                code = re.sub(r'\b' + var + r'\b', replacement, code)
            return code
        
        norm1 = normalize(code1)
        norm2 = normalize(code2)
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _find_code_matches(self, code1, code2, min_length=5):
        """Find matching code segments using sequence alignment"""
        lines1 = [line.strip() for line in code1.split('\n') if line.strip()]
        lines2 = [line.strip() for line in code2.split('\n') if line.strip()]
        
        matcher = SequenceMatcher(None, lines1, lines2)
        matches = []
        
        for match in matcher.get_matching_blocks():
            if match.size >= min_length:
                matches.append({
                    'text1_start': match.a,
                    'text1_end': match.a + match.size,
                    'text2_start': match.b,
                    'text2_end': match.b + match.size,
                    'similarity': 1.0  # Exact match in this simple implementation
                })
        
        return matches
    
    def _compare_java_classes(self, tree1, tree2):
        """Compare Java class structures"""
        def get_classes(tree):
            return [path.name for path in tree.types if isinstance(path, javalang.tree.ClassDeclaration)]
        
        classes1 = get_classes(tree1)
        classes2 = get_classes(tree2)
        
        if not classes1 and not classes2:
            return 1.0
        if not classes1 or not classes2:
            return 0.0
            
        common = set(classes1) & set(classes2)
        return len(common) / max(len(classes1), len(classes2))
    
    def _compare_java_methods(self, tree1, tree2):
        """Compare Java method signatures"""
        def get_methods(tree):
            methods = []
            for path in tree.types:
                if isinstance(path, javalang.tree.ClassDeclaration):
                    for member in path.body:
                        if isinstance(member, javalang.tree.MethodDeclaration):
                            methods.append((member.name, len(member.parameters)))
            return methods
        
        methods1 = get_methods(tree1)
        methods2 = get_methods(tree2)
        
        if not methods1 and not methods2:
            return 1.0
        if not methods1 or not methods2:
            return 0.0
            
        common = set(methods1) & set(methods2)
        return len(common) / max(len(methods1), len(methods2))
    
    def _compare_java_imports(self, tree1, tree2):
        """Compare Java import statements"""
        imports1 = {imp.path for imp in tree1.imports}
        imports2 = {imp.path for imp in tree2.imports}
        
        if not imports1 and not imports2:
            return 1.0
        if not imports1 or not imports2:
            return 0.0
            
        common = imports1 & imports2
        return len(common) / max(len(imports1), len(imports2))
    
    def _compare_cpp_ast(self, tu1, tu2):
        """Compare C++ AST structures"""
        def traverse(node, depth=0):
            if not node:
                return []
            result = [node.kind.name]
            for child in node.get_children():
                result.extend(traverse(child, depth+1))
            return result
        
        ast1 = traverse(tu1.cursor)
        ast2 = traverse(tu2.cursor)
        
        return SequenceMatcher(None, str(ast1), str(ast2)).ratio()
    
    def _compare_cpp_functions(self, code1, code2):
        """Compare C++ function signatures"""
        func_pattern = r'\b\w+\s+\w+\s*\([^)]*\)\s*(?:const)?\s*{'
        funcs1 = re.findall(func_pattern, code1)
        funcs2 = re.findall(func_pattern, code2)
        
        if not funcs1 and not funcs2:
            return 1.0
        if not funcs1 or not funcs2:
            return 0.0
            
        # Simple comparison of function counts
        return min(len(funcs1), len(funcs2)) / max(len(funcs1), len(funcs2))
    
    def _compare_cpp_includes(self, code1, code2):
        """Compare C++ include directives"""
        includes1 = set(re.findall(r'#include\s+[<"][^>"]+[>"]', code1))
        includes2 = set(re.findall(r'#include\s+[<"][^>"]+[>"]', code2))
        
        if not includes1 and not includes2:
            return 1.0
        if not includes1 or not includes2:
            return 0.0
            
        common = includes1 & includes2
        return len(common) / max(len(includes1), len(includes2))
    
    def _calculate_python_score(self, code1, code2):
        """Weighted average of Python analysis metrics"""
        metrics = self._compare_python(code1, code2)
        weights = {
            'ast_similarity': 0.4,
            'function_similarity': 0.3,
            'logic_similarity': 0.2,
            'variable_similarity': 0.1
        }
        return sum(metrics[k] * weights[k] for k in weights)
    
    def _calculate_java_score(self, code1, code2):
        """Weighted average of Java analysis metrics"""
        metrics = self._get_java_metrics(code1, code2)
        weights = {
            'class_similarity': 0.3,
            'method_similarity': 0.5,
            'import_similarity': 0.2
        }
        return sum(metrics[k] * weights[k] for k in weights)

    def _get_java_metrics(self, code1, code2):
        tree1 = javalang.parse.parse(code1)
        tree2 = javalang.parse.parse(code2)
        return {
            'class_similarity': float(self._compare_java_classes(tree1, tree2)),
            'method_similarity': float(self._compare_java_methods(tree1, tree2)),
            'import_similarity': float(self._compare_java_imports(tree1, tree2)),
        }
    
    def _calculate_cpp_score(self, code1, code2):
        """Weighted average of C++ analysis metrics"""
        metrics = self._compare_cpp(code1, code2)
        weights = {
            'ast_similarity': 0.4,
            'function_similarity': 0.4,
            'include_similarity': 0.2
        }
        return sum(metrics[k] * weights[k] for k in weights)