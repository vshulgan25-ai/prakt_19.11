# Bookstore API — автентифікація і захист

> Цей файл — **шаблон вашого звіту**. Заповніть розділи нижче і закомітьте разом із кодом.
> Умова завдання — у Moodle.

## Варіант

- Номер варіанта: **16**
- Схема: **JWT** (djangorestframework-simplejwt)
- Право: **P3** — читання всім, створення будь-якому автентифікованому, зміна/видалення лише власнику або групі Moderators (`bookstore/permissions.py`)
- Throttle: **17** запитів/год для аноніма · **340** запитів/добу для користувача
- Інтеграція: **I1** — вкладений автор, `owner` рядком, `author_id` на запис, без N+1
- Відеозахист (до 3 хв): <ВСТАВТЕ ПОСИЛАННЯ>

## Запуск

```bash
python3 -m venv venv              # Windows: py -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed             # автори, 30 книг, користувачі й групи
python manage.py runserver
python manage.py test
```

Тестові користувачі (`python manage.py seed`), пароль `pass12345`:

| Користувач | Пошта | Акаунт | Група / роль |
|---|---|---|---|
| alice | alice@kpi.edu.ua | 30 днів | Editors, власниця третини книг |
| bob | bob@lnu.edu.ua | 30 днів | Editors |
| carol | carol@gmail.com | 30 днів | — |
| newbie | newbie@kpi.edu.ua | щойно | Editors |
| moder | moder@gmail.com | 30 днів | Moderators |
| staff | staff@gmail.com | 30 днів | `is_staff` |
| admin | admin@example.com | — | суперкористувач, пароль `admin` |

## Результат тестів

Вставте останні рядки `python manage.py test`:

```
<Found 59 test(s).
System check identified no issues (0 silenced).

Ran 59 tests in 36.712s

OK (skipped=37)>
```

## Журнал `curl -i`

Спочатку `python manage.py runserver`, потім в іншому терміналі. Нижче команди; під кожною вставте **перші рядки** справжньої відповіді.

### 1. Вхід і вихід

```bash
# вхід
curl -i -X POST http://127.0.0.1:8000/api/v1/auth/jwt/create/ \
  -H "Content-Type: application/json" -d '{"username":"alice","password":"pass12345"}'
# змінні для наступних команд
ACCESS=<access з відповіді>
REFRESH=<refresh з відповіді>
# запит із токеном
curl -i http://127.0.0.1:8000/api/v1/books/ -H "Authorization: Bearer $ACCESS"
# вихід (refresh -> чорний список)
curl -i -X POST http://127.0.0.1:8000/api/v1/auth/jwt/logout/ \
  -H "Content-Type: application/json" -d "{\"refresh\":\"$REFRESH\"}"
# refresh після виходу -> 401
curl -i -X POST http://127.0.0.1:8000/api/v1/auth/jwt/refresh/ \
  -H "Content-Type: application/json" -d "{\"refresh\":\"$REFRESH\"}"
# старий access після виходу (див. питання JWT-3)
curl -i http://127.0.0.1:8000/api/v1/books/ -H "Authorization: Bearer $ACCESS"
```

```
<ВІДПОВІДІ:
Вхід: HTTP 200 - отримано access і refresh токени.
Запит до /api/v1/books/ з access-токеном: HTTP 200.
Вихід (logout): HTTP 200.
Запит зі старим access-токеном після logout: HTTP 200.>
```

### 2. Право доступу P3: дозволено і заборонено

```bash
# анонім пише -> 401
curl -i -X POST http://127.0.0.1:8000/api/v1/books/ -H "Content-Type: application/json" \
  -d '{"title":"T","price":"10","author_id":1}'
# bob змінює книгу alice -> 403 (книга №1 належить alice; перевірте через GET)
curl -i -X PATCH http://127.0.0.1:8000/api/v1/books/1/ -H "Authorization: Bearer <access bob>" \
  -H "Content-Type: application/json" -d '{"title":"Hack"}'
# alice змінює свою -> 200;  moder змінює чужу -> 200
```

```
<ВІДПОВІДІ:
Анонімний користувач створює книгу: HTTP 401 - потрібна автентифікація.
Користувач bob змінює книгу alice: HTTP 403 - доступ заборонено.
Користувач alice змінює власну книгу: HTTP 200 - зміни дозволені.
Користувач із групи Moderators змінює чужу книгу: HTTP 200 - зміни дозволені.>
```

### 3. Throttling: останній дозволений запит і `429`

```bash
for i in $(seq 1 18); do curl -s -o /dev/null -w "$i -> %{http_code}\n" http://127.0.0.1:8000/api/v1/authors/; done
curl -i http://127.0.0.1:8000/api/v1/authors/        # 429 + Retry-After
```

```
<ВІДПОВІДІ: 17 разів 200, 18-й 429>
```

### 4. Інтеграційна вимога I1

```bash
curl -i http://127.0.0.1:8000/api/v1/books/1/                    # author = {"id","name"}, owner = "alice"
curl -i -X POST http://127.0.0.1:8000/api/v1/books/ -H "Authorization: Bearer <access alice>" \
  -H "Content-Type: application/json" -d '{"title":"T","price":"10","author_id":999999}'   # 400
```

```
<ВІДПОВІДІ:GET /api/v1/books/1/ — HTTP 200. У відповіді автор повертається вкладеним об'єктом із полями id та name, а owner — рядком "alice".
POST /api/v1/books/ із неіснуючим author_id (999999) — HTTP 400 (Bad Request). API відхиляє неправильний author_id.>
```

## Журнал помилок

Вставте **свої** справжні помилки (приклади нижче замініть, якщо у вас були інші).

| Що побачили (текст помилки або код) | Причина | Що змінили |
|---|---|---|
| `<source is not recognized>` | `<Команда Linux у PowerShell>` | `<Використано venv\Scripts\activate ps1>` |
| `<&& is not a valid statement separator>` | `<Версія PowerShell не підтримує такий запис>` | `<Команди Git виконано окремо>` |
| `<key does not contain a section>` | `<Неправильний синтаксис git config>` | `<Використано git config --global user.name "Veronika">` |


## Дослідницькі питання

Відповіді — моїми словами; джерела: [DRF Authentication](https://www.django-rest-framework.org/api-guide/authentication/), [DRF Throttling](https://www.django-rest-framework.org/api-guide/throttling/), [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/), вихідний код `rest_framework/views.py` та `rest_framework_simplejwt/tokens.py`.

**1. (JWT) Які claims в access і refresh, і за яким сервер їх розрізняє?**
Обидва токени — підписаний JSON із полями `token_type`, `exp`, `iat`, `jti` і `user_id`. Відрізняються вони значенням `token_type`: `"access"` або `"refresh"`. Коли `JWTAuthentication` отримує токен, він перевіряє `token_type` (метод `verify_token_type` у `tokens.py`), тому refresh, подані як Bearer, відхиляються з 401 (це перевіряє тест `test_refresh_token_is_not_access`). Строк життя теж різний: `exp - iat` = 15 хв для access і 1 доба для refresh.

**2. Що роблять разом `ROTATE_REFRESH_TOKENS` і `BLACKLIST_AFTER_ROTATION`?**
`ROTATE_REFRESH_TOKENS=True` змушує `/auth/jwt/refresh/` повертати разом з новим access ще й **новий refresh**. `BLACKLIST_AFTER_ROTATION=True` заносить **старий** refresh у чорний список (таблиця застосунку `token_blacklist`). У результаті кожен refresh можна використати лише один раз: якщо хтось вкрав старий refresh, сервер його не прийме. Без чорного списку ротація нічого б не захищала, бо старий refresh і далі діяв би до закінчення строку.

**3. Що буде зі старим access після logout?**
Після виконання logout запит зі старим access-токеном повернув HTTP 200. Це означає, що access-токен залишається дійсним до завершення терміну його дії. Під час logout до чорного списку додається refresh-токен, але вже виданий access-токен не анулюється.

**4. У якому порядку DRF перевіряє автентифікацію, права і ліміти? Чому 401 не витрачає ліміт аноніма?**
У `APIView.initial()` (`rest_framework/views.py`) викликаються по черзі: `perform_authentication` → `check_permissions` → `check_throttles`. Якщо анонім робить `POST /api/v1/books/`, наш клас прав у `check_permissions` кидає відмову (`NotAuthenticated` → 401), і до `check_throttles` код не доходить. Запис про запит у кеш пише саме метод `allow_request` у throttle, тому 401-запити лічильник аноніма не збільшують. У моєму варіанті це видно так: 30 анонімних `POST /books/` поспіль повертають 401 і ніколи 429, а 18-й анонімний `GET /authors/` (там права `AllowAny`) уже дає 429.

## Якщо користувались ШІ

Що саме питали і що з відповіді виявилось неправильним або не підійшло до вашого коду.
Якщо не користувались — так і напишіть.

<### Використання ШІ

Під час виконання практичної роботи я використовувала ChatGPT як допоміжний інструмент для навчання та розв'язання проблем.
він допомагав :
- розібратися з принципами роботи Django REST Framework та JWT-автентифікації;
- зрозуміти налаштування дозволів користувачів і системи обмеження запитів (throttling);
- розібратися з помилками під час роботи в PowerShell;
- отримати пояснення щодо команд Git та роботи з GitHub;
- оформити README з описом виконаної роботи та результатів перевірки.
>
