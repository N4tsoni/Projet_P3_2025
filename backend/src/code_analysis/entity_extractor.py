"""
Extracteur d'entités et relations pour le knowledge graph de code.
Construit les relations entre classes, fonctions, variables, etc.
"""

from typing import List, Dict, Set, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, field

from src.models.code_entities import (
    ProjectModel,
    ModuleModel,
    ClassModel,
    FunctionModel,
    VariableModel,
    ImportModel,
    PackageModel,
    ContainsRelation,
    ImportsRelation,
    InheritsRelation,
    CallsRelation,
    UsesRelation,
    Language,
)
from src.code_analysis.python_parser import parse_python_file, ParseResult


@dataclass
class CodeGraph:
    """
    Représente un knowledge graph de code complet.
    Contient toutes les entités et leurs relations.
    """
    # Entités
    project: ProjectModel
    modules: List[ModuleModel] = field(default_factory=list)
    classes: List[ClassModel] = field(default_factory=list)
    functions: List[FunctionModel] = field(default_factory=list)
    variables: List[VariableModel] = field(default_factory=list)
    imports: List[ImportModel] = field(default_factory=list)
    packages: List[PackageModel] = field(default_factory=list)

    # Relations
    contains_relations: List[ContainsRelation] = field(default_factory=list)
    imports_relations: List[ImportsRelation] = field(default_factory=list)
    inherits_relations: List[InheritsRelation] = field(default_factory=list)
    calls_relations: List[CallsRelation] = field(default_factory=list)
    uses_relations: List[UsesRelation] = field(default_factory=list)

    # Indices pour recherche rapide
    _class_index: Dict[str, ClassModel] = field(default_factory=dict, init=False, repr=False)
    _function_index: Dict[str, FunctionModel] = field(default_factory=dict, init=False, repr=False)
    _module_index: Dict[str, ModuleModel] = field(default_factory=dict, init=False, repr=False)

    def build_indices(self):
        """Construit les indices pour recherche rapide"""
        self._class_index = {cls.full_name: cls for cls in self.classes}
        self._function_index = {func.full_name: func for func in self.functions}
        self._module_index = {mod.name: mod for mod in self.modules}

    def get_class(self, full_name: str) -> Optional[ClassModel]:
        """Récupère une classe par son nom complet"""
        return self._class_index.get(full_name)

    def get_function(self, full_name: str) -> Optional[FunctionModel]:
        """Récupère une fonction par son nom complet"""
        return self._function_index.get(full_name)

    def get_module(self, name: str) -> Optional[ModuleModel]:
        """Récupère un module par son nom"""
        return self._module_index.get(name)


class CodeEntityExtractor:
    """
    Extracteur d'entités et relations pour construire un knowledge graph de code.
    """

    def __init__(self, project_path: str, project_name: str):
        self.project_path = Path(project_path)
        self.project_name = project_name

        # Tracking des entités et relations
        self.parse_results: List[ParseResult] = []
        self.packages: Dict[str, PackageModel] = {}

        # Tracking pour construire les relations
        self.function_calls: Dict[str, List[str]] = {}  # caller -> [callees]
        self.class_inheritance: Dict[str, List[str]] = {}  # class -> [parents]

    def extract_project(self) -> CodeGraph:
        """
        Extrait toutes les entités et relations d'un projet.

        Returns:
            CodeGraph contenant toutes les entités et relations
        """
        # Créer le modèle de projet
        project = ProjectModel(
            name=self.project_name,
            path=str(self.project_path),
            language=Language.PYTHON,
            version=self._extract_version(),
            description=self._extract_description(),
        )

        # Parser tous les fichiers Python du projet
        print(f"Analyzing project: {self.project_name}")
        self._parse_all_files()

        # Construire le graph
        graph = self._build_graph(project)

        print(f"Extracted: {len(graph.modules)} modules, {len(graph.classes)} classes, "
              f"{len(graph.functions)} functions")

        return graph

    def _parse_all_files(self):
        """Parse tous les fichiers Python du projet"""
        for py_file in self.project_path.rglob("*.py"):
            # Ignorer certains dossiers
            if self._should_ignore_path(py_file):
                continue

            try:
                result = parse_python_file(str(py_file))
                self.parse_results.append(result)

                # Tracker les appels de fonctions et l'héritage
                self._track_relationships(result)

                print(f"Parsed: {py_file.relative_to(self.project_path)}")
            except Exception as e:
                print(f"Error parsing {py_file}: {e}")

    def _should_ignore_path(self, path: Path) -> bool:
        """Vérifie si un chemin doit être ignoré"""
        ignore_patterns = {
            '.venv', 'venv', '__pycache__', '.git', '.pytest_cache',
            'build', 'dist', '.eggs', '*.egg-info', 'node_modules'
        }

        for part in path.parts:
            if part in ignore_patterns or part.startswith('.'):
                return True
        return False

    def _track_relationships(self, result: ParseResult):
        """Track les relations pour construction ultérieure du graph"""
        # Tracker l'héritage de classes
        for cls in result.classes:
            if cls.base_classes:
                self.class_inheritance[cls.full_name] = cls.base_classes

        # Note: Les appels de fonctions sont trackés dans le parser

    def _build_graph(self, project: ProjectModel) -> CodeGraph:
        """Construit le knowledge graph à partir des résultats de parsing"""
        graph = CodeGraph(project=project)

        # Collecter toutes les entités
        for result in self.parse_results:
            graph.modules.append(result.module)
            graph.classes.extend(result.classes)
            graph.functions.extend(result.functions)
            graph.variables.extend(result.variables)
            graph.imports.extend(result.imports)

        # Construire les indices
        graph.build_indices()

        # Extraire les packages externes
        self._extract_packages(graph)

        # Construire les relations
        self._build_contains_relations(graph)
        self._build_imports_relations(graph)
        self._build_inherits_relations(graph)
        # TODO: Implémenter calls et uses relations

        return graph

    def _extract_packages(self, graph: CodeGraph):
        """Extrait les packages externes depuis les imports"""
        package_usage: Dict[str, int] = {}

        for imp in graph.imports:
            # Extraire le package racine
            package_name = imp.module_name.split('.')[0]

            # Ignorer les imports relatifs et stdlib
            if package_name.startswith('.') or self._is_stdlib(package_name):
                continue

            # Compter les usages
            package_usage[package_name] = package_usage.get(package_name, 0) + 1

        # Créer les modèles de packages
        for name, count in package_usage.items():
            package = PackageModel(
                name=name,
                version=None,  # TODO: Extraire depuis requirements.txt ou pyproject.toml
                is_external=True,
                usage_count=count,
            )
            graph.packages.append(package)

    def _build_contains_relations(self, graph: CodeGraph):
        """Construit les relations CONTAINS (Project->Module, Module->Class, etc.)"""
        # Project CONTAINS Modules
        for i, module in enumerate(graph.modules):
            relation = ContainsRelation(
                source_id=graph.project.name,
                target_id=module.name,
                order=i,
            )
            graph.contains_relations.append(relation)

        # Module CONTAINS Classes
        for cls in graph.classes:
            module_name = cls.full_name.split('.')[0]
            if module := graph.get_module(module_name):
                relation = ContainsRelation(
                    source_id=module.name,
                    target_id=cls.full_name,
                )
                graph.contains_relations.append(relation)

        # Class/Module CONTAINS Functions
        for func in graph.functions:
            # Déterminer le conteneur (classe ou module)
            parts = func.full_name.split('.')
            if len(parts) >= 3 and func.is_method:
                # C'est une méthode: module.Class.method
                class_name = '.'.join(parts[:-1])
                if cls := graph.get_class(class_name):
                    relation = ContainsRelation(
                        source_id=class_name,
                        target_id=func.full_name,
                    )
                    graph.contains_relations.append(relation)
            else:
                # C'est une fonction au niveau module
                module_name = parts[0]
                if module := graph.get_module(module_name):
                    relation = ContainsRelation(
                        source_id=module.name,
                        target_id=func.full_name,
                    )
                    graph.contains_relations.append(relation)

    def _build_imports_relations(self, graph: CodeGraph):
        """Construit les relations IMPORTS"""
        for imp in graph.imports:
            # Trouver le module source
            # Note: Il faudrait tracker quel module a fait l'import
            # Pour l'instant on crée une relation basique

            relation = ImportsRelation(
                source_id="unknown",  # TODO: Tracker le module source
                target_id=imp.module_name,
                import_type=imp.import_type,
                line_number=imp.line_number,
            )
            graph.imports_relations.append(relation)

    def _build_inherits_relations(self, graph: CodeGraph):
        """Construit les relations INHERITS (Class->Class)"""
        for class_name, base_classes in self.class_inheritance.items():
            for i, base_class in enumerate(base_classes):
                # Résoudre le nom complet de la classe parent
                # (peut nécessiter de regarder les imports)
                parent_full_name = self._resolve_class_name(base_class, class_name, graph)

                relation = InheritsRelation(
                    source_id=class_name,
                    target_id=parent_full_name,
                    inheritance_order=i,
                    is_multiple=len(base_classes) > 1,
                )
                graph.inherits_relations.append(relation)

    def _resolve_class_name(self, class_name: str, context: str, graph: CodeGraph) -> str:
        """
        Résout le nom complet d'une classe en utilisant le contexte.
        Simplifié pour l'instant, devrait regarder les imports.
        """
        # Si déjà qualifié
        if '.' in class_name:
            return class_name

        # Chercher dans les classes connues
        module_name = context.split('.')[0]
        potential_name = f"{module_name}.{class_name}"

        if graph.get_class(potential_name):
            return potential_name

        # Sinon retourner tel quel (peut être une classe externe)
        return class_name

    def _is_stdlib(self, package_name: str) -> bool:
        """Vérifie si un package est dans la stdlib Python"""
        stdlib_modules = {
            'os', 'sys', 'ast', 'json', 'datetime', 'pathlib', 'typing',
            'collections', 'itertools', 'functools', 're', 'math', 'random',
            'io', 'logging', 'unittest', 'asyncio', 'dataclasses', 'enum',
            'abc', 'contextlib', 'time', 'copy', 'pickle', 'warnings',
            'inspect', 'importlib', 'argparse', 'subprocess', 'shutil',
        }
        return package_name in stdlib_modules

    def _extract_version(self) -> Optional[str]:
        """Tente d'extraire la version du projet depuis pyproject.toml ou __init__.py"""
        # TODO: Implémenter lecture de pyproject.toml ou __init__.py
        return None

    def _extract_description(self) -> Optional[str]:
        """Tente d'extraire la description depuis README ou pyproject.toml"""
        readme_path = self.project_path / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Prendre la première ligne non-vide qui n'est pas un titre
                    for line in lines:
                        stripped = line.strip()
                        if stripped and not stripped.startswith('#'):
                            return stripped[:200]  # Limiter à 200 chars
            except:
                pass
        return None


def extract_code_graph(project_path: str, project_name: Optional[str] = None) -> CodeGraph:
    """
    Extrait le knowledge graph d'un projet de code.

    Args:
        project_path: Chemin racine du projet
        project_name: Nom du projet (optionnel, déduit du chemin sinon)

    Returns:
        CodeGraph contenant toutes les entités et relations
    """
    if project_name is None:
        project_name = Path(project_path).name

    extractor = CodeEntityExtractor(project_path, project_name)
    return extractor.extract_project()
