from dataclasses import dataclass

from fastapi import status


@dataclass
class URL:
    """Все пути используемые в тестах."""

    ADMIN_AUTH: str = '/api/v1/admin/auth/'
    ADMIN_LOGIN: str = '/api/v1/admin/auth/login'
    ADMIN_LOGOUT: str = '/api/v1/admin/auth/logout'
    ADMIN_ME: str = '/api/v1/admin/auth/me'
    ADMIN_REFRESH: str = '/api/v1/admin/auth/refresh-token'
    USER_LOGIN: str = '/api/v1/auth/login'
    USER_LOGOUT: str = '/api/v1/auth/logout'
    USER_REFRESH: str = '/api/v1/auth/refresh-token'

    # URLs для problem_feeds.py
    MESSAGE_FEED_URL: str = '/api/v1/Zorg/problems/1/thread'
    MESSAGE_FEED_BAD_URL: str = '/api/v1/Zorg/problems/2/thread'
    COMMENTS_URL: str = '/api/v1/Zorg/problems/1/1/comments'
    COMMENTS_WRONG_MESSAGE_FEED_URL: str = '/api/v1/Zorg/problems/1/2/comments'
    COMMENTS_PATCH_DELETE_URL: str = '/api/v1/Zorg/problems/1/1/comments/1'
    COMMENTS_PATCH_DELETE_404_URL: str = '/api/v1/Zorg/problems/1/1/comments/99'
    LIKE_URL: str = '/api/v1/Zorg/problems/1/1/comments/1/like'
    LIKE_BAD_URL: str = '/api/v1/Zorg/problems/1/2/comments/1/like'
    UNLIKE_URL: str = '/api/v1/Zorg/problems/1/1/comments/1/unlike'


GOOD_PASSWORD: str = 'string123STRING'
BAD_PASSWORD: tuple[str, ...] = (
    'string123STRING',
    'STRING123STRING',
    'stringSTRING',
    'string123string',
    '!string123STRING',
    's123S',
)
BAD_EMAIL: tuple[str, ...] = (
    'user@example.',
    'user@.com',
    '@example.com',
    'user@exa mple.com',
    'user@ex@ample.com',
)
PAYLOAD_FOR_CREATE_ADMIN: tuple[dict, ...] = (
    {
        'patronymic': 'string',
        'phone_number': 'string',
        'email': 'user1@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
    {
        'phone_number': 'string',
        'email': 'user2@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
    {
        'patronymic': 'string',
        'email': 'user3@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
    {
        'email': 'user4@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
)
PAYLOAD_BAD_FOR_CREATE_ADMIN: tuple[dict, ...] = (
    {
        'email': 'user1@example.com',
        'password': GOOD_PASSWORD,
        'name': 'string',
    },
    {
        'email': 'user2@example.com',
        'password': GOOD_PASSWORD,
        'surname': 'string',
    },
    {
        'password': GOOD_PASSWORD,
        'name': 'string',
        'surname': 'string',
    },
    {
        'email': 'user4@example.com',
        'name': 'string',
        'surname': 'string',
    },
)
PAYLOAD_FOR_PATCH_ADMIN: tuple[dict, ...] = (
    {
        'patronymic': 'Императрица',
        'phone_number': '8 800 700-06-11',
        'name': 'Киширика',
        'surname': 'Киширису',
    },
    {
        'phone_number': '8 800 700-06-11',
        'surname': 'Киширису',
    },
    {
        'patronymic': 'Императрица',
    },
)

# Константы для тестов problem_feeds.py
MESSAGE_FEED_CREATE_NEW: tuple[tuple] = (
    ({'text': 'feed with important field', 'important': True}, True),
    ({'text': 'feed w/o important field'}, False),
)
MESSAGE_FEED_CREATE_BAD: tuple[tuple] = (
    ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ({'text': 'feed with extra field', 'problem_id': 5}, status.HTTP_422_UNPROCESSABLE_ENTITY),
)
MESSAGE_FEED_CREATE_FOR_ANOTHER_COMPANY: dict[str] = {'text': 'feed for another company'}
PROBLEM_FEEDS_GET_404: tuple[str, ...] = (
    '/api/v1/Zorg/problems/99/thread',
    '/api/v1/Zorg/problems/1/99/comments',
    '/api/v1/Zorg/problems/1/1/comments/99/like',
    '/api/v1/Zorg/problems/1/1/comments/99/unlike',
)
COMMENT_CREATE_NEW: dict[str] = {'text': 'new comment'}
COMMENT_CREATE_BAD: tuple[tuple] = (
    ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ({'text': 'comment with extra field', 'message_id': 5}, status.HTTP_422_UNPROCESSABLE_ENTITY),
)
COMMENT_UPDATE: dict[str] = {'text': 'updated comment'}
COMMENT_UPDATE_BAD: tuple[tuple] = (
    ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ({'text': 'comment with extra field', 'rating': 5}, status.HTTP_422_UNPROCESSABLE_ENTITY),
)
