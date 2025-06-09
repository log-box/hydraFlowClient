# context_storage.py — глобальное хранилище всех контекстов по session_id
from typing import Optional

from fastapi import HTTPException

from app.core.context import SessionContext
from app.logger import logger

# Глобальный словарь {session_id: SessionContext}
_context_store: dict[str, SessionContext] = {}


def get_context(session_id: str) -> Optional[SessionContext]:
    """Только возвращает уже существующий контекст. Не создаёт новый."""
    return _context_store.get(session_id)


def set_context(session_id: str, context: SessionContext):
    _context_store[session_id] = context
    logger.debug(f"Контекст сохранён для session_id: {session_id}")


def delete_context(session_id: str):
    _context_store.pop(session_id, None)
    logger.debug(f"Контекст удалён для session_id: {session_id}")


def clear_all_contexts():
    _context_store.clear()
    logger.warning("Очищено всё хранилище контекстов")


def get_session_context(session_id: str) -> SessionContext:
    context = get_context(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="Session not found")
    return context


# Глобальная таблица сопоставлений state -> session_id
_state_to_session: dict[str, str] = {}


def map_state_to_session(state: str, session_id: str):
    _state_to_session[state] = session_id
    logger.debug(f"Сопоставление сохранено: state={state} → session_id={session_id}")


def get_session_id_by_state(state: str) -> Optional[str]:
    return _state_to_session.get(state)
