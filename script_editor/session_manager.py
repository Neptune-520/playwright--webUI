import asyncio
import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from django.conf import settings
from django.utils import timezone

from script_editor.recording_engine import RecordingEngine
from script_editor.recording_scripts import MAX_RECORDING_DURATION

logger = logging.getLogger(__name__)


@dataclass
class RecordingSession:
    session_id: str
    target_url: str
    status: str = 'starting'
    actions: List[Dict[str, Any]] = field(default_factory=list)
    engine: Optional[RecordingEngine] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    error: Optional[str] = None
    loop: Optional[asyncio.AbstractEventLoop] = None
    thread: Optional[threading.Thread] = None
    viewport_width: int = 1920
    viewport_height: int = 1080


class RecordingSessionManager:
    _sessions: Dict[str, RecordingSession] = {}

    @classmethod
    def create_session(cls, target_url: str, user=None, viewport_width=1920, viewport_height=1080) -> str:
        for sid, sess in cls._sessions.items():
            if sess.status in ('starting', 'recording'):
                if user is None or sess.status == 'recording':
                    raise ValueError("已有正在进行的录制会话，请先停止当前录制")

        session_id = f"rec_{timezone.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        session = RecordingSession(
            session_id=session_id,
            target_url=target_url,
            started_at=timezone.now(),
        )
        cls._sessions[session_id] = session

        session.viewport_width = viewport_width
        session.viewport_height = viewport_height
        thread = threading.Thread(
            target=cls._run_recording,
            args=(session_id, target_url, viewport_width, viewport_height),
            daemon=True,
        )
        session.thread = thread
        thread.start()

        return session_id

    @classmethod
    def _run_recording(cls, session_id: str, target_url: str, viewport_width=1920, viewport_height=1080):
        session = cls._sessions.get(session_id)
        if not session:
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session.loop = loop

        engine = RecordingEngine()
        session.engine = engine

        try:
            loop.run_until_complete(engine.start_recording(target_url, session_id, viewport_width, viewport_height))
            session.status = 'recording'

            elapsed = 0
            while engine.is_recording and elapsed < MAX_RECORDING_DURATION:
                loop.run_until_complete(asyncio.sleep(1))
                elapsed += 1
                session.actions = engine.get_actions()

            if engine.is_recording:
                logger.info(f"Recording session {session_id} timed out after {MAX_RECORDING_DURATION}s")
                loop.run_until_complete(engine.stop_recording())

        except Exception as e:
            logger.error(f"Recording session {session_id} error: {e}")
            session.status = 'error'
            session.error = str(e)
            try:
                loop.run_until_complete(engine.close())
            except Exception:
                pass
        finally:
            if session.status != 'error':
                session.status = 'stopped'
            session.stopped_at = timezone.now()
            session.actions = engine.get_actions()
            loop.close()

    @classmethod
    def get_session(cls, session_id: str) -> Optional[RecordingSession]:
        return cls._sessions.get(session_id)

    @classmethod
    def stop_session(cls, session_id: str) -> Optional[List[Dict[str, Any]]]:
        session = cls._sessions.get(session_id)
        if not session:
            return None

        if session.engine and session.engine.is_recording:
            session.engine.is_recording = False

        if session.loop and session.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                session.engine.stop_recording(),
                session.loop,
            )

        session.status = 'stopped'
        session.stopped_at = timezone.now()
        return session.actions

    @classmethod
    def get_session_actions(cls, session_id: str) -> Optional[Dict[str, Any]]:
        session = cls._sessions.get(session_id)
        if not session:
            return None

        if session.engine and session.engine.is_recording:
            session.actions = session.engine.get_actions()

        return {
            'session_id': session_id,
            'status': session.status,
            'action_count': len(session.actions),
            'actions': session.actions,
            'error': session.error,
        }

    @classmethod
    def cleanup_session(cls, session_id: str):
        session = cls._sessions.pop(session_id, None)
        if session and session.engine:
            try:
                if session.loop and not session.loop.is_closed():
                    asyncio.run_coroutine_threadsafe(
                        session.engine.close(),
                        session.loop,
                    )
            except Exception:
                pass

    @classmethod
    def cleanup_old_sessions(cls, max_age_seconds: int = 3600):
        now = timezone.now()
        to_remove = []
        for sid, session in cls._sessions.items():
            if session.status in ('stopped', 'error'):
                if session.stopped_at and (now - session.stopped_at).total_seconds() > max_age_seconds:
                    to_remove.append(sid)
        for sid in to_remove:
            cls.cleanup_session(sid)
