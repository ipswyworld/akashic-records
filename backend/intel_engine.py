from transformers import pipeline
import torch
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np
from typing import List, Dict

from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import datetime

from sklearn.cluster import KMeans
from collections import Counter
import re

from sklearn.svm import OneClassSVM
try:
    import xgboost as xgb
except ImportError:
    xgb = None
import hashlib

class IntelEngine:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 1. Automated Summarization (DistilBART)
        self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=device)
        
        # 2. Cross-Lingual Translation (MarianMT)
        self.translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr", device=device)
        
        # 3. Anomaly Detection (Isolation Forest & SVM)
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.immune_svm = OneClassSVM(kernel='rbf', gamma=0.1, nu=0.05)

        # 4. NLI - Phase 3
        try:
            self.nli_pipeline = pipeline("text-classification", model="cross-encoder/nli-deberta-v3-base", device=device)
        except Exception:
            self.nli_pipeline = None

        # 5. Cognitive State HMM (Transitions: Focus, Research, Idle)
        self.state_transitions = np.array([
            [0.7, 0.2, 0.1], # From Focus
            [0.3, 0.6, 0.1], # From Research
            [0.1, 0.3, 0.6]  # From Idle
        ])
        self.current_state = 2 # Start at Idle

    def extract_user_name(self, text: str) -> str:
        """Extracts user name from text (e.g., 'My name is JB')."""
        patterns = [
            r"(?:my name is|i'm|i am|call me) ([\w\s]+)",
            r"this is ([\w\s]+) speaking"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Simple cleanup: take only the first two words if they exist
                parts = name.split()
                if len(parts) > 2:
                    name = " ".join(parts[:2])
                return name.title()
        return None

    def calculate_simhash(self, text: str) -> str:
        """Rapid near-duplicate detection using 64-bit SimHash."""
        features = re.findall(r'\w+', text.lower())
        if not features: return "0x0"
        
        v = [0] * 64
        for f in features:
            h = int(hashlib.md5(f.encode()).hexdigest(), 16)
            for i in range(64):
                bit = (h >> i) & 1
                if bit: v[i] += 1
                else: v[i] -= 1
        
        fingerprint = 0
        for i in range(64):
            if v[i] >= 0:
                fingerprint |= (1 << i)
        return hex(fingerprint)

    def detect_immune_threat(self, embeddings: List[List[float]]) -> bool:
        """One-Class SVM to detect if new data violates pod topology (Anomaly Detection)."""
        if len(embeddings) < 5: return False
        
        # Train on historical embeddings (excluding the latest one)
        train_data = np.array(embeddings[:-1])
        new_data = np.array([embeddings[-1]])
        
        try:
            self.immune_svm.fit(train_data)
            prediction = self.immune_svm.predict(new_data)
            return prediction[0] == -1 # True if outlier/threat
        except Exception:
            return False

    def infer_cognitive_state(self, activity_intensity: float) -> str:
        """HMM-based cognitive state inference using Viterbi-like transition logic."""
        states = ["DEEP_WORK", "EXPLORATORY_RESEARCH", "PASSIVE_IDLE"]
        
        # Observation probabilities (Mocked for intensity)
        # Deep Work: High intensity
        # Research: Medium intensity
        # Idle: Low intensity
        
        obs_probs = [
            0.9 if activity_intensity > 0.8 else 0.1, # DEEP_WORK
            0.8 if 0.4 <= activity_intensity <= 0.8 else 0.2, # EXPLORATORY_RESEARCH
            0.9 if activity_intensity < 0.4 else 0.1  # PASSIVE_IDLE
        ]
        
        # Calculate next state probabilities: P(S_t | S_{t-1}) * P(O_t | S_t)
        next_probs = self.state_transitions[self.current_state] * obs_probs
        self.current_state = np.argmax(next_probs)
        
        return states[self.current_state]

    def calculate_iit_consciousness(self, graph_metrics: Dict) -> float:
        """Calculates a 'Phi' score (Integrated Information Theory) for the pod."""
        # Phi is high when integration (PageRank density) and diversity (Louvain clusters) are both high
        top_influencers = graph_metrics.get('top_influencers', [])
        integration = np.mean([m['score'] for m in top_influencers]) if top_influencers else 0.1
        
        clusters = graph_metrics.get('thematic_clusters', {})
        diversity = len(clusters) if clusters else 1
        
        # Complexity = Integration * Diversity (simplified IIT)
        phi = integration * diversity * 10
        return round(float(phi), 2)

    # ... (keep all existing forecast/topic modeling methods)

    def summarize(self, text: str) -> str:
        """Create a 'Daily Spirit' summary of memories."""
        if len(text) < 100:
            return text
        try:
            summary = self.summarizer(text[:1024], max_length=50, min_length=10, do_sample=False)
            return summary[0]['summary_text']
        except Exception:
            return text[:100] + "..."

    def translate_to_french(self, text: str) -> str:
        """Example translation (Cross-Lingual Access)."""
        try:
            translated = self.translator(text[:512])
            return translated[0]['translation_text']
        except Exception:
            return text

    def detect_anomalies(self, embeddings: List[List[float]]) -> List[int]:
        """Detect 'false' or outlier memories in the vector space."""
        if len(embeddings) < 5:
            return [1] * len(embeddings)
        df = pd.DataFrame(embeddings)
        # Returns 1 for inliers, -1 for outliers
        return self.anomaly_detector.fit_predict(df).tolist()

    def determine_causality(self, mem1: str, mem2: str) -> str:
        """Mock Causal Inference Engine logic."""
        # In production, use causal-graph models like CausalNex
        return "Nexus Probability: 0.85 (Related Threads Detected)"

    def analyze_graph_topology(self, graph_engine, user_id: str) -> Dict:
        """Orchestrates GDS algorithms to understand the user's graph structure."""
        if not graph_engine or not graph_engine.is_active:
            return {"error": "GraphEngine is inactive."}
            
        print(f"IntelEngine: Initiating Topological Analysis for user {user_id}...")
        
        # 1. Run the algorithms (writes to Neo4j)
        graph_engine.run_graph_topology_analytics(user_id)
        
        # 2. Retrieve metrics
        metrics = graph_engine.get_topology_metrics(user_id)
        
        # 3. Add 'Intelligence' interpretation
        summary = f"Identified {len(metrics['top_influencers'])} key influencers and {len(metrics['thematic_clusters'])} major thematic clusters."
        metrics["intelligence_summary"] = summary
        
        return metrics

    # --- Temporal Analytical Intelligence (Phase 2) ---

    def forecast_interests(self, record_history: List[Dict]) -> Dict:
        """Forecasts future interest trends using Linear Regression on entity frequencies."""
        if len(record_history) < 5: return {"error": "Insufficient history for forecasting."}
        
        df = pd.DataFrame(record_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Aggregate top entities per day
        entity_counts = []
        for _, row in df.iterrows():
            entities = row.get('metadata', {}).get('entities', [])
            for ent in entities:
                entity_counts.append({'date': row['date'], 'entity': ent})
        
        if not entity_counts: return {"forecast": []}
        
        edf = pd.DataFrame(entity_counts)
        # Get top 5 entities
        top_ents = edf['entity'].value_counts().head(5).index.tolist()
        
        forecasts = []
        for ent in top_ents:
            # Time-series for this entity
            ent_ts = edf[edf['entity'] == ent].groupby('date').size().reset_index(name='count')
            ent_ts['day_num'] = (ent_ts['date'] - ent_ts['date'].min()).apply(lambda x: x.days)
            
            if len(ent_ts) < 2: continue
            
            # Simple Linear Regression
            X = ent_ts[['day_num']]
            y = ent_ts['count']
            model = LinearRegression().fit(X, y)
            
            # Predict for next 7 days
            next_day = ent_ts['day_num'].max() + 7
            prediction = model.predict([[next_day]])[0]
            
            forecasts.append({
                "entity": ent,
                "current_trend": "UP" if model.coef_[0] > 0 else "DOWN",
                "predicted_intensity": max(0, round(float(prediction), 2)),
                "growth_rate": round(float(model.coef_[0]), 4)
            })
            
        return {"forecast": sorted(forecasts, key=lambda x: x['growth_rate'], reverse=True)}

    def detect_interest_shifts(self, record_history: List[Dict]) -> List[Dict]:
        """Detects sudden 'Change Points' in topic engagement."""
        if len(record_history) < 10: return []
        
        df = pd.DataFrame(record_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Simple rolling window volatility
        shifts = []
        # Group by category over time
        df['week'] = df['timestamp'].dt.isocalendar().week
        cat_trends = df.groupby(['week', 'artifact_type']).size().unstack(fill_value=0)
        
        if len(cat_trends) < 2: return []
        
        # Detect sudden drops or spikes
        diff = cat_trends.diff().iloc[-1]
        for cat, change in diff.items():
            if abs(change) > 2: # Threshold for 'significant shift'
                shifts.append({
                    "category": cat,
                    "magnitude": int(change),
                    "type": "SPIKE" if change > 0 else "DROP",
                    "description": f"Significant {cat} interest {'increase' if change > 0 else 'decrease'} detected."
                })
        
        return shifts

    def calculate_knowledge_survival(self, record_history: List[Dict]) -> Dict:
        """Predicts the relevance 'shelf-life' of the knowledge base."""
        if not record_history: return {"stability": 1.0}
        
        # Stability is the inverse of volatility
        # We calculate the mean time between updates
        df = pd.DataFrame(record_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        if len(df) < 2: return {"stability": 1.0, "shelf_life": "UNKNOWN"}
        
        time_diffs = df['timestamp'].diff().dropna().dt.total_seconds()
        mean_diff = time_diffs.mean()
        
        # Stability score: 1.0 (Low turnover) to 0.0 (High turnover)
        stability = 1.0 / (1.0 + (mean_diff / 86400)) # Normalized by day
        
        return {
            "mental_stability_score": round(stability, 2),
            "avg_memory_duration_days": round(mean_diff / 86400, 2),
            "entropy": round(1.0 - stability, 4)
        }

    # --- Deep Semantics & NLP (Phase 3) ---

    def perform_topic_modeling(self, embeddings: List[List[float]], texts: List[str], n_topics: int = 5) -> Dict:
        """Cluster-based topic modeling. Fallback for BERTopic."""
        if len(embeddings) < n_topics: return {"topics": []}
        
        # 1. Cluster embeddings using KMeans
        kmeans = KMeans(n_clusters=n_topics, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        
        # 2. Extract representative terms for each cluster (Tf-Idf style logic)
        topics = []
        for i in range(n_topics):
            cluster_texts = [texts[idx] for idx, label in enumerate(labels) if label == i]
            if not cluster_texts: continue
            
            # Simple word count as keyword extraction
            words = re.findall(r'\b\w{4,}\b', " ".join(cluster_texts).lower())
            top_words = [w for w, _ in Counter(words).most_common(5)]
            
            topics.append({
                "topic_id": i,
                "keywords": top_words,
                "count": len(cluster_texts)
            })
            
        return {"topics": topics, "assignments": labels.tolist()}

    def score_contradiction(self, prem: str, hyp: str) -> float:
        """Mathematically score the contradiction probability using NLI."""
        if not self.nli_pipeline: return 0.5
        
        try:
            # Format for NLI (premise, hypothesis)
            result = self.nli_pipeline({"text": prem[:500], "text_pair": hyp[:500]})
            # result is [{'label': 'LABEL_X', 'score': 0.YY}, ...]
            # Assuming labels are 0: entailment, 1: neutral, 2: contradiction
            # The model cross-encoder/nli-deberta-v3-base uses 'entailment', 'neutral', 'contradiction'
            for r in result:
                if r['label'] == 'contradiction':
                    return r['score']
        except Exception:
            return 0.5
        return 0.0

    def calculate_stylometry(self, text: str) -> Dict:
        """Calculate basic stylistic markers (TTR, sentence complexity)."""
        words = re.findall(r'\b\w+\b', text.lower())
        sentences = re.split(r'[.!?]+', text)
        
        if not words or not sentences: return {}
        
        unique_words = set(words)
        ttr = len(unique_words) / len(words) # Type-Token Ratio
        avg_sent_len = len(words) / len(sentences)
        
        # Word length distribution
        avg_word_len = sum(len(w) for w in words) / len(words)
        
        return {
            "type_token_ratio": round(ttr, 4),
            "avg_sentence_length": round(avg_sent_len, 2),
            "avg_word_length": round(avg_word_len, 2),
            "lexical_diversity": "HIGH" if ttr > 0.6 else "MEDIUM" if ttr > 0.4 else "LOW"
        }

    # --- Temporal Analytical Intelligence (Phase 2) ---

    def forecast_interests(self, record_history: List[Dict]) -> Dict:
        """Forecasts future interest trends using Linear Regression on entity frequencies."""
        if len(record_history) < 5: return {"error": "Insufficient history for forecasting."}
        
        df = pd.DataFrame(record_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Aggregate top entities per day
        entity_counts = []
        for _, row in df.iterrows():
            entities = row.get('metadata', {}).get('entities', [])
            for ent in entities:
                entity_counts.append({'date': row['date'], 'entity': ent})
        
        if not entity_counts: return {"forecast": []}
        
        edf = pd.DataFrame(entity_counts)
        # Get top 5 entities
        top_ents = edf['entity'].value_counts().head(5).index.tolist()
        
        forecasts = []
        for ent in top_ents:
            # Time-series for this entity
            ent_ts = edf[edf['entity'] == ent].groupby('date').size().reset_index(name='count')
            ent_ts['day_num'] = (ent_ts['date'] - ent_ts['date'].min()).apply(lambda x: x.days)
            
            if len(ent_ts) < 2: continue
            
            # Simple Linear Regression
            X = ent_ts[['day_num']]
            y = ent_ts['count']
            model = LinearRegression().fit(X, y)
            
            # Predict for next 7 days
            next_day = ent_ts['day_num'].max() + 7
            prediction = model.predict([[next_day]])[0]
            
            forecasts.append({
                "entity": ent,
                "current_trend": "UP" if model.coef_[0] > 0 else "DOWN",
                "predicted_intensity": max(0, round(float(prediction), 2)),
                "growth_rate": round(float(model.coef_[0]), 4)
            })
            
        return {"forecast": sorted(forecasts, key=lambda x: x['growth_rate'], reverse=True)}

    def detect_interest_shifts(self, record_history: List[Dict]) -> List[Dict]:
        """Detects sudden 'Change Points' in topic engagement."""
        if len(record_history) < 10: return []
        
        df = pd.DataFrame(record_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Simple rolling window volatility
        shifts = []
        # Group by category over time
        df['week'] = df['timestamp'].dt.isocalendar().week
        cat_trends = df.groupby(['week', 'artifact_type']).size().unstack(fill_value=0)
        
        if len(cat_trends) < 2: return []
        
        # Detect sudden drops or spikes
        diff = cat_trends.diff().iloc[-1]
        for cat, change in diff.items():
            if abs(change) > 2: # Threshold for 'significant shift'
                shifts.append({
                    "category": cat,
                    "magnitude": int(change),
                    "type": "SPIKE" if change > 0 else "DROP",
                    "description": f"Significant {cat} interest {'increase' if change > 0 else 'decrease'} detected."
                })
        
        return shifts

    def calculate_knowledge_survival(self, record_history: List[Dict]) -> Dict:
        """Predicts the relevance 'shelf-life' of the knowledge base."""
        if not record_history: return {"stability": 1.0}
        
        # Stability is the inverse of volatility
        # We calculate the mean time between updates
        df = pd.DataFrame(record_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        if len(df) < 2: return {"stability": 1.0, "shelf_life": "UNKNOWN"}
        
        time_diffs = df['timestamp'].diff().dropna().dt.total_seconds()
        mean_diff = time_diffs.mean()
        
        # Stability score: 1.0 (Low turnover) to 0.0 (High turnover)
        stability = 1.0 / (1.0 + (mean_diff / 86400)) # Normalized by day
        
        return {
            "mental_stability_score": round(stability, 2),
            "avg_memory_duration_days": round(mean_diff / 86400, 2),
            "entropy": round(1.0 - stability, 4)
        }
