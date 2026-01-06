"""
Intégrateur Graphiti pour peupler Neo4j avec le knowledge graph de code.
Utilise Graphiti pour gérer le graphe de connaissances du code source.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode, EpisodicNode
from graphiti_core.edges import EntityEdge

from src.code_analysis.entity_extractor import CodeGraph, extract_code_graph
from src.models.code_entities import (
    ProjectModel,
    ModuleModel,
    ClassModel,
    FunctionModel,
    VariableModel,
    PackageModel,
)


class CodeGraphitiIntegrator:
    """
    Intégrateur Graphiti pour le knowledge graph de code.
    Convertit les entités de code en nodes/edges Graphiti et les stocke dans Neo4j.
    """

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        openai_api_key: Optional[str] = None,
    ):
        """
        Initialise l'intégrateur Graphiti.

        Args:
            neo4j_uri: URI de connexion Neo4j
            neo4j_user: Utilisateur Neo4j
            neo4j_password: Mot de passe Neo4j
            openai_api_key: Clé API OpenAI pour les embeddings (optionnel)
        """
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.openai_api_key = openai_api_key

        # Client Graphiti (sera initialisé de manière asynchrone)
        self.graphiti: Optional[Graphiti] = None

    async def initialize(self):
        """Initialise la connexion Graphiti de manière asynchrone"""
        if self.graphiti is None:
            self.graphiti = Graphiti(
                uri=self.neo4j_uri,
                user=self.neo4j_user,
                password=self.neo4j_password,
            )
            await self.graphiti.build_indices_and_constraints()
            print("✅ Graphiti initialized and indices built")

    async def close(self):
        """Ferme la connexion Graphiti"""
        if self.graphiti:
            await self.graphiti.close()
            print("✅ Graphiti connection closed")

    async def populate_from_project(self, project_path: str, project_name: Optional[str] = None):
        """
        Analyse un projet et peuple Neo4j avec le knowledge graph via Graphiti.

        Args:
            project_path: Chemin racine du projet
            project_name: Nom du projet (optionnel)
        """
        await self.initialize()

        print(f"\n{'='*60}")
        print(f"Populating Neo4j with code graph from: {project_path}")
        print(f"{'='*60}\n")

        # Extraire le code graph
        print("1️⃣  Extracting code graph...")
        code_graph = extract_code_graph(project_path, project_name)

        # Créer un épisode pour ce projet
        print("2️⃣  Creating episode...")
        episode_id = await self._create_episode(code_graph.project)

        # Peupler les entités
        print("3️⃣  Populating entities...")
        await self._populate_entities(code_graph, episode_id)

        # Peupler les relations
        print("4️⃣  Populating relations...")
        await self._populate_relations(code_graph, episode_id)

        print(f"\n✅ Successfully populated Neo4j with {len(code_graph.classes)} classes, "
              f"{len(code_graph.functions)} functions, {len(code_graph.modules)} modules")

    async def _create_episode(self, project: ProjectModel) -> str:
        """
        Crée un épisode Graphiti pour le projet.
        Un épisode représente l'analyse d'un projet à un moment donné.
        """
        episode_content = (
            f"Code analysis of project '{project.name}' at {project.path}. "
            f"Language: {project.language.value}. "
            f"Analyzed at: {datetime.now().isoformat()}"
        )

        if project.description:
            episode_content += f" Description: {project.description}"

        # Créer l'épisode dans Graphiti
        episode = await self.graphiti.add_episode(
            name=f"code_analysis_{project.name}",
            episode_body=episode_content,
            source_description=f"Static code analysis of {project.name}",
            reference_time=datetime.now(),
        )

        print(f"   Created episode: {episode.name} (ID: {episode.uuid})")
        return str(episode.uuid)

    async def _populate_entities(self, code_graph: CodeGraph, episode_id: str):
        """Peuple les entités dans Graphiti"""
        # Project entity
        await self._add_project_entity(code_graph.project, episode_id)

        # Module entities
        for module in code_graph.modules:
            await self._add_module_entity(module, episode_id)

        # Class entities
        for cls in code_graph.classes:
            await self._add_class_entity(cls, episode_id)

        # Function entities
        for func in code_graph.functions:
            await self._add_function_entity(func, episode_id)

        # Package entities
        for pkg in code_graph.packages:
            await self._add_package_entity(pkg, episode_id)

        total_entities = (len(code_graph.modules) + len(code_graph.classes) +
                         len(code_graph.functions) + len(code_graph.packages) + 1)
        print(f"   Added {total_entities} entities")

    async def _add_project_entity(self, project: ProjectModel, episode_id: str):
        """Ajoute une entité Project"""
        fact = (
            f"Project '{project.name}' is a {project.language.value} project "
            f"located at {project.path}."
        )

        if project.description:
            fact += f" {project.description}"

        await self.graphiti.add_episode(
            name=f"project_{project.name}",
            episode_body=fact,
            source_description="Project metadata",
            reference_time=datetime.now(),
        )

    async def _add_module_entity(self, module: ModuleModel, episode_id: str):
        """Ajoute une entité Module"""
        fact = (
            f"Module '{module.name}' at {module.path} contains {module.lines_of_code} "
            f"lines of code and {module.imports_count} imports."
        )

        if module.docstring:
            fact += f" Documentation: {module.docstring[:200]}"

        await self.graphiti.add_episode(
            name=f"module_{module.name}",
            episode_body=fact,
            source_description=f"Module {module.path}",
            reference_time=datetime.now(),
        )

    async def _add_class_entity(self, cls: ClassModel, episode_id: str):
        """Ajoute une entité Class"""
        fact = f"Class '{cls.name}' is defined at lines {cls.line_start}-{cls.line_end}."

        if cls.base_classes:
            fact += f" It inherits from: {', '.join(cls.base_classes)}."

        if cls.is_abstract:
            fact += " It is an abstract class."

        if cls.decorators:
            fact += f" It uses decorators: {', '.join(cls.decorators)}."

        if cls.docstring:
            fact += f" Documentation: {cls.docstring[:200]}"

        await self.graphiti.add_episode(
            name=f"class_{cls.full_name}",
            episode_body=fact,
            source_description=f"Class {cls.full_name}",
            reference_time=datetime.now(),
        )

    async def _add_function_entity(self, func: FunctionModel, episode_id: str):
        """Ajoute une entité Function"""
        func_type = "method" if func.is_method else "function"
        if func.is_async:
            func_type = f"async {func_type}"

        fact = (
            f"The {func_type} '{func.name}' has signature: {func.signature}. "
            f"It is defined at lines {func.line_start}-{func.line_end}. "
            f"Complexity: {func.complexity}."
        )

        if func.parameters:
            param_names = [p.name for p in func.parameters]
            fact += f" Parameters: {', '.join(param_names)}."

        if func.return_type:
            fact += f" Returns: {func.return_type}."

        if func.decorators:
            fact += f" Decorators: {', '.join(func.decorators)}."

        if func.docstring:
            fact += f" Documentation: {func.docstring[:200]}"

        await self.graphiti.add_episode(
            name=f"function_{func.full_name}",
            episode_body=fact,
            source_description=f"Function {func.full_name}",
            reference_time=datetime.now(),
        )

    async def _add_package_entity(self, pkg: PackageModel, episode_id: str):
        """Ajoute une entité Package"""
        fact = (
            f"External package '{pkg.name}' is used {pkg.usage_count} times in the project."
        )

        if pkg.version:
            fact += f" Version: {pkg.version}."

        await self.graphiti.add_episode(
            name=f"package_{pkg.name}",
            episode_body=fact,
            source_description=f"Package {pkg.name}",
            reference_time=datetime.now(),
        )

    async def _populate_relations(self, code_graph: CodeGraph, episode_id: str):
        """Peuple les relations dans Graphiti"""
        # Pour l'instant, on utilise les facts narratifs dans les episodes
        # Les relations seront extraites automatiquement par Graphiti

        # Relations CONTAINS
        for rel in code_graph.contains_relations:
            fact = f"{rel.source_id} contains {rel.target_id}."
            await self.graphiti.add_episode(
                name=f"contains_{rel.source_id}_{rel.target_id}",
                episode_body=fact,
                source_description="CONTAINS relation",
                reference_time=datetime.now(),
            )

        # Relations INHERITS
        for rel in code_graph.inherits_relations:
            fact = f"Class {rel.source_id} inherits from {rel.target_id}."
            await self.graphiti.add_episode(
                name=f"inherits_{rel.source_id}_{rel.target_id}",
                episode_body=fact,
                source_description="INHERITS relation",
                reference_time=datetime.now(),
            )

        print(f"   Added {len(code_graph.contains_relations) + len(code_graph.inherits_relations)} relations")

    async def query_code_graph(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Interroge le knowledge graph de code avec une question en langage naturel.

        Args:
            query: Question en langage naturel
            num_results: Nombre de résultats à retourner

        Returns:
            Liste de faits pertinents du code graph
        """
        await self.initialize()

        print(f"\n🔍 Query: {query}")

        # Rechercher dans le graphe
        results = await self.graphiti.search(query, num_results=num_results)

        print(f"✅ Found {len(results)} results\n")

        formatted_results = []
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.name}")
            print(f"   {result.fact}")
            print(f"   Score: {result.score:.3f}\n")

            formatted_results.append({
                "name": result.name,
                "fact": result.fact,
                "score": result.score,
            })

        return formatted_results


async def populate_project_to_neo4j(
    project_path: str,
    project_name: Optional[str] = None,
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j",
    neo4j_password: str = "password",
):
    """
    Fonction utilitaire pour peupler Neo4j avec un projet.

    Args:
        project_path: Chemin du projet à analyser
        project_name: Nom du projet (optionnel)
        neo4j_uri: URI Neo4j
        neo4j_user: Utilisateur Neo4j
        neo4j_password: Mot de passe Neo4j
    """
    integrator = CodeGraphitiIntegrator(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
    )

    try:
        await integrator.populate_from_project(project_path, project_name)
    finally:
        await integrator.close()


async def query_code_knowledge(
    query: str,
    num_results: int = 5,
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j",
    neo4j_password: str = "password",
) -> List[Dict[str, Any]]:
    """
    Fonction utilitaire pour interroger le knowledge graph de code.

    Args:
        query: Question en langage naturel
        num_results: Nombre de résultats
        neo4j_uri: URI Neo4j
        neo4j_user: Utilisateur Neo4j
        neo4j_password: Mot de passe Neo4j

    Returns:
        Liste de résultats pertinents
    """
    integrator = CodeGraphitiIntegrator(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
    )

    try:
        results = await integrator.query_code_graph(query, num_results)
        return results
    finally:
        await integrator.close()


# Script principal pour tests
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Configuration Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

    # Chemin du projet à analyser
    PROJECT_PATH = str(Path(__file__).parent.parent.parent)
    PROJECT_NAME = "jarvis"

    async def main():
        """Fonction principale de test"""
        print("🚀 Starting Code Knowledge Graph Population")

        # 1. Peupler Neo4j
        await populate_project_to_neo4j(
            project_path=PROJECT_PATH,
            project_name=PROJECT_NAME,
            neo4j_uri=NEO4J_URI,
            neo4j_user=NEO4J_USER,
            neo4j_password=NEO4J_PASSWORD,
        )

        # 2. Tester des requêtes
        print("\n" + "="*60)
        print("Testing Queries")
        print("="*60)

        queries = [
            "What are the main classes in this project?",
            "Which functions have high complexity?",
            "What external packages are used?",
            "Show me functions related to voice processing",
        ]

        for query in queries:
            await query_code_knowledge(
                query=query,
                num_results=3,
                neo4j_uri=NEO4J_URI,
                neo4j_user=NEO4J_USER,
                neo4j_password=NEO4J_PASSWORD,
            )
            print()

    # Exécuter
    asyncio.run(main())
