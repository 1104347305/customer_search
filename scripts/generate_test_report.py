#!/usr/bin/env python3
"""
客户搜索系统 - 测试报告生成器
生成HTML格式的可视化测试报告
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>客户搜索系统 - 真实场景测试报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }}

        .summary-card h3 {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .summary-card .value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}

        .summary-card .value.success {{
            color: #10b981;
        }}

        .summary-card .value.warning {{
            color: #f59e0b;
        }}

        .summary-card .value.error {{
            color: #ef4444;
        }}

        .section {{
            padding: 40px;
            border-bottom: 1px solid #e5e7eb;
        }}

        .section:last-child {{
            border-bottom: none;
        }}

        .section h2 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #1f2937;
        }}

        .priority-section {{
            margin-bottom: 30px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }}

        .priority-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .priority-header h3 {{
            font-size: 18px;
            color: #1f2937;
        }}

        .priority-badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}

        .priority-badge.p0 {{
            background: #fee2e2;
            color: #dc2626;
        }}

        .priority-badge.p1 {{
            background: #fef3c7;
            color: #d97706;
        }}

        .priority-badge.p2 {{
            background: #dbeafe;
            color: #2563eb;
        }}

        .test-list {{
            padding: 20px;
        }}

        .test-item {{
            padding: 15px;
            border-left: 4px solid #e5e7eb;
            margin-bottom: 15px;
            background: #f9fafb;
            border-radius: 4px;
        }}

        .test-item.passed {{
            border-left-color: #10b981;
            background: #f0fdf4;
        }}

        .test-item.failed {{
            border-left-color: #ef4444;
            background: #fef2f2;
        }}

        .test-item-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .test-id {{
            font-weight: bold;
            color: #667eea;
        }}

        .test-status {{
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}

        .test-status.passed {{
            background: #10b981;
            color: white;
        }}

        .test-status.failed {{
            background: #ef4444;
            color: white;
        }}

        .test-name {{
            font-size: 16px;
            color: #1f2937;
            margin-bottom: 8px;
        }}

        .test-metrics {{
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #6b7280;
        }}

        .metric {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .metric-label {{
            font-weight: 500;
        }}

        .performance-chart {{
            margin-top: 20px;
        }}

        .chart-bar {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}

        .chart-label {{
            width: 150px;
            font-size: 14px;
            color: #6b7280;
        }}

        .chart-bar-container {{
            flex: 1;
            height: 30px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }}

        .chart-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }}

        .chart-value {{
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }}

        .badge.excellent {{
            background: #d1fae5;
            color: #065f46;
        }}

        .badge.good {{
            background: #dbeafe;
            color: #1e40af;
        }}

        .badge.fair {{
            background: #fef3c7;
            color: #92400e;
        }}

        .badge.poor {{
            background: #fee2e2;
            color: #991b1b;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>客户搜索系统 - 真实场景测试报告</h1>
            <p>基于94条代理人原始搜索诉求</p>
            <p>测试时间: {test_time}</p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="value">{total_tests}</div>
            </div>
            <div class="summary-card">
                <h3>通过数</h3>
                <div class="value success">{total_passed}</div>
            </div>
            <div class="summary-card">
                <h3>失败数</h3>
                <div class="value {fail_class}">{total_failed}</div>
            </div>
            <div class="summary-card">
                <h3>通过率</h3>
                <div class="value {pass_rate_class}">{pass_rate}%</div>
            </div>
            <div class="summary-card">
                <h3>平均响应时间</h3>
                <div class="value">{avg_time}ms</div>
            </div>
        </div>

        <div class="section">
            <h2>各优先级测试结果</h2>
            {priority_sections}
        </div>

        <div class="section">
            <h2>性能分析</h2>
            <div class="performance-chart">
                {performance_chart}
            </div>
        </div>

        <div class="footer">
            <p>客户搜索系统 V3.0 | 生成时间: {generation_time}</p>
            <p>测试代理人: A000001 | 数据量: 99,488条</p>
        </div>
    </div>
</body>
</html>
"""

def load_test_report(report_file: str) -> Dict[str, Any]:
    """加载测试报告JSON文件"""
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_performance_badge(avg_time: float) -> str:
    """获取性能评级徽章"""
    if avg_time < 50:
        return '<span class="badge excellent">优秀</span>'
    elif avg_time < 100:
        return '<span class="badge good">良好</span>'
    elif avg_time < 200:
        return '<span class="badge fair">一般</span>'
    else:
        return '<span class="badge poor">需优化</span>'

def generate_priority_section(suite_name: str, results: Dict[str, Any]) -> str:
    """生成优先级测试部分的HTML"""
    priority = suite_name.split("级")[0]
    priority_class = priority.lower()

    pass_rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0

    html = f"""
    <div class="priority-section">
        <div class="priority-header">
            <h3>{suite_name}</h3>
            <div>
                <span class="priority-badge {priority_class}">{priority}</span>
                <span style="margin-left: 10px;">通过: {results["passed"]}/{results["total"]} ({pass_rate:.1f}%)</span>
                <span style="margin-left: 10px;">平均: {results["avg_time"]:.2f}ms</span>
                {get_performance_badge(results["avg_time"])}
            </div>
        </div>
        <div class="test-list">
    """

    for detail in results["details"]:
        status_class = "passed" if detail["passed"] else "failed"
        status_text = "通过" if detail["passed"] else "失败"

        html += f"""
            <div class="test-item {status_class}">
                <div class="test-item-header">
                    <span class="test-id">{detail["test_id"]}</span>
                    <span class="test-status {status_class}">{status_text}</span>
                </div>
                <div class="test-name">{detail["name"]}</div>
                <div class="test-metrics">
                    <div class="metric">
                        <span class="metric-label">响应时间:</span>
                        <span>{detail["response_time"]:.2f}ms</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">结果数:</span>
                        <span>{detail["total_results"]}</span>
                    </div>
                </div>
            </div>
        """

    html += """
        </div>
    </div>
    """

    return html

def generate_performance_chart(all_results: Dict[str, Dict]) -> str:
    """生成性能图表HTML"""
    html = ""

    max_time = max(r["avg_time"] for r in all_results.values() if r["avg_time"] > 0)

    for suite_name, results in all_results.items():
        if results["avg_time"] > 0:
            percentage = (results["avg_time"] / max_time * 100)
            html += f"""
            <div class="chart-bar">
                <div class="chart-label">{suite_name}</div>
                <div class="chart-bar-container">
                    <div class="chart-bar-fill" style="width: {percentage}%"></div>
                    <div class="chart-value">{results["avg_time"]:.2f}ms</div>
                </div>
            </div>
            """

    return html

def generate_html_report(report_data: Dict[str, Any], output_file: str):
    """生成HTML测试报告"""
    # 计算总体统计
    total_tests = sum(r["total"] for r in report_data.values())
    total_passed = sum(r["passed"] for r in report_data.values())
    total_failed = sum(r["failed"] for r in report_data.values())
    pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    all_avg_times = [r["avg_time"] for r in report_data.values() if r["avg_time"] > 0]
    avg_time = sum(all_avg_times) / len(all_avg_times) if all_avg_times else 0

    # 确定样式类
    fail_class = "error" if total_failed > 0 else "success"
    if pass_rate >= 95:
        pass_rate_class = "success"
    elif pass_rate >= 90:
        pass_rate_class = "warning"
    else:
        pass_rate_class = "error"

    # 生成各优先级部分
    priority_sections = ""
    for suite_name, results in report_data.items():
        priority_sections += generate_priority_section(suite_name, results)

    # 生成性能图表
    performance_chart = generate_performance_chart(report_data)

    # 填充模板
    html = HTML_TEMPLATE.format(
        test_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_tests=total_tests,
        total_passed=total_passed,
        total_failed=total_failed,
        fail_class=fail_class,
        pass_rate=f"{pass_rate:.1f}",
        pass_rate_class=pass_rate_class,
        avg_time=f"{avg_time:.2f}",
        priority_sections=priority_sections,
        performance_chart=performance_chart,
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # 保存HTML文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML测试报告已生成: {output_file}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python generate_test_report.py <test_report.json>")
        print("示例: python generate_test_report.py test_report_20260303_120000.json")
        sys.exit(1)

    report_file = sys.argv[1]

    if not Path(report_file).exists():
        print(f"错误: 找不到测试报告文件: {report_file}")
        sys.exit(1)

    print(f"正在加载测试报告: {report_file}")
    report_data = load_test_report(report_file)

    # 生成HTML报告文件名
    output_file = report_file.replace('.json', '.html')

    print(f"正在生成HTML报告...")
    generate_html_report(report_data, output_file)

    print(f"\n可以在浏览器中打开查看:")
    print(f"  open {output_file}")

if __name__ == "__main__":
    main()
