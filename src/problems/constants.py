# Константы к валидаторам (Общие)
ERROR_COMPANY_NOT_FOUND = 'Такая компания не найдена'
ERROR_PROBLEM_NOT_FOUND = 'Такая проблема не найдена'
ERROR_TASK_NOT_FOUND = 'Такая задача не найдена'


# Константы к валидаторам (Problem)
ERROR_PROBLEM_NAME_EMPTY = 'Название проблемы не может быть пустым'


# Константы к валидаторам (Meeting)
ERROR_MEETING_TITLE_EMPTY = 'Название встречи не может быть пустым'
ERROR_MEETING_TITLE_ALREADY_IN_USE = 'Такое название встречи уже используется'
ERROR_DATE_CANNOT_BE_EARLIER = 'Дата не может быть раньше'
ERROR_DATE_MEETING_ALREADY_IN_USE = 'Дата встречи уже занята'


# Константы к валидаторам (Task)
ERROR_TASK_NAME_EMPTY = 'Название задачи не может быть пустым'
ERROR_EXECUTORS_MUST_BE_UUID_FORMAT = 'Исполнители должны быть в формате UUID'
ERROR_TASK_FOR_PROBLEM_NOT_FOUND = 'Задач для проблем нет'
ERROR_DATE_SHOULD_BE_FUTURE = 'Дата должна быть в будущем'


# Константы к схемам
TITLE_COMMENTS_TEXT_CREATE: str = 'Новый комментарий к треду.'
TITLE_COMMENTS_TEXT_UPDATE: str = 'Обновить комментарий к треду.'
TITLE_MESSAGE_FEED_IMPORTANT: str = 'Важность треда.'
TITLE_MESSAGE_FEED_TEXT: str = 'Название треда.'

# Константы к валидаторам
VALID_WRONG_COMPANY: str = 'Разрешён доступ только к своей компании.'
VALID_WRONG_PROBLEM: str = 'Разрешён доступ только к проблемам своей компании.'
VALID_WRONG_MESSAGE_FEED: str = 'Для указанной проблемы запрошенный тред не найден.'
VALID_COMMENT_NOT_OWNER: str = 'Вы можете изменять только свои комментарии.'
VALID_LIKE_OWN_COMMENT: str = 'Нельзя менять рейтинг собственного комментария.'
VALID_REPEATED_LIKE: str = 'Вы уже лайкнули данный комментарий.'
VALID_NOT_LIKED_COMMENT: str = 'Вы не лайкали данный комментарий.'
