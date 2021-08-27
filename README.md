# praktikum_new_diplom
![foodgram-project-react workflow](https://github.com/Dvoryanoff/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Продуктовый помощник Foodgram.

Проект развернут по адресу: http:/130.193.38.100/

## Описание сервиса

Проект Продуктовый помощник - это сайт, который позволяет пользователям публиковать и делиться рецептами, добавлять чужие рецепты в избранное и подписываться на публикации других авторов, а также автоматически создавать список продуктов, , которые нужно купить для приготовления выбранных блюд, и скачивать его.

## Установка сервиса

* backend - образ бэкенда
* frontend - образ фронтенда
* postgres - образ базы данных PostgreSQL v 12.04
* nginx

## Команда клонирования репозитория:

```
- git clone https://github.com/dvoryanoff/foodgram-project-react.git
```

## Заполнение .env:

Чтобы добавить переменную в .env необходимо открыть файл .env в корневой директории проекта и поместить туда переменную в формате имя_переменной=значение. Пример .env файла:

```
- DB_ENGINE=my_db
- DB_NAME=postgres
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- DB_HOST=db
- DB_PORT=5432
```
## Запуск проекта:
 * Установите Докер
 * Перейдите в папку в проекте infra/
 * Выполните команду:

```
- docker-compose up -d --build
```

## Первоначальная настройка Django:

```
- sudo docker-compose exec backend python manage.py migrate --noinput
- sudo docker-compose exec backend python manage.py collectstatic --no-input
```

## Создание суперпользователя:
```
- sudo docker-compose exec backend python manage.py createsuperuser
```
## Загружаем фикстуры ингредиентов:
```
- sudo docker-compose exec backend  python manage.py loaddata ingredients.json
```


## После каждого обновления репозитория:

 * Проверка кода на соответствие стандарту PEP8 (flake8)
 * Сборка и доставка докер-образов на Docker Hub
 * Деплой
 * Отправка уведомления в Telegram

## Данные для входа:

### Суперпользователь:

* ## Email: superuser@mail.ru
* ## Password: 123456


### Тестовый пользователь:

* ## Email: vpupkin@mail.ru
* ## Password: vasyarun182


## Разработчик: 
* [Владимир Дворянов](https://github.com/dvoryanoff)
