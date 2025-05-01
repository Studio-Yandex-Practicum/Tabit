# import random
# import string
# from datetime import datetime, timedelta


# def generate_task_data(
#     problem_id=None, meeting_id=None, owner_id=None, executers=None, all_fields=False
# ):
#     """Генерирует реалистичные данные для создания задач."""

#     def random_string(length=10):
#         """Генерирует случайную строку указанной длины."""
#         return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

#     data = {
#         'name': f'Задача {random_string(7)}',
#         'date_completion': date_completion,
#         'status': 'Новая',
#         'problem_id': problem_id,
#         'meeting_id': meeting_id,
#         'owner_id': owner_id,
#         'date_meeting': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
#         'place': f'Место встречи {random_string(6)}',
#     }
#     if all_fields:
#         data.update(
#             {
#                 'description': f'Описание встречи {random_string(15)}',
#             }
#         )
#     if members:
#         data.update(
#             {
#                 'members': members,
#             }
#         )
#     return data
