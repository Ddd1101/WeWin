"""
WeWin 数据库备份脚本

用法：
    python backup_db.py                # 备份一次，保留最近 10 份
    python backup_db.py --keep 20      # 备份一次，保留最近 20 份

说明：
    - 使用 SQLite 在线备份 API（sqlite3.Connection.backup），即使后端运行中也安全。
    - 备份文件命名：db.sqlite3.bak.<YYYYMMDDHHMMSS>，与现有历史备份命名一致。
    - 备份保存在 Server/ 目录，与 db.sqlite3 同级。
"""
import sys
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db.sqlite3"


def backup(keep: int = 10) -> int:
    if not DB_PATH.exists():
        print(f"错误：数据库文件不存在 {DB_PATH}", file=sys.stderr)
        return 1

    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    dest = BASE_DIR / f"db.sqlite3.bak.{ts}"

    # SQLite 在线备份，避免直接复制运行中的库导致数据不一致
    src = sqlite3.connect(str(DB_PATH))
    dst = sqlite3.connect(str(dest))
    try:
        with dst:
            src.backup(dst)
    finally:
        src.close()
        dst.close()

    print(f"备份成功：{dest.name} ({dest.stat().st_size} bytes)")

    # 清理旧备份，仅保留最近 keep 份
    backups = sorted(BASE_DIR.glob("db.sqlite3.bak.*"), key=lambda p: p.stat().st_mtime)
    removed = 0
    for old in backups[:-keep] if keep > 0 else []:
        old.unlink()
        removed += 1
        print(f"清理旧备份：{old.name}")

    print(f"当前共 {max(len(backups) - removed, 1)} 份备份，保留最近 {keep} 份")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WeWin 数据库备份")
    parser.add_argument("--keep", type=int, default=10, help="保留最近 N 份备份（默认 10）")
    args = parser.parse_args()
    sys.exit(backup(args.keep))
