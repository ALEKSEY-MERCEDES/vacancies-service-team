# Vacancies Service Team Project
Telegram-бот для поиска и управления актуальными вакансиями. Бот парсит вакансии с сайтов компаний, предоставляет умные рекомендации и позволяет кандидатам и рекрутерам эффективно взаимодействовать.
# Состав команды
* Алексев Докучаев – Тимлид
* Петров Егор
* Арсений Рыбаков
* Георгий Аненко
* Анна Богословская 

# Графики и схемы
```mermaid
graph TD
    %% Определяем стили узлов
    classDef user fill:#f9f,stroke:#333,stroke-width:2px,color:black;
    classDef tg fill:#37aee2,stroke:#333,stroke-width:2px,color:white;
    classDef python fill:#ffd43b,stroke:#333,stroke-width:2px,color:black;
    classDef db fill:#aed581,stroke:#333,stroke-width:2px,color:black;

    %% Узлы
    User((Пользователь<br>Telegram)):::user
    TG[Серверы Telegram<br>Bot API]:::tg
    
    subgraph Server [Ваш Сервер / Python App]
        direction TB
        Aiogram[Aiogram 3<br>Движок бота]:::python
        Router[Роутер / Handlers<br>Логика обработки]:::python
        FSM["FSM<br>Машина состояний<br>(Анкеты)"]:::python
        ORM[SQLAlchemy ORM<br>Работа с данными]:::python
    end
    
    DB[(SQLite<br>База Данных)]:::db

    %% Связи
    User -->|"1. Нажатия кнопок, команды"| TG
    TG -->|"2. Webhook / Updates (JSON)"| Aiogram
    
    Aiogram -->|"3. Маршрутизация"| Router
    Router <-->|"4. Управление шагами"| FSM
    Router -->|"5. Запросы к данным"| ORM
    
    ORM <-->|"6. SQL запросы (CRUD)"| DB
    
    Router -->|"7. Сформированный ответ"| Aiogram
    Aiogram -->|"8. Отправка сообщения"| TG
    TG -->|"9. Сообщение в чате"| User

    %% Применение стилей к рамке
    style Server fill:#fffcee,stroke:#ffd43b,stroke-width:2px;
```

```mermaid
erDiagram
    users ||--o| candidates : "имеет профиль (если соискатель)"
    users ||--o| recruiters : "имеет профиль (если рекрутер)"
    recruiters ||--o{ vacancies : "публикует (1:N)"
    candidates ||--o{ applications : "создает (1:N)"
    vacancies ||--o{ applications : "получает (1:N)"

    users {
        bigint telegram_id PK "Уникальный ID в ТГ"
        string username
        enum role "candidate, recruiter, admin"
        datetime created_at
    }

    candidates {
        int id PK
        bigint user_id FK "Связь с users"
        string full_name
        int age
        string city
        string specialization "IT, Маркетинг..."
        string resume_file_id "ID файла в ТГ"
        string current_company "Текущее место работы"
    }

    recruiters {
        int id PK
        bigint user_id FK "Связь с users"
        string company_name
        boolean is_approved "Подтвержден админом?"
    }

    vacancies {
        int id PK
        int recruiter_id FK "Кто создал"
        string title "Название должности"
        string description "Текст вакансии"
        int salary_min
        int salary_max
        string city
        boolean is_active "Активна ли"
    }

    applications {
        int id PK
        int candidate_id FK "Кто"
        int vacancy_id FK "Куда"
        enum status "liked, applied, complained, disliked, invited, rejected"
        datetime created_at
    }
```

# Описание проекта

## Визуализация интерфейса пользователя
## Функционал

## Распределение задач, времени и  ролей в команде
| №  | Задача                           | Подзадачи (кратко)                                                  | Оценка (часы) | Ответственный |
|----|----------------------------------|----------------------------------------------------------------------|---------------|---------------|
| 1  | **Проектирование БД**              | User, Company, Vacancy, Application, роли, связи, флаги скрытия     | 6             |Алексей         |
| 2  | **Backend: auth и роли**            | регистрация/логин, JWT, роли (seeker/recruiter/admin)               | 8             | Егор          |
| 3  | **Backend: компании и рекрутеры**   | CRUD Company, привязка рекрутера к компании                         | 8             | Георгий          |
| 4  | **Backend: вакансии**               | CRUD вакансий, статусы, фильтры, связь с компанией                  | 10            | Арсений          |
| 5  | **Backend: отклики (Application)**  | создание отклика, статусы, выборка откликов для рекрутера           | 8             | Анна          |
| 6  | **Backend: лайки/дизлайки**         | модель Reaction, логика скрытия “дизлайкнутых” вакансий             | 6             | Арсений             |
| 7  | **Логика прав и скрытий**           | проверка ролей, скрытие кандидатов от их компаний и заданных компаний| 8            | Егор             |
| 8  | **TG-бот: соискатель**              | регистрация, профиль, лента вакансий, фильтры, лайк/дизлайк, отклики| 12            | Лёша          |
| 9  | **TG-бот: рекрутер**               | вход, создание/редактирование вакансий, просмотр откликов           | 12            | Анна             |
| 10 | **TG-бот: админ**                   | управление пользователями, ролями, компаниями                        | 10            | Георгий             |
| 11 | **Тесты**                           | unit + интеграционные, coverage ≥ 65%                               | 16            | все участники          |
| 12 | **Докер + деплой**                  | Dockerfile, docker-compose, запуск backend+БД+бота                  | 10            | Анна    |


# Стек технологий

| Технология                | За что отвечает |
|---------------------------|-----------------|
| **Python**                | Основная логика проекта, backend, работа с БД |
| **FastAPI**               | Backend API для бота, маршруты, обработка запросов |
| **PostgreSQL**            | Хранение пользователей, ролей, компаний, вакансий, откликов, лайков |
| **SQLAlchemy (async)**    | Асинхронная ORM, работа с БД, CRUD-операции |
| **Alembic**               | Миграции схемы БД (создание/изменение таблиц) |
| **Aiogram**               | Telegram-бот: сценарии для соискателя, рекрутера и админа |
| **Pytest**                | Unit- и интеграционные тесты, проверка логики и API |
| **Pydantic v2**           | Валидация и сериализация данных в API (модели запросов/ответов) |
| **python-dotenv**         | Загрузка конфигурации и секретов из `.env` (БД, токен бота, JWT-ключ) |
| **Docker / Docker Compose** | Запуск backend, БД и бота в контейнерах, единая среда, деплой |



