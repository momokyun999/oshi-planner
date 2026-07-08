"""
遠征記録の保存・読込。
将来：データベース（Supabase等）に切り替え予定
"""

import json
import os

RECORDS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "oshi_records.json",
)


def load_records():
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _write_records(records):
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def save_record(record):
    records = load_records()
    records.append(record)
    _write_records(records)
    return records


def delete_record(record_id):
    records = load_records()
    records = [r for r in records if r["id"] != record_id]
    _write_records(records)
    return records


def update_record(record_id, updated_data):
    """指定IDのレコードを更新する"""
    records = load_records()
    for i, r in enumerate(records):
        if r["id"] == record_id:
            records[i] = updated_data
            break
    _write_records(records)
    return records
