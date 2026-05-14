"""
session_state_helper.py
=======================
مساعد مشترك لقراءة وكتابة basira_runtime/session_state.json
بمسارات مطلقة وآمنة على كل الأنظمة.

استخدام:
  from session_state_helper import write_session_state, read_session_state
"""
import json
from pathlib import Path
from datetime import datetime, timezone


def _state_path(base_dir: Path) -> Path:
    runtime_dir = base_dir / "basira_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    return runtime_dir / "session_state.json"


def write_session_state(base_dir: Path, **fields) -> None:
    """
    يكتب حقول في session_state.json بمسارات مطلقة.
    
    مثال:
        write_session_state(
            BASE_DIR,
            raw_dataset_path="uploads/myfile.csv",
            task_type="classification",
        )
    """
    path = _state_path(base_dir)

    # اقرأ الحالة الموجودة إن وجدت
    existing: dict = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # حوّل أي مسار نسبي إلى مطلق
    resolved_fields: dict = {}
    for key, value in fields.items():
        if isinstance(value, str) and ("/" in value or "\\" in value):
            # مسار — حوّله إلى مطلق بالنسبة لـ base_dir
            resolved_fields[key] = str((base_dir / value).resolve())
        else:
            resolved_fields[key] = value

    existing.update(resolved_fields)
    existing["base_dir"] = str(base_dir.resolve())
    existing["updated_at"] = datetime.now(timezone.utc).isoformat()

    path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


def read_session_state(base_dir: Path) -> dict:
    """
    يقرأ session_state.json ويرجع dict مع مسارات مطلقة.
    يرجع dict فارغ لو الملف غير موجود.
    """
    path = _state_path(base_dir)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    saved_base = Path(data.get("base_dir", str(base_dir)))

    # حوّل أي مسار مخزون إلى مطلق
    resolved = {}
    for key, value in data.items():
        if isinstance(value, str) and key.endswith("_path"):
            p = Path(value)
            if not p.is_absolute():
                p = (saved_base / p).resolve()
            resolved[key] = str(p)
        else:
            resolved[key] = value

    return resolved
