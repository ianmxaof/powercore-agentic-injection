#!/usr/bin/env python3
"""
Agentic Injection System v2.0
Dynamic AI Agent Orchestration with MetaAgent Optimization

This system dynamically spawns and manages AI agents based on YAML configuration
and project context, with self-optimizing capabilities through MetaAgent analysis.
"""

import asyncio
import json
import logging
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Agent:
    """Represents an AI agent with its configuration and state."""
    name: str
    agent_type: str
    priority: str
    config: Dict[str, Any]
    status: str = "idle"
    created_at: datetime = None
    last_executed: datetime = None
    execution_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Trigger:
    """Represents a trigger condition for agent activation."""
    name: str
    condition: str
    agents: List[Agent]
    enabled: bool = True

class MetaAgent:
    """Self-optimizing component that learns from execution patterns."""
    
    def __init__(self):
        self.execution_history = []
        self.optimization_rules = []
        self.performance_metrics = {}
        
    async def analyze_execution(self, agent: Agent, result: Dict[str, Any]):
        """Analyze agent execution and update optimization rules."""
        execution_data = {
            'agent_name': agent.name,
            'agent_type': agent.agent_type,
            'execution_time': datetime.now(),
            'result': result,
            'performance_score': self._calculate_performance_score(result)
        }
        
        self.execution_history.append(execution_data)
        await self._update_optimization_rules(execution_data)
        
    def _calculate_performance_score(self, result: Dict[str, Any]) -> float:
        """Calculate performance score based on execution result."""
        # Simple scoring algorithm - can be enhanced
        score = 0.0
        
        if result.get('success', False):
            score += 0.5
            
        if result.get('quality_score'):
            score += result['quality_score'] * 0.3
            
        if result.get('execution_time'):
            # Faster execution = higher score
            execution_time = result['execution_time']
            if execution_time < 5.0:
                score += 0.2
            elif execution_time < 10.0:
                score += 0.1
                
        return min(score, 1.0)
        
    async def _update_optimization_rules(self, execution_data: Dict[str, Any]):
        """Update optimization rules based on execution analysis."""
        # Analyze patterns and suggest optimizations
        if len(self.execution_history) > 10:
            recent_executions = self.execution_history[-10:]
            avg_score = sum(e['performance_score'] for e in recent_executions) / len(recent_executions)
            
            if avg_score < 0.6:
                optimization = {
                    'type': 'performance_improvement',
                    'agent_name': execution_data['agent_name'],
                    'suggestion': 'Consider adjusting agent configuration for better performance',
                    'priority': 'medium'
                }
                self.optimization_rules.append(optimization)
                
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """Get current optimization suggestions."""
        return self.optimization_rules

class AgentRegistry:
    """Manages available agent types and their configurations."""
    
    def __init__(self):
        self.agents = {
            'code_analysis': {
                'description': 'Analyzes code quality and suggests improvements',
                'capabilities': ['code_review', 'refactoring_suggestions', 'bug_detection'],
                'default_config': {
                    'model': 'gpt-4',
                    'max_tokens': 2000,
                    'temperature': 0.1
                }
            },
            'test_automation': {
                'description': 'Generates and maintains test suites',
                'capabilities': ['unit_test_generation', 'integration_test_setup', 'test_maintenance'],
                'default_config': {
                    'model': 'gpt-4',
                    'max_tokens': 3000,
                    'temperature': 0.2
                }
            },
            'documentation': {
                'description': 'Generates and updates project documentation',
                'capabilities': ['readme_generation', 'api_docs', 'code_comments'],
                'default_config': {
                    'model': 'gpt-4',
                    'max_tokens': 2500,
                    'temperature': 0.3
                }
            },
            'deployment': {
                'description': 'Handles deployment and infrastructure setup',
                'capabilities': ['ci_cd_setup', 'infrastructure_as_code', 'deployment_automation'],
                'default_config': {
                    'model': 'gpt-4',
                    'max_tokens': 4000,
                    'temperature': 0.1
                }
            }
        }
    
    def get_agent_info(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent type."""
        return self.agents.get(agent_type)
    
    def list_agents(self) -> List[str]:
        """List all available agent types."""
        return list(self.agents.keys())

class InjectionEngine:
    """Main orchestrator for agent injection and management."""
    
    def __init__(self):
        self.meta_agent = MetaAgent()
        self.agent_registry = AgentRegistry()
        self.active_agents: Dict[str, Agent] = {}
        self.triggers: List[Trigger] = []
        self.rules_file = "injection_rules.yaml"
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.openai_client = openai.OpenAI(api_key=api_key)
        
    async def load_rules(self, rules_content: Optional[str] = None):
        """Load injection rules from YAML file or string."""
        try:
            if rules_content:
                rules_data = yaml.safe_load(rules_content)
            else:
                with open(self.rules_file, 'r') as f:
                    rules_data = yaml.safe_load(f)
                    
            self.triggers = []
            for trigger_data in rules_data.get('triggers', []):
                agents = []
                for agent_data in trigger_data.get('agents', []):
                    agent = Agent(
                        name=agent_data['name'],
                        agent_type=agent_data['type'],
                        priority=agent_data.get('priority', 'medium'),
                        config=agent_data.get('config', {})
                    )
                    agents.append(agent)
                    
                trigger = Trigger(
                    name=trigger_data['name'],
                    condition=trigger_data['condition'],
                    agents=agents,
                    enabled=trigger_data.get('enabled', True)
                )
                self.triggers.append(trigger)
                
            logger.info(f"Loaded {len(self.triggers)} triggers with {sum(len(t.agents) for t in self.triggers)} agents")
            
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            raise
            
    async def process_project_request(self, project_request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a project request and trigger appropriate agents."""
        logger.info(f"Processing project request: {project_request.get('description', 'No description')}")
        
        results = {
            'project_id': project_request.get('id', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'agents_executed': [],
            'overall_status': 'success',
            'meta_agent_insights': []
        }
        
        try:
            # Evaluate triggers based on project context
            for trigger in self.triggers:
                if not trigger.enabled:
                    continue
                    
                if await self._evaluate_trigger(trigger, project_request):
                    logger.info(f"Trigger '{trigger.name}' activated")
                    
                    # Execute agents for this trigger
                    for agent in trigger.agents:
                        agent_result = await self._execute_agent(agent, project_request)
                        results['agents_executed'].append({
                            'agent_name': agent.name,
                            'agent_type': agent.agent_type,
                            'result': agent_result
                        })
                        
                        # Update MetaAgent with execution data
                        await self.meta_agent.analyze_execution(agent, agent_result)
            
            # Get MetaAgent insights
            results['meta_agent_insights'] = self.meta_agent.get_optimization_suggestions()
            
        except Exception as e:
            logger.error(f"Error processing project request: {e}")
            results['overall_status'] = 'error'
            results['error'] = str(e)
            
        return results
    
    async def _evaluate_trigger(self, trigger: Trigger, project_request: Dict[str, Any]) -> bool:
        """Evaluate if a trigger should be activated based on project context."""
        condition = trigger.condition.lower()
        
        if condition == "always":
            return True
        elif condition == "file_changed":
            return project_request.get('files_modified', False)
        elif condition == "test_files_modified":
            return any('test' in f.lower() for f in project_request.get('files_modified', []))
        elif condition == "complexity_high":
            return project_request.get('complexity', 'medium') == 'high'
        elif condition == "platform_web":
            return project_request.get('platform', '') == 'web'
        elif condition == "platform_mobile":
            return project_request.get('platform', '') == 'mobile'
        else:
            # Custom condition evaluation
            return await self._evaluate_custom_condition(condition, project_request)
    
    async def _evaluate_custom_condition(self, condition: str, project_request: Dict[str, Any]) -> bool:
        """Evaluate custom conditions using AI."""
        try:
            prompt = f"""
            Evaluate if the following project request meets the condition: "{condition}"
            
            Project Request: {json.dumps(project_request, indent=2)}
            
            Respond with only 'true' or 'false'.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )
            
            result = response.choices[0].message.content.strip().lower()
            return result == 'true'
            
        except Exception as e:
            logger.error(f"Error evaluating custom condition: {e}")
            return False
    
    async def _execute_agent(self, agent: Agent, project_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific agent with the project context."""
        logger.info(f"Executing agent: {agent.name} ({agent.agent_type})")
        
        start_time = datetime.now()
        agent.status = "executing"
        
        try:
            # Get agent configuration
            agent_info = self.agent_registry.get_agent_info(agent.agent_type)
            if not agent_info:
                raise ValueError(f"Unknown agent type: {agent.agent_type}")
            
            # Merge default config with agent-specific config
            config = {**agent_info['default_config'], **agent.config}
            
            # Execute agent based on type
            if agent.agent_type == 'code_analysis':
                result = await self._execute_code_analysis_agent(agent, project_request, config)
            elif agent.agent_type == 'test_automation':
                result = await self._execute_test_automation_agent(agent, project_request, config)
            elif agent.agent_type == 'documentation':
                result = await self._execute_documentation_agent(agent, project_request, config)
            elif agent.agent_type == 'deployment':
                result = await self._execute_deployment_agent(agent, project_request, config)
            else:
                result = await self._execute_generic_agent(agent, project_request, config)
            
            # Update agent state
            agent.status = "completed"
            agent.last_executed = datetime.now()
            agent.execution_count += 1
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result['execution_time'] = execution_time
            result['success'] = True
            
            logger.info(f"Agent {agent.name} completed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error executing agent {agent.name}: {e}")
            agent.status = "error"
            
            return {
                'success': False,
                'error': str(e),
                'execution_time': (datetime.now() - start_time).total_seconds()
            }
    
    async def _execute_code_analysis_agent(self, agent: Agent, project_request: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code analysis agent."""
        prompt = f"""
        Perform a comprehensive code analysis for the following project:
        
        Project Description: {project_request.get('description', 'No description')}
        Platform: {project_request.get('platform', 'Unknown')}
        Complexity: {project_request.get('complexity', 'Medium')}
        Features: {project_request.get('features', [])}
        
        Provide:
        1. Code quality assessment
        2. Potential improvements
        3. Security considerations
        4. Performance optimization suggestions
        
        Be specific and actionable in your recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config['max_tokens'],
            temperature=config['temperature']
        )
        
        return {
            'analysis': response.choices[0].message.content,
            'quality_score': 0.85,  # This could be calculated based on analysis
            'recommendations_count': 5
        }
    
    async def _execute_test_automation_agent(self, agent: Agent, project_request: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test automation agent."""
        prompt = f"""
        Generate comprehensive test automation strategy for:
        
        Project: {project_request.get('description', 'No description')}
        Platform: {project_request.get('platform', 'Unknown')}
        
        Include:
        1. Unit test framework recommendations
        2. Integration test setup
        3. Test coverage strategy
        4. CI/CD integration
        5. Sample test cases
        
        Provide practical, implementable solutions.
        """
        
        response = self.openai_client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config['max_tokens'],
            temperature=config['temperature']
        )
        
        return {
            'test_strategy': response.choices[0].message.content,
            'frameworks_recommended': ['Jest', 'Cypress', 'Playwright'],
            'coverage_target': '90%'
        }
    
    async def _execute_documentation_agent(self, agent: Agent, project_request: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation agent."""
        prompt = f"""
        Create comprehensive documentation for:
        
        Project: {project_request.get('description', 'No description')}
        Platform: {project_request.get('platform', 'Unknown')}
        
        Generate:
        1. README.md structure
        2. API documentation template
        3. Setup instructions
        4. Contributing guidelines
        5. Code documentation standards
        
        Make it developer-friendly and comprehensive.
        """
        
        response = self.openai_client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config['max_tokens'],
            temperature=config['temperature']
        )
        
        return {
            'documentation': response.choices[0].message.content,
            'sections_created': ['README', 'API Docs', 'Setup Guide', 'Contributing'],
            'completeness_score': 0.9
        }
    
    async def _execute_deployment_agent(self, agent: Agent, project_request: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment agent."""
        prompt = f"""
        Design deployment strategy for:
        
        Project: {project_request.get('description', 'No description')}
        Platform: {project_request.get('platform', 'Unknown')}
        
        Provide:
        1. Infrastructure requirements
        2. Deployment pipeline
        3. Environment configuration
        4. Monitoring setup
        5. Scaling strategy
        
        Focus on modern, cloud-native approaches.
        """
        
        response = self.openai_client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config['max_tokens'],
            temperature=config['temperature']
        )
        
        return {
            'deployment_strategy': response.choices[0].message.content,
            'infrastructure_type': 'Cloud-native',
            'deployment_method': 'CI/CD Pipeline'
        }
    
    async def _execute_generic_agent(self, agent: Agent, project_request: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a generic agent for unknown types."""
        prompt = f"""
        As a {agent.agent_type} agent, provide assistance for:
        
        Project: {project_request.get('description', 'No description')}
        Platform: {project_request.get('platform', 'Unknown')}
        
        Provide comprehensive guidance and recommendations.
        """
        
        response = self.openai_client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=config['max_tokens'],
            temperature=config['temperature']
        )
        
        return {
            'output': response.choices[0].message.content,
            'agent_type': agent.agent_type
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics."""
        return {
            'active_agents': len(self.active_agents),
            'total_triggers': len(self.triggers),
            'enabled_triggers': len([t for t in self.triggers if t.enabled]),
            'meta_agent_insights': self.meta_agent.get_optimization_suggestions(),
            'available_agent_types': self.agent_registry.list_agents(),
            'system_health': 'healthy'
        }

async def main():
    """Main entry point for the Agentic Injection System."""
    try:
        # Initialize the injection engine
        engine = InjectionEngine()
        
        # Load default rules if no override provided
        await engine.load_rules()
        
        # Example project request
        project_request = {
            'id': 'demo-project-001',
            'description': 'A modern web application for task management',
            'platform': 'web',
            'complexity': 'medium',
            'features': ['user_authentication', 'task_management', 'real_time_updates'],
            'files_modified': ['src/components/TaskList.js', 'src/api/tasks.js']
        }
        
        # Process the request
        result = await engine.process_project_request(project_request)
        
        # Output results
        print(json.dumps(result, indent=2, default=str))
        
        # Show system status
        status = engine.get_system_status()
        print("\nSystem Status:")
        print(json.dumps(status, indent=2))
        
    except Exception as e:
        logger.error(f"System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
