"""Unit tests for the new User and Alert ORM models (schema-level checks)."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from backend.app.db.session import Base
import backend.app.models  # registers all models on Base.metadata  # noqa: F401


@pytest.fixture(scope="module")
def in_memory_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


def test_users_table_exists(in_memory_db):
    inspector = inspect(in_memory_db)
    assert "users" in inspector.get_table_names()


def test_alerts_table_exists(in_memory_db):
    inspector = inspect(in_memory_db)
    assert "alerts" in inspector.get_table_names()


def test_incidents_has_resolved_at(in_memory_db):
    inspector = inspect(in_memory_db)
    col_names = [c["name"] for c in inspector.get_columns("incidents")]
    assert "resolved_at" in col_names


def test_users_columns(in_memory_db):
    inspector = inspect(in_memory_db)
    col_names = [c["name"] for c in inspector.get_columns("users")]
    for expected in ["id", "email", "username", "hashed_password", "role", "is_active", "is_verified"]:
        assert expected in col_names, f"Missing column: {expected}"


def test_alerts_columns(in_memory_db):
    inspector = inspect(in_memory_db)
    col_names = [c["name"] for c in inspector.get_columns("alerts")]
    for expected in ["id", "metric_field", "operator", "threshold_value", "severity", "is_active"]:
        assert expected in col_names, f"Missing column: {expected}"


def test_user_create_and_query(in_memory_db):
    from datetime import datetime, timezone
    from sqlalchemy.orm import Session
    from backend.app.models.user import User

    Session_ = sessionmaker(bind=in_memory_db)
    with Session_() as session:
        user = User(
            email="admin@example.com",
            username="admin",
            hashed_password="hashed_secret",
            role="admin",
        )
        session.add(user)
        session.commit()
        fetched = session.query(User).filter_by(email="admin@example.com").first()
        assert fetched is not None
        assert fetched.role == "admin"
        assert fetched.is_active is True
        assert fetched.is_verified is False


def test_alert_create_and_query(in_memory_db):
    from sqlalchemy.orm import Session
    from backend.app.models.alert import Alert

    Session_ = sessionmaker(bind=in_memory_db)
    with Session_() as session:
        rule = Alert(
            name="High CPU",
            metric_field="cpu_usage",
            operator="gt",
            threshold_value=85.0,
            severity="critical",
        )
        session.add(rule)
        session.commit()
        fetched = session.query(Alert).filter_by(name="High CPU").first()
        assert fetched is not None
        assert fetched.threshold_value == 85.0
        assert fetched.is_active is True
