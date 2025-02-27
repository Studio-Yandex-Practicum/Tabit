#!/bin/sh

# Проверка на наличие переменной PGADMIN_DEFAULT_EMAIL в .env
if [ -z ${PGADMIN_DEFAULT_EMAIL} ]
then
    echo "Отсутствует переменная PGADMIN_DEFAULT_EMAIL в .env."
    exit
fi

# Создаём из PGADMIN_DEFAULT_EMAIL название директории в формате <имя>_<домен>
EMAIL_NAME=$(echo ${PGADMIN_DEFAULT_EMAIL} | cut -d "@" -f 1)
EMAIL_DOMAIN=$(echo ${PGADMIN_DEFAULT_EMAIL} | cut -d "@" -f 2)
FOLDER_NAME="${EMAIL_NAME}_${EMAIL_DOMAIN}"

# Содаём нужную папку, присваиваем .pgpass определённые права
mkdir -p /var/lib/pgadmin/storage/${FOLDER_NAME};
cp -f /pgadmin4/.pgpass /var/lib/pgadmin/storage/${FOLDER_NAME}/.pgpass;
chmod 600 /var/lib/pgadmin/storage/${FOLDER_NAME}/.pgpass;

# Запускаем родной entrypoint.sh контейнера
exec /entrypoint.sh;
