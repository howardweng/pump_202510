#!/usr/bin/env python3
"""運行測試並生成中文報告"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 項目根目錄
project_root = Path(__file__).parent.parent
tests_dir = project_root / "tests"
reports_dir = tests_dir / "reports"

# 創建報告目錄
reports_dir.mkdir(parents=True, exist_ok=True)

# 生成時間戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_file = reports_dir / f"測試報告_{timestamp}.html"

print("="*60)
print("🧪 幫浦測試平台 - 自動化測試")
print("="*60)
print(f"📁 測試目錄: {tests_dir}")
print(f"📊 報告將保存到: {report_file}")
print("="*60)
print()

# 運行 pytest
cmd = [
    sys.executable, "-m", "pytest",
    str(tests_dir),
    "-v",
    "--tb=short",
    f"--html={report_file}",
    "--self-contained-html",
    "--css=tests/reports/custom.css",
    "--color=yes"
]

try:
    result = subprocess.run(cmd, cwd=project_root, check=False)
    
    print()
    print("="*60)
    if result.returncode == 0:
        print("✅ 所有測試通過！")
    else:
        print(f"⚠️ 測試完成，但有 {result.returncode} 個失敗項目")
    print(f"📊 詳細報告: {report_file}")
    print("="*60)
    
    sys.exit(result.returncode)
    
except KeyboardInterrupt:
    print("\n⏸️ 測試被中斷")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 運行測試時發生錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

