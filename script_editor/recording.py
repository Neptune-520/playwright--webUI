# 兼容层：此文件保留以支持向后兼容
# 所有功能已迁移到 script_editor 子模块
from script_editor.recording_scripts import RECORDING_JS, MAX_RECORDING_DURATION
from script_editor.recording_engine import RecordingEngine
from script_editor.session_manager import RecordingSession, RecordingSessionManager

__all__ = ['RECORDING_JS', 'MAX_RECORDING_DURATION', 'RecordingEngine', 'RecordingSession', 'RecordingSessionManager']
