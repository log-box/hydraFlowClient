from sqlalchemy import create_engine, MetaData, select, desc, func, and_
from sqlalchemy.orm import sessionmaker
from tenacity import retry, wait_fixed, stop_after_delay, retry_if_exception_type
from app.logger import logger


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
Session = sessionmaker(bind=engine)


class FlowTableNotReady(Exception): pass

@retry(
    wait=wait_fixed(2),
    stop=stop_after_delay(30),
    retry=retry_if_exception_type(FlowTableNotReady)
)
def get_flow_table():
    logger.info("Пробуем получить таблицу hydra_oauth2_flow...")
    metadata = MetaData()
    metadata.reflect(bind=engine, only=["hydra_oauth2_flow"])
    if "hydra_oauth2_flow" not in metadata.tables:
        logger.warning("Таблица ещё не готова, повторим позже.")
        raise FlowTableNotReady("hydra_oauth2_flow отсутствует")
    return metadata.tables["hydra_oauth2_flow"]


def fetch_latest_flow_by_session_and_subject(login_session_id: str, subject: str) -> dict | None:
    session = Session()
    try:
        flow = get_flow_table()
        query = (
            select(flow)
            .where(and_(
                flow.c.login_session_id == login_session_id,
                flow.c.subject == subject,
                func.jsonb_array_length(flow.c.granted_scope) > 0,
                flow.c.consent_error == '{}',
                flow.c.login_error == '{}'
            ))
            .order_by(desc(flow.c.requested_at))
            .limit(1)
        )
        row = session.execute(query).mappings().first()
        return dict(row) if row else None
    finally:
        session.close()
