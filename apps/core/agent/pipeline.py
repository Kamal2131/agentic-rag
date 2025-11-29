"""
RAG Pipeline Implementation.
"""

from apps.core.agent.router import Router
from apps.core.agent.llm_client import LLMClient
from apps.core.tools.serper import SerperDevTool
from apps.core.tools.local_search import LocalSearchTool

class RAGPipeline:
    """
    Orchestrates the RAG pipeline: Routing -> Retrieval -> Context -> Generation.
    """
    
    def __init__(self):
        self.router = Router()
        self.llm_client = LLMClient()
        self.serper_tool = SerperDevTool()
        self.local_search_tool = LocalSearchTool()
    
    def run(self, query, summary=None):
        """
        Execute the pipeline.
        
        Args:
            query (str): User query
            summary (str): Summary of local document for routing
            
        Returns:
            dict: Final answer and steps
        """
        steps = []
        
        # Step 1: Routing
        source = self.router.route(query, summary)
        steps.append({"step": "routing", "result": source})
        
        # Step 2: Retrieval
        context_data = []
        
        if source in ["local", "both"]:
            local_results = self.local_search_tool.search(query)
            context_data.extend([f"[Local] {r['content']}" for r in local_results])
            steps.append({"step": "retrieval_local", "count": len(local_results)})
            
        if source in ["web", "both"]:
            web_results = self.serper_tool.search(query)
            if "organic" in web_results:
                for res in web_results["organic"][:3]:
                    context_data.append(f"[Web] {res.get('snippet', '')}")
            steps.append({"step": "retrieval_web", "count": len(web_results.get("organic", []))})
            
        # Step 3: Context Building
        context_text = "\n\n".join(context_data)
        steps.append({"step": "context_building", "length": len(context_text)})
        
        # Step 4: Generation
        system_prompt = """You are a helpful assistant. 
        Answer the user's query using the provided context. 
        If the context doesn't contain the answer, say so, but try to be helpful.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuery: {query}"}
        ]
        
        answer = self.llm_client.chat(messages)
        
        return {
            "answer": answer,
            "steps": steps,
            "source": source
        }
