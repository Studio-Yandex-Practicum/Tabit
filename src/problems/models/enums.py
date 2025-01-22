from enum import Enum


class ConfirmationStatus(str, Enum):
    """Класс для значений поля status модели ConfirmationParticipation"""

    PARTICIPANT = 'Участник'
    OBSERVER = 'Наблюдатель'
