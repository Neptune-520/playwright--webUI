"""
Error message manager test - Django integrated
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automation_test_platform.settings')

import django
django.setup()

from core.engines.error_message_manager import error_message_manager


def test_main():
    # Test navigation error with browser closed
    error1 = 'Page.goto: Target page, context or browser has been closed Call log: - navigating to "https://dsbeon.uspp.com/quote/belt-buckles-quote", waiting until "networkidle"'
    result1 = error_message_manager.format_error_message(
        error1, 
        action_type='navigate',
        context={'url': 'https://dsbeon.uspp.com/quote/belt-buckles-quote'}
    )
    print("Test 1 - Browser closed:")
    print(f"  Expected: 导航到https://dsbeon.uspp.com/quote/belt-buckles-quote失败，目标页面或浏览器意外关闭，建议重新执行任务")
    print(f"  Got:      {result1}")
    assert "目标页面或浏览器意外关闭" in result1
    assert "导航到" in result1
    print("  ✓ PASS\n")
    
    # Test navigation timeout error
    error2 = 'Page.goto: Timeout 35000ms exceeded. Call log: - navigating to "https://dsbeon.uspp.com/quote/belt-buckles-quote", waiting until "networkidle"'
    result2 = error_message_manager.format_error_message(
        error2,
        action_type='navigate',
        context={'url': 'https://dsbeon.uspp.com/quote/belt-buckles-quote'}
    )
    print("Test 2 - Navigation timeout:")
    print(f"  Expected: 导航到https://dsbeon.uspp.com/quote/belt-buckles-quote失败，页面在35秒内未加载完成，建议检查网络，或增加全局配置-默认超时时间")
    print(f"  Got:      {result2}")
    assert "页面在35秒内未加载完成" in result2
    assert "建议检查网络" in result2
    print("  ✓ PASS\n")
    
    print("All tests passed!")


if __name__ == '__main__':
    test_main()
