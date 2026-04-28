import logging
from django.utils import timezone
from test_manager.models import TaskGroup, TaskGroupItem

logger = logging.getLogger(__name__)


def on_script_execution_completed(sender, **kwargs):
    """
    @deprecated 任务组功能已废弃
    此信号处理器保留用于向后兼容，但不再执行任何实际操作
    """
    task_group_id = kwargs.get('task_group_id')
    task_group_item_id = kwargs.get('task_group_item_id')

    if not task_group_id or not task_group_item_id:
        return

    logger.info(f'[DEPRECATED] 收到已废弃的任务组信号: task_group_id={task_group_id}')


def _check_and_update_task_group_status(task_group_id):
    """
    @deprecated 任务组功能已废弃
    """
    pass
