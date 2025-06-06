from sqlalchemy import create_engine, MetaData, select, desc, func, and_, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker


class DBSettings:
    DB_HOST = "postgres"
    DB_PORT = 5432
    DB_NAME = "hydra"
    DB_USER = "hydra"
    DB_PASSWORD = "hydra_pass123"

    @property
    def url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


db_settings = DBSettings()

engine = create_engine(db_settings.url)
metadata = MetaData()
metadata.reflect(bind=engine)

flow = metadata.tables["hydra_oauth2_flow"]
Session = sessionmaker(bind=engine)


def fetch_latest_flow_by_session_and_subject(login_session_id: str, subject: str) -> dict | None:
    session = Session()
    try:
        query = (
            select(flow)
            .where(and_(
                flow.c.login_session_id == login_session_id,
                flow.c.subject == subject,
                func.jsonb_array_length(flow.c.granted_scope) > 0,
                flow.c.consent_error == '{}'
            ))
            .order_by(desc(flow.c.requested_at))
            .limit(1)
        )
        row = session.execute(query).mappings().first()
        return dict(row) if row else None
    finally:
        session.close()
