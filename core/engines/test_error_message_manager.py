"""
错误信息管理器测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.engines.error_message_manager import error_message_manager, ErrorMessageManager


def test_navigation_errors():
    """测试导航相关错误"""
    print("=" * 60)
    print("测试导航相关错误")
    print("=" * 60)
    
    context = {'url': 'https://dsbeon.uspp.com/quote/belt-buckles-quote'}
    
    # 测试1: 浏览器关闭错误
    error1 = 'Page.goto: Target page, context or browser has been closed Call log: - navigating to "https://dsbeon.uspp.com/quote/belt-buckles-quote", waiting until "networkidle"'
    result1 = error_message_manager.format_error_message(error1, action_type='navigate', context=context)
    print(f"\n原始错误: {error1}")
    print(f"格式化后: {result1}")
    
    # 测试2: 超时错误
    error2 = 'Page.goto: Timeout 35000ms exceeded. Call log: - navigating to "https://dsbeon.uspp.com/quote/belt-buckles-quote", waiting until "networkidle"'
    result2 = error_message_manager.format_error_message(error2, action_type='navigate', context=context)
    print(f"\n原始错误: {error2}")
    print(f"格式化后: {result2}")
    
    # 测试3: 网络连接错误
    error3 = 'Page.goto: net::ERR_CONNECTION_REFUSED at https://example.com'
    result3 = error_message_manager.format_error_message(error3, action_type='navigate', context={'url': 'https://example.com'})
    print(f"\n原始错误: {error3}")
    print(f"格式化后: {result3}")


def test_click_errors():
    """测试点击相关错误"""
    print("\n" + "=" * 60)
    print("测试点击相关错误")
    print("=" * 60)
    
    # 测试1: 元素不可见
    error1 = 'element is not visible'
    result1 = error_message_manager.format_error_message(error1, action_type='click')
    print(f"\n原始错误: {error1}")
    print(f"格式化后: {result1}")
    
    # 测试2: 元素被遮挡
    error2 = 'element click intercepted'
    result2 = error_message_manager.format_error_message(error2, action_type='click')
    print(f"\n原始错误: {error2}")
    print(f"格式化后: {result2}")
    
    # 测试3: 超时
    error3 = 'Timeout 30000ms exceeded'
    result3 = error_message_manager.format_error_message(error3, action_type='click')
    print(f"\n原始错误: {error3}")
    print(f"格式化后: {result3}")


def test_fill_errors():
    """测试填写相关错误"""
    print("\n" + "=" * 60)
    print("测试填写相关错误")
    print("=" * 60)
    
    # 测试1: 元素不是input
    error1 = 'element is not an <input>'
    result1 = error_message_manager.format_error_message(error1, action_type='fill')
    print(f"\n原始错误: {error1}")
    print(f"格式化后: {result1}")
    
    # 测试2: 元素被禁用
    error2 = 'element is disabled'
    result2 = error_message_manager.format_error_message(error2, action_type='fill')
    print(f"\n原始错误: {error2}")
    print(f"格式化后: {result2}")


def test_assertion_errors():
    """测试断言相关错误"""
    print("\n" + "=" * 60)
    print("测试断言相关错误")
    print("=" * 60)
    
    # 测试1: 文本断言失败
    error1 = 'Text assertion failed. Expected: "Hello", Actual: "World"'
    result1 = error_message_manager.format_error_message(error1, action_type='assert_text')
    print(f"\n原始错误: {error1}")
    print(f"格式化后: {result1}")
    
    # 测试2: 可见性断言失败
    error2 = 'Element is not visible'
    result2 = error_message_manager.format_error_message(error2, action_type='assert_visible')
    print(f"\n原始错误: {error2}")
    print(f"格式化后: {result2}")


def test_generic_errors():
    """测试通用错误"""
    print("\n" + "=" * 60)
    print("测试通用错误")
    print("=" * 60)
    
    # 测试1: 通用超时
    error1 = 'Timeout 60000ms exceeded'
    result1 = error_message_manager.format_error_message(error1)
    print(f"\n原始错误: {error1}")
    print(f"格式化后: {result1}")
    
    # 测试2: 通用浏览器关闭
    error2 = 'Target page, context or browser has been closed'
    result2 = error_message_manager.format_error_message(error2)
    print(f"\n原始错误: {error2}")
    print(f"格式化后: {result2}")
    
    # 测试3: 未匹配的错误
    error3 = 'Some unknown error occurred'
    result3 = error_message_manager.format_error_message(error3)
    print(f"\n原始错误: {error3}")
    print(f"格式化后: {result3}")


def test_supported_actions():
    """测试支持的操作类型"""
    print("\n" + "=" * 60)
    print("支持的操作类型")
    print("=" * 60)
    actions = error_message_manager.get_supported_actions()
    print(f"\n{actions}")


if __name__ == '__main__':
    test_navigation_errors()
    test_click_errors()
    test_fill_errors()
    test_assertion_errors()
    test_generic_errors()
    test_supported_actions()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
