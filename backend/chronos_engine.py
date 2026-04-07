import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

try:
    from langchain.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
except ImportError:
    pass

from models import UserTask, UserCalendarEvent, LibraryArtifact, UserPsychology
from database import SessionLocal

logger = logging.getLogger(__name__)

class ChronosEngine:
    """
    Temporal Reasoning Engine: The 'Pulse' of Akasha.
    Handles proactive reminders, daily planning, and deadline detection.
    """
    def __init__(self, ai_engine, pod_manager, executive=None):
        self.ai = ai_engine
        self.pod_manager = pod_manager
        self.executive = executive
        # APScheduler could be initialized here or in main.py
        
    async def trigger_temporal_actions(self, user_id: str):
        """
        Analyzes the current temporal state and triggers autonomous actions 
        via the Executive Butler.
        """
        if not self.executive: return
        
        logger.info(f"Chronos: Analyzing temporal goals for {user_id}...")
        
        # 1. Check for upcoming deadlines
        alerts = await self.detect_temporal_deadlines(user_id)
        for alert in alerts:
            # Trigger the butler to act on these alerts
            goal = f"Urgent deadline approaching for task: {alert['description']}. Remind the user immediately."
            await self.executive.butler.evaluate_and_act(goal, alert)
            
        # 2. Daily Routine Logic (Mock)
        now = datetime.utcnow()
        if now.hour == 9 and now.minute < 10:
            # Morning Briefing Trigger
            await self.executive.butler.evaluate_and_act(
                "Morning briefing is ready. Provide a summary of today's priorities.", 
                {"context": "MORNING_ROUTINE"}
            )
        
    async def run_knowledge_gap_analysis(self, user_id: str) -> Optional[str]:
        """
        Proactively scans the user's recent artifacts to identify missing knowledge gaps.
        """
        db: Session = SessionLocal()
        try:
            # Fetch recent artifacts
            time_threshold = datetime.utcnow() - timedelta(days=3)
            recent_artifacts = db.query(LibraryArtifact).filter(
                LibraryArtifact.user_id == user_id,
                LibraryArtifact.timestamp >= time_threshold
            ).all()

            if len(recent_artifacts) < 3:
                return None

            context = [a.content for a in recent_artifacts]
            
            # Use Sentinel to find gaps
            gap = self.ai.council.sentinel.analyze_gaps(context)
            if gap and "No gaps detected" not in gap:
                logger.info(f"Chronos: Knowledge Gap detected for {user_id}: {gap}")
                return gap
            return None
        except Exception as e:
            logger.error(f"Chronos: Knowledge gap analysis failed: {e}")
            return None
        finally:
            db.close()

    async def run_observer_intel(self, user_id: str, db_session: Session) -> str:
        """
        The Observer Background Loop: Finds new web intel based on user interests.
        """
        try:
            from graph_engine import GraphEngine
            from ingest_engine import IngestEngine
            
            # 1. Get User Psychology (Ego)
            psych = db_session.query(UserPsychology).filter(UserPsychology.user_id == user_id).first()
            ego_context = "Neutral"
            if psych:
                ego_context = f"Openness: {psych.openness}, Conscientiousness: {psych.conscientiousness}, Extraversion: {psych.extraversion}, Agreeableness: {psych.agreeableness}, Neuroticism: {psych.neuroticism}"
            
            # 2. Get Top Entities from Graph
            graph = GraphEngine()
            metrics = graph.get_topology_metrics(user_id)
            top_entities = [m['name'] for m in metrics.get("top_influencers", [])[:5]]
            entities_str = ", ".join(top_entities) if top_entities else "General Knowledge"
            
            # 3. Deduce an interesting emerging topic
            topic_prompt = PromptTemplate(
                template="Based on the user's psychological profile and their core interests (top entities), deduce one highly interesting, emerging, and specific research topic that the user would likely find fascinating right now. Return ONLY the topic string.\nUser Profile: {ego}\nTop Interests: {entities}\nEmerging Topic:",
                input_variables=["ego", "entities"]
            )
            topic_chain = topic_prompt | self.ai.council.llm | StrOutputParser()
            
            loop = asyncio.get_event_loop()
            topic = await loop.run_in_executor(None, topic_chain.invoke, {"ego": ego_context, "entities": entities_str})
            topic = topic.strip()
            
            logger.info(f"Chronos Observer: Deduced topic '{topic}' for {user_id}")
            
            # 4. Use Scout to find 2-3 new articles
            ingest = IngestEngine()
            intel_briefing = await loop.run_in_executor(None, self.ai.council.scout.deep_research, topic, ingest)
            
            # 5. Automated Ingestion: Store the forage as a research_report artifact
            from models import LibraryArtifact
            new_artifact = LibraryArtifact(
                user_id=user_id,
                title=f"Proactive Forage: {topic}",
                content=intel_briefing,
                artifact_type="research_report",
                metadata_json={"source": "chronos_observer", "topic": topic}
            )
            db_session.add(new_artifact)
            db_session.commit()
            
            # Broadcast completion to UI
            try:
                from main import manager
                import json
                asyncio.create_task(manager.broadcast(json.dumps({
                    "event": "NEW_ARTIFACT_INGESTED", 
                    "id": new_artifact.id, 
                    "title": new_artifact.title,
                    "status": "COMPLETED"
                })))
            except: pass
            
            return f"Web Intel Briefing on '{topic}':\n\n{intel_briefing}"
            
        except Exception as e:
            logger.error(f"Chronos Observer: Failed to run intel loop: {e}")
            return "The Observer encountered a fog in the digital æther."

    async def get_daily_summary_plan(self, user_id: str) -> str:
        """
        Synthesizes the user's goals and calendar into an Akasha-style morning briefing.
        """
        db: Session = SessionLocal()
        try:
            now = datetime.utcnow()
            today_end = now + timedelta(days=1)
            
            # 1. Fetch Today's Tasks
            tasks = db.query(UserTask).filter(
                UserTask.user_id == user_id,
                UserTask.status == "PENDING"
            ).all()
            
            # 2. Fetch Today's Calendar
            events = db.query(UserCalendarEvent).filter(
                UserCalendarEvent.user_id == user_id,
                UserCalendarEvent.start_time >= now,
                UserCalendarEvent.start_time <= today_end
            ).all()
            
            # 3. Synthesize via Oracle Agent
            task_str = "\n".join([f"- {t.task_description} (Priority: {t.priority})" for t in tasks])
            event_str = "\n".join([f"- {e.summary} at {e.start_time.strftime('%H:%M')}" for e in events])
            
            context = f"Tasks for Today:\n{task_str}\n\nCalendar Events:\n{event_str}"
            
            # Request a proactive synthesis from the Head Archivist
            # We use a custom prompt for the briefing
            briefing_prompt = (
                "You are the Akasha Archivist. Based on the user's tasks and calendar for today, "
                "provide a concise, proactive morning briefing. Prioritize the most critical tasks "
                "and suggest a logical flow for the day. Use a calm, professional tone. If the user has a high cognitive load, suggest a break."
            )
            
            # Use the Oracle's synthesis logic
            briefing_result = self.ai.council.oracle.divine(
                query="Generate my proactive morning briefing. Prioritize tasks and logical flow.",
                vector_context=[context],
                graph_context=[],
                persona=briefing_prompt
            )
            
            return briefing_result.get("answer", "I was unable to synthesize your morning briefing. However, your records remain secure.")
        except Exception as e:
            logger.error(f"Chronos: Failed to generate briefing: {e}")
            return "I was unable to synthesize your morning briefing. However, your records remain secure."
        finally:
            db.close()

    async def monitor_health_interventions(self, user_id: str, db_session: Session) -> Optional[str]:
        """
        Proactively monitors the user's 'Digital Ego' for signs of high stress or burnout.
        Triggers an intervention if neuroticism is high and sentiment is negative.
        """
        try:
            # Check recent artifact sentiments
            time_threshold = datetime.utcnow() - timedelta(hours=24)
            recent_artifacts = db_session.query(LibraryArtifact).filter(
                LibraryArtifact.user_id == user_id,
                LibraryArtifact.timestamp >= time_threshold
            ).all()
            
            negative_count = sum(1 for a in recent_artifacts if "NEGATIVE" in (a.analysis_metadata.get("sentiment_label", "") if a.analysis_metadata else ""))
            
            # Check psychology profile
            psych = db_session.query(UserPsychology).filter(UserPsychology.user_id == user_id).first()
            if psych and (psych.neuroticism > 0.7 or (negative_count > 3 and psych.neuroticism > 0.5)):
                intervention_prompt = (
                    "You are the Akasha Sentinel, monitoring the user's digital wellbeing. "
                    "The user's recent data indicates high cognitive load and potential stress/burnout. "
                    "Draft a gentle, empathetic, and extremely brief (2 sentences) intervention message suggesting they step away or change context."
                )
                intervention_chain = PromptTemplate(template="{prompt}", input_variables=["prompt"]) | self.ai.council.llm | StrOutputParser()
                loop = asyncio.get_event_loop()
                message = await loop.run_in_executor(None, intervention_chain.invoke, {"prompt": intervention_prompt})
                logger.info(f"Chronos: Health intervention triggered for {user_id}.")
                return message
            return None
        except Exception as e:
            logger.error(f"Chronos: Health intervention monitor failed: {e}")
            return None

    async def detect_temporal_deadlines(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Scans tasks for upcoming deadlines and flags them for the Sentinel.
        """
        db: Session = SessionLocal()
        try:
            warning_window = datetime.utcnow() + timedelta(hours=6)
            urgent_tasks = db.query(UserTask).filter(
                UserTask.user_id == user_id,
                UserTask.status == "PENDING",
                UserTask.deadline <= warning_window
            ).all()
            
            alerts = []
            for task in urgent_tasks:
                alerts.append({
                    "type": "DEADLINE_ALERT",
                    "task_id": task.id,
                    "description": task.task_description,
                    "deadline": str(task.deadline)
                })
            return alerts
        finally:
            db.close()

    async def schedule_reminder(self, user_id: str, text: str, delay_seconds: int):
        """
        Simple in-memory scheduling for short-term reminders.
        In production, this would use Celery 'apply_async' with countdown.
        """
        await asyncio.sleep(delay_seconds)
        # Trigger notification (Broadcasting via WebSocket ConnectionManager)
        # This will be integrated with main.py's manager
        logger.info(f"Chronos Reminder for {user_id}: {text}")
        return text

    async def run_nocturnal_consolidation(self, user_id: str):
        """
        Phase 4: Autonomous Dream Phase & Nocturnal Learning.
        Agents debate memories AND forage the web for fresh knowledge while the user sleeps.
        """
        db: Session = SessionLocal()
        try:
            print(f"Chronos: Initiating Nocturnal Cycle for {user_id}...")
            
            eureka = "No specific dream connections made."
            research_report = "No new research conducted."
            
            # 1. DREAM PHASE: Agentic Debate
            artifacts = db.query(LibraryArtifact).filter(LibraryArtifact.user_id == user_id).order_by(func.random()).limit(2).all()
            if len(artifacts) >= 2:
                print(f"Chronos: Synthesizing lateral connections...")
                debate_topic = f"Find a hidden connection between: {artifacts[0].title} and {artifacts[1].title}"
                loop = asyncio.get_event_loop()
                eureka = await loop.run_in_executor(None, self.ai.council.debate_council.run_debate, debate_topic)
                from main import ingest_library_artifact
                await ingest_library_artifact(f"Eureka: {artifacts[0].title} × {artifacts[1].title}", eureka, "memory", {"source": "dream_phase"}, db, user_id)

            # 2. LEARNING PHASE: Autonomous Foraging
            # Determine most active recent theme
            recent = db.query(LibraryArtifact).filter(LibraryArtifact.user_id == user_id).order_by(LibraryArtifact.timestamp.desc()).limit(10).all()
            themes = " ".join([a.title for a in recent])
            forage_prompt = f"Based on these recent interests: {themes}, identify one advanced research topic to forage from the web. Return ONLY the topic."
            target_topic = self.ai.council.llm.invoke(forage_prompt).strip()
            
            if target_topic and len(target_topic) > 3:
                print(f"Chronos: Autonomously foraging the web for '{target_topic}'...")
                from main import IngestEngine
                ingest_eng = IngestEngine()
                loop = asyncio.get_event_loop()
                research_report = await loop.run_in_executor(None, self.ai.council.scout.deep_research, target_topic, ingest_eng)
                from main import ingest_library_artifact
                await ingest_library_artifact(f"Nocturnal Learning: {target_topic}", research_report, "research_report", {"source": "nocturnal_forage", "topic": target_topic}, db, user_id)

            # --- Feature 7: Serendipity Report ---
            print(f"Chronos: Generating Serendipity Report...")
            report_prompt = f"Based on the nocturnal dream phase ({eureka}) and learning phase ({research_report}), generate a 'Morning Briefing' for the user. It should be concise, insightful, and highlight the serendipitous connections found while they slept. Format nicely."
            serendipity_report = self.ai.council.llm.invoke(report_prompt).strip()
            
            from main import ingest_library_artifact
            await ingest_library_artifact(
                title=f"Morning Briefing: {datetime.utcnow().strftime('%Y-%m-%d')}",
                content=serendipity_report,
                artifact_type="serendipity_report",
                extra_meta={"source": "nocturnal_consolidation"},
                db=db,
                user_id=user_id
            )
            print(f"Chronos: Serendipity Report generated and saved.")
            # ---------------------------------------

            print(f"Chronos: Nocturnal Cycle complete.")
            
        except Exception as e:
            print(f"Chronos: Nocturnal Cycle failed: {e}")
        finally:
            db.close()

    async def run_behavioral_pattern_mining(self, user_id: str):
        """
        Deep Behavioral Analysis: Mines the UserActivity stream for recurring habits, 
        content affinity, and temporal patterns. Updates the User's Psychological Profile.
        """
        db: Session = SessionLocal()
        try:
            from models import UserActivity
            # 1. Fetch activities from the last 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            activities = db.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.timestamp >= seven_days_ago
            ).all()

            if len(activities) < 10:
                logger.info(f"Chronos: Not enough activity data for behavioral mining for {user_id}.")
                return

            # 2. Summarize the activity stream for the LLM
            # Group by day and type for a compressed view
            activity_summary = {}
            for act in activities:
                day = act.timestamp.strftime('%A')
                act_type = act.activity_type or "Unknown"
                title = act.title or "No Title"
                if day not in activity_summary: activity_summary[day] = []
                activity_summary[day].append(f"[{act_type}] {title}")

            formatted_history = ""
            for day, acts in activity_summary.items():
                formatted_history += f"--- {day} ---\n" + "\n".join(acts[:15]) + "\n\n"

            # 3. Ask the Behavioral Analyst (via Head Archivist) to find deep patterns
            analysis_prompt = (
                "You are the Akasha Behavioral Analyst. Analyze the following 7-day activity stream of the user. "
                "Look for recurring themes, specific people/content the user engages with frequently, and any "
                "temporal patterns (e.g., 'The user focuses on X every Monday'). \n"
                "Then, infer how this behavior reflects the user's current psychological state, interests, and potential biases.\n\n"
                "Activity History:\n{history}\n\n"
                "Provide a 2-paragraph analysis. Paragraph 1: Detected Patterns. Paragraph 2: Psychological Inference."
            )
            
            loop = asyncio.get_event_loop()
            behavioral_insight = await loop.run_in_executor(None, self.ai.council.head_archivist.council.llm.invoke, analysis_prompt.format(history=formatted_history[:6000]))
            behavioral_insight = behavioral_insight.strip()

            logger.info(f"Chronos: Behavioral mining complete for {user_id}.")

            # 4. Save the insight as a special 'Psychological Reflection' Artifact
            new_insight = LibraryArtifact(
                user_id=user_id,
                title=f"Behavioral & Psychological Analysis: {datetime.utcnow().strftime('%Y-%m-%d')}",
                content=behavioral_insight,
                artifact_type="behavioral_insight",
                privacy_tier="PRIVATE"
            )
            db.add(new_insight)
            
            # Broadcast completion to UI
            try:
                from main import manager
                import json
                asyncio.create_task(manager.broadcast(json.dumps({
                    "event": "NEW_ARTIFACT_INGESTED", 
                    "id": new_insight.id, 
                    "title": new_insight.title,
                    "status": "COMPLETED"
                })))
            except: pass

            # 5. Update UserPsychology based on this new insight
            # This triggers a more profound update than just simple artifact ingestion
            await self.ai.refine_psychology_from_behavior(user_id, behavioral_insight, db)
            
            db.commit()
            return behavioral_insight

        except Exception as e:
            logger.error(f"Chronos: Behavioral mining failed: {e}")
            db.rollback()
        finally:
            db.close()

    async def generate_daily_reflection(self, db_session: Session, user_id: str):
        """
        Evening Reflection: Fetches artifacts from the last 15 hours and synthesizes a journal entry.
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=15)
            artifacts = db_session.query(LibraryArtifact).filter(
                LibraryArtifact.user_id == user_id,
                LibraryArtifact.timestamp >= time_threshold
            ).all()

            if not artifacts:
                logger.info(f"Chronos: No artifacts found for daily reflection for {user_id}.")
                return

            context_text = "\n\n".join([f"Title: {a.title}\nContent: {a.content}" for a in artifacts])
            
            # Use Scribe to write the reflection
            reflection_prompt = PromptTemplate(
                template="You are the Akasha Scribe. Based on the user's activities and artifacts from the last 15 hours, "
                         "write a 3-paragraph 'Day in Review' journal entry.\n"
                         "Paragraph 1: The Story (What happened?)\n"
                         "Paragraph 2: The Lessons (What was learned?)\n"
                         "Paragraph 3: The Mood (What was the emotional tone?)\n\n"
                         "Context:\n{context}\n\nReflection:",
                input_variables=["context"]
            )
            reflection_chain = reflection_prompt | self.ai.council.llm | StrOutputParser()
            loop = asyncio.get_event_loop()
            reflection_text = await loop.run_in_executor(None, reflection_chain.invoke, {"context": context_text[:4000]})
            
            # Save as new LibraryArtifact
            new_reflection = LibraryArtifact(
                user_id=user_id,
                title=f"Daily Reflection: {datetime.utcnow().strftime('%Y-%m-%d')}",
                content=reflection_text,
                artifact_type="journal_reflection",
                privacy_tier="PRIVATE"
            )
            db_session.add(new_reflection)
            db_session.commit()
            
            logger.info(f"Chronos: Daily reflection generated and saved for {user_id}.")
            return reflection_text
        except Exception as e:
            logger.error(f"Chronos: Failed to generate daily reflection: {e}")
            db_session.rollback()
            return None
