"""
Parser Python utilisant AST pour extraire les entités de code.
Analyse un fichier Python et extrait classes, fonctions, variables, imports, etc.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

from src.models.code_entities import (
    ModuleModel,
    ClassModel,
    FunctionModel,
    VariableModel,
    ImportModel,
    ParameterModel,
    CommentModel,
    Language,
    AccessModifier,
    Scope,
    ImportType,
    CommentType,
)


@dataclass
class ParseResult:
    """Résultat de l'analyse d'un fichier Python"""
    module: ModuleModel
    classes: List[ClassModel] = field(default_factory=list)
    functions: List[FunctionModel] = field(default_factory=list)
    variables: List[VariableModel] = field(default_factory=list)
    imports: List[ImportModel] = field(default_factory=list)
    comments: List[CommentModel] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class PythonCodeParser(ast.NodeVisitor):
    """
    Visiteur AST pour extraire les entités d'un fichier Python.
    Utilise le pattern Visitor pour parcourir l'arbre syntaxique.
    """

    def __init__(self, file_path: str, module_name: str):
        self.file_path = file_path
        self.module_name = module_name
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None

        # Collections d'entités extraites
        self.classes: List[ClassModel] = []
        self.functions: List[FunctionModel] = []
        self.variables: List[VariableModel] = []
        self.imports: List[ImportModel] = []
        self.comments: List[CommentModel] = []

        # Tracking pour les appels de fonctions
        self.function_calls: Dict[str, List[str]] = {}  # function -> [called_functions]

        # Tracking pour l'utilisation de variables/classes
        self.variable_usage: Dict[str, Set[str]] = {}  # variable -> {using_contexts}

    def parse_file(self) -> ParseResult:
        """
        Parse un fichier Python et extrait toutes les entités.

        Returns:
            ParseResult contenant toutes les entités extraites
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Parse le code en AST
            tree = ast.parse(source_code, filename=self.file_path)

            # Visite l'arbre AST
            self.visit(tree)

            # Extraire le docstring du module
            module_docstring = ast.get_docstring(tree)

            # Compter les lignes de code (sans commentaires/lignes vides)
            loc = self._count_lines_of_code(source_code)

            # Créer le modèle de module
            module = ModuleModel(
                name=self.module_name,
                path=self.file_path,
                language=Language.PYTHON,
                lines_of_code=loc,
                docstring=module_docstring,
                imports_count=len(self.imports),
            )

            return ParseResult(
                module=module,
                classes=self.classes,
                functions=self.functions,
                variables=self.variables,
                imports=self.imports,
                comments=self.comments,
                errors=[]
            )

        except SyntaxError as e:
            return ParseResult(
                module=ModuleModel(
                    name=self.module_name,
                    path=self.file_path,
                    language=Language.PYTHON,
                ),
                errors=[f"Syntax error: {str(e)}"]
            )
        except Exception as e:
            return ParseResult(
                module=ModuleModel(
                    name=self.module_name,
                    path=self.file_path,
                    language=Language.PYTHON,
                ),
                errors=[f"Parse error: {str(e)}"]
            )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visite une définition de classe"""
        # Construire le nom complet
        if self.current_class:
            full_name = f"{self.module_name}.{self.current_class}.{node.name}"
        else:
            full_name = f"{self.module_name}.{node.name}"

        # Extraire les décorateurs
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        # Extraire les classes de base
        base_classes = [self._get_name(base) for base in node.bases]

        # Déterminer si c'est une classe abstraite
        is_abstract = any('ABC' in base or 'abstractmethod' in dec
                         for base in base_classes
                         for dec in decorators)

        # Extraire le docstring
        docstring = ast.get_docstring(node)

        # Créer le modèle de classe
        class_model = ClassModel(
            name=node.name,
            full_name=full_name,
            docstring=docstring,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            is_abstract=is_abstract,
            decorators=decorators,
            access_modifier=self._get_access_modifier(node.name),
            base_classes=base_classes,
        )

        self.classes.append(class_model)

        # Visiter les méthodes de la classe
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visite une définition de fonction ou méthode"""
        self._process_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visite une définition de fonction asynchrone"""
        self._process_function(node, is_async=True)

    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool) -> None:
        """Traite une définition de fonction (sync ou async)"""
        # Construire le nom complet
        if self.current_class:
            full_name = f"{self.module_name}.{self.current_class}.{node.name}"
            is_method = True
        else:
            full_name = f"{self.module_name}.{node.name}"
            is_method = False

        # Extraire les décorateurs
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        # Déterminer le type de méthode
        is_static = 'staticmethod' in decorators
        is_class_method = 'classmethod' in decorators

        # Extraire les paramètres
        parameters = self._extract_parameters(node.args)

        # Extraire le type de retour
        return_type = self._get_annotation(node.returns) if node.returns else None

        # Extraire le docstring
        docstring = ast.get_docstring(node)

        # Construire la signature
        params_str = ", ".join([self._format_parameter(p) for p in parameters])
        signature = f"{'async ' if is_async else ''}def {node.name}({params_str})"
        if return_type:
            signature += f" -> {return_type}"

        # Calculer la complexité cyclomatique
        complexity = self._calculate_complexity(node)

        # Créer le modèle de fonction
        function_model = FunctionModel(
            name=node.name,
            full_name=full_name,
            docstring=docstring,
            signature=signature,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            is_async=is_async,
            is_generator=self._is_generator(node),
            is_method=is_method,
            is_static=is_static,
            is_class_method=is_class_method,
            parameters=parameters,
            return_type=return_type,
            complexity=complexity,
            decorators=decorators,
        )

        self.functions.append(function_model)

        # Visiter le corps de la fonction pour extraire les appels
        old_function = self.current_function
        self.current_function = full_name
        self.function_calls[full_name] = []
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visite une assignation de variable"""
        # Extraire les variables globales et attributs de classe
        if not self.current_function:  # Seulement au niveau module/classe
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    full_name = f"{self.module_name}.{var_name}"

                    if self.current_class:
                        full_name = f"{self.module_name}.{self.current_class}.{var_name}"
                        scope = Scope.CLASS
                    else:
                        scope = Scope.GLOBAL

                    # Déterminer si c'est une constante (convention: UPPER_CASE)
                    is_constant = var_name.isupper()

                    # Essayer d'extraire le type si annoté
                    type_annotation = None
                    if hasattr(node, 'annotation') and node.annotation:
                        type_annotation = self._get_annotation(node.annotation)

                    # Essayer d'extraire la valeur pour les constantes simples
                    value = None
                    if is_constant and isinstance(node.value, ast.Constant):
                        value = str(node.value.value)

                    variable_model = VariableModel(
                        name=var_name,
                        full_name=full_name,
                        type_annotation=type_annotation,
                        value=value,
                        is_constant=is_constant,
                        scope=scope,
                        line_number=node.lineno,
                    )

                    self.variables.append(variable_model)

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visite une assignation avec annotation de type"""
        if not self.current_function and isinstance(node.target, ast.Name):
            var_name = node.target.id
            full_name = f"{self.module_name}.{var_name}"

            if self.current_class:
                full_name = f"{self.module_name}.{self.current_class}.{var_name}"
                scope = Scope.CLASS
            else:
                scope = Scope.GLOBAL

            type_annotation = self._get_annotation(node.annotation)
            is_constant = var_name.isupper()

            value = None
            if node.value and isinstance(node.value, ast.Constant):
                value = str(node.value.value)

            variable_model = VariableModel(
                name=var_name,
                full_name=full_name,
                type_annotation=type_annotation,
                value=value,
                is_constant=is_constant,
                scope=scope,
                line_number=node.lineno,
            )

            self.variables.append(variable_model)

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visite un import simple (import x, import x as y)"""
        for alias in node.names:
            import_model = ImportModel(
                module_name=alias.name,
                imported_names=[],  # Import complet du module
                alias=alias.asname,
                is_relative=False,
                import_type=self._determine_import_type(alias.name),
                line_number=node.lineno,
            )
            self.imports.append(import_model)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visite un import from (from x import y)"""
        module_name = node.module or ""
        imported_names = [alias.name for alias in node.names]

        # Gérer les imports relatifs
        is_relative = node.level > 0
        if is_relative:
            module_name = "." * node.level + module_name

        import_model = ImportModel(
            module_name=module_name,
            imported_names=imported_names,
            alias=None,
            is_relative=is_relative,
            import_type=self._determine_import_type(module_name),
            line_number=node.lineno,
        )
        self.imports.append(import_model)

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visite un appel de fonction"""
        if self.current_function:
            called_func = self._get_name(node.func)
            if called_func:
                self.function_calls[self.current_function].append(called_func)

        self.generic_visit(node)

    # Méthodes utilitaires

    def _extract_parameters(self, args: ast.arguments) -> List[ParameterModel]:
        """Extrait les paramètres d'une fonction"""
        parameters = []

        # Arguments positionnels
        for i, arg in enumerate(args.args):
            param = ParameterModel(
                name=arg.arg,
                type_annotation=self._get_annotation(arg.annotation) if arg.annotation else None,
                default_value=None,
                is_optional=False,
                is_variadic=False,
            )

            # Vérifier si le paramètre a une valeur par défaut
            defaults_offset = len(args.args) - len(args.defaults)
            if i >= defaults_offset:
                default_idx = i - defaults_offset
                if default_idx < len(args.defaults):
                    param.default_value = ast.unparse(args.defaults[default_idx])
                    param.is_optional = True

            parameters.append(param)

        # *args
        if args.vararg:
            parameters.append(ParameterModel(
                name=f"*{args.vararg.arg}",
                type_annotation=self._get_annotation(args.vararg.annotation) if args.vararg.annotation else None,
                is_variadic=True,
            ))

        # Keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            default_value = None
            if i < len(args.kw_defaults) and args.kw_defaults[i]:
                default_value = ast.unparse(args.kw_defaults[i])

            parameters.append(ParameterModel(
                name=arg.arg,
                type_annotation=self._get_annotation(arg.annotation) if arg.annotation else None,
                default_value=default_value,
                is_optional=default_value is not None,
            ))

        # **kwargs
        if args.kwarg:
            parameters.append(ParameterModel(
                name=f"**{args.kwarg.arg}",
                type_annotation=self._get_annotation(args.kwarg.annotation) if args.kwarg.annotation else None,
                is_variadic=True,
            ))

        return parameters

    def _format_parameter(self, param: ParameterModel) -> str:
        """Formate un paramètre pour la signature"""
        result = param.name
        if param.type_annotation and not param.is_variadic:
            result += f": {param.type_annotation}"
        if param.default_value:
            result += f" = {param.default_value}"
        return result

    def _get_annotation(self, annotation: ast.expr) -> str:
        """Extrait une annotation de type sous forme de string"""
        try:
            return ast.unparse(annotation)
        except:
            return str(annotation)

    def _get_name(self, node: ast.expr) -> str:
        """Extrait le nom d'un nœud (Name, Attribute, etc.)"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        else:
            try:
                return ast.unparse(node)
            except:
                return ""

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extrait le nom d'un décorateur"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return self._get_name(decorator.func)
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        else:
            return str(decorator)

    def _get_access_modifier(self, name: str) -> AccessModifier:
        """Détermine le modificateur d'accès basé sur les conventions Python"""
        if name.startswith('__') and not name.endswith('__'):
            return AccessModifier.PRIVATE
        elif name.startswith('_'):
            return AccessModifier.PROTECTED
        else:
            return AccessModifier.PUBLIC

    def _determine_import_type(self, module_name: str) -> ImportType:
        """Détermine si un import est standard, third-party ou local"""
        # Liste des modules standard Python
        stdlib_modules = {
            'os', 'sys', 'ast', 'json', 'datetime', 'pathlib', 'typing',
            'collections', 'itertools', 'functools', 're', 'math', 'random',
            'io', 'logging', 'unittest', 'asyncio', 'dataclasses', 'enum',
        }

        base_module = module_name.split('.')[0]

        if base_module in stdlib_modules:
            return ImportType.STANDARD
        elif module_name.startswith('.') or module_name.startswith('src.'):
            return ImportType.LOCAL
        else:
            return ImportType.THIRD_PARTY

    def _is_generator(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Vérifie si une fonction est un générateur (contient yield)"""
        for child in ast.walk(node):
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                return True
        return False

    def _calculate_complexity(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """
        Calcule la complexité cyclomatique d'une fonction.
        Complexité = nombre de chemins d'exécution = 1 + nombre de décisions
        """
        complexity = 1

        for child in ast.walk(node):
            # Points de décision qui augmentent la complexité
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # and/or dans les conditions
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1

        return complexity

    def _count_lines_of_code(self, source_code: str) -> int:
        """Compte les lignes de code (sans lignes vides et commentaires)"""
        lines = source_code.split('\n')
        loc = 0

        for line in lines:
            stripped = line.strip()
            # Ignorer les lignes vides et les commentaires
            if stripped and not stripped.startswith('#'):
                loc += 1

        return loc


def parse_python_file(file_path: str) -> ParseResult:
    """
    Parse un fichier Python et extrait toutes les entités.

    Args:
        file_path: Chemin du fichier Python à analyser

    Returns:
        ParseResult contenant toutes les entités extraites
    """
    # Déterminer le nom du module
    module_name = Path(file_path).stem

    parser = PythonCodeParser(file_path, module_name)
    return parser.parse_file()


def parse_python_project(project_path: str) -> List[ParseResult]:
    """
    Parse tous les fichiers Python d'un projet.

    Args:
        project_path: Chemin racine du projet

    Returns:
        Liste de ParseResult pour chaque fichier Python
    """
    results = []
    project_root = Path(project_path)

    # Trouver tous les fichiers .py
    for py_file in project_root.rglob("*.py"):
        # Ignorer les fichiers dans venv, .venv, __pycache__, etc.
        if any(part.startswith('.') or part in ['venv', '__pycache__', 'build', 'dist']
               for part in py_file.parts):
            continue

        try:
            result = parse_python_file(str(py_file))
            results.append(result)
        except Exception as e:
            print(f"Error parsing {py_file}: {e}")

    return results
