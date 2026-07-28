# 06 Env variables secrets build-time runtime

<!-- CARD-NAV-TOP:START -->
[← 05 Nginx static serving SPA fallback cache headers](<./05 Nginx static serving SPA fallback cache headers.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Production troubleshooting logs rollback smoke tests →](<./07 Production troubleshooting logs rollback smoke tests.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как работать с environment variables и secrets во frontend pipeline?

#### Ответ

Environment variable, или переменная окружения, передаёт процессу конфигурацию вне исходного кода. Во frontend нужно сразу разделить публичную конфигурацию браузера и секреты. Адрес публичного API, имя окружения или публичный Sentry DSN можно отдать клиенту. Пароль базы, приватный ключ API, ключ подписи и токен развёртывания должны использоваться только сервером или CI и никогда не попадать в JavaScript, HTML, карту исходного кода (`source map`) или сетевой ответ браузеру.

Build-time переменная читается во время сборки. Vite статически заменяет обращения к `import.meta.env.VITE_*`, а Next.js встраивает `NEXT_PUBLIC_*` в клиентскую сборку (`bundle`). После `npm run build` значение стало частью файлов, и изменение environment запущенного Nginx или контейнера его не заменит. Префикс означает «разрешено раскрыть браузеру», а не «значение защищено».

Runtime-переменная читается запущенным серверным процессом. Серверный код Next.js может получать значения только для сервера (`server-only`) из `process.env`, но нужно учитывать способ рендеринга: код статически созданной страницы мог выполниться во время build, а динамический серверный обработчик - в runtime. Граница определяется местом выполнения кода, а не только именем файла или переменной.

У статической SPA нет серверного JavaScript, поэтому для runtime config нужен отдельный публичный ресурс. Entrypoint контейнера может создать `config.json` перед запуском Nginx, либо backend может вернуть конфигурацию через отдельную операцию API. Приложение загружает и валидирует config до создания API-клиента и старта запросов. Такой файл не содержит секретов и обычно получает `Cache-Control: no-cache` или версионированный URL, чтобы окружение не осталось со старым адресом.

Подход build once, deploy many означает: CI один раз создаёт артефакт, а staging и production передают ему разную допустимую runtime-конфигурацию. Он уменьшает расхождение между проверенной и выпущенной сборкой. Однако не каждое значение обязано быть runtime: удаление кода на этапе компиляции, публичный базовый путь и некоторые настройки сборщика действительно определяются во время build.

Конфигурацию проверяют как входные данные. Схема задаёт обязательные поля, типы, формат URL и разрешённые значения. Ошибка должна остановить build или server с понятным сообщением. Для SPA, которая загружает config по сети, нужен отдельный экран ошибки и запрет отправлять запросы до успешной проверки. Нельзя молча подставлять production URL при неизвестном окружении.

Секреты хранят в CI/CD variables, secret manager или в механизме платформы. В GitLab protected variable ограничивает доверенные branches и tags, environment scope - конкретное окружение, masked или hidden уменьшает раскрытие через интерфейс и logs. Но job script с доступом к значению может его отправить наружу, поэтому секрет получают только доверенные jobs и на минимальное время. Для Docker build используют BuildKit secret, а не `ARG TOKEN`.

Файлы `.env` являются способом загрузки значений, а не хранилищем секретов. Локальный `.env` добавляют в `.gitignore`, в репозитории оставляют `.env.example` без настоящих credentials. Значения production поступают из платформы. Даже случайно удалённый из Git secret нужно отозвать и заменить: он остаётся в истории и клонах.

Публичная runtime-конфигурация тоже требует контроля. Изменённый `API_BASE_URL` может направить приложение на чужой сервер, поэтому URL ограничивают ожидаемыми origin, CSP `connect-src` и настройками backend CORS. В логи записывают наличие и версию config, но не полные токены и персональные значения.

#### Встречные вопросы

> [!followup] Публичная конфигурация и секрет
> **Вопрос:** Как определить, можно ли передать значение во frontend?
>
> **Ответ:** Нужно предположить, что пользователь прочитает весь загруженный код, HTML, вкладку Network и browser storage. Если знание значения даёт доступ или позволяет подписать доверенный запрос, оно должно остаться на сервере. Публичный идентификатор проекта или DSN допустим, если безопасность строится на серверной проверке прав, origin и ограничении частоты запросов (`rate limit`), а не на его скрытности.

> [!followup] Префикс VITE
> **Вопрос:** Что означает префикс `VITE_`?
>
> **Ответ:** Vite предоставляет переменную клиентскому коду через `import.meta.env` и статически подставляет её значение во время build. Любой `VITE_*` нужно считать публичным. Переменная без префикса не попадает в клиент автоматически, но может раскрыться, если plugin или собственный config явно передаст её в bundle.

> [!followup] Build-time и runtime
> **Вопрос:** Как проверить, на каком этапе используется переменная?
>
> **Ответ:** Нужно найти процесс, который её читает. Если это Vite, Webpack `DefinePlugin` или `NEXT_PUBLIC_*` при `npm run build`, значение build-time и остаётся в artifact. Если `process.env` читает запущенный Node.js server при обработке запроса, это runtime. Если entrypoint создаёт `config.json`, environment читается при старте container, а браузер получает уже публичный результат.

> [!followup] Один image для окружений
> **Вопрос:** Как использовать один Docker image в staging и production?
>
> **Ответ:** Образ содержит одинаковые файлы с хешем. При старте контейнера из разрешённых переменных окружения создаётся публичный `config.json`, либо его предоставляет отдельный сервис конфигурации. Приложение загружает файл до запуска (`bootstrap`) и получает разные API URL и публичные feature flags без новой сборки.
>
> Config не должен кэшироваться как immutable asset и не должен содержать secret. Версию config полезно показывать в диагностике и связывать с release.

> [!followup] Next.js
> **Вопрос:** Все ли переменные Next.js можно менять после build?
>
> **Ответ:** Нет. `NEXT_PUBLIC_*` встраиваются в browser bundle во время `next build` и после этого зафиксированы. Server-only `process.env` может читаться в runtime server code, но статическая генерация выполняет часть кода во время build. Нужно знать режим конкретного route и не считать любое обращение на сервере автоматически динамическим.

> [!followup] Проверка схемы
> **Вопрос:** Зачем валидировать environment variables?
>
> **Ответ:** Без проверки отсутствующий URL превращается в запрос к `undefined`, строка `false` может ошибочно считаться истинной, а опечатка окружения проявится белым экраном. Схема преобразует строки в нужные типы, проверяет обязательность и формат и завершает build или запуск сообщением с именем переменной, но без её секретного значения.

> [!followup] Protected, masked и hidden
> **Вопрос:** Что дают protected, masked и hidden variables в GitLab?
>
> **Ответ:** Protected ограничивает доступ pipeline из protected branches и tags. Masked пытается заменить значение в job log, а hidden не показывает его повторно в интерфейсе после сохранения. Environment scope ограничивает, например, только production job.
>
> Эти свойства снижают случайное раскрытие, но доверенный script всё ещё может прочитать переменную. Изменение `.gitlab-ci.yml`, которое отправляет секрет во внешний запрос, требует такого же внимательного review, как изменение production-кода.

> [!followup] Файлы .env
> **Вопрос:** Безопасно ли хранить secret в `.env`, если файл находится в `.gitignore`?
>
> **Ответ:** Это защищает только от обычного commit. Файл остаётся на диске, может попасть в Docker context, backup, artifact или log. Для локальной разработки это допустимый способ загрузки временных credentials, но production secret должен приходить из управляемого хранилища, иметь ограниченные права и возможность ротации.

> [!followup] Утечка секрета
> **Вопрос:** Что делать, если secret попал в repository или client bundle?
>
> **Ответ:** Сразу отозвать или заменить credential и проверить журналы использования. Простого удаления из последнего commit недостаточно: значение могло попасть в Git history, CI artifacts, Docker cache, CDN и браузеры. Затем очищают доступные копии по процедуре команды и добавляют проверку, предотвращающую повтор.

> [!followup] Feature flags
> **Вопрос:** Следует ли хранить feature flags в environment variables?
>
> **Ответ:** Статичный build-time flag подходит для исключения кода или постоянной настройки конкретной сборки. Для постепенного включения по пользователям, быстрого отключения и изменения без deploy нужен runtime flag service или серверная конфигурация. Клиентский flag управляет интерфейсом, но сервер всё равно проверяет права и доступ к функции.

#### Где это встречается во frontend

> [!context] Практика
> | Значение | Правильная граница |
> | --- | --- |
> | `VITE_API_URL` | Публичное build-time значение |
> | `NEXT_PUBLIC_ANALYTICS_ID` | Публичное значение browser bundle |
> | Database password | Только server runtime или secret manager |
> | Приватный npm-токен | Доверенная задача CI и BuildKit secret |
> | Один SPA image для окружений | Публичный runtime `config.json` |
> | Постепенное включение функции | Runtime feature flag service |
> | Неверный или отсутствующий config | Schema validation и явная остановка |

#### Связанные темы

- [03 GitLab CI для frontend](<./03 GitLab CI для frontend.md>)
- [04 Docker для frontend multi-stage build](<./04 Docker для frontend multi-stage build.md>)
- [07 Env variables frontend build runtime secrets](<../Tooling/07 Env variables frontend build runtime secrets.md>)
- [03 Server Components Client Components и use client](<../Next.js/03 Server Components Client Components и use client.md>)
- [08 Supply chain npm dependencies secrets third-party scripts](<../Security/08 Supply chain npm dependencies secrets third-party scripts.md>)

#### Источники

- [Vite: Env Variables and Modes](https://vite.dev/guide/env-and-mode)
- [Next.js: Environment Variables](https://nextjs.org/docs/app/guides/environment-variables)
- [GitLab: CI/CD variables](https://docs.gitlab.com/ci/variables/)
- [Docker: Build secrets](https://docs.docker.com/build/building/secrets/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Nginx static serving SPA fallback cache headers](<./05 Nginx static serving SPA fallback cache headers.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Production troubleshooting logs rollback smoke tests →](<./07 Production troubleshooting logs rollback smoke tests.md>)
<!-- CARD-NAV-BOTTOM:END -->
