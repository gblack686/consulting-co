"""
Multi-layered knowledge graph builder using networkx.

Creates relationship networks between:
- Prompts (DELEGATES_TO)
- Code (CALLS, IMPORTS, DEFINES)
- Configs (USES_ENV, DEPENDS_ON)
- Concepts (DEMONSTRATES, IMPLEMENTS)
"""

import json
import networkx as nx
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from pyvis.network import Network


@dataclass
class RelationshipType:
    """Define relationship types and their properties"""
    name: str
    color: str
    weight: float
    description: str


# Relationship type definitions
RELATIONSHIP_TYPES = {
    # Code relationships (syntactic)
    'CALLS': RelationshipType('CALLS', '#FF6B6B', 1.0, 'Function calls another function'),
    'IMPORTS': RelationshipType('IMPORTS', '#4ECDC4', 0.8, 'Module imports another module'),
    'DEFINES': RelationshipType('DEFINES', '#45B7D1', 0.7, 'Class defines method'),
    'INHERITS': RelationshipType('INHERITS', '#96CEB4', 0.9, 'Class inherits from parent'),
    'DECORATES': RelationshipType('DECORATES', '#FFEAA7', 0.6, 'Decorator applied to function'),

    # Document relationships (semantic)
    'DELEGATES_TO': RelationshipType('DELEGATES_TO', '#DDA15E', 1.0, 'Prompt delegates to another prompt'),
    'INVOKES': RelationshipType('INVOKES', '#BC6C25', 0.9, 'Script invokes prompt'),
    'REFERENCES': RelationshipType('REFERENCES', '#B5838D', 0.5, 'Document references another'),

    # Infrastructure relationships
    'USES_ENV': RelationshipType('USES_ENV', '#6A994E', 0.7, 'Uses environment variable'),
    'DEPENDS_ON': RelationshipType('DEPENDS_ON', '#A7C957', 0.8, 'Depends on external package'),
    'CONFIGURED_BY': RelationshipType('CONFIGURED_BY', '#F2E8CF', 0.6, 'Configured by config file'),

    # Conceptual relationships (semantic)
    'DEMONSTRATES': RelationshipType('DEMONSTRATES', '#E63946', 1.0, 'Code demonstrates concept'),
    'IMPLEMENTS': RelationshipType('IMPLEMENTS', '#F1FAEE', 0.9, 'Implements tactic/pattern'),
    'SIMILAR_TO': RelationshipType('SIMILAR_TO', '#A8DADC', 0.4, 'Semantically similar'),
    'EXPLAINED_IN': RelationshipType('EXPLAINED_IN', '#457B9D', 0.7, 'Explained in transcript'),
}


class KnowledgeGraphBuilder:
    """Build multi-layered knowledge graph from extracted entities"""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.node_types = {}  # Track node type for each node

    def load_data(self, data_dir: Path) -> None:
        """Load all extracted entity data"""
        print("Loading data from:", data_dir)

        # Load prompts
        prompts_file = data_dir / "prompts.json"
        if prompts_file.exists():
            prompts = json.loads(prompts_file.read_text())
            self._add_prompt_nodes(prompts)
            self._add_prompt_edges(prompts)

        # Load code entities
        code_file = data_dir / "code_entities.json"
        if code_file.exists():
            code_data = json.loads(code_file.read_text())
            self._add_code_nodes(code_data)
            self._add_code_edges(code_data)

        # Load configs
        config_file = data_dir / "config_entities.json"
        if config_file.exists():
            config_data = json.loads(config_file.read_text())
            self._add_config_nodes(config_data)
            self._add_config_edges(config_data)

        # Load concepts (if available)
        concepts_file = data_dir.parent / "lesson-2" / "concepts.json"
        if concepts_file.exists():
            concepts = json.loads(concepts_file.read_text())
            self._add_concept_nodes(concepts)

        # Load semantic matches (if available)
        semantic_file = data_dir.parent / "semantic" / "semantic_matches.json"
        if semantic_file.exists():
            semantic_data = json.loads(semantic_file.read_text())
            self._add_semantic_edges(semantic_data)

    def _add_prompt_nodes(self, prompts: List[Dict[str, Any]]) -> None:
        """Add prompt entities as nodes"""
        for prompt in prompts:
            node_id = f"prompt:{prompt['name']}"
            self.graph.add_node(
                node_id,
                label=prompt['name'],
                type='Prompt',
                prompt_type=prompt['prompt_type'],
                file_path=prompt['file_path'],
                color='#FF6B6B',
                size=20
            )
            self.node_types[node_id] = 'Prompt'

    def _add_prompt_edges(self, prompts: List[Dict[str, Any]]) -> None:
        """Add delegation relationships between prompts"""
        for prompt in prompts:
            source = f"prompt:{prompt['name']}"

            # Add DELEGATES_TO edges
            for delegation in prompt['delegations']:
                target = f"prompt:{delegation}"
                if target in self.graph.nodes:
                    rel = RELATIONSHIP_TYPES['DELEGATES_TO']
                    self.graph.add_edge(
                        source,
                        target,
                        type=rel.name,
                        color=rel.color,
                        weight=rel.weight,
                        title=rel.description
                    )

    def _add_code_nodes(self, code_data: Dict[str, Any]) -> None:
        """Add code entities (modules, functions, classes) as nodes"""
        for module in code_data['modules']:
            # Add module node
            module_id = f"module:{module['name']}"
            self.graph.add_node(
                module_id,
                label=module['name'],
                type='Module',
                file_path=module['file_path'],
                lines_of_code=module['lines_of_code'],
                color='#4ECDC4',
                size=15
            )
            self.node_types[module_id] = 'Module'

            # Add function nodes
            for func in module['functions']:
                func_id = f"function:{module['name']}.{func['name']}"
                self.graph.add_node(
                    func_id,
                    label=func['name'],
                    type='Function',
                    module=module['name'],
                    line_start=func['line_start'],
                    complexity=func['complexity_hint'],
                    is_async=func['is_async'],
                    color='#45B7D1',
                    size=12
                )
                self.node_types[func_id] = 'Function'

                # DEFINES relationship: module defines function
                rel = RELATIONSHIP_TYPES['DEFINES']
                self.graph.add_edge(
                    module_id,
                    func_id,
                    type=rel.name,
                    color=rel.color,
                    weight=rel.weight
                )

            # Add class nodes
            for cls in module['classes']:
                cls_id = f"class:{module['name']}.{cls['name']}"
                self.graph.add_node(
                    cls_id,
                    label=cls['name'],
                    type='Class',
                    module=module['name'],
                    line_start=cls['line_start'],
                    color='#96CEB4',
                    size=14
                )
                self.node_types[cls_id] = 'Class'

                # DEFINES relationship: module defines class
                rel = RELATIONSHIP_TYPES['DEFINES']
                self.graph.add_edge(
                    module_id,
                    cls_id,
                    type=rel.name,
                    color=rel.color,
                    weight=rel.weight
                )

    def _add_code_edges(self, code_data: Dict[str, Any]) -> None:
        """Add code relationship edges (calls, imports)"""
        for module in code_data['modules']:
            module_id = f"module:{module['name']}"

            # Add IMPORTS edges
            for imp in module['imports']:
                target_module = f"module:{imp['module']}"
                # Only add edge if target exists in our graph
                if target_module in self.graph.nodes:
                    rel = RELATIONSHIP_TYPES['IMPORTS']
                    self.graph.add_edge(
                        module_id,
                        target_module,
                        type=rel.name,
                        color=rel.color,
                        weight=rel.weight
                    )

            # Add CALLS edges
            for func in module['functions']:
                func_id = f"function:{module['name']}.{func['name']}"

                for called_func in func['calls']:
                    # Try to find the called function in the graph
                    # This is a simple heuristic - could be improved
                    for node in self.graph.nodes:
                        if node.startswith('function:') and called_func in node:
                            rel = RELATIONSHIP_TYPES['CALLS']
                            self.graph.add_edge(
                                func_id,
                                node,
                                type=rel.name,
                                color=rel.color,
                                weight=rel.weight
                            )
                            break

    def _add_config_nodes(self, config_data: Dict[str, Any]) -> None:
        """Add configuration entities as nodes"""
        # Add environment variable nodes
        for env_var in config_data['env_vars']:
            node_id = f"env:{env_var['name']}"
            self.graph.add_node(
                node_id,
                label=env_var['name'],
                type='EnvVar',
                required=env_var['required'],
                color='#6A994E',
                size=10
            )
            self.node_types[node_id] = 'EnvVar'

        # Add MCP server nodes
        for server in config_data['mcp_servers']:
            node_id = f"mcp:{server['name']}"
            self.graph.add_node(
                node_id,
                label=server['name'],
                type='MCPServer',
                command=server['command'],
                color='#DDA15E',
                size=16
            )
            self.node_types[node_id] = 'MCPServer'

    def _add_config_edges(self, config_data: Dict[str, Any]) -> None:
        """Add configuration relationship edges"""
        # Add USES_ENV edges from MCP servers to env vars
        for server in config_data['mcp_servers']:
            server_id = f"mcp:{server['name']}"
            for env_key in server['env_vars'].keys():
                env_id = f"env:{env_key}"
                if env_id in self.graph.nodes:
                    rel = RELATIONSHIP_TYPES['USES_ENV']
                    self.graph.add_edge(
                        server_id,
                        env_id,
                        type=rel.name,
                        color=rel.color,
                        weight=rel.weight
                    )

    def _add_concept_nodes(self, concepts_data: Dict[str, Any]) -> None:
        """Add concept entities as nodes"""
        for concept in concepts_data.get('concepts', []):
            node_id = f"concept:{concept['name']}"
            self.graph.add_node(
                node_id,
                label=concept['name'],
                type='Concept',
                category=concept['category'],
                definition=concept.get('definition', ''),
                color='#E63946',
                size=18
            )
            self.node_types[node_id] = 'Concept'

    def _add_semantic_edges(self, semantic_data: Dict[str, Any]) -> None:
        """Add DEMONSTRATES_CONCEPT edges from semantic matching"""
        for match in semantic_data.get('matches', []):
            # Build source node ID based on type
            source_type = match['source_type']
            source_name = match['source_name']

            if source_type == 'prompt':
                source_id = f"prompt:{source_name}"
            elif source_type == 'function':
                # Functions are stored as "function:module.function_name"
                # We need to find the matching function node
                source_id = None
                for node in self.graph.nodes:
                    if node.startswith('function:') and source_name in node:
                        source_id = node
                        break
            else:
                continue  # Unknown source type

            # Build target concept node ID
            target_id = f"concept:{match['concept_name']}"

            # Add edge if both nodes exist
            if source_id and source_id in self.graph.nodes and target_id in self.graph.nodes:
                rel = RELATIONSHIP_TYPES['DEMONSTRATES']
                self.graph.add_edge(
                    source_id,
                    target_id,
                    type=rel.name,
                    color=rel.color,
                    weight=rel.weight,
                    title=f"{rel.description} (similarity: {match['similarity_score']})",
                    similarity=match['similarity_score'],
                    confidence=match['confidence']
                )

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        node_counts = {}
        for node_type in set(self.node_types.values()):
            node_counts[node_type] = sum(1 for nt in self.node_types.values() if nt == node_type)

        edge_counts = {}
        for _, _, data in self.graph.edges(data=True):
            edge_type = data.get('type', 'Unknown')
            edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_counts': node_counts,
            'edge_counts': edge_counts,
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph)
        }

    def save_graph(self, output_file: Path) -> None:
        """Save graph to file"""
        data = nx.node_link_data(self.graph)
        output_file.write_text(json.dumps(data, indent=2))
        print(f"Graph saved to: {output_file}")

    def visualize_interactive(self, output_file: Path, height: str = "750px") -> None:
        """Create interactive HTML visualization using pyvis"""
        net = Network(height=height, width="100%", directed=True, notebook=False)

        # Copy nodes and edges from networkx graph
        for node, data in self.graph.nodes(data=True):
            net.add_node(
                node,
                label=data.get('label', node),
                color=data.get('color', '#97C2FC'),
                size=data.get('size', 10),
                title=f"Type: {data.get('type', 'Unknown')}"
            )

        for source, target, data in self.graph.edges(data=True):
            net.add_edge(
                source,
                target,
                color=data.get('color', '#848484'),
                title=data.get('title', data.get('type', '')),
                arrows='to'
            )

        # Configure physics
        net.set_options("""
        {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -30000,
              "springLength": 150,
              "springConstant": 0.04
            },
            "minVelocity": 0.75
          }
        }
        """)

        net.save_graph(str(output_file))
        print(f"Interactive visualization saved to: {output_file}")


def build_knowledge_graph(data_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Build complete knowledge graph from all entity data.

    Args:
        data_dir: Directory containing extracted entity JSON files
        output_dir: Where to save graph outputs

    Returns:
        Graph statistics
    """
    builder = KnowledgeGraphBuilder()

    # Load all data
    builder.load_data(data_dir)

    # Get statistics
    stats = builder.get_statistics()

    # Save graph
    output_dir.mkdir(parents=True, exist_ok=True)
    builder.save_graph(output_dir / "knowledge_graph.json")

    # Create interactive visualization
    builder.visualize_interactive(output_dir / "knowledge_graph.html")

    return stats


if __name__ == "__main__":
    # Build graph from tac-2 data
    data_dir = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\data\tac-2")
    output_dir = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\graphs")

    print("Building knowledge graph...")
    stats = build_knowledge_graph(data_dir, output_dir)

    print("\n" + "="*60)
    print("KNOWLEDGE GRAPH STATISTICS")
    print("="*60)
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Total edges: {stats['total_edges']}")
    print(f"Graph density: {stats['density']:.4f}")
    print(f"Is connected: {stats['is_connected']}")

    print("\nNode counts by type:")
    for node_type, count in stats['node_counts'].items():
        print(f"  {node_type}: {count}")

    print("\nEdge counts by type:")
    for edge_type, count in stats['edge_counts'].items():
        print(f"  {edge_type}: {count}")
