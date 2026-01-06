"""
Script de test pour l'analyseur de code.
Permet de tester le parsing et l'extraction d'entités.
"""

import sys
from pathlib import Path
import json

# Ajouter le dossier parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.code_analysis.entity_extractor import extract_code_graph
from src.code_analysis.python_parser import parse_python_file


def test_parse_single_file(file_path: str):
    """
    Test du parsing d'un seul fichier.
    """
    print(f"\n{'='*60}")
    print(f"Testing single file: {file_path}")
    print(f"{'='*60}\n")

    result = parse_python_file(file_path)

    print(f"Module: {result.module.name}")
    print(f"  Path: {result.module.path}")
    print(f"  Lines of code: {result.module.lines_of_code}")
    print(f"  Imports: {result.module.imports_count}")

    if result.module.docstring:
        print(f"  Docstring: {result.module.docstring[:100]}...")

    print(f"\nClasses ({len(result.classes)}):")
    for cls in result.classes:
        print(f"  - {cls.name} (lines {cls.line_start}-{cls.line_end})")
        if cls.base_classes:
            print(f"    Inherits from: {', '.join(cls.base_classes)}")
        if cls.decorators:
            print(f"    Decorators: {', '.join(cls.decorators)}")

    print(f"\nFunctions ({len(result.functions)}):")
    for func in result.functions[:10]:  # Limiter à 10 pour la lisibilité
        method_type = "async " if func.is_async else ""
        method_type += "method" if func.is_method else "function"
        print(f"  - {func.name} ({method_type}, complexity: {func.complexity})")
        print(f"    Signature: {func.signature}")
        if func.parameters:
            params = ", ".join([p.name for p in func.parameters])
            print(f"    Parameters: {params}")

    print(f"\nVariables ({len(result.variables)}):")
    for var in result.variables[:10]:
        const_marker = " [CONSTANT]" if var.is_constant else ""
        print(f"  - {var.name}: {var.type_annotation or 'Any'} ({var.scope.value}){const_marker}")

    print(f"\nImports ({len(result.imports)}):")
    for imp in result.imports[:10]:
        if imp.imported_names:
            names = ', '.join(imp.imported_names)
            print(f"  - from {imp.module_name} import {names}")
        else:
            alias = f" as {imp.alias}" if imp.alias else ""
            print(f"  - import {imp.module_name}{alias}")

    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  - {error}")


def test_extract_project(project_path: str):
    """
    Test de l'extraction complète d'un projet.
    """
    print(f"\n{'='*60}")
    print(f"Testing project extraction: {project_path}")
    print(f"{'='*60}\n")

    graph = extract_code_graph(project_path)

    print(f"Project: {graph.project.name}")
    print(f"  Path: {graph.project.path}")
    print(f"  Language: {graph.project.language.value}")
    if graph.project.description:
        print(f"  Description: {graph.project.description[:100]}...")

    print(f"\nStatistics:")
    print(f"  Modules: {len(graph.modules)}")
    print(f"  Classes: {len(graph.classes)}")
    print(f"  Functions: {len(graph.functions)}")
    print(f"  Variables: {len(graph.variables)}")
    print(f"  Imports: {len(graph.imports)}")
    print(f"  External Packages: {len(graph.packages)}")

    print(f"\nRelations:")
    print(f"  CONTAINS: {len(graph.contains_relations)}")
    print(f"  IMPORTS: {len(graph.imports_relations)}")
    print(f"  INHERITS: {len(graph.inherits_relations)}")
    print(f"  CALLS: {len(graph.calls_relations)}")
    print(f"  USES: {len(graph.uses_relations)}")

    print(f"\nTop External Packages:")
    sorted_packages = sorted(graph.packages, key=lambda p: p.usage_count, reverse=True)
    for pkg in sorted_packages[:10]:
        print(f"  - {pkg.name}: {pkg.usage_count} usages")

    print(f"\nTop Complex Functions:")
    sorted_funcs = sorted(graph.functions, key=lambda f: f.complexity or 0, reverse=True)
    for func in sorted_funcs[:10]:
        print(f"  - {func.name}: complexity {func.complexity} (lines {func.line_start}-{func.line_end})")

    # Analyse de qualité
    total_funcs = len(graph.functions)
    documented_funcs = sum(1 for f in graph.functions if f.docstring)
    doc_coverage = (documented_funcs / total_funcs * 100) if total_funcs > 0 else 0

    print(f"\nQuality Metrics:")
    print(f"  Documentation coverage: {doc_coverage:.1f}% ({documented_funcs}/{total_funcs} functions)")

    avg_complexity = sum(f.complexity or 0 for f in graph.functions) / total_funcs if total_funcs > 0 else 0
    print(f"  Average complexity: {avg_complexity:.2f}")

    high_complexity = sum(1 for f in graph.functions if (f.complexity or 0) > 10)
    print(f"  High complexity functions (>10): {high_complexity}")


def export_graph_to_json(graph, output_path: str):
    """
    Exporte le graph en JSON pour inspection.
    """
    data = {
        "project": graph.project.dict(),
        "modules": [m.dict() for m in graph.modules],
        "classes": [c.dict() for c in graph.classes],
        "functions": [f.dict() for f in graph.functions[:100]],  # Limiter pour la taille
        "variables": [v.dict() for v in graph.variables[:100]],
        "packages": [p.dict() for p in graph.packages],
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)

    print(f"\nGraph exported to: {output_path}")


if __name__ == "__main__":
    # Test 1: Parser un seul fichier
    test_file = Path(__file__).parent / "python_parser.py"
    if test_file.exists():
        test_parse_single_file(str(test_file))

    # Test 2: Extraire le projet complet
    project_root = Path(__file__).parent.parent.parent
    test_extract_project(str(project_root))

    # Test 3: Exporter en JSON
    graph = extract_code_graph(str(project_root))
    output_file = project_root / "data" / "code_graph.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    export_graph_to_json(graph, str(output_file))

    print(f"\n{'='*60}")
    print("All tests completed!")
    print(f"{'='*60}\n")
