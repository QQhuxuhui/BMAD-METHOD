"""BMAD Eight-Agent System - Configuration Loader.

This module handles loading and parsing YAML configuration files for the BMAD workflow.
It provides backward compatibility with existing workflow.yaml formats and supports
dynamic configuration of agents, models, and prompt templates.

Usage:
    config = load_workflow_config("config/workflow.yaml")
    node_mapping = map_yaml_to_nodes(config)
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
import logging

from app.core.langgraph.agents import (
    algorithm_expert_node,
    code_impl_expert_node,
    constraint_expert_node,
    domain_expert_node,
    extension_expert_node,
    objective_expert_node,
    orchestrator_node,
    quality_expert_node,
)
from app.core.langgraph.agents.approval_nodes import (
    p1_approval_node,
    p2_conflict_node,
    p25_approval_node,
)
from app.core.logging import logger


# Default agent node mapping
DEFAULT_NODE_MAPPING = {
    "orchestrator": orchestrator_node,
    "algorithm": algorithm_expert_node,
    "constraint": constraint_expert_node,
    "objective": objective_expert_node,
    "domain": domain_expert_node,
    "code_impl": code_impl_expert_node,
    "extension": extension_expert_node,
    "quality": quality_expert_node,
    "p1_approval": p1_approval_node,
    "p2_conflict": p2_conflict_node,
    "p25_approval": p25_approval_node,
}


def load_workflow_config(config_path: str) -> Dict[str, Any]:
    """Load workflow configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Dict[str, Any]: Parsed configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
        Exception: For other loading errors
    """
    try:
        config_file = Path(config_path)

        if not config_file.exists():
            logger.error("config_file_not_found", path=config_path)
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        logger.info("config_loaded_successfully", path=config_path)
        return config

    except yaml.YAMLError as e:
        logger.error("config_yaml_parsing_failed", path=config_path, error=str(e))
        raise yaml.YAMLError(f"Failed to parse YAML config: {str(e)}")
    except Exception as e:
        logger.error("config_loading_failed", path=config_path, error=str(e))
        raise Exception(f"Failed to load config: {str(e)}")


def map_yaml_to_nodes(config: Dict[str, Any]) -> Dict[str, Callable]:
    """Map YAML configuration to agent node functions.

    This function creates a mapping between agent names defined in the YAML
    configuration and their corresponding node functions.

    Args:
        config: Parsed YAML configuration dictionary

    Returns:
        Dict[str, Callable]: Mapping of node names to their functions
    """
    try:
        # Use default mapping for now - can be extended for dynamic node loading
        node_mapping = DEFAULT_NODE_MAPPING.copy()

        # Check if config specifies custom agent mappings
        agents_config = config.get('agents', {})
        for agent_name, agent_config in agents_config.items():
            if agent_name not in node_mapping:
                logger.warning(
                    "unknown_agent_in_config",
                    agent_name=agent_name,
                    available_agents=list(node_mapping.keys())
                )

        logger.info(
            "yaml_nodes_mapped",
            agent_count=len(agents_config),
            total_nodes=len(node_mapping)
        )

        return node_mapping

    except Exception as e:
        logger.error("yaml_to_nodes_mapping_failed", error=str(e))
        # Return default mapping as fallback
        return DEFAULT_NODE_MAPPING


def get_agent_config(config: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent.

    Args:
        config: Parsed YAML configuration
        agent_name: Name of the agent

    Returns:
        Dict[str, Any]: Agent-specific configuration or empty dict
    """
    try:
        agents_config = config.get('agents', {})
        agent_config = agents_config.get(agent_name, {})

        # Set sensible defaults
        default_config = {
            'model': None,  # Use default from settings
            'temperature': 0.7,
            'max_tokens': None,  # Use default from settings
            'prompt_template': None,  # Will use default prompts
        }

        # Merge with provided config
        merged_config = {**default_config, **agent_config}

        logger.debug(
            "agent_config_loaded",
            agent_name=agent_name,
            config_keys=list(merged_config.keys())
        )

        return merged_config

    except Exception as e:
        logger.error(
            "get_agent_config_failed",
            agent_name=agent_name,
            error=str(e)
        )
        return {}


def get_phases_config(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get phases configuration from YAML.

    Args:
        config: Parsed YAML configuration

    Returns:
        List[Dict[str, Any]]: List of phase configurations
    """
    try:
        phases_config = config.get('phases', [])
        logger.info(
            "phases_config_loaded",
            phase_count=len(phases_config)
        )
        return phases_config

    except Exception as e:
        logger.error("phases_config_load_failed", error=str(e))
        return []


def get_checkpointer_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get checkpointer configuration from YAML.

    Args:
        config: Parsed YAML configuration

    Returns:
        Dict[str, Any]: Checkpointer configuration
    """
    try:
        checkpointer_config = config.get('checkpointer', {})

        default_config = {
            'enabled': True,
            'backend': 'postgresql',
            'table_prefix': 'checkpoints',
        }

        merged_config = {**default_config, **checkpointer_config}

        logger.info(
            "checkpointer_config_loaded",
            enabled=merged_config['enabled'],
            backend=merged_config['backend']
        )

        return merged_config

    except Exception as e:
        logger.error("checkpointer_config_load_failed", error=str(e))
        return {'enabled': True, 'backend': 'postgresql'}


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate the configuration and return any issues.

    Args:
        config: Parsed YAML configuration

    Returns:
        List[str]: List of validation warnings/errors (empty if valid)
    """
    issues = []

    try:
        # Check required sections
        required_sections = ['workflow', 'agents']
        for section in required_sections:
            if section not in config:
                issues.append(f"Missing required section: {section}")

        # Validate workflow section
        workflow = config.get('workflow', {})
        if 'name' not in workflow:
            issues.append("Missing workflow name")

        if 'version' not in workflow:
            issues.append("Missing workflow version")

        # Validate agents section
        agents = config.get('agents', {})
        required_agents = [
            'orchestrator', 'algorithm', 'constraint', 'objective',
            'domain', 'code_impl', 'extension', 'quality'
        ]

        for agent in required_agents:
            if agent not in agents:
                issues.append(f"Missing required agent: {agent}")

        # Validate phases section
        phases = config.get('phases', [])
        if len(phases) == 0:
            issues.append("No phases defined")

        for i, phase in enumerate(phases):
            if 'id' not in phase:
                issues.append(f"Phase {i} missing id")
            if 'agents' not in phase:
                issues.append(f"Phase {i} missing agents")

        if issues:
            logger.warning("config_validation_issues", issues=issues)
        else:
            logger.info("config_validation_passed")

        return issues

    except Exception as e:
        logger.error("config_validation_failed", error=str(e))
        return [f"Config validation error: {str(e)}"]


def create_default_config() -> Dict[str, Any]:
    """Create a default configuration dictionary.

    Returns:
        Dict[str, Any]: Default BMAD workflow configuration
    """
    default_config = {
        'workflow': {
            'name': 'BMAD Eight-Agent Workflow',
            'version': '1.0',
            'description': 'Complete BMAD workflow with 8 agents and approval checkpoints'
        },
        'agents': {
            'orchestrator': {
                'prompt_template': 'prompts/orchestrator.md',
                'temperature': 0.7
            },
            'algorithm': {
                'prompt_template': 'prompts/algorithm.md',
                'temperature': 0.3
            },
            'constraint': {
                'prompt_template': 'prompts/constraint.md',
                'temperature': 0.2
            },
            'objective': {
                'prompt_template': 'prompts/objective.md',
                'temperature': 0.3
            },
            'domain': {
                'prompt_template': 'prompts/domain.md',
                'temperature': 0.5
            },
            'code_impl': {
                'prompt_template': 'prompts/code_impl.md',
                'temperature': 0.1
            },
            'extension': {
                'prompt_template': 'prompts/extension.md',
                'temperature': 0.4
            },
            'quality': {
                'prompt_template': 'prompts/quality.md',
                'temperature': 0.2
            }
        },
        'phases': [
            {'id': 'P0', 'agents': ['orchestrator']},
            {'id': 'P1', 'agents': ['algorithm', 'constraint', 'objective'], 'approval_required': True, 'approval_point': 'P1'},
            {'id': 'P2', 'agents': ['domain']},
            {'id': 'P3', 'agents': ['code_impl', 'extension'], 'approval_required': True, 'approval_point': 'P2.5'},
            {'id': 'P4', 'agents': ['quality']}
        ],
        'checkpointer': {
            'enabled': True,
            'backend': 'postgresql'
        }
    }

    logger.info("default_config_created")
    return default_config


# Export functions
__all__ = [
    'load_workflow_config',
    'map_yaml_to_nodes',
    'get_agent_config',
    'get_phases_config',
    'get_checkpointer_config',
    'validate_config',
    'create_default_config',
    'DEFAULT_NODE_MAPPING'
]