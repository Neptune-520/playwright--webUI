import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class TestResultExporter:
    def __init__(self, results_dir: Path = None):
        self.results_dir = results_dir or settings.TEST_RESULTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def save_result(self, task_id: int, result_data: Dict[str, Any]) -> Path:
        filename = f"task_{task_id}_result.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_result(self, task_id: int) -> Optional[Dict[str, Any]]:
        filename = f"task_{task_id}_result.json"
        filepath = self.results_dir / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def export_report(self, task_id: int, format: str = 'json') -> Path:
        result_data = self.load_result(task_id)
        if not result_data:
            raise FileNotFoundError(f"No result found for task {task_id}")
        
        if format == 'json':
            filename = f"task_{task_id}_report.json"
            filepath = self.results_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
        elif format == 'html':
            filename = f"task_{task_id}_report.html"
            filepath = self.results_dir / filename
            html_content = self._generate_html_report(result_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return filepath
    
    def _generate_html_report(self, result_data: Dict[str, Any]) -> str:
        total_steps = len(result_data.get('step_results', []))
        passed = sum(1 for r in result_data.get('step_results', []) if r.get('status') == 'passed')
        failed = sum(1 for r in result_data.get('step_results', []) if r.get('status') == 'failed')
        skipped = sum(1 for r in result_data.get('step_results', []) if r.get('status') == 'skipped')
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - {result_data.get('task_name', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary-card h3 {{ margin: 0; color: #666; font-size: 14px; }}
        .summary-card .value {{ font-size: 32px; font-weight: bold; margin-top: 10px; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .skipped {{ color: #ffc107; }}
        .total {{ color: #007bff; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-skipped {{ color: #ffc107; font-weight: bold; }}
        .error {{ background: #fff3cd; padding: 10px; border-radius: 4px; margin-top: 10px; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>测试报告: {result_data.get('task_name', 'Unknown')}</h1>
        <p><strong>执行时间:</strong> {result_data.get('started_at', 'N/A')} - {result_data.get('finished_at', 'N/A')}</p>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总步骤数</h3>
                <div class="value total">{total_steps}</div>
            </div>
            <div class="summary-card">
                <h3>通过</h3>
                <div class="value passed">{passed}</div>
            </div>
            <div class="summary-card">
                <h3>失败</h3>
                <div class="value failed">{failed}</div>
            </div>
            <div class="summary-card">
                <h3>跳过</h3>
                <div class="value skipped">{skipped}</div>
            </div>
        </div>
        
        <h2>详细结果</h2>
        <table>
            <thead>
                <tr>
                    <th>序号</th>
                    <th>步骤名称</th>
                    <th>状态</th>
                    <th>耗时(秒)</th>
                    <th>错误信息</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for i, step in enumerate(result_data.get('step_results', [])):
            status_class = f"status-{step.get('status', 'unknown')}"
            status_text = {
                'passed': '通过',
                'failed': '失败',
                'skipped': '跳过',
            }.get(step.get('status'), step.get('status'))
            
            html += f"""
                <tr>
                    <td>{i + 1}</td>
                    <td>{step.get('step_name', 'Unknown')}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{step.get('duration', 0):.2f}</td>
                    <td>{step.get('error', '') or '-'}</td>
                </tr>
"""
            if step.get('error'):
                html += f"""
                <tr>
                    <td colspan="5">
                        <div class="error">{step.get('error')}</div>
                    </td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html
