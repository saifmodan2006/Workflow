import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    Date,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "websites.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Website(Base):
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    website = Column(String(512), nullable=False, index=True)
    contact_name = Column(String(256), nullable=True)
    contact_email = Column(String(256), nullable=True)
    module = Column(String(32), nullable=True)  # Free, Outreach, Exchange, Pay
    traffic = Column(Integer, nullable=True)
    da = Column(Integer, nullable=True)
    status = Column(String(64), nullable=True)
    outreach_count = Column(Integer, default=0)
    last_contacted = Column(Date, nullable=True)
    next_followup = Column(Date, nullable=True)
    assignee = Column(String(128), nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, nullable=False, index=True)
    action = Column(String(128), nullable=False)
    note = Column(Text, nullable=True)
    user = Column(String(128), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    """Create database file and tables if they don't exist."""
    os.makedirs(BASE_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()


def add_website(data: Dict[str, Any], user: Optional[str] = None) -> Website:
    s = get_session()
    try:
        w = Website(**data)
        s.add(w)
        s.commit()
        s.refresh(w)

        # create activity log for creation
        log = ActivityLog(website_id=w.id, action='created', note=None, user=user)
        s.add(log)
        s.commit()

        return w
    finally:
        s.close()


def update_website(website_id: int, updates: Dict[str, Any], user: Optional[str] = None) -> Optional[Website]:
    s = get_session()
    try:
        w = s.query(Website).filter(Website.id == website_id).first()
        if not w:
            return None
        for k, v in updates.items():
            if hasattr(w, k):
                setattr(w, k, v)
        w.updated_at = datetime.utcnow()
        s.add(w)
        s.commit()
        s.refresh(w)

        # create activity log
        action = updates.get('action') or 'update'
        note = updates.get('notes') if 'notes' in updates else None
        log = ActivityLog(website_id=w.id, action=action, note=note, user=user)
        s.add(log)
        s.commit()

        return w
    finally:
        s.close()


def list_websites(filters: Dict[str, Any] = None, limit: int = 1000) -> List[Website]:
    s = get_session()
    try:
        q = s.query(Website)
        if filters:
            if 'module' in filters and filters['module']:
                q = q.filter(Website.module == filters['module'])
            if 'status' in filters and filters['status']:
                q = q.filter(Website.status == filters['status'])
            if 'assignee' in filters and filters['assignee']:
                q = q.filter(Website.assignee == filters['assignee'])
            if 'min_da' in filters and filters['min_da'] is not None:
                q = q.filter(Website.da >= filters['min_da'])
            if 'max_da' in filters and filters['max_da'] is not None:
                q = q.filter(Website.da <= filters['max_da'])
        return q.order_by(Website.id).limit(limit).all()
    finally:
        s.close()


def get_activity(website_id: int) -> List[ActivityLog]:
    s = get_session()
    try:
        return s.query(ActivityLog).filter(ActivityLog.website_id == website_id).order_by(ActivityLog.timestamp.desc()).all()
    finally:
        s.close()


def import_csv(path: str, source: str = "upload") -> int:
    """Import CSV to the database. Returns number of rows added.

    Expected headers (case-insensitive): website, contact_email, contact_name, module, traffic, da, status, assignee, notes
    """
    import pandas as pd

    df = pd.read_csv(path)
    # normalize columns
    col_map = {c.lower(): c for c in df.columns}
    rows_added = 0
    s = get_session()
    try:
        for _, row in df.iterrows():
            record = {
                'website': row.get(col_map.get('website')) or row.get(col_map.get('url')) or None,
                'contact_email': row.get(col_map.get('contact_email')) or None,
                'contact_name': row.get(col_map.get('contact_name')) or None,
                'module': row.get(col_map.get('module')) or None,
                'traffic': int(row.get(col_map.get('traffic')) or 0) if not pd.isna(row.get(col_map.get('traffic'))) else None,
                'da': int(row.get(col_map.get('da')) or 0) if not pd.isna(row.get(col_map.get('da'))) else None,
                'status': row.get(col_map.get('status')) or 'New',
                'assignee': row.get(col_map.get('assignee')) or None,
                'notes': row.get(col_map.get('notes')) or None,
                'source': source,
            }
            if record['website']:
                w = Website(**record)
                s.add(w)
                rows_added += 1
        s.commit()
    finally:
        s.close()
    return rows_added


def export_csv(path: str) -> int:
    import pandas as pd

    s = get_session()
    try:
        rows = s.query(Website).all()
        data = []
        for r in rows:
            data.append({
                'id': r.id,
                'website': r.website,
                'contact_name': r.contact_name,
                'contact_email': r.contact_email,
                'module': r.module,
                'traffic': r.traffic,
                'da': r.da,
                'status': r.status,
                'assignee': r.assignee,
                'notes': r.notes,
                'source': r.source,
                'created_at': r.created_at,
                'updated_at': r.updated_at,
            })
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)
        return len(data)
    finally:
        s.close()
