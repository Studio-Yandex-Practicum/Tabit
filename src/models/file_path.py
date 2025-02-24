from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseFileLink


class FileProblem(BaseFileLink):
    """
    Модель хранения ссылок на файлы проблем.

    Поля:
        id: Идентификационный номер записи.
        file_path: Путь до файла.
        problem_id: id Problem, внешний ключ.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        problem - Problem.
    """

    # TODO: Каскадное удаление не только записи в таблице, но и самого файла. Сложно.
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='file')


class FileMeeting(BaseFileLink):
    """
    Модель хранения ссылок на файлы встреч.

    Поля:
        id: Идентификационный номер записи.
        file_path: Путь до файла.
        meeting_id: id Meeting, внешний ключ.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        meeting - Meeting.
    """

    # TODO: Каскадное удаление не только записи в таблице, но и самого файла. Сложно.
    meeting_id: Mapped[int] = mapped_column(ForeignKey('meeting.id'))
    meeting: Mapped['Meeting'] = relationship(back_populates='file')


class FileTask(BaseFileLink):
    """
    Модель хранения ссылок на файлы задач.

    Поля:
        id: Идентификационный номер записи.
        file_path: Путь до файла.
        task_id: id Task, внешний ключ.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        task - Task.
    """

    # TODO: Каскадное удаление не только записи в таблице, но и самого файла. Сложно.
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id'))
    task: Mapped['Task'] = relationship(back_populates='file')


class FileMessage(BaseFileLink):
    """
    Модель хранения ссылок на файлы сообщений.

    Поля:
        id: Идентификационный номер записи.
        file_path: Путь до файла.
        message_id: id MessageFeed, внешний ключ.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        message - MessageFeed.
    """

    # TODO: Каскадное удаление не только записи в таблице, но и самого файла. Сложно.
    message_id: Mapped[int] = mapped_column(ForeignKey('messagefeed.id'))
    message: Mapped['MessageFeed'] = relationship(back_populates='file')
