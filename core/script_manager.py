# 兼容层：此文件保留以支持向后兼容
# 所有功能已迁移到 core.managers 模块
from core.managers.script_manager import ScriptManager, SCRIPT_SCHEMA
from core.managers.element_locator_manager import ElementLocatorManager
from core.managers.test_result_manager import TestResultExporter

__all__ = ['ScriptManager', 'SCRIPT_SCHEMA', 'ElementLocatorManager', 'TestResultExporter']
