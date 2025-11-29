"""
Agent Executor implementing ReAct-style reasoning loop.
"""

from django.conf import settings
from apps.rag.agent.llm_client import LLMClient
from apps.rag.agent.prompts import get_system_prompt
from apps.rag.tools.registry import ToolRegistry
from apps.rag.models import ToolLog


class AgentExecutor:
    """
    ReAct-style agent executor for agentic RAG.
    """
    
    def __init__(self):
        """Initialize the agent executor."""
        self.llm_client = LLMClient()
        self.tool_registry = ToolRegistry()
        self.max_steps = settings.AGENT_CONFIG['MAX_STEPS']
    
    def run(self, user_query):
        """
        Execute the agentic RAG pipeline.
        
        Args:
            user_query (str): User's question/query
            
        Returns:
            dict: Final answer with sources and execution steps
        """
        # Initialize
        system_prompt = get_system_prompt(self.tool_registry)
        messages = [{'role': 'user', 'content': user_query}]
        observations = []
        steps_taken = []
        step = 0
        
        while step < self.max_steps:
            step += 1
            
            # Build context with observations
            context_messages = messages.copy()
            if observations:
                obs_text = "\n\n".join([
                    f"Observation {i+1} (from {obs['tool']}):\n{obs['result']}"
                    for i, obs in enumerate(observations)
                ])
                context_messages.append({
                    'role': 'user',
                    'content': f"Previous observations:\n{obs_text}\n\nWhat should we do next?"
                })
            
            # Ask LLM for next action
            try:
                agent_output = self.llm_client.plan(system_prompt, context_messages)
            except Exception as e:
                return {
                    'answer': f'Error in agent planning: {str(e)}',
                    'sources': [],
                    'steps_taken': steps_taken
                }
            
            # Log the thought
            steps_taken.append({
                'step': step,
                'thought': agent_output.get('thought', ''),
                'tool': agent_output.get('tool'),
                'tool_input': agent_output.get('tool_input')
            })
            
            # Check if we have a final answer
            if agent_output.get('final_answer'):
                # Extract sources from observations
                sources = []
                for obs in observations:
                    if 'results' in obs.get('result', {}):
                        for result in obs['result']['results']:
                            if isinstance(result, dict):
                                sources.append({
                                    'id': result.get('id'),
                                    'title': result.get('title'),
                                    'content': result.get('content', '')[:200] + '...'
                                })
                
                return {
                    'answer': agent_output['final_answer'],
                    'sources': sources,
                    'steps_taken': steps_taken
                }
            
            # Execute tool if requested
            tool_name = agent_output.get('tool')
            if tool_name:
                tool_input = agent_output.get('tool_input', {}) or {}
                
                # Execute tool
                try:
                    result = self.tool_registry.call(tool_name, **tool_input)
                    
                    # Log tool execution
                    ToolLog.objects.create(
                        tool_name=tool_name,
                        input_data=tool_input,
                        output_data=result
                    )
                    
                    # Store observation
                    observations.append({
                        'tool': tool_name,
                        'input': tool_input,
                        'result': result
                    })
                    
                    # Update step with result
                    steps_taken[-1]['result'] = result
                    
                except Exception as e:
                    error_result = {
                        'success': False,
                        'error': str(e)
                    }
                    observations.append({
                        'tool': tool_name,
                        'input': tool_input,
                        'result': error_result
                    })
                    steps_taken[-1]['result'] = error_result
            else:
                # No tool requested but no final answer either
                return {
                    'answer': 'Agent did not provide a final answer or tool to execute.',
                    'sources': [],
                    'steps_taken': steps_taken
                }
        
        # Max steps reached
        return {
            'answer': f'Maximum steps ({self.max_steps}) reached without final answer. Please try rephrasing your query.',
            'sources': [],
            'steps_taken': steps_taken
        }
