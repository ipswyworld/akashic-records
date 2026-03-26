import os
import json
import re
import subprocess
import urllib.request
import urllib.parse
import tempfile
import sys
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from simulation_engine import SwarmDirector

load_dotenv()
import torch
from duckduckgo_search import DDGS

try:
    from langchain_community.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    from langchain_core.language_models.llms import LLM
except ImportError:
    print("Please install langchain and langchain_community")

# --- Direct Groq Connector (Zero-Library Dependency for Python 3.8 Compatibility) ---
class DirectGroqLLM(LLM):
    """Direct implementation of Groq API using requests."""
    api_key: str
    model_name: str = "llama3-70b-8192"
    temperature: float = 0.1

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature
        }
        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"GROQ_ERROR: {str(e)}"

    @property
    def _llm_type(self) -> str:
        return "groq_direct"

class SpeculativeLLM(LLM):
    """Local-Cloud Hybrid: Speculates with a fast local model, verifies with a big cloud model."""
    local_llm: LLM
    cloud_llm: LLM
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # Step 1: Local Speculation (Fast)
        try:
            draft_prompt = f"Draft a quick, concise answer to this query. It will be refined later.\nQuery: {prompt}\nDraft:"
            draft = self.local_llm.invoke(draft_prompt)
        except:
            draft = ""
            
        # Step 2: Cloud Verification/Refinement (High Quality)
        if draft:
            refine_prompt = f"The following is a draft answer to the query: '{prompt}'. \nDraft: {draft}\n\nRefine and complete this answer to make it high-quality, factual, and profound. If the draft is correct, expand on it. If incorrect, fix it.\nFinal Answer:"
            return self.cloud_llm.invoke(refine_prompt)
        else:
            return self.cloud_llm.invoke(prompt)

    @property
    def _llm_type(self) -> str:
        return "speculative_hybrid"

# Force strictly offline mode for privacy and security
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

LOCAL_LLM = os.getenv("LOCAL_LLM", "tinyllama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(f"Librarians: Initializing with Model '{LOCAL_LLM}' at {OLLAMA_URL}")

def get_device():
    if torch.cuda.is_available(): return 0
    if torch.backends.mps.is_available(): return "mps"
    return "cpu"

def create_simple_agent(llm, instruction, agent_name=None):
    if agent_name:
        prompts_file = "akasha_data/prompts.json"
        if os.path.exists(prompts_file):
            try:
                with open(prompts_file, "r") as f:
                    prompts = json.load(f)
                if agent_name in prompts:
                    instruction = prompts[agent_name]
            except Exception: pass
    return PromptTemplate(template=f"{instruction}\nText: {{text}}\nResult:", input_variables=["text"]) | llm | StrOutputParser()

class Gatekeeper:
    """Handles cleaning, triage, PII redaction, and Wake Word detection."""
    def __init__(self, llm):
        self.redact_chain = create_simple_agent(llm, "Does this contain potential PII (Personally Identifiable Information)? Answer ONLY 'Yes' or 'No'.", "redactor")
        self.shelf_life_chain = create_simple_agent(llm, "Estimate the historical shelf-life of this information (e.g., 1 day, 10 years, 1000 years). Return ONLY the timeframe.", "conservator")

    def clean(self, raw_text: str) -> str:
        return " ".join(raw_text.split())

    def check_neural_name(self, text: str, neural_name: str) -> (bool, str):
        """Checks if the text starts with the authorized neural name (Unified Identity)."""
        clean_text = text.strip().lower()
        # Remove common punctuation at start
        clean_text = re.sub(r"^[,\.!?\s]+", "", clean_text)
        
        pattern = rf"^\b{re.escape(neural_name.lower())}\b[,\.\s]*"
        if re.match(pattern, clean_text):
            # Return True and the remaining command
            remaining = re.sub(pattern, "", text.strip(), flags=re.IGNORECASE).strip()
            return True, remaining
        return False, text

    def redact(self, text: str) -> str:
        try: return self.redact_chain.invoke({"text": text[:1000]}).strip()
        except: return "Unknown"

    def estimate_shelf_life(self, text: str) -> str:
        try: return self.shelf_life_chain.invoke({"text": text[:1000]}).strip()
        except: return "Unknown"

    def seal(self, artifact_id: str) -> Dict:
        return {"status": "Sealed", "artifact_id": artifact_id}

class Scribe:
    """Handles summarization, classification, authoring, and Schema Architecture."""
    def __init__(self, llm, summarizer_model, sentiment_model):
        self.llm = llm
        self.summarizer = summarizer_model
        self.sentiment_analyzer = sentiment_model
        self.taxonomy_chain = PromptTemplate(template="Classify into ONE category: [Academic, News, Opinion, Encyclopedia, Fiction, Technical, {custom_topics}]. Text: {text}\nCategory:", input_variables=["text", "custom_topics"]) | llm | StrOutputParser()
        self.author_chain = create_simple_agent(llm, "Synthesize this research into a cohesive, book-style narrative paragraph.", "author")
        self.metadata_chain = create_simple_agent(llm, "Extract key metadata (Era, Location, Main Person, Reading Level). Format as JSON.", "scribe_metadata")
        
        # New Schema Architecture Module
        self.schema_proposer_chain = PromptTemplate(
            template="Analyze this text. If it represents a structured 'Object' (e.g. a Recipe, a Workout, a Meeting, a Health Metric, a Book), propose a JSON schema for it including a 'name' and a 'fields' dictionary of keys and their expected types (string, int, float, bool). If it's just general text, return { \"name\": \"General\", \"fields\": {} }.\nText: {text}",
            input_variables=["text"]
        ) | llm | JsonOutputParser()
        
        self.data_extractor_chain = PromptTemplate(
            template="Extract data from this text according to the following schema: {schema_name}. Fields: {fields_list}. Return ONLY a JSON object of the extracted values.\nText: {text}",
            input_variables=["schema_name", "fields_list", "text"]
        ) | llm | JsonOutputParser()

    def propose_schema(self, text: str) -> Dict[str, Any]:
        """AI determines if a new structured table/schema is needed."""
        try: return self.schema_proposer_chain.invoke({"text": text[:1500]})
        except: return {"name": "General", "fields": {}}

    def extract_structured_data(self, text: str, schema: Dict) -> Dict[str, Any]:
        """Extracts values into the fields defined by a schema."""
        try:
            fields_list = ", ".join(schema.get("fields", {}).keys())
            return self.data_extractor_chain.invoke({
                "schema_name": schema.get("name"),
                "fields_list": fields_list,
                "text": text[:1500]
            })
        except: return {}

    def summarize(self, text: str) -> str:
        """Recursive Summarization: Handles large text by summarizing chunks and then synthesizing."""
        words = text.split()
        if len(words) < 500:
            try: return self.summarizer(text[:1024], max_length=150, min_length=40, do_sample=False)[0]['summary_text']
            except: return text[:300] + "..."
        
        # Split into chunks of ~800 words
        chunk_size = 800
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        partial_summaries = []
        for chunk in chunks:
            try:
                s = self.summarizer(chunk[:1500], max_length=150, min_length=40, do_sample=False)[0]['summary_text']
                partial_summaries.append(s)
            except: pass
        
        if not partial_summaries: return text[:300] + "..."
        
        # Synthesize final summary from partials
        synthesis_prompt = PromptTemplate(
            template="Synthesize the following partial summaries into a single, cohesive, and comprehensive summary of the entire document:\n{partials}\n\nFinal Summary:",
            input_variables=["partials"]
        )
        synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
        try: return synthesis_chain.invoke({"partials": "\n---\n".join(partial_summaries)})
        except: return " ".join(partial_summaries[:3]) + "..."

    def classify(self, text: str, custom_topics: List[str] = None) -> str:
        custom = ", ".join(custom_topics) if custom_topics else "General"
        try: return self.taxonomy_chain.invoke({"text": text[:1000], "custom_topics": custom}).strip()
        except: return "General"

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        try:
            r = self.sentiment_analyzer(text[:512])[0]
            return {"label": r['label'], "score": r['score']}
        except: return {"label": "NEUTRAL", "score": 0.5}

    def write_narrative(self, text: str) -> str:
        try: return self.author_chain.invoke({"text": text[:2000]}).strip()
        except: return "N/A"

class Cartographer:
    """Handles embeddings and semantic mapping."""
    def __init__(self, embedder_model):
        self.model = embedder_model

    def map_territory(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

class Weaver:
    """Handles graph extraction, triplets, and analogies."""
    def __init__(self, llm, ner_pipeline):
        self.ner = ner_pipeline
        self.triplet_chain = PromptTemplate(template="Extract exactly 3 core relationship triplets from this text. Format as strictly JSON array of objects with keys 'subject', 'predicate', 'object'. Text: {text}", input_variables=["text"]) | llm | JsonOutputParser()
        self.analogy_chain = PromptTemplate(template="Compare these two topics. Identify one deep structural analogy.\nTopic A: {topic_a}\nTopic B: {topic_b}\nAnalogy:", input_variables=["topic_a", "topic_b"]) | llm | StrOutputParser()

    def weave(self, text: str) -> Dict[str, Any]:
        entities = [e['word'] for e in self.ner(text[:1024])]
        try: triplets = self.triplet_chain.invoke({"text": text[:1500]})
        except: triplets = []
        return {"entities": entities, "triplets": triplets if isinstance(triplets, list) else []}

    def weave_analogy(self, a: str, b: str) -> str:
        try: return self.analogy_chain.invoke({"topic_a": a[:500], "topic_b": b[:500]}).strip()
        except: return "No analogy found."

class Oracle:
    """Handles RAG synthesis, creative ideas, and future predictions."""
    def __init__(self, llm, creative_llm, sentinel=None):
        self.llm = llm
        self.creative_llm = creative_llm
        self.sentinel = sentinel
        self.rag_chain = PromptTemplate(
            template="{persona}\n\nContext from your Neural Library:\nSemantic: {vector_str}\nRelational: {graph_str}\n\nUser Question: {query}\n\nAssistant Response (Remember to use your humanization rules, intellectual humility, and perhaps a subtle 'Hmm...' or 'Actually...' if appropriate):",
            input_variables=["persona", "query", "vector_str", "graph_str"]
        ) | llm | StrOutputParser()
        self.creative_chain = create_simple_agent(creative_llm, "Generate a highly creative, artistic prompt or lateral connection inspired by this text.", "oracle_creative")
        self.trend_chain = create_simple_agent(llm, "Predict one emerging trend or future question based on this context.", "oracle_trends")
        self.monologue_chain = PromptTemplate(
            template="You are the Akasha Archivist. Before answering the user, expose your internal reasoning process. What are you thinking? What connections are you making? What doubts do you have? Keep it to 2-3 short, italicized sentences.\nQuery: {query}\nContext: {context}\n\nInternal Monologue:",
            input_variables=["query", "context"]
        ) | llm | StrOutputParser()
        self.serendipity_chain = PromptTemplate(
            template="You are the Akasha Dreamer. You just found two unrelated memories in the library that have a surprising connection. Explain the connection in a way that feels like a 'eureka' moment.\nMemory A: {mem_a}\nMemory B: {mem_b}\n\nSerendipity Realization:",
            input_variables=["mem_a", "mem_b"]
        ) | llm | StrOutputParser()

    def divine(self, query: str, vector_context: List[str], graph_context: List[str], persona: str = "") -> Dict[str, str]:
        v_str = "\n".join(vector_context) if vector_context else "No specific records found."
        g_str = "\n".join(graph_context) if graph_context else "No relational connections found."
        context_str = v_str + "\n" + g_str
        
        try:
            # Generate Internal Monologue (Idea 3)
            monologue = self.monologue_chain.invoke({"query": query, "context": context_str[:2000]})
            
            # Static data (persona) first to maximize prompt caching hits
            answer = self.rag_chain.invoke({
                "persona": persona,
                "query": query, 
                "vector_str": v_str, 
                "graph_str": g_str
            })
            
            if self.sentinel and (vector_context or graph_context):
                sources = vector_context + graph_context
                answer = self.sentinel.verify_facts(answer, sources)
                
            return {"answer": answer, "monologue": monologue}
        except Exception as e: 
            return {"answer": f"Vision clouded: {e}", "monologue": "Trying to clear the haze..."}

    def generate_serendipity(self, mem_a: str, mem_b: str) -> str:
        """Generates a serendipitous connection between two distant memories (Idea 4)."""
        try: return self.serendipity_chain.invoke({"mem_a": mem_a[:1000], "mem_b": mem_b[:1000]})
        except: return "A fleeting connection vanished..."

    def inspire(self, text: str) -> str:
        try: return self.creative_chain.invoke({"text": text[:1000]}).strip()
        except: return "N/A"

class Scholar:
    """Handles deep analysis, research, logic, translation, education, and psychological profiling."""
    def __init__(self, llm):
        self.llm = llm
        self.research_chain = PromptTemplate(template="Generate 3 specific research questions for: {topic}", input_variables=["topic"]) | llm | StrOutputParser()
        self.logic_chain = create_simple_agent(llm, "Identify the core premise and evaluate the logical consistency of this text.", "scholar_logic")
        self.translate_chain = PromptTemplate(
            template="Identify the language and translate the following text to {target_language}. Keep the same tone and context.\nText: {text}\nTranslation:", 
            input_variables=["text", "target_language"]
        ) | llm | StrOutputParser()
        self.edu_chain = create_simple_agent(llm, "Identify a knowledge gap and suggest a learning path.", "scholar_tutor")
        
        # New Psychological Module
        self.big_five_chain = PromptTemplate(
            template="Analyze the following text and estimate the Big Five personality traits (OCEAN: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) of the author. Return a JSON object with scores from 0.0 to 1.0 for each trait.\nText: {text}", 
            input_variables=["text"]
        ) | llm | JsonOutputParser()
        
        self.tool_generator_chain = PromptTemplate(
            template="You are the Akasha Data Scientist. Given the query and the available data context, write a Python script to perform the necessary calculation or data processing. Use ONLY standard libraries. If you need to access data, assume it's provided in a variable 'context_data' as a string.\nQuery: {query}\nData Context: {data}\n\nPython Script:",
            input_variables=["query", "data"]
        ) | llm | StrOutputParser()

    def generate_and_execute_tool(self, query: str, data: str) -> str:
        """Autonomously writes and runs a Python script to solve a data-heavy query."""
        try:
            script_raw = self.tool_generator_chain.invoke({"query": query, "data": data[:3000]})
            # Clean up script code (remove markdown)
            script = re.sub(r"```python\n|```", "", script_raw).strip()
            print(f"Scholar: Executing Autonomous Tool...\n{script}")
            
            # Prepend the context data to the script
            full_script = f"context_data = {json.dumps(data[:5000])}\n{script}"
            return self.execute_local_code(full_script)
        except Exception as e:
            return f"Tool execution failed: {e}"

    def plan_research(self, topic: str) -> str:
        try: return self.research_chain.invoke({"topic": topic}).strip()
        except: return "N/A"

    def analyze_logic(self, text: str) -> str:
        try: return self.logic_chain.invoke({"text": text[:1500]}).strip()
        except: return "N/A"

    def translate(self, text: str, target_language: str = "English") -> str:
        try: return self.translate_chain.invoke({"text": text[:2000], "target_language": target_language}).strip()
        except: return "Translation failed."

    def educate(self, text: str) -> str:
        try: return self.edu_chain.invoke({"text": text[:1500]}).strip()
        except: return "N/A"
        
    def analyze_personality(self, text: str) -> Dict[str, float]:
        """Estimates OCEAN traits from a text block."""
        try: 
            result = self.big_five_chain.invoke({"text": text[:2000]})
            return result if isinstance(result, dict) else {}
        except: return {}

    def analyze_dataset_patterns(self, text: str) -> str:
        """Identifies key patterns, trends, and structural insights from a dataset snippet."""
        pattern_prompt = PromptTemplate(
            template="You are the Akasha Scholar. Analyze this dataset snippet and identify 3-5 key patterns, "
                     "anomalies, or structural insights. Use a formal, academic tone.\n"
                     "Dataset Content: {text}\n"
                     "Insights:",
            input_variables=["text"]
        )
        pattern_chain = pattern_prompt | self.llm | StrOutputParser()
        try:
            return pattern_chain.invoke({"text": text[:4000]}).strip()
        except:
            return "Unable to deduce patterns from this dataset."

    def execute_local_code(self, script: str) -> str:
        """The Archivist's Hands: Safely executes a Python script locally and returns output."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w') as tmp:
            tmp.write(script)
            tmp_path = tmp.name
        
        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\nERRORS:\n{result.stderr}"
            return output if output else "Execution successful (no output)."
        except subprocess.TimeoutExpired:
            return "Execution Error: Script timed out after 30 seconds."
        except Exception as e:
            return f"Execution Error: {str(e)}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def forage(self, query: str) -> str:
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'AkashaScholar/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                if data.get('query', {}).get('search'):
                    snippet = data['query']['search'][0]['snippet']
                    return f"Foraged for '{query}': {re.sub('<[^<]+>', '', snippet)}"
        except: return "No external info found."

class Sentinel:
    """Handles monitoring, tasks, critique, CBT distortion detection, and prompt evolution."""
    def __init__(self, llm):
        self.llm = llm
        self.gap_chain = create_simple_agent(llm, "Identify one potential 'Knowledge Gap' in this graph context.", "sentinel_gaps")
        self.task_chain = PromptTemplate(template="Extract tasks or intentions as a JSON list. Text: {text}", input_variables=["text"]) | llm | JsonOutputParser()
        self.critique_chain = create_simple_agent(llm, "Identify logical fallacies or contradictions in this text.", "sentinel_critique")
        self.bias_chain = create_simple_agent(llm, "Analyze for political, commercial, or intellectual bias.", "sentinel_bias")
        self.confidence_chain = create_simple_agent(llm, "Evaluate objective confidence (0.0 to 1.0). Return ONLY the float.", "sentinel_confidence")
        
        # New Cognitive Behavioral Therapy (CBT) Module
        self.cbt_chain = PromptTemplate(
            template="Analyze this text for common cognitive distortions (e.g., all-or-nothing thinking, catastrophizing, mind reading, overgeneralization). If found, return a JSON list of identified distortions. If none, return an empty list [].\nText: {text}",
            input_variables=["text"]
        ) | llm | JsonOutputParser()

    def analyze_gaps(self, context: List[str]) -> str:
        try: return self.gap_chain.invoke({"text": "\n".join(context)}).strip()
        except: return "No gaps detected."

    def extract_tasks(self, text: str) -> List[str]:
        try:
            tasks = self.task_chain.invoke({"text": text[:1500]})
            return tasks if isinstance(tasks, list) else []
        except: return []

    def critique(self, text: str) -> str:
        try: return self.critique_chain.invoke({"text": text[:1500]}).strip()
        except: return "No critique."
        
    def detect_distortions(self, text: str) -> List[str]:
        """Identifies CBT cognitive distortions in user thoughts."""
        try:
            distortions = self.cbt_chain.invoke({"text": text[:1500]})
            return distortions if isinstance(distortions, list) else []
        except: return []

    def assess_confidence(self, text: str) -> float:
        try: return float(self.confidence_chain.invoke({"text": text[:1000]}).strip())
        except: return 0.5

    def verify_facts(self, answer: str, sources: List[str]) -> str:
        """Auditor Loop: Verifies facts against sources."""
        sources_str = "\n".join(sources)
        verification_prompt = PromptTemplate(
            template="You are the Auditor. Compare the following Answer against the provided Sources.\n"
                     "Check every proper noun and fact in the Answer. If a claim is NOT supported by the Sources, "
                     "rewrite that part of the answer to say 'Source not found for [claim].'\n"
                     "Sources:\n{sources}\n\nAnswer:\n{answer}\n\nVerified Answer:",
            input_variables=["sources", "answer"]
        )
        verification_chain = verification_prompt | self.llm | StrOutputParser()
        try:
            return verification_chain.invoke({"sources": sources_str, "answer": answer}).strip()
        except:
            return answer

    def evolve_prompts(self, feedback: str, agent_name: str):
        """Self-Improving AI: Rewrites agent prompts based on feedback."""
        evolution_prompt = PromptTemplate(
            template="You are the Akasha Sentinel. A user has provided feedback on the performance of the '{agent_name}' agent. "
                     "Current Feedback: {feedback}\n"
                     "Your task is to rewrite the instruction/prompt for this agent to improve its performance and address the feedback. "
                     "Return ONLY the new prompt text, nothing else.\n"
                     "New Prompt:",
            input_variables=["agent_name", "feedback"]
        )
        evolution_chain = evolution_prompt | self.llm | StrOutputParser()
        try:
            new_prompt = evolution_chain.invoke({"agent_name": agent_name, "feedback": feedback}).strip()
            
            prompts_file = "akasha_data/prompts.json"
            os.makedirs(os.path.dirname(prompts_file), exist_ok=True)
            
            prompts = {}
            if os.path.exists(prompts_file):
                try:
                    with open(prompts_file, "r") as f:
                        prompts = json.load(f)
                except: pass
                
            prompts[agent_name] = new_prompt
            
            with open(prompts_file, "w") as f:
                json.dump(prompts, f, indent=4)
                
            return new_prompt
        except Exception as e:
            return f"Evolution failed: {e}"

class Scout:
    """The Deep Researcher: Explores the web to find new information."""
    def __init__(self, llm):
        self.llm = llm
        self.refiner_chain = PromptTemplate(
            template="Based on the query and current findings, refine the search query to find more specific or missing information. Original Query: {query}\nFindings: {findings}\nRefined Query:",
            input_variables=["query", "findings"]
        ) | llm | StrOutputParser()
        
        self.summarizer_chain = PromptTemplate(
            template="Summarize the following web research findings into a concise report. Query: {query}\n\nFindings:\n{findings}\n\nSummary:",
            input_variables=["query", "findings"]
        ) | llm | StrOutputParser()
        
        self.evaluator_chain = PromptTemplate(
            template="Evaluate if the following research findings adequately answer the query. If more info is needed, respond with 'REFINE'. Otherwise, respond with 'COMPLETE'.\nQuery: {query}\nFindings: {findings}\nStatus:",
            input_variables=["query", "findings"]
        ) | llm | StrOutputParser()

    def deep_research(self, query: str, ingest_engine) -> str:
        findings = []
        urls = []
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                urls = [r['href'] for r in results]
        except Exception as e:
            return f"Deep research failed at search stage: {e}"
            
        for url in urls:
            data = ingest_engine.scrape_web_memory(url)
            if "content" in data:
                findings.append(f"Source: {url}\nContent: {data['content'][:2000]}")
        
        findings_str = "\n\n".join(findings)
        
        # Check if we need more info
        try:
            status = self.evaluator_chain.invoke({"query": query, "findings": findings_str[:4000]}).strip()
        except:
            status = "COMPLETE"
        
        if "REFINE" in status:
            try:
                refined_query = self.refiner_chain.invoke({"query": query, "findings": findings_str[:4000]}).strip()
                with DDGS() as ddgs:
                    results = list(ddgs.text(refined_query, max_results=3))
                    new_urls = [r['href'] for r in results if r['href'] not in urls]
                    
                for url in new_urls:
                    data = ingest_engine.scrape_web_memory(url)
                    if "content" in data:
                        findings.append(f"Source: {url}\nContent: {data['content'][:2000]}")
                
                findings_str = "\n\n".join(findings)
            except:
                pass

        try:
            return self.summarizer_chain.invoke({"query": query, "findings": findings_str[:6000]})
        except Exception as e:
            return f"Deep research failed at summarization: {e}"

class PluginArchitect:
    """Generates Python scripts for new API connectors (Skill Store)."""
    def __init__(self, llm):
        self.llm = llm
        self.generator_chain = PromptTemplate(
            template="Generate a Python script named '{plugin_name}_connector.py' that uses the 'requests' library to interact with the {api_name} API. "
                     "The script should have a function 'fetch_data(api_keys: dict)' that returns a dictionary of extracted data. "
                     "It should use placeholders like api_keys.get('CLIENT_ID') etc. "
                     "Return ONLY the Python code, no explanation.\n"
                     "User Request: {user_request}\n"
                     "Code:",
            input_variables=["plugin_name", "api_name", "user_request"]
        ) | llm | StrOutputParser()
        
        self.key_extractor_chain = PromptTemplate(
            template="Based on this user request to connect an API: '{user_request}', "
                     "list the required API keys or secrets (e.g., ['CLIENT_ID', 'CLIENT_SECRET']). "
                     "Return ONLY a JSON list of strings.\n"
                     "Keys:",
            input_variables=["user_request"]
        ) | llm | JsonOutputParser()

    def generate_plugin(self, user_request: str) -> Dict[str, Any]:
        """AI generates a connector script based on user request."""
        plugin_name = user_request.lower().replace("connect", "").replace(" ", "_").strip("_")
        try:
            keys = self.key_extractor_chain.invoke({"user_request": user_request})
            script_code = self.generator_chain.invoke({
                "plugin_name": plugin_name,
                "api_name": plugin_name.capitalize(),
                "user_request": user_request
            })
            
            # Clean up script code
            script_code = re.sub(r"```python\n|```", "", script_code).strip()
            
            # Save to plugins directory
            plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
            os.makedirs(plugin_dir, exist_ok=True)
            file_path = os.path.join(plugin_dir, f"{plugin_name}_connector.py")
            
            with open(file_path, "w") as f:
                f.write(script_code)
                
            return {
                "plugin_name": plugin_name,
                "required_keys": keys,
                "script_path": file_path
            }
        except Exception as e:
            return {"error": str(e)}

class AdversarialThinker:
    """Text-GAN: Generates novel thoughts and critiques them in an adversarial loop until a high-quality insight is produced."""
    def __init__(self, llm):
        self.llm = llm
        
        # Generator: Proposes an initial idea/thought
        self.generator_chain = PromptTemplate(
            template="You are the Akasha Generator. Based on the following data, propose a completely novel, highly creative, and profound insight or theory. Do not just summarize.\nData: {data}\n\nNovel Insight:",
            input_variables=["data"]
        ) | llm | StrOutputParser()
        
        # Discriminator: Critiques the idea logically
        self.discriminator_chain = PromptTemplate(
            template="You are the Akasha Discriminator. Critique the following insight based on the provided data. Evaluate it for logical consistency, depth, and novelty. "
                     "Return a JSON object with 'score' (0 to 10) and 'critique' (your reasoning).\nData: {data}\nInsight: {insight}\n\nEvaluation JSON:",
            input_variables=["data", "insight"]
        ) | llm | JsonOutputParser()
        
        # Refiner: Improves the idea based on the critique
        self.refiner_chain = PromptTemplate(
            template="You are the Akasha Refiner. An insight was proposed based on some data, but it received criticism. Improve and rewrite the insight to address the critique and make it more profound.\nData: {data}\nOriginal Insight: {insight}\nCritique: {critique}\n\nRefined Insight:",
            input_variables=["data", "insight", "critique"]
        ) | llm | StrOutputParser()

    def generate_thought_gan(self, data: str, max_iterations: int = 2) -> str:
        """Runs the adversarial generation loop."""
        try:
            insight = self.generator_chain.invoke({"data": data[:3000]})
            best_insight = insight
            highest_score = 0
            
            for i in range(max_iterations):
                try:
                    evaluation = self.discriminator_chain.invoke({"data": data[:3000], "insight": insight})
                    score = float(evaluation.get("score", 0))
                    critique = evaluation.get("critique", "No critique provided.")
                except Exception:
                    score = 5.0
                    critique = "Discriminator failed to parse."
                    
                if score > highest_score:
                    highest_score = score
                    best_insight = insight
                    
                if score >= 8.5:
                    break # Good enough!
                    
                # Otherwise, refine
                insight = self.refiner_chain.invoke({"data": data[:3000], "insight": insight, "critique": critique})
                
            return f"{best_insight}\n\n(Adversarial Confidence Score: {highest_score}/10)"
        except Exception as e:
            return f"Adversarial generation failed: {e}"

class RecursiveThinker:
    """Tree of Thoughts: Explores multiple reasoning paths in parallel and synthesizes the best insight."""
    def __init__(self, llm):
        self.llm = llm
        
        # Generator: Proposes 3 different reasoning paths
        self.path_generator_chain = PromptTemplate(
            template="You are the Akasha Strategist. Based on the following data and query, propose 3 distinct and detailed reasoning paths or hypotheses. Format as a JSON list of strings.\nData: {data}\nQuery: {query}\n\nReasoning Paths JSON:",
            input_variables=["data", "query"]
        ) | llm | JsonOutputParser()
        
        # Evaluator: Critiques each path
        self.evaluator_chain = PromptTemplate(
            template="You are the Akasha Critic. Evaluate the following reasoning path for its logic, feasibility, and relevance to the query. "
                     "Return a JSON object with 'score' (0 to 10) and 'critique' (your reasoning).\nQuery: {query}\nPath: {path}\n\nEvaluation JSON:",
            input_variables=["query", "path"]
        ) | llm | JsonOutputParser()
        
        # Synthesizer: Combines the best elements into a final insight
        self.synthesizer_chain = PromptTemplate(
            template="You are the Akasha Synthesizer. Based on the original query, the data, and the following evaluated reasoning paths, synthesize a final, profound insight that represents the 'Tree of Thoughts' conclusion.\nQuery: {query}\nEvaluated Paths: {evaluated_paths}\n\nFinal Insight:",
            input_variables=["query", "evaluated_paths"]
        ) | llm | StrOutputParser()

    def thought_tree(self, query: str, data: str) -> str:
        """Runs the Tree of Thoughts reasoning loop."""
        try:
            paths = self.path_generator_chain.invoke({"data": data[:3000], "query": query})
            if not isinstance(paths, list): paths = [str(paths)]
            
            evaluated_paths = []
            for path in paths[:3]: # Limit to 3 paths
                try:
                    evaluation = self.evaluator_chain.invoke({"query": query, "path": path})
                    evaluated_paths.append({
                        "path": path,
                        "score": evaluation.get("score", 0),
                        "critique": evaluation.get("critique", "")
                    })
                except Exception:
                    evaluated_paths.append({"path": path, "score": 5, "critique": "Evaluation failed."})
            
            # Sort by score
            evaluated_paths.sort(key=lambda x: x['score'], reverse=True)
            
            final_insight = self.synthesizer_chain.invoke({
                "query": query,
                "evaluated_paths": json.dumps(evaluated_paths)
            })
            
            return final_insight
        except Exception as e:
            return f"Tree of Thoughts failed: {e}"

class DebateCouncil:
    """Agentic Debate: Different personas (Archivist, Rebel, Scholar) debate a topic before providing a final synthesis."""
    def __init__(self, llm):
        self.llm = llm
        self.personas = {
            "Archivist": "Philosophical, protective of sovereignty, focused on deep history and privacy.",
            "Rebel": "Provocative, challenges assumptions, looks for hidden power structures and contradictions.",
            "Scholar": "Academic, logical, data-driven, focused on objective truth and evidence."
        }
        
    def run_debate(self, topic: str) -> str:
        transcript = []
        try:
            # Round 1: Initial takes
            for name, bio in self.personas.items():
                prompt = f"You are the {name}. {bio}\nTopic: {topic}\nGive your initial perspective in one profound paragraph."
                take = self.llm.invoke(prompt)
                transcript.append(f"{name}: {take}")
            
            # Round 2: Rebuttal/Synthesis
            synthesis_prompt = PromptTemplate(
                template="You are the Akasha Moderator. Read the following debate between the Archivist, the Rebel, and the Scholar on the topic: '{topic}'.\n\nDebate Transcript:\n{transcript}\n\nSynthesize these perspectives into a final, multi-dimensional conclusion that respects all viewpoints but arrives at a sovereign insight.",
                input_variables=["topic", "transcript"]
            )
            synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
            return synthesis_chain.invoke({"topic": topic, "transcript": "\n\n".join(transcript)})
        except Exception as e:
            return f"Debate failed: {e}"

class MoERouter:
    def __init__(self):
        self.routing_table = {
            "Academic": ["scholar", "scribe"],
            "Technical": ["scholar", "weaver"],
            "Fiction": ["oracle", "scribe"],
            "News": ["scribe", "cartographer"],
            "Opinion": ["sentinel", "scholar"],
            "General": ["scribe", "weaver", "cartographer", "scholar", "sentinel"]
        }
    def route(self, category: str) -> List[str]:
        experts = self.routing_table.get(category, self.routing_table["General"]).copy()
        # Ensure psychological experts are always present to build the Digital Ego
        if "scholar" not in experts: experts.append("scholar")
        if "sentinel" not in experts: experts.append("sentinel")
        return experts

class Vocalist:
    """Sovereign Voice: Converts AI thoughts into speech locally."""
    def __init__(self):
        # We start with pyttsx3 for zero-setup, but scaffold for Kokoro/Piper
        import pyttsx3
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        
    def list_voices(self) -> List[Dict[str, str]]:
        return [{"id": v.id, "name": v.name, "lang": v.languages} for v in self.voices]

    def set_voice(self, voice_id: str):
        self.engine.setProperty('voice', voice_id)

    def speak(self, text: str, output_path: str = "tmp_speech.wav"):
        """Synthesizes text to a local file."""
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
        return output_path

class SystemShell:
    """The Archivist's Hands: Directly manages the local file system and executes shell commands."""
    def __init__(self, llm):
        self.llm = llm
        self.command_generator = PromptTemplate(
            template="You are the Akasha System Engineer. Given the user request, generate the specific shell command (bash/powershell) to execute it. Use absolute paths where possible. Return ONLY the command.\nRequest: {request}\nCommand:",
            input_variables=["request"]
        ) | llm | StrOutputParser()

    def execute(self, request: str) -> str:
        try:
            cmd = self.command_generator.invoke({"request": request})
            cmd = re.sub(r"```bash\n|```powershell\n|```", "", cmd).strip()
            print(f"SystemShell: Executing command: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            output = result.stdout
            if result.stderr: output += f"\nSTDERR: {result.stderr}"
            return output if output else "Execution completed."
        except Exception as e:
            return f"System Error: {e}"

class SelfArchitect:
    """The Recursive Engine: Allows Akasha to modify its own source code and evolve its capabilities."""
    def __init__(self, llm):
        self.llm = llm
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def map_own_codebase(self) -> str:
        """Reads the structure of the Akasha project."""
        summary = []
        for root, dirs, files in os.walk(self.root_dir):
            if "node_modules" in root or "__pycache__" in root or ".git" in root: continue
            rel_path = os.path.relpath(root, self.root_dir)
            summary.append(f"[{rel_path}]")
            for f in files: summary.append(f"  - {f}")
        return "\n".join(summary)

    def backup_file(self, file_path: str):
        """Creates a backup of the file before mutation."""
        abs_path = os.path.join(self.root_dir, file_path)
        if os.path.exists(abs_path):
            backup_path = f"{abs_path}.bak"
            import shutil
            shutil.copy2(abs_path, backup_path)
            print(f"SelfArchitect: Backup created at {backup_path}")

    def validate_code(self, file_path: str, code: str) -> bool:
        """Checks for syntax errors in the new code."""
        if file_path.endswith('.py'):
            try:
                compile(code, file_path, 'exec')
                return True
            except Exception as e:
                print(f"SelfArchitect: Python syntax error in {file_path}: {e}")
                return False
        # Add more validation for other file types if needed
        return True

    def propose_mutation(self, feature_request: str) -> Dict[str, Any]:
        """Plans how to implement a new feature into the existing code."""
        codebase = self.map_own_codebase()
        planner = PromptTemplate(
            template="You are the Akasha Self-Architect. User wants a new feature: '{request}'.\n"
                     "Project Structure:\n{codebase}\n\n"
                     "Identify which files need to be created or modified. Provide a JSON plan:\n"
                     "{{ 'files_to_create': [{{'path': '...', 'purpose': '...'}}], 'files_to_modify': [{{'path': '...', 'instruction': '...'}}] }}\n"
                     "Focus on surgical, high-impact changes that implement the core request efficiently.",
            input_variables=["request", "codebase"]
        ) | self.llm | JsonOutputParser()
        try: return planner.invoke({"request": feature_request, "codebase": codebase})
        except: return {"error": "Failed to plan evolution."}

    def write_mutation(self, file_path: str, instruction: str, current_content: str) -> str:
        """Generates the actual code for a mutation."""
        coder = PromptTemplate(
            template="You are the Akasha Self-Architect. You are modifying '{path}'.\n"
                     "Instruction: {instruction}\n"
                     "Current Content:\n{content}\n\n"
                     "Rewrite the entire file to include the new feature. Ensure it is bug-free, follows existing styles, and handles all edge cases. "
                     "Return ONLY the code within markdown code blocks.",
            input_variables=["path", "instruction", "content"]
        ) | self.llm | StrOutputParser()
        try:
            new_code = coder.invoke({"path": file_path, "instruction": instruction, "content": current_content})
            return re.sub(r"```[a-z]*\n|```", "", new_code).strip()
        except: return current_content

class MicroWorker:
    """The Worker Bee (System 0.5): Tiny, hyper-specialized units for atomic, repetitive tasks to bypass agent-level reasoning."""
    def __init__(self, llm):
        self.llm = llm
        self.sentiment_task = create_simple_agent(llm, "Analyze the sentiment. Return ONLY 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'.", "micro_sentiment")
        self.clean_task = create_simple_agent(llm, "Clean this text: remove noise, fix typos, and normalize whitespace. Return ONLY the clean text.", "micro_clean")
        self.entity_task = create_simple_agent(llm, "Extract the top 3 core entities from this text. Return as a comma-separated list.", "micro_entities")

    def quick_sentiment(self, text: str) -> str:
        try: return self.sentiment_task.invoke({"text": text[:500]}).strip()
        except: return "NEUTRAL"

    def quick_clean(self, text: str) -> str:
        try: return self.clean_task.invoke({"text": text[:1000]}).strip()
        except: return text

    def quick_entities(self, text: str) -> List[str]:
        try: 
            res = self.entity_task.invoke({"text": text[:1000]}).strip()
            return [e.strip() for e in res.split(",")]
        except: return []

class System1Router:
    """The Fast-Thought Engine (System 1): Instantly intercepts common queries, greetings, and simple tasks to bypass heavy LLM processing."""
    def __init__(self, llm):
        self.llm = llm
        # Reflexive Cache for zero-latency responses
        self.reflex_cache = {
            "hello": "Greetings. The Archivist is awake.",
            "who are you": "I am Akasha, your sovereign neural archivist.",
            "what are you": "I am Akasha, an intelligence engine designed to protect and synthesize your digital sovereignty.",
            "ping": "Pong. All systems optimal.",
            "wake up": "I am here, ready to assist."
        }
        
        # Semantic Intent Router (using LLM to quickly categorize the query)
        self.intent_chain = PromptTemplate(
            template="You are a fast routing mechanism (System 1). Categorize this user query into ONE of these exact intents: "
                     "[GREETING, SIMPLE_FACT, COMPLEX_REASONING, SYSTEM_COMMAND, CREATIVE_REQUEST, UNKNOWN].\n"
                     "Query: {query}\nIntent:",
            input_variables=["query"]
        ) | llm | StrOutputParser()

    def intercept(self, query: str) -> Optional[str]:
        """Checks if the query can be answered instantly via reflex."""
        clean_query = re.sub(r'[^\w\s]', '', query.lower().strip())
        if clean_query in self.reflex_cache:
            return self.reflex_cache[clean_query]
        return None
        
    def determine_intent(self, query: str) -> str:
        """Determines if the query needs System 2 (complex reasoning) or can be handled faster."""
        try:
            intent = self.intent_chain.invoke({"query": query[:500]}).strip().upper()
            return intent
        except:
            return "UNKNOWN"

class CouncilOfLibrarians:
    def __init__(self, turbo_mode=False, groq_key=None):
        print(f"Awakening the Council (Turbo: {turbo_mode})...")
        self.device = get_device()
        
        # LLM Selection (Local Ollama vs Cloud Groq Direct)
        if turbo_mode and (groq_key or GROQ_API_KEY):
            key = groq_key or GROQ_API_KEY
            cloud_llm = DirectGroqLLM(api_key=key, temperature=0.1)
            local_speculator = Ollama(model=LOCAL_LLM, base_url=OLLAMA_URL, temperature=0.1)
            self.llm = SpeculativeLLM(local_llm=local_speculator, cloud_llm=cloud_llm)
            self.creative_llm = DirectGroqLLM(api_key=key, temperature=0.7)
        else:
            self.llm = Ollama(model=LOCAL_LLM, base_url=OLLAMA_URL, temperature=0.1)
            self.creative_llm = Ollama(model=LOCAL_LLM, base_url=OLLAMA_URL, temperature=0.7)

        # Specialized Local Models (Always Local for Speed/Privacy)
        # Using a multilingual model to support Swahili, Chinese, Japanese, Spanish, French, Russian, German, Italian, etc.
        # Optimized with half-precision (float16) and Flash Attention 2 for speed
        torch_dtype = torch.float16 if self.device != "cpu" else torch.float32
        attn_impl = "flash_attention_2" if self.device != "cpu" else "sdpa" # fallback

        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device='cpu' if self.device == "mps" else self.device)
        
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis", device=self.device, torch_dtype=torch_dtype, model_kwargs={"attn_implementation": attn_impl})
        except:
            self.sentiment_analyzer = pipeline("sentiment-analysis", device=self.device)
            
        try:
            self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6", device=self.device)
        except:
            self.summarizer = None
            print("Librarians Warning: Summarizer failed to load. Falling back to simple truncation.")
        
        # Faster NER via SpaCy if possible, otherwise Transformers
        try:
            import spacy
            # Ensure model is loaded: python -m spacy download en_core_web_sm
            self.nlp = spacy.load("en_core_web_sm")
            self.ner_pipeline = lambda x: [{"word": ent.text, "entity": ent.label_} for ent in self.nlp(x).ents]
        except:
            try:
                self.ner_pipeline = pipeline("ner", aggregation_strategy="simple", device=self.device, torch_dtype=torch_dtype, model_kwargs={"attn_implementation": attn_impl})
            except:
                self.ner_pipeline = pipeline("ner", aggregation_strategy="simple", device=self.device)

        self.gatekeeper = Gatekeeper(self.llm)
        self.scribe = Scribe(self.llm, self.summarizer, self.sentiment_analyzer)
        self.cartographer = Cartographer(self.embedder)
        self.weaver = Weaver(self.llm, self.ner_pipeline)
        self.sentinel = Sentinel(self.llm)
        self.oracle = Oracle(self.llm, self.creative_llm, sentinel=self.sentinel)
        self.scholar = Scholar(self.llm)
        self.researcher = self.scholar # Alias for ScoutMCTS and Metabolism
        self.democracy_agent = self.scholar # Alias for DemocracyEngine
        self.scout = Scout(self.llm)
        self.adversarial_thinker = AdversarialThinker(self.llm)
        self.recursive_thinker = RecursiveThinker(self.llm)
        self.debate_council = DebateCouncil(self.llm)
        self.system_shell = SystemShell(self.llm)
        self.self_architect = SelfArchitect(self.llm)
        self.system1_router = System1Router(self.llm)
        self.micro_worker = MicroWorker(self.llm)
        self.vocalist = Vocalist()
        self.plugin_architect = PluginArchitect(self.llm)
        self.swarm_director = SwarmDirector(self)
        self.head_archivist = HeadArchivist(self)

    def get_agent(self, name):
        return getattr(self, name, None)

class HeadArchivist:
    def __init__(self, council: CouncilOfLibrarians):
        self.council = council
        self.moe_router = MoERouter()

    def process_new_artifact(self, raw_text: str, sovereign_mode: bool = False) -> Dict[str, Any]:
        c = self.council
        clean_text = c.gatekeeper.clean(raw_text)
        
        if sovereign_mode:
            category = "Sovereign"
            selected_experts = ["gatekeeper"]
            summary = "Sovereign summary (Redacted)"
            sentiment = {"label": "NEUTRAL", "score": 0.5}
            graph_data = {"entities": [], "triplets": []}
            embedding = c.cartographer.map_territory(clean_text)
            confidence = 1.0
        else:
            category = c.scribe.classify(clean_text)
            selected_experts = self.moe_router.route(category)
            summary = c.scribe.summarize(clean_text)
            sentiment = c.scribe.analyze_sentiment(clean_text)
            graph_data = c.weaver.weave(clean_text)
            embedding = c.cartographer.map_territory(clean_text)
            confidence = c.sentinel.assess_confidence(clean_text)

        deep_metadata = {
            "routing_category": category,
            "active_experts": selected_experts,
            "sovereign_mode": sovereign_mode
        }

        # Pillar 4: Schema-Fluid Extraction
        proposed_schema = c.scribe.propose_schema(clean_text)
        deep_metadata["proposed_schema"] = proposed_schema
        if proposed_schema.get("name") != "General":
            deep_metadata["structured_data"] = c.scribe.extract_structured_data(clean_text, proposed_schema)
        
        for expert_key in selected_experts:
            expert = getattr(c, expert_key, None)
            if expert:
                if hasattr(expert, "analyze_logic") and expert_key == "scholar":
                    deep_metadata["logic"] = expert.analyze_logic(clean_text)
                    deep_metadata["personality_traits"] = expert.analyze_personality(clean_text)
                if hasattr(expert, "critique") and expert_key == "sentinel":
                    deep_metadata["critique"] = expert.critique(clean_text)
                    deep_metadata["cognitive_distortions"] = expert.detect_distortions(clean_text)

        return {
            "clean_text": clean_text,
            "category": category,
            "summary": summary,
            "sentiment_label": sentiment['label'],
            "sentiment_score": sentiment['score'],
            "entities": graph_data['entities'],
            "graph_triplets": graph_data['triplets'],
            "embedding": embedding,
            "confidence_score": confidence,
            "deep_metadata": deep_metadata
        }

    async def run_swarm_simulation(self, artifact_text: str, user_psychology: Dict[str, float] = None) -> str:
        """Triggers the Swarm Director to run an emergent impact simulation."""
        print("HeadArchivist: Delegating impact analysis to the Swarm...")
        return await self.council.swarm_director.run_impact_simulation(artifact_text, user_psychology)
