# Файл для дополнительных настроек PGAdmin. Заменяет параметры из config.py в контейнере.
# Можно использовать либо этот файл, либо в .env указать те же самые параметры, но с приставкой
# PGADMIN_CONFIG_<название параметра>.
# Пример: PGADMIN_CONFIG_UPGRADE_CHECK_ENABLED=False - данный вариант должен использоваться в .env
UPGRADE_CHECK_ENABLED = False
