"""Модели для ленты сообщений к проблеме."""

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.annotations import int_pk, owner
from src.models import BaseTabitModel, BaseTag

if TYPE_CHECKING:
    from src.models import CommentFeed, FileMessage, Problem, UserTabit, VotingFeed


class MessageFeed(BaseTabitModel):
    """
    Модель ленты сообщений к проблеме.

    Назначение:
        На странице с проблемой есть возможность вести короткие сообщения по форме форума.

    Поля:
        id: Идентификатор.
        problem_id: Идентификатор проблемы, к которой относится лента сообщений.
        owner_id: Автор сообщения. Внешний ключ.
        text: Текст сообщения.
        important: bool - Есть возможность указать, что сообщение важное.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        problem - Problem;
        owner - UserTabit;
        comments - CommentFeed: к сообщением можно оставлять комментарии;
        voting - VotingFeed: есть возможность в сообщение начать голосование - это варианты;
        file - FileMessage: к сообщению могут быть прикреплены файлы.
    """

    id: Mapped[int_pk]
    problem_id: Mapped[int] = mapped_column(ForeignKey('problem.id'))
    problem: Mapped['Problem'] = relationship(back_populates='messages')
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='messages')
    text: Mapped[str]
    important: Mapped[bool] = mapped_column(default=False)
    comments: Mapped[List['CommentFeed']] = relationship(
        back_populates='message', cascade='all, delete-orphan'
    )
    voting: Mapped[List['VotingFeed']] = relationship(
        back_populates='message', cascade='all, delete-orphan'
    )
    file: Mapped[List['FileMessage']] = relationship(
        back_populates='message', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'owner_id={self.owner_id!r}, '
            f'problem_id={self.problem_id!r})'
        )


class CommentFeed(BaseTabitModel):
    """
    Модель комментариев к сообщению, оставленного к проблеме.

    Назначение:
        На странице с проблемой есть возможность вести короткие сообщения по форме форума.
        Эта модель описывает комментарии к этим сообщениям.

    Поля:
        id: Идентификатор.
        message_id: Идентификатор сообщения, к которому относится комментарий.
        owner_id: Автор комментария. Внешний ключ.
        text: Текст комментария.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        message - MessageFeed;
        owner - UserTabit.
    """

    id: Mapped[int_pk]
    message_id: Mapped[int] = mapped_column(ForeignKey('messagefeed.id'))
    message: Mapped['MessageFeed'] = relationship(back_populates='comments')
    owner_id: Mapped[owner]
    owner: Mapped['UserTabit'] = relationship(back_populates='comments')
    text: Mapped[str]

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'owner_id={self.owner_id!r}, '
            f'message_id={self.message_id!r})'
        )


class VotingFeed(BaseTag):
    """
    Модель вариантов голосований в сообщениях, оставленных к проблеме.

    Назначение:
        На странице с проблемой есть возможность вести короткие сообщения по форме форума.
        А так же позволяет начать голосование в сообщение.
        Эта модель описывает варианты к этим голосованиям.

    Поля:
        id: Идентификатор.
        name: Название варианта.
        message_id: Идентификатор сообщения, к которому относится вариант.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        message - MessageFeed;
        by_user - VotingByUser: связь к таблице с выборами этих вариантов.
    """

    message_id: Mapped[int] = mapped_column(ForeignKey('messagefeed.id'))
    message: Mapped['MessageFeed'] = relationship(back_populates='voting')
    by_user: Mapped['VotingByUser'] = relationship(
        back_populates='voting', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'name={self.name!r}, '
            f'message_id={self.message_id!r})'
        )


class VotingByUser(BaseTabitModel):
    """
    Модель выборов  пользователями вариантов голосований в сообщениях, оставленных к проблеме.

    Назначение:
        На странице с проблемой есть возможность вести короткие сообщения по форме форума.
        А так же позволяет начать голосование в сообщение.
        Эта модель описывает кто какие варианты выбрал.

    Поля:
        id: Идентификатор.
        user_id: id голосовавшего пользователя. Внешний ключ.
        voting_id: Идентификатор варианта голосования.
        created_at: Дата создания записи в таблице. Автозаполнение.
        updated_at: Дата изменения записи в таблице. Автозаполнение.

    Связи (атрибут - Модель):
        user - UserTabit;
        voting - VotingFeed.
    """

    id: Mapped[int_pk]
    user_id: Mapped[owner]
    user: Mapped['UserTabit'] = relationship(back_populates='voting_by')
    voting_id: Mapped[int] = mapped_column(ForeignKey('votingfeed.id'))
    voting: Mapped['VotingFeed'] = relationship(back_populates='by_user')

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'id={self.id!r}, '
            f'user_id={self.user_id!r}, '
            f'voting_id={self.voting_id!r})'
        )
