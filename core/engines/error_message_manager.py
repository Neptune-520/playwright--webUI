"""
错误信息管理器 - 将技术性错误转换为用户友好的提示信息
"""
import re
import os
import json
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class ErrorRule:
    """错误规则定义"""
    name: str
    pattern: str
    message_template: str
    action_type: Optional[str] = None


class ErrorMessageManager:
    """
    错误信息管理器
    根据匹配的错误信息，展示对应的用户友好错误信息
    """
    
    def __init__(self):
        self._rules: List[ErrorRule] = []
        self._config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'error_config.json')
        self._init_rules()
        self._load_custom_rules()
    
    def _init_rules(self):
        """初始化错误规则"""
        # 导航相关错误
        self.add_rule(
            name="导航_页面或浏览器已关闭",
            action_type="navigate",
            pattern=r"Page\.goto:.*Target page, context or browser has been closed",
            message_template="导航到{url}失败，目标页面或浏览器意外关闭，建议重新执行任务"
        )
        
        self.add_rule(
            name="导航_超时",
            action_type="navigate",
            pattern=r"Page\.goto:.*Timeout (\d+)ms exceeded",
            message_template="导航到{url}失败，页面在{timeout}秒内未加载完成，建议检查网络，或增加全局配置-默认超时时间"
        )
        
        self.add_rule(
            name="导航_网络连接失败",
            action_type="navigate",
            pattern=r"net::ERR_.*",
            message_template="导航到{url}失败，网络连接错误，请检查目标网址是否可访问"
        )
        
        self.add_rule(
            name="导航_页面被拦截",
            action_type="navigate",
            pattern=r"Page\.goto:.*net::ERR_BLOCKED_BY_CLIENT",
            message_template="导航到{url}失败，页面被客户端拦截，可能受到浏览器扩展程序影响"
        )
        
        # 点击相关错误
        self.add_rule(
            name="点击_元素不可点击",
            action_type="click",
            pattern=r"element is not visible",
            message_template="点击操作失败，目标元素不可见，请检查元素是否存在或被其他元素遮挡"
        )
        
        self.add_rule(
            name="点击_元素被遮挡",
            action_type="click",
            pattern=r"element click intercepted",
            message_template="点击操作失败，目标元素被其他元素遮挡，请尝试使用强制点击或调整页面滚动"
        )
        
        self.add_rule(
            name="点击_超时",
            action_type="click",
            pattern=r"Timeout (\d+)ms exceeded",
            message_template="点击操作失败，等待元素可点击状态超时（{timeout}秒），建议检查元素状态或增加超时时间"
        )
        
        # 填写相关错误
        self.add_rule(
            name="填写_元素不可编辑",
            action_type="fill",
            pattern=r"element is not an <input>",
            message_template="填写操作失败，目标元素不是可编辑的输入框，请检查元素类型"
        )
        
        self.add_rule(
            name="填写_元素被禁用",
            action_type="fill",
            pattern=r"element is disabled",
            message_template="填写操作失败，目标输入框已被禁用，无法填写内容"
        )
        
        self.add_rule(
            name="填写_超时",
            action_type="fill",
            pattern=r"Timeout (\d+)ms exceeded",
            message_template="填写操作失败，等待元素可编辑状态超时（{timeout}秒），建议检查元素状态"
        )
        
        # 选择相关错误
        self.add_rule(
            name="选择_选项不存在",
            action_type="select",
            pattern=r"Options are not selectable",
            message_template="选择操作失败，目标元素不是下拉选择框，请检查元素类型"
        )
        
        self.add_rule(
            name="选择_选项值无效",
            action_type="select",
            pattern=r"Option \"(.*)\" not found",
            message_template="选择操作失败，下拉选项中不存在\"{option}\"，请检查选项值是否正确"
        )
        
        # 等待相关错误
        self.add_rule(
            name="等待_元素未出现",
            action_type="wait_for_selector",
            pattern=r"Timeout (\d+)ms exceeded",
            message_template="等待操作失败，目标元素在{timeout}秒内未出现，建议检查元素定位或增加超时时间"
        )
        
        # 断言相关错误
        self.add_rule(
            name="断言_文本不匹配",
            action_type="assert_text",
            pattern=r"Text assertion failed",
            message_template="文本断言失败，预期文本与实际文本不一致"
        )
        
        self.add_rule(
            name="断言_元素不可见",
            action_type="assert_visible",
            pattern=r"Element is not visible",
            message_template="可见性断言失败，目标元素当前不可见"
        )
        
        self.add_rule(
            name="断言_值不匹配",
            action_type="assert_value",
            pattern=r"Value assertion failed",
            message_template="值断言失败，预期值与实际值不一致"
        )
        
        # 上传相关错误
        self.add_rule(
            name="上传_文件不存在",
            action_type="upload",
            pattern=r"File not found",
            message_template="上传操作失败，指定的文件不存在，请检查文件路径"
        )
        
        # 通用超时错误
        self.add_rule(
            name="通用_超时",
            pattern=r"Timeout (\d+)ms exceeded",
            message_template="操作超时，在{timeout}秒内未完成，建议检查网络状态或增加全局配置-默认超时时间"
        )
        
        # 通用浏览器关闭错误
        self.add_rule(
            name="通用_浏览器已关闭",
            pattern=r"Target page, context or browser has been closed",
            message_template="操作失败，浏览器或页面意外关闭，建议重新执行任务"
        )
        
        # 通用元素未找到错误
        self.add_rule(
            name="通用_元素未找到",
            pattern=r"element(s)? not found|No element(s) found",
            message_template="操作失败，未找到目标元素，请检查元素定位器是否正确"
        )
    
    def _load_custom_rules(self):
        """从JSON配置文件加载自定义规则"""
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    custom_rules = json.load(f)
                    for rule_data in custom_rules:
                        self.add_rule(
                            name=rule_data.get('name', ''),
                            pattern=rule_data.get('pattern', ''),
                            message_template=rule_data.get('message_template', ''),
                            action_type=rule_data.get('action_type') or None
                        )
            except Exception as e:
                print(f"加载自定义错误规则失败: {e}")
    
    def add_rule(self, name: str, pattern: str, message_template: str, 
                 action_type: Optional[str] = None):
        """添加错误规则"""
        self._rules.append(ErrorRule(
            name=name,
            pattern=pattern,
            message_template=message_template,
            action_type=action_type
        ))
    
    def format_error_message(self, original_error: str, action_type: Optional[str] = None,
                            context: Optional[Dict] = None) -> str:
        """
        格式化错误信息
        
        Args:
            original_error: 原始错误信息
            action_type: 操作类型（navigate, click, fill等）
            context: 上下文信息（如url, step_name等）
            
        Returns:
            用户友好的错误信息
        """
        context = context or {}
        
        # 首先尝试匹配特定操作类型的规则
        if action_type:
            for rule in self._rules:
                if rule.action_type == action_type:
                    match = re.search(rule.pattern, original_error, re.IGNORECASE | re.DOTALL)
                    if match:
                        return self._build_message(rule, match, context)
        
        # 然后尝试匹配通用规则
        for rule in self._rules:
            if rule.action_type is None:
                match = re.search(rule.pattern, original_error, re.IGNORECASE | re.DOTALL)
                if match:
                    return self._build_message(rule, match, context)
        
        # 如果没有匹配的规则，返回原始错误
        return original_error
    
    def _build_message(self, rule: ErrorRule, match, context: Dict) -> str:
        """构建错误消息"""
        message = rule.message_template
        
        # 替换URL
        if '{url}' in message:
            url = context.get('url', '未知页面')
            message = message.replace('{url}', url)
        
        # 替换超时时间
        if '{timeout}' in message:
            timeout_ms = match.group(1) if match.lastindex and match.group(1) else '未知'
            timeout_sec = int(timeout_ms) // 1000 if timeout_ms != '未知' else '未知'
            message = message.replace('{timeout}', str(timeout_sec))
        
        # 替换选项值
        if '{option}' in message:
            option = match.group(1) if match.lastindex and match.group(1) else '未知'
            message = message.replace('{option}', option)
        
        # 替换步骤名称
        if '{step_name}' in message:
            step_name = context.get('step_name', '当前步骤')
            message = message.replace('{step_name}', step_name)
        
        return message
    
    def get_supported_actions(self) -> List[str]:
        """获取支持的操作类型列表"""
        actions = set()
        for rule in self._rules:
            if rule.action_type:
                actions.add(rule.action_type)
        return sorted(list(actions))
    
    def get_rules_for_action(self, action_type: Optional[str] = None) -> List[ErrorRule]:
        """获取指定操作类型的规则"""
        if action_type:
            return [rule for rule in self._rules if rule.action_type == action_type]
        return self._rules
    
    def get_all_rules(self) -> List[Dict]:
        """获取所有规则的字典列表（用于前端展示）"""
        return [
            {
                'name': rule.name,
                'pattern': rule.pattern,
                'message_template': rule.message_template,
                'action_type': rule.action_type or '',
            }
            for rule in self._rules
        ]


# 创建全局实例
error_message_manager = ErrorMessageManager()

