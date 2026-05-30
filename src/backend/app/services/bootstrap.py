from sqlalchemy import inspect, text

from ..database import Base, engine


def _ensure_sqlite_columns() -> None:
    inspector = inspect(engine)

    if "learning_sessions" in inspector.get_table_names():
        learning_session_columns = {column["name"] for column in inspector.get_columns("learning_sessions")}
        if "recommendation_summary" not in learning_session_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE learning_sessions ADD COLUMN recommendation_summary TEXT DEFAULT ''"))

    if "agent_traces" in inspector.get_table_names():
        agent_trace_columns = {column["name"] for column in inspector.get_columns("agent_traces")}
        with engine.begin() as connection:
            if "decision_reason" not in agent_trace_columns:
                connection.execute(text("ALTER TABLE agent_traces ADD COLUMN decision_reason TEXT DEFAULT ''"))
            if "impact_on_result" not in agent_trace_columns:
                connection.execute(text("ALTER TABLE agent_traces ADD COLUMN impact_on_result TEXT DEFAULT ''"))


def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_columns()
