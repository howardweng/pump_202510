"""Pytest Markdown 報告生成器"""
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class MarkdownReport:
    """生成 Markdown 格式的測試報告"""
    
    def __init__(self, report_path: Path):
        self.report_path = report_path
        self.test_results: List[Dict[str, Any]] = []
        self.summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "error": 0,
            "xfailed": 0,
            "xpassed": 0,
            "duration": 0.0
        }
    
    def pytest_runtest_logreport(self, report):
        """收集測試結果"""
        if report.when == "call":  # 只記錄實際測試執行
            result = {
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "duration": getattr(report, "duration", 0.0),
                "longrepr": str(report.longrepr) if hasattr(report, "longrepr") and report.longrepr else None,
                "sections": report.sections if hasattr(report, "sections") else [],
            }
            self.test_results.append(result)
            self.summary["total"] += 1
            self.summary[report.outcome] = self.summary.get(report.outcome, 0) + 1
            self.summary["duration"] += result["duration"]
    
    def generate_markdown(self) -> str:
        """生成 Markdown 報告內容"""
        lines = []
        
        # 標題
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"# 測試報告")
        lines.append("")
        lines.append(f"**生成時間**: {timestamp}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # 摘要
        lines.append("## 📊 測試摘要")
        lines.append("")
        lines.append("| 項目 | 數量 |")
        lines.append("|------|------|")
        lines.append(f"| 總測試數 | {self.summary['total']} |")
        lines.append(f"| ✅ 通過 | {self.summary['passed']} |")
        lines.append(f"| ❌ 失敗 | {self.summary['failed']} |")
        lines.append(f"| ⏭️ 跳過 | {self.summary.get('skipped', 0)} |")
        lines.append(f"| ⚠️ 錯誤 | {self.summary.get('error', 0)} |")
        lines.append(f"| ⏱️ 總執行時間 | {self.summary['duration']:.2f} 秒 |")
        lines.append("")
        
        # 成功率
        if self.summary['total'] > 0:
            success_rate = (self.summary['passed'] / self.summary['total']) * 100
            lines.append(f"**成功率**: {success_rate:.1f}%")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        # 測試結果詳情
        lines.append("## 📋 測試結果詳情")
        lines.append("")
        
        # 按結果分組
        by_outcome = {}
        for test in self.test_results:
            outcome = test["outcome"]
            if outcome not in by_outcome:
                by_outcome[outcome] = []
            by_outcome[outcome].append(test)
        
        # 顯示順序：failed, error, skipped, passed
        outcome_order = ["failed", "error", "skipped", "passed", "xfailed", "xpassed"]
        outcome_icons = {
            "passed": "✅",
            "failed": "❌",
            "skipped": "⏭️",
            "error": "⚠️",
            "xfailed": "🔶",
            "xpassed": "🔷"
        }
        
        for outcome in outcome_order:
            if outcome not in by_outcome:
                continue
            
            tests = by_outcome[outcome]
            icon = outcome_icons.get(outcome, "•")
            outcome_name = {
                "passed": "通過",
                "failed": "失敗",
                "skipped": "跳過",
                "error": "錯誤",
                "xfailed": "預期失敗",
                "xpassed": "意外通過"
            }.get(outcome, outcome)
            
            lines.append(f"### {icon} {outcome_name} ({len(tests)} 個)")
            lines.append("")
            
            for test in tests:
                # 測試名稱
                test_name = test["nodeid"].split("::")[-1]
                test_file = test["nodeid"].split("::")[0]
                lines.append(f"#### `{test_name}`")
                lines.append("")
                lines.append(f"- **文件**: `{test_file}`")
                lines.append(f"- **完整路徑**: `{test['nodeid']}`")
                lines.append(f"- **執行時間**: {test['duration']:.3f} 秒")
                lines.append("")
                
                # 錯誤信息
                if test["longrepr"] and outcome in ["failed", "error"]:
                    lines.append("**錯誤詳情**:")
                    lines.append("")
                    lines.append("```")
                    # 清理錯誤信息，移除 HTML 實體
                    error_msg = test["longrepr"]
                    error_msg = error_msg.replace("&amp;", "&")
                    error_msg = error_msg.replace("&lt;", "<")
                    error_msg = error_msg.replace("&gt;", ">")
                    error_msg = error_msg.replace("&quot;", '"')
                    error_msg = error_msg.replace("&#x27;", "'")
                    lines.append(error_msg)
                    lines.append("```")
                    lines.append("")
                
                # 日誌輸出
                if test["sections"]:
                    for section_name, section_content in test["sections"]:
                        if section_content.strip():
                            lines.append(f"**{section_name}**:")
                            lines.append("")
                            lines.append("```")
                            lines.append(section_content)
                            lines.append("```")
                            lines.append("")
                
                lines.append("---")
                lines.append("")
        
        return "\n".join(lines)
    
    def pytest_sessionfinish(self, session, exitstatus):
        """測試會話結束時生成報告"""
        markdown_content = self.generate_markdown()
        self.report_path.write_text(markdown_content, encoding="utf-8")
        print(f"\n📝 Markdown 報告已生成: {self.report_path}")


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """註冊 Markdown 報告插件"""
    report_path = config.getoption("--md-report", default=None)
    if report_path:
        report_path = Path(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_report = MarkdownReport(report_path)
        config.pluginmanager.register(markdown_report)


def pytest_addoption(parser):
    """添加命令行選項"""
    parser.addoption(
        "--md-report",
        action="store",
        default=None,
        help="生成 Markdown 格式的測試報告"
    )

