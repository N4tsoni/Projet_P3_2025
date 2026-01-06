"""
Modèles Pydantic pour les entités du knowledge graph de code.
Ces modèles représentent les différents éléments d'un codebase.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


# Enums pour les types

class Language(str, Enum):
    """Langages de programmation supportés"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    JAVA = "java"
    RUST = "rust"
    UNKNOWN = "unknown"


class AccessModifier(str, Enum):
    """Modificateurs d'accès"""
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


class Scope(str, Enum):
    """Portée d'une variable"""
    GLOBAL = "global"
    CLASS = "class"
    INSTANCE = "instance"
    LOCAL = "local"


class ImportType(str, Enum):
    """Type d'import"""
    STANDARD = "standard"
    THIRD_PARTY = "third_party"
    LOCAL = "local"


class CommentType(str, Enum):
    """Type de commentaire"""
    COMMENT = "comment"
    TODO = "todo"
    FIXME = "fixme"
    NOTE = "note"
    HACK = "hack"


class CodeBlockType(str, Enum):
    """Type de bloc de code"""
    IF = "if"
    FOR = "for"
    WHILE = "while"
    TRY = "try"
    WITH = "with"
    MATCH = "match"  # Python 3.10+
    SWITCH = "switch"  # JS/TS


# Modèles d'entités principales

class ProjectModel(BaseModel):
    """Représente un projet/repository de code"""
    name: str = Field(..., description="Nom du projet")
    path: str = Field(..., description="Chemin racine du projet")
    language: Language = Field(..., description="Langage principal")
    version: Optional[str] = Field(None, description="Version du projet")
    description: Optional[str] = Field(None, description="Description du projet")
    created_at: Optional[datetime] = Field(None, description="Date de création")
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Date d'analyse")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "my-project",
                "path": "/home/user/projects/my-project",
                "language": "python",
                "version": "1.0.0",
                "description": "Un super projet"
            }
        }


class ModuleModel(BaseModel):
    """Représente un fichier source (module)"""
    name: str = Field(..., description="Nom du module")
    path: str = Field(..., description="Chemin relatif du fichier")
    language: Language = Field(..., description="Langage du fichier")
    lines_of_code: int = Field(0, description="Nombre de lignes de code")
    docstring: Optional[str] = Field(None, description="Documentation du module")
    imports_count: int = Field(0, description="Nombre d'imports")
    complexity_score: Optional[float] = Field(None, description="Score de complexité")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "utils",
                "path": "src/utils.py",
                "language": "python",
                "lines_of_code": 150,
                "imports_count": 5
            }
        }


class ClassModel(BaseModel):
    """Représente une classe/type dans le code"""
    name: str = Field(..., description="Nom de la classe")
    full_name: str = Field(..., description="Nom qualifié complet (module.Class)")
    docstring: Optional[str] = Field(None, description="Documentation de la classe")
    line_start: int = Field(..., description="Ligne de début")
    line_end: int = Field(..., description="Ligne de fin")
    is_abstract: bool = Field(False, description="Est une classe abstraite")
    decorators: List[str] = Field(default_factory=list, description="Liste des décorateurs")
    access_modifier: AccessModifier = Field(AccessModifier.PUBLIC, description="Modificateur d'accès")
    base_classes: List[str] = Field(default_factory=list, description="Classes parentes")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "MyClass",
                "full_name": "module.MyClass",
                "line_start": 10,
                "line_end": 50,
                "decorators": ["dataclass"],
                "base_classes": ["BaseClass"]
            }
        }


class ParameterModel(BaseModel):
    """Représente un paramètre de fonction"""
    name: str = Field(..., description="Nom du paramètre")
    type_annotation: Optional[str] = Field(None, description="Annotation de type")
    default_value: Optional[str] = Field(None, description="Valeur par défaut")
    is_optional: bool = Field(False, description="Paramètre optionnel")
    is_variadic: bool = Field(False, description="*args ou **kwargs")


class FunctionModel(BaseModel):
    """Représente une fonction/méthode dans le code"""
    name: str = Field(..., description="Nom de la fonction")
    full_name: str = Field(..., description="Nom qualifié complet")
    docstring: Optional[str] = Field(None, description="Documentation de la fonction")
    signature: str = Field(..., description="Signature complète avec types")
    line_start: int = Field(..., description="Ligne de début")
    line_end: int = Field(..., description="Ligne de fin")
    is_async: bool = Field(False, description="Est une fonction asynchrone")
    is_generator: bool = Field(False, description="Est un générateur")
    is_method: bool = Field(False, description="Est une méthode de classe")
    is_static: bool = Field(False, description="Est une méthode statique")
    is_class_method: bool = Field(False, description="Est une méthode de classe (@classmethod)")
    parameters: List[ParameterModel] = Field(default_factory=list, description="Liste des paramètres")
    return_type: Optional[str] = Field(None, description="Type de retour")
    complexity: Optional[int] = Field(None, description="Complexité cyclomatique")
    decorators: List[str] = Field(default_factory=list, description="Liste des décorateurs")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "process_data",
                "full_name": "module.MyClass.process_data",
                "signature": "def process_data(self, data: List[str]) -> Dict[str, Any]",
                "line_start": 25,
                "line_end": 40,
                "is_method": True,
                "return_type": "Dict[str, Any]"
            }
        }


class VariableModel(BaseModel):
    """Représente une variable/constante dans le code"""
    name: str = Field(..., description="Nom de la variable")
    full_name: str = Field(..., description="Nom qualifié complet")
    type_annotation: Optional[str] = Field(None, description="Type de la variable")
    value: Optional[str] = Field(None, description="Valeur initiale (si constante)")
    is_constant: bool = Field(False, description="Est une constante (UPPER_CASE)")
    scope: Scope = Field(Scope.LOCAL, description="Portée de la variable")
    line_number: int = Field(..., description="Ligne de déclaration")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "API_KEY",
                "full_name": "config.API_KEY",
                "type_annotation": "str",
                "is_constant": True,
                "scope": "global"
            }
        }


class ImportModel(BaseModel):
    """Représente une déclaration d'import"""
    module_name: str = Field(..., description="Nom du module importé")
    imported_names: List[str] = Field(default_factory=list, description="Noms spécifiques importés")
    alias: Optional[str] = Field(None, description="Alias utilisé")
    is_relative: bool = Field(False, description="Import relatif ou absolu")
    import_type: ImportType = Field(ImportType.LOCAL, description="Type d'import")
    line_number: int = Field(..., description="Ligne de l'import")

    class Config:
        json_schema_extra = {
            "example": {
                "module_name": "datetime",
                "imported_names": ["datetime", "timedelta"],
                "import_type": "standard",
                "line_number": 3
            }
        }


class PackageModel(BaseModel):
    """Représente un package/dépendance externe"""
    name: str = Field(..., description="Nom du package")
    version: Optional[str] = Field(None, description="Version utilisée")
    is_external: bool = Field(True, description="Package externe ou interne")
    usage_count: int = Field(0, description="Nombre d'utilisations dans le projet")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "requests",
                "version": "2.31.0",
                "is_external": True,
                "usage_count": 15
            }
        }


class CommentModel(BaseModel):
    """Représente un commentaire ou TODO dans le code"""
    content: str = Field(..., description="Contenu du commentaire")
    type: CommentType = Field(CommentType.COMMENT, description="Type de commentaire")
    line_number: int = Field(..., description="Ligne du commentaire")
    author: Optional[str] = Field(None, description="Auteur (si extrait de git blame)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "TODO: Refactor this function",
                "type": "todo",
                "line_number": 42
            }
        }


class CodeBlockModel(BaseModel):
    """Représente un bloc de code significatif"""
    type: CodeBlockType = Field(..., description="Type de bloc (if, for, while, etc.)")
    condition: Optional[str] = Field(None, description="Condition (pour if/while)")
    line_start: int = Field(..., description="Ligne de début")
    line_end: int = Field(..., description="Ligne de fin")
    nesting_level: int = Field(0, description="Niveau d'imbrication")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "if",
                "condition": "x > 0",
                "line_start": 10,
                "line_end": 15,
                "nesting_level": 1
            }
        }


# Modèles de relations

class RelationshipModel(BaseModel):
    """Modèle de base pour une relation entre entités"""
    source_id: str = Field(..., description="ID de l'entité source")
    target_id: str = Field(..., description="ID de l'entité cible")
    relation_type: str = Field(..., description="Type de relation")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Propriétés de la relation")


class ContainsRelation(RelationshipModel):
    """Relation CONTAINS (Project->Module, Class->Method, etc.)"""
    relation_type: Literal["CONTAINS"] = "CONTAINS"
    order: Optional[int] = Field(None, description="Ordre de définition")


class ImportsRelation(RelationshipModel):
    """Relation IMPORTS (Module->Module/Package)"""
    relation_type: Literal["IMPORTS"] = "IMPORTS"
    import_type: ImportType = Field(..., description="Type d'import")
    line_number: int = Field(..., description="Ligne de l'import")


class InheritsRelation(RelationshipModel):
    """Relation INHERITS (Class->Class)"""
    relation_type: Literal["INHERITS"] = "INHERITS"
    inheritance_order: int = Field(0, description="Ordre dans la liste des parents")
    is_multiple: bool = Field(False, description="Héritage multiple")


class CallsRelation(RelationshipModel):
    """Relation CALLS (Function->Function)"""
    relation_type: Literal["CALLS"] = "CALLS"
    call_count: int = Field(1, description="Nombre d'appels estimé")
    is_recursive: bool = Field(False, description="Appel récursif")
    line_numbers: List[int] = Field(default_factory=list, description="Lignes où les appels sont faits")


class UsesRelation(RelationshipModel):
    """Relation USES (Function/Class->Variable/Class)"""
    relation_type: Literal["USES"] = "USES"
    usage_type: Literal["read", "write", "both"] = Field("read", description="Type d'utilisation")
    line_numbers: List[int] = Field(default_factory=list, description="Lignes d'utilisation")


# Modèles d'analyse

class ComplexityMetrics(BaseModel):
    """Métriques de complexité pour une entité"""
    cyclomatic_complexity: Optional[int] = Field(None, description="Complexité cyclomatique")
    cognitive_complexity: Optional[int] = Field(None, description="Complexité cognitive")
    nesting_depth: Optional[int] = Field(None, description="Profondeur d'imbrication max")
    lines_of_code: int = Field(0, description="Lignes de code")


class QualityMetrics(BaseModel):
    """Métriques de qualité pour un projet/module"""
    code_duplication: Optional[float] = Field(None, description="Pourcentage de code dupliqué")
    test_coverage: Optional[float] = Field(None, description="Couverture de tests estimée")
    documentation_coverage: Optional[float] = Field(None, description="% de fonctions documentées")
    maintainability_index: Optional[float] = Field(None, description="Indice de maintenabilité")


class AnalysisResult(BaseModel):
    """Résultat d'analyse d'un projet"""
    project: ProjectModel
    modules: List[ModuleModel]
    classes: List[ClassModel]
    functions: List[FunctionModel]
    variables: List[VariableModel]
    imports: List[ImportModel]
    packages: List[PackageModel]
    complexity_metrics: ComplexityMetrics
    quality_metrics: QualityMetrics
    analyzed_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "project": {"name": "my-project", "path": "/path/to/project", "language": "python"},
                "modules": [],
                "classes": [],
                "functions": [],
                "analyzed_at": "2025-01-01T00:00:00"
            }
        }
