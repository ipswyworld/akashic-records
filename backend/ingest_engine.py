import feedparser
import requests
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image
import io
import os
import wikipedia
import arxiv
import asyncio
import whisper
import tempfile
import pandas as pd
import PyPDF2
from typing import List, Dict, Any

from connectors.professional import GitHubConnector, GmailConnector, JiraConnector
from connectors.cultural import SpotifyConnector, YouTubeConnector, KindleConnector
from connectors.physical import WeatherConnector
from connectors.digital import BrowserHistoryConnector, GoogleMapsConnector, SocialMediaConnector
from connectors.financial import PlaidConnector, CryptoConnector, SubscriptionConnector
from connectors.creative import GooglePhotosConnector, VoiceMemoConnector, JournalConnector

class SpeakerVerifier:
    """Neural Voice Fingerprinting: Identifies the owner by their vocal signature."""
    def __init__(self):
        # In a production environment, we would use 'speechbrain/spkrec-ecapa-voxceleb'
        # For this local, sovereign implementation, we use a lighter fingerprinting logic.
        self.enabled = True

    def extract_fingerprint(self, audio_bytes: bytes) -> List[float]:
        """Extracts a unique 128d vocal embedding from audio."""
        # MOCK: In a real implementation, this would use a pre-trained speaker model.
        # We simulate this by generating a consistent hash-based vector for now.
        import hashlib
        import numpy as np
        h = hashlib.sha256(audio_bytes).digest()
        vector = np.frombuffer(h, dtype=np.uint8).astype(float) / 255.0
        return np.tile(vector, 4).tolist()[:128] # Expand to 128d

    def verify(self, audio_bytes: bytes, reference_print: List[float], threshold: float = 0.85) -> bool:
        """Verifies if the audio matches the owner's fingerprint."""
        if not reference_print: return True # Default to True if no fingerprint enrolled
        
        current_print = self.extract_fingerprint(audio_bytes)
        # Calculate Cosine Similarity
        import numpy as np
        a = np.array(current_print)
        b = np.array(reference_print)
        similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        print(f"SpeakerVerifier: Voice similarity score: {similarity:.4f}")
        return similarity >= threshold

class LifeIngestEngine:
    """The central coordinator for 100+ personal life streams."""
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.connectors = [
            # Cluster 1: Professional
            GitHubConnector(user_id),
            GmailConnector(user_id),
            JiraConnector(user_id),
            # Cluster 2: Cultural
            SpotifyConnector(user_id),
            YouTubeConnector(user_id),
            KindleConnector(user_id),
            # Cluster 6: Physical
            WeatherConnector(user_id),
            # Cluster 4: Digital
            BrowserHistoryConnector(user_id),
            GoogleMapsConnector(user_id),
            SocialMediaConnector(user_id),
            # Cluster 5: Financial
            PlaidConnector(user_id),
            CryptoConnector(user_id),
            SubscriptionConnector(user_id),
            # Cluster 7: Creative
            GooglePhotosConnector(user_id),
            VoiceMemoConnector(user_id),
            JournalConnector(user_id)
        ]

    def run_all_syncs(self, db_session):
        results = {}
        for connector in self.connectors:
            try:
                count = connector.sync(db_session)
                results[connector.__class__.__name__] = count
            except Exception as e:
                print(f"Sync failed for {connector.__class__.__name__}: {e}")
        return results

class IngestEngine:
    def __init__(self, p2p_node=None):
        self.p2p = p2p_node
        self.default_rss_feeds = [
            "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
            "http://feeds.bbci.co.uk/news/world/rss.xml"
        ]
        self.stream_queue = asyncio.Queue()
        self.seen_urls = set()
        self.ingested_hashes = set()
        # Initialize whisper model lazily
        self._whisper_model = None
        self.life_engines = {} # user_id -> LifeIngestEngine

    def get_life_engine(self, user_id: str) -> LifeIngestEngine:
        if user_id not in self.life_engines:
            self.life_engines[user_id] = LifeIngestEngine(user_id)
        return self.life_engines[user_id]

    @property
    def whisper_model(self):
        if self._whisper_model is None:
            print("IngestEngine: Loading Whisper model (tiny)...")
            self._whisper_model = whisper.load_model("tiny")
        return self._whisper_model

    async def coordinate_forage(self, resource_url: str, pod_id: str = "global") -> bool:
        """Collaborative Foraging logic."""
        import hashlib
        from datetime import datetime
        resource_hash = hashlib.sha256(resource_url.encode()).hexdigest()
        if resource_hash in self.ingested_hashes: return False 
        if self.p2p:
            if self.p2p.intel.is_known(resource_hash): return False
            await self.p2p.broadcast_record({
                "type": "FORAGE_START",
                "pod_id": pod_id,
                "resource_hash": resource_hash,
                "timestamp": str(datetime.utcnow())
            })
        self.ingested_hashes.add(resource_hash)
        return True

    def fetch_latest_news(self) -> List[Dict]:
        """Polls default RSS feeds and extracts the latest news."""
        all_news = []
        for feed_url in self.default_rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]: # Limit to 5 per feed to avoid overwhelm
                    if entry.link not in self.seen_urls:
                        # Full scrape of the article content
                        scraped = self.scrape_web_memory(entry.link)
                        if "content" in scraped:
                            scraped["category"] = "news_article"
                            scraped["link"] = entry.link
                            all_news.append(scraped)
                            self.seen_urls.add(entry.link)
            except Exception as e:
                print(f"Failed to poll feed {feed_url}: {e}")
        return all_news

    def fetch_wikipedia_article(self, topic: str) -> Dict:
        try:
            page = wikipedia.page(topic, auto_suggest=False)
            return {"title": page.title, "content": page.content[:10000], "link": page.url, "category": "encyclopedia"}
        except Exception as e: return {"error": str(e)}

    def ingest_youtube_video(self, url: str) -> Dict:
        """YouTube-to-Vault: Extracts transcript and metadata from a YouTube video."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            import urllib.parse as urlparse
            
            # Extract video ID
            parsed_url = urlparse.urlparse(url)
            video_id = urlparse.parse_qs(parsed_url.query).get('v')
            if not video_id:
                video_id = parsed_url.path.split('/')[-1]
            else:
                video_id = video_id[0]

            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([t['text'] for t in transcript_list])
            
            return {
                "title": f"YouTube Transcript: {video_id}",
                "content": transcript_text,
                "link": url,
                "category": "video_transcript",
                "metadata": {"source": "youtube", "video_id": video_id}
            }
        except Exception as e:
            return {"error": f"YouTube ingestion failed: {e}"}

    def autonomous_web_scrape(self, topic: str, max_results: int = 5) -> List[Dict]:
        """Autonomous Web Scraper: Searches DDG and ingests the top results."""
        from duckduckgo_search import DDGS
        results = []
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(topic, max_results=max_results))
                urls = [r['href'] for r in search_results]
                
            for url in urls:
                scraped_data = self.scrape_web_memory(url)
                if "content" in scraped_data:
                    scraped_data["category"] = "web_research"
                    scraped_data["metadata"] = {"source": "autonomous_scrape", "topic": topic}
                    results.append(scraped_data)
        except Exception as e:
            print(f"Autonomous scrape failed: {e}")
        return results

    def fetch_arxiv_papers(self, query: str, max_results: int = 3) -> List[Dict]:
        try:
            client = arxiv.Client()
            search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
            return [{"title": r.title, "content": r.summary, "authors": [a.name for a in r.authors], "link": r.entry_id, "category": "academic_paper"} for r in client.results(search)]
        except: return []

    def scrape_web_memory(self, url: str) -> Dict:
        """
        Extracts clean text and title from a URL. 
        Uses Playwright for JS-heavy sites if available, falls back to BeautifulSoup.
        """
        try:
            # Try Playwright for dynamic content
            try:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    page.goto(url, timeout=15000)
                    # Wait for network idle or a specific time to let JS render
                    page.wait_for_timeout(2000) 
                    content = page.content()
                    title = page.title()
                    browser.close()
                    soup = BeautifulSoup(content, 'html.parser')
            except Exception as e:
                print(f"IngestEngine: Playwright failed or not installed, falling back to BeautifulSoup: {e}")
                headers = {"User-Agent": "Mozilla/5.0 AkashaArchivist/1.0"}
                response = requests.get(url, timeout=10, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else url

            # Clean the soup
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return {"title": title, "content": clean_text, "link": url}
        except Exception as e:
            return {"error": f"Scrape failed: {str(e)}"}

    async def transcribe_audio_memory(self, audio_bytes: bytes) -> str:
        """Transcribes audio data using OpenAI Whisper."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            # Transcription is CPU/GPU heavy, run in executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.whisper_model.transcribe, tmp_path)
            
            os.unlink(tmp_path)
            return result.get("text", "").strip()
        except Exception as e:
            return f"Transcription Failed: {str(e)}"

    def ocr_document(self, image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return pytesseract.image_to_string(image)
        except Exception as e: return f"OCR Error: {e}"

    async def sync_slack(self, token: str, channel_id: str) -> List[Dict]:
        """Mocks Slack ingestion using requests."""
        # In a real scenario, this would call Slack's conversations.history API
        print(f"Syncing Slack channel {channel_id}...")
        # Mocking response
        mock_messages = [
            {"text": "Hey team, don't forget the meeting at 3pm.", "user": "U123", "ts": "1700000000.001"},
            {"text": "I've uploaded the new project specs.", "user": "U456", "ts": "1700000005.002"}
        ]
        return [{"title": f"Slack Message: {m['ts']}", "content": m['text'], "artifact_type": "communication", "metadata": {"source": "slack", "user": m['user']}} for m in mock_messages]

    async def sync_calendar(self, user_id: str) -> List[Dict]:
        """Mocks Calendar ingestion."""
        print(f"Syncing Calendar for {user_id}...")
        # Mocking calendar events
        mock_events = [
            {"summary": "Project Alpha Review", "start": "2023-10-27T10:00:00Z", "end": "2023-10-27T11:00:00Z"},
            {"summary": "Lunch with Satoshi", "start": "2023-10-27T13:00:00Z", "end": "2023-10-27T14:00:00Z"}
        ]
        return [{"title": f"Calendar: {e['summary']}", "content": f"Event: {e['summary']} from {e['start']} to {e['end']}", "artifact_type": "event", "metadata": {"source": "calendar", "start": e['start']}} for e in mock_events]

    async def sync_email(self, imap_server: str, email_user: str, email_pass: str) -> List[Dict]:
        """Basic Email ingestion using imaplib."""
        import imaplib
        import email
        from email.header import decode_header
        
        print(f"Syncing Email for {email_user}...")
        artifacts = []
        try:
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(email_user, email_pass)
            mail.select("inbox")
            
            # Search for all emails
            status, messages = mail.search(None, 'ALL')
            # Get only last 5 for brevity
            msg_ids = messages[0].split()[-5:]
            
            for msg_id in msg_ids:
                res, msg_data = mail.fetch(msg_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()
                        
                        artifacts.append({
                            "title": f"Email: {subject}",
                            "content": body,
                            "artifact_type": "communication",
                            "metadata": {"source": "email", "from": msg["From"]}
                        })
            mail.logout()
        except Exception as e:
            print(f"Email sync failed: {e}")
            # Fallback to mock if it fails (e.g. no connection)
            artifacts.append({"title": "Email Sync Failed", "content": f"Error: {str(e)}", "artifact_type": "system_log"})
            
        return artifacts

    def start_directory_watcher(self, watch_path: str, user_id: str, db_callback):
        """MCP Foundation: Watches a local directory and auto-ingests new/modified files."""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        import time

        class AkashaMCPHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if not event.is_directory:
                    self.process(event.src_path)
            def on_created(self, event):
                if not event.is_directory:
                    self.process(event.src_path)
            def process(self, path):
                ext = os.path.splitext(path)[1].lower()
                if ext in ['.txt', '.md', '.py', '.js', '.csv', '.json', '.pdf', '.xlsx', '.xls', '.docx']:
                    print(f"MCP: Detected change in {path}. Ingesting...")
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        title = f"MCP Auto-Ingest: {os.path.basename(path)}"
                        asyncio.run_coroutine_threadsafe(
                            db_callback(title, content, "mcp_auto_ingest", {"path": path}, None, user_id),
                            asyncio.get_event_loop()
                        )
                    except Exception as e:
                        print(f"MCP Ingestion Error for {path}: {e}")

        os.makedirs(watch_path, exist_ok=True)
        observer = Observer()
        observer.schedule(AkashaMCPHandler(), watch_path, recursive=True)
        observer.start()
        print(f"MCP: Watching directory {watch_path} for real-time ingestion...")
        return observer

    def ingest_dataset(self, file_path: str, file_name: str, chunk_size: int = 50) -> List[Dict]:
        """Parses CSV, JSON, and PDF files into ingestible artifacts. Large datasets are chunked."""
        artifacts = []
        ext = os.path.splitext(file_name)[1].lower()
        
        try:
            if ext == '.csv':
                df = pd.read_csv(file_path)
                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i:i + chunk_size]
                    content = chunk.to_string()
                    artifacts.append({
                        "title": f"Dataset (CSV): {file_name} [Part {i//chunk_size + 1}]",
                        "content": content,
                        "artifact_type": "dataset",
                        "metadata": {"filename": file_name, "rows": len(chunk), "total_rows": len(df), "columns": list(df.columns)}
                    })
            elif ext == '.json':
                df = pd.read_json(file_path)
                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i:i + chunk_size]
                    content = chunk.to_string()
                    artifacts.append({
                        "title": f"Dataset (JSON): {file_name} [Part {i//chunk_size + 1}]",
                        "content": content,
                        "artifact_type": "dataset",
                        "metadata": {"filename": file_name, "rows": len(chunk), "total_rows": len(df)}
                    })
            elif ext == '.pdf':
                text = ""
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                artifacts.append({
                    "title": f"Dataset (PDF): {file_name}",
                    "content": text,
                    "artifact_type": "dataset",
                    "metadata": {"filename": file_name, "pages": len(reader.pages)}
                })
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i:i + chunk_size]
                    content = chunk.to_string()
                    artifacts.append({
                        "title": f"Dataset (Excel): {file_name} [Part {i//chunk_size + 1}]",
                        "content": content,
                        "artifact_type": "dataset",
                        "metadata": {"filename": file_name, "rows": len(chunk), "total_rows": len(df), "columns": list(df.columns)}
                    })
            elif ext == '.docx':
                import docx
                doc = docx.Document(file_path)
                full_text = []
                for para in doc.paragraphs:
                    full_text.append(para.text)
                content = "\n".join(full_text)
                artifacts.append({
                    "title": f"Document (Word): {file_name}",
                    "content": content,
                    "artifact_type": "dataset",
                    "metadata": {"filename": file_name, "paragraphs": len(doc.paragraphs)}
                })
            elif ext == '.doc':
                return [{"error": f"Legacy Word format (.doc) not directly supported. Please convert {file_name} to .docx for ingestion."}]
            else:
                return [{"error": f"Unsupported file type: {ext}"}]
        except Exception as e:
            return [{"error": f"Dataset parsing failed: {str(e)}"}]
            
        return artifacts
