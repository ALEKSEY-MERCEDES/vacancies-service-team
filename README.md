# Vacancies Service Team Project
Telegram-бот для поиска и управления актуальными вакансиями. Бот парсит вакансии с сайтов компаний, предоставляет умные рекомендации и позволяет кандидатам и рекрутерам эффективно взаимодействовать.
# Состав команды
* Алексев Докучаев – Тимлид
* Петров Егор
* Арсений Рыбаков
* Георгий Аненко
* Анна Богословская 

# Графики и схемы

## Архитектура бота вакансий
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

## Реляционная база данных
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
        boolean seen
    }
```

## Регистрация пользователей
```mermaid 
graph TD
    Start(/start) --> CheckDB{Есть в БД?}
    
    CheckDB -- Да --> Menu[Главное Меню]
    CheckDB -- Нет --> RoleSelect{Выбор роли}
    
    %% Ветка Соискателя
    RoleSelect -- Соискатель --> FormCand[FSM: Заполнение анкеты]
    FormCand --> FileUpload[Загрузка резюме]
    FileUpload --> SaveCand[Сохранение в БД]
    SaveCand --> Menu
    
    %% Ветка Рекрутера
    RoleSelect -- Рекрутер --> FormRec[FSM: Описание вакансии]
    FormRec --> SaveRec[Сохранение в БД]
    SaveRec --> WaitCheck(Ожидание модерации Админом)
    
    WaitCheck -.->|Админ одобрил| Notify(Уведомление в ТГ)
    Notify --> Menu
    
    %% Ветка Админа
    RoleSelect -- Админ --> ConfigCheck{ID в config.py?}
    ConfigCheck -- Да --> AdminPanel[Админ Панель]
    ConfigCheck -- Нет --> Ban[Блокировка]
```

## Описание действий соискателя
```mermaid
sequenceDiagram
    actor C as Соискатель
    participant Bot as Бот (Python)
    participant DB as База Данных
    actor R as Рекрутер

    C->>Bot: Нажал "Смотреть вакансии"
    loop Цикл просмотра
        Bot->>DB: Запрос: Дай вакансию (которую я не видел, подходит по фильтрам)
        DB-->>Bot: Данные вакансии (ID: 123)
        
        alt Вакансии закончились
            Bot-->>C: "На сегодня вакансий больше нет"
        else Вакансия найдена
            Bot-->>C: Карточка вакансии + Кнопки
            
            par Ожидание действия
                C->>Bot: Нажал "Откликнуться"
                Bot->>DB: INSERT INTO applications (status='applied')
                Bot->>R: Уведомление: "Новый отклик на вакансию 123!"
                Bot-->>C: "Отклик отправлен!"
            and
                C->>Bot: Нажал "Лайк"
                Bot->>DB: INSERT INTO applications (status='liked')
            and
                C->>Bot: Нажал "Дизлайк"
                Bot->>DB: INSERT INTO applications (status='disliked')
             and
                C->>Bot: Нажал "Пожаловаться"
                 Bot->>DB: Отметка вакансии + репорт админу
            end

            Bot->>Bot: Загрузка следующей вакансии (повтор цикла)
        end
    end
```

## Описание действий рекрутера
```mermaid
sequenceDiagram
    autonumber
    actor R as Рекрутер (User)
    participant Bot as Бот (Logic)
    participant DB as База Данных

    note over R,Bot: Запуск FSM для создания вакансии
    R->>Bot: Нажал кнопку "Создать вакансию"
    
    par Проверка статуса
        Bot->>DB: SELECT: Проверить статус is_approved
        DB-->>Bot: is_approved = True (Одобрен)
    and
        Bot->>Bot: Запуск FSM: VacancyCreation
    end

    rect rgb(19, 94, 123)
    note right of Bot: Пошаговый сбор данных (FSM)
    
    Bot->>R: Запрос: Введите название должности
    R->>Bot: Вводит Название
    
    Bot->>R: Запрос: Описание вакансии
    R->>Bot: Вводит Описание
    
    Bot->>R: Запрос: Вилка зарплаты (от-до)
    R->>Bot: Вводит Зарплату
    
    Bot->>R: Запрос: Город
    R->>Bot: Вводит Город

    Bot->>R: Запрос: Формат работы
    R->>Bot: Вводит Формат работы
    end
    
    note over Bot,DB: Сохранение и публикация
    Bot->>DB: INSERT INTO vacancies (recruiter_id, title, description, ...)
    DB-->>Bot: ID новой вакансии
    
    Bot-->>R: Подтверждение: "Вакансия опубликована!"
```


# Описание проекта

## Визуализация интерфейса пользователя
<div align="center">
  
### Работа бота от лица соискателя

<img src="images/photo_2025-11-25_13-02-10.jpg" width="280" alt="Сообщение бота 1">
<img src="images/photo_2025-11-25_13-02-27.jpg" width="280" alt="Сообщение бота 2">
<img src="images/photo_2025-11-25_13-02-52.jpg" width="280" alt="Сообщение бота 3">
<img src="images/photo_2025-11-25_13-41-47.jpg" width="280" alt="Сообщение бота 8">

### Работа бота от лица рекрутера
<img src="images/photo_2025-11-25_13-03-10.jpg" width="280" alt="Сообщение бота 4">

### Работа бота от лица админа
<img src="images/photo_2025-11-25_13-03-29.jpg" width="280" alt="Сообщение бота 5">
<img src="images/photo_2025-11-25_13-03-49.jpg" width="280" alt="Сообщение бота 6">

<img src="images/photo_2025-11-25_13-04-11.jpg" width="280" alt="Сообщение бота 7">

<img src="images/photo_2025-11-25_13-42-21.jpg" width="280" alt="Сообщение бота 9">

</div>


## Распределение задач, времени и  ролей в команде
| №  | Задача                           | Подзадачи (кратко)                                                  | Оценка (часы) | Ответственный |
|----|----------------------------------|----------------------------------------------------------------------|---------------|---------------|
| 1  | **Проектирование БД**              | User, Condidates, Recruiters, Application, Vacancies, роли, связи     | 10            |Алексей         |
| 2  | **Backend: auth и роли**            | регистрация/логин, JWT, роли (seeker/recruiter/admin)               | 8             | Егор          |
| 3  | **Backend: рекрутеры и соискатели**   | кнопки, связи с бд, обработка ошибок ввода                    | 8             | Георгий          |
| 4  | **Backend: вакансии**               | CRUD вакансий, статусы, фильтры, связь с компанией                  | 10            | Арсений          |
| 5  | **Backend: отклики (Application)**  | создание отклика, статусы, выборка откликов для рекрутера           | 8             | Анна          |
| 6  | **Backend: лайки/дизлайки**         | модель Reaction, логика скрытия “дизлайкнутых” вакансий             | 6             | Арсений             |
| 7  | **TG-бот: соискатель**              | регистрация, профиль, лента вакансий, фильтры, лайк/дизлайк, отклики| 12            | Егор          |
| 8  | **TG-бот: рекрутер**               | вход, создание/редактирование вакансий, просмотр откликов           | 12            | Анна             |
| 9 | **TG-бот: админ**                   | управление пользователями, ролями, компаниями                        | 10            | Георгий             |
| 10 | **Докер + деплой**                  | Dockerfile, docker-compose, запуск backend+БД+бота                  | 10            | Анна    |


# Стек технологий

| Технология                | За что отвечает |
|---------------------------|-----------------|
| **Python**                | Основная логика проекта, backend, работа с БД |
| **FastAPI**               | Backend API для бота, маршруты, обработка запросов |
| **PostgreSQL**            | Хранение пользователей, ролей, компаний, вакансий, откликов, лайков |
| **SQLAlchemy (async)**    | Асинхронная ORM, работа с БД, CRUD-операции |
| **Alembic**               | Миграции схемы БД (создание/изменение таблиц) |
| **Aiogram**               | Telegram-бот: сценарии для соискателя, рекрутера и админа |
| **Pydantic v2**           | Валидация и сериализация данных в API (модели запросов/ответов) |
| **python-dotenv**         | Загрузка конфигурации и секретов из `.env` (БД, токен бота, JWT-ключ) |
| **Docker / Docker Compose** | Запуск backend, БД и бота в контейнерах, единая среда, деплой |



