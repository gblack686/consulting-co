"""
Configuration parser for MCP servers, YAML configs, and environment files.

Extracts:
- MCP server definitions (.mcp.json)
- Tool configurations
- Environment variables
- YAML/JSON config files
"""

import json
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


@dataclass
class MCPServerEntity:
    """Represents an MCP server configuration"""
    name: str
    command: str
    args: List[str]
    env_vars: Dict[str, str]
    file_path: str
    tools: List[str]  # Will be populated if we can detect tool names


@dataclass
class ToolEntity:
    """Represents a tool/command definition"""
    name: str
    description: Optional[str]
    server: Optional[str]  # Which MCP server provides this
    parameters: Dict[str, Any]
    file_path: str


@dataclass
class EnvVarEntity:
    """Represents an environment variable"""
    name: str
    value: Optional[str]  # May be masked/hidden
    required: bool
    file_path: str
    used_by: List[str]  # Which servers/tools use this


@dataclass
class ConfigEntity:
    """Represents a configuration file"""
    name: str
    file_path: str
    config_type: str  # json, yaml, env, toml, etc.
    content: Dict[str, Any]
    settings: List[str]  # Top-level keys


class ConfigParser:
    """Parser for configuration files"""

    def parse_mcp_config(self, file_path: Path) -> List[MCPServerEntity]:
        """Parse .mcp.json file for server definitions"""
        try:
            config = json.loads(file_path.read_text(encoding='utf-8'))
            servers = []

            mcp_servers = config.get('mcpServers', {})

            for server_name, server_config in mcp_servers.items():
                server = MCPServerEntity(
                    name=server_name,
                    command=server_config.get('command', ''),
                    args=server_config.get('args', []),
                    env_vars=server_config.get('env', {}),
                    file_path=str(file_path),
                    tools=[]  # Will be populated later if tool definitions are found
                )
                servers.append(server)

            return servers

        except Exception as e:
            print(f"Error parsing MCP config {file_path}: {e}")
            return []

    def parse_yaml_config(self, file_path: Path) -> Optional[ConfigEntity]:
        """Parse YAML configuration file"""
        try:
            content = yaml.safe_load(file_path.read_text(encoding='utf-8'))

            if not isinstance(content, dict):
                return None

            return ConfigEntity(
                name=file_path.stem,
                file_path=str(file_path),
                config_type='yaml',
                content=content,
                settings=list(content.keys())
            )

        except Exception as e:
            print(f"Error parsing YAML {file_path}: {e}")
            return None

    def parse_json_config(self, file_path: Path) -> Optional[ConfigEntity]:
        """Parse JSON configuration file"""
        try:
            content = json.loads(file_path.read_text(encoding='utf-8'))

            if not isinstance(content, dict):
                return None

            return ConfigEntity(
                name=file_path.stem,
                file_path=str(file_path),
                config_type='json',
                content=content,
                settings=list(content.keys())
            )

        except Exception as e:
            print(f"Error parsing JSON {file_path}: {e}")
            return None

    def parse_env_file(self, file_path: Path) -> List[EnvVarEntity]:
        """Parse .env file for environment variables"""
        try:
            content = file_path.read_text(encoding='utf-8')
            env_vars = []

            for line in content.splitlines():
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE format
                match = re.match(r'^([A-Z_][A-Z0-9_]*)=(.*)$', line)
                if match:
                    key, value = match.groups()

                    # Mask sensitive values
                    masked_value = None
                    if any(sensitive in key.upper() for sensitive in ['KEY', 'SECRET', 'TOKEN', 'PASSWORD']):
                        masked_value = '***MASKED***'
                    else:
                        masked_value = value

                    env_vars.append(EnvVarEntity(
                        name=key,
                        value=masked_value,
                        required=True,  # Assume required if defined
                        file_path=str(file_path),
                        used_by=[]  # Will be populated later
                    ))

            return env_vars

        except Exception as e:
            print(f"Error parsing .env file {file_path}: {e}")
            return []

    def parse_package_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse package.json for Node.js dependencies"""
        try:
            content = json.loads(file_path.read_text(encoding='utf-8'))

            return {
                'name': content.get('name'),
                'version': content.get('version'),
                'dependencies': content.get('dependencies', {}),
                'devDependencies': content.get('devDependencies', {}),
                'scripts': content.get('scripts', {}),
                'file_path': str(file_path)
            }

        except Exception as e:
            print(f"Error parsing package.json {file_path}: {e}")
            return None

    def parse_requirements_txt(self, file_path: Path) -> List[str]:
        """Parse requirements.txt for Python dependencies"""
        try:
            content = file_path.read_text(encoding='utf-8')
            requirements = []

            for line in content.splitlines():
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Extract package name (before == or >=)
                package = re.split(r'[=<>!]', line)[0].strip()
                requirements.append(package)

            return requirements

        except Exception as e:
            print(f"Error parsing requirements.txt {file_path}: {e}")
            return []


def parse_config_directory(root_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Parse all configuration files in a directory.

    Args:
        root_path: Root directory to search
        output_dir: Where to save extracted data

    Returns:
        Dictionary with all parsed configs
    """
    parser = ConfigParser()

    mcp_servers = []
    yaml_configs = []
    json_configs = []
    env_vars = []
    dependencies = {
        'python': [],
        'node': {}
    }

    # Find MCP configs
    for mcp_file in root_path.rglob('.mcp.json'):
        print(f"Parsing MCP config: {mcp_file.relative_to(root_path)}")
        servers = parser.parse_mcp_config(mcp_file)
        mcp_servers.extend(servers)

    # Find YAML configs
    for yaml_file in root_path.rglob('*.yaml'):
        config = parser.parse_yaml_config(yaml_file)
        if config:
            yaml_configs.append(config)

    for yml_file in root_path.rglob('*.yml'):
        config = parser.parse_yaml_config(yml_file)
        if config:
            yaml_configs.append(config)

    # Find JSON configs (exclude package.json and .mcp.json)
    for json_file in root_path.rglob('*.json'):
        if json_file.name in ['package.json', '.mcp.json', 'package-lock.json']:
            continue
        config = parser.parse_json_config(json_file)
        if config:
            json_configs.append(config)

    # Find .env files
    for env_file in root_path.rglob('.env*'):
        if env_file.is_file():
            print(f"Parsing env file: {env_file.relative_to(root_path)}")
            vars = parser.parse_env_file(env_file)
            env_vars.extend(vars)

    # Find package.json
    for pkg_file in root_path.rglob('package.json'):
        print(f"Parsing package.json: {pkg_file.relative_to(root_path)}")
        pkg_data = parser.parse_package_json(pkg_file)
        if pkg_data:
            dependencies['node'] = pkg_data

    # Find requirements.txt
    for req_file in root_path.rglob('requirements.txt'):
        print(f"Parsing requirements.txt: {req_file.relative_to(root_path)}")
        reqs = parser.parse_requirements_txt(req_file)
        dependencies['python'].extend(reqs)

    # Create catalog
    catalog = {
        "metadata": {
            "root_path": str(root_path),
            "mcp_servers_count": len(mcp_servers),
            "yaml_configs_count": len(yaml_configs),
            "json_configs_count": len(json_configs),
            "env_vars_count": len(env_vars)
        },
        "mcp_servers": [
            {
                "name": s.name,
                "command": s.command,
                "args": s.args,
                "env_vars": s.env_vars,
                "file_path": s.file_path
            }
            for s in mcp_servers
        ],
        "yaml_configs": [
            {
                "name": c.name,
                "file_path": c.file_path,
                "settings": c.settings
            }
            for c in yaml_configs
        ],
        "json_configs": [
            {
                "name": c.name,
                "file_path": c.file_path,
                "settings": c.settings
            }
            for c in json_configs
        ],
        "env_vars": [
            {
                "name": v.name,
                "value": v.value,
                "required": v.required,
                "file_path": v.file_path
            }
            for v in env_vars
        ],
        "dependencies": dependencies
    }

    # Save to file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "config_entities.json"
    output_file.write_text(json.dumps(catalog, indent=2))

    print(f"\n✅ Extracted {len(mcp_servers)} MCP servers")
    print(f"✅ Extracted {len(yaml_configs)} YAML configs")
    print(f"✅ Extracted {len(json_configs)} JSON configs")
    print(f"✅ Extracted {len(env_vars)} environment variables")
    print(f"✅ Saved to: {output_file}")

    return catalog


if __name__ == "__main__":
    # Test on tac-2
    root = Path(r"C:\Users\gblac\OneDrive\Desktop\tac\tac-2")
    output = Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\tac-learning-system\data\tac-2")

    catalog = parse_config_directory(root, output)

    # Print summary
    print("\n" + "="*60)
    print("CONFIG PARSING SUMMARY")
    print("="*60)

    if catalog['mcp_servers']:
        print("\n🔧 MCP Servers:")
        for server in catalog['mcp_servers']:
            print(f"  - {server['name']}")
            print(f"    Command: {server['command']}")
            if server['env_vars']:
                print(f"    Env vars: {', '.join(server['env_vars'].keys())}")

    if catalog['dependencies']['python']:
        print(f"\n📦 Python Dependencies: {', '.join(catalog['dependencies']['python'][:10])}")
        if len(catalog['dependencies']['python']) > 10:
            print(f"    ... and {len(catalog['dependencies']['python']) - 10} more")

    if catalog['dependencies']['node'].get('dependencies'):
        node_deps = list(catalog['dependencies']['node']['dependencies'].keys())
        print(f"\n📦 Node Dependencies: {', '.join(node_deps[:10])}")
        if len(node_deps) > 10:
            print(f"    ... and {len(node_deps) - 10} more")
