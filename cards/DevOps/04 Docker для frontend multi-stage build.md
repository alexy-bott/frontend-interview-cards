# Docker для frontend multi-stage build

<!-- CARD-NAV-TOP:START -->
[← 03 GitLab CI для frontend](<./03 GitLab CI для frontend.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Nginx static serving SPA fallback cache headers →](<./05 Nginx static serving SPA fallback cache headers.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем Docker во frontend и как устроен multi-stage Dockerfile для SPA?**

<h2></h2>

<br>
<dl>
<dd>

Docker image, или образ, - неизменяемый шаблон файловой системы и настроек процесса. Container, или контейнер, - запущенный экземпляр образа. Во frontend Docker фиксирует среду сборки и упаковывает готовое приложение вместе со способом запуска. Для статической SPA Node.js нужен во время build, а в production готовые файлы может отдавать Nginx. Для Next.js с SSR во время выполнения (`runtime`) остаётся Node.js-процесс.

Multi-stage build, или многоэтапная сборка, использует несколько `FROM` в одном Dockerfile. Этап сборки (`build stage`) содержит Node.js, менеджер пакетов, devDependencies и исходники. Этап выполнения (`runtime stage`) получает только необходимые результаты через `COPY --from=build`. Это уменьшает размер финального образа и не переносит в него компиляторы, тесты и исходный `node_modules`.

Каждая инструкция Dockerfile создаёт слой или меняет метаданные образа. Кэш сборки (`build cache`) переиспользует слой, если инструкция и влияющие на неё файлы не изменились. Поэтому `package.json` и lock-файл копируют до исходников: изменение компонента инвалидирует `COPY . .` и последующие слои, но не заставляет заново устанавливать неизменные зависимости.

Пример для Vite SPA:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

COPY . .
RUN npm run build

FROM nginx:1.30-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Теги базовых образов фиксируют хотя бы по основной и дополнительной версии, а для строгой повторяемости - по digest, то есть хешу содержимого. Tag может начать указывать на обновлённый образ, digest остаётся неизменным. При этом digest нужно регулярно обновлять автоматизированным merge request, иначе воспроизводимость закрепит старые уязвимости.

`.dockerignore` уменьшает контекст сборки (`build context`) - набор файлов, отправляемых Docker builder. Обычно исключают `.git`, `node_modules`, `dist`, coverage, логи, редакторские файлы и локальные `.env`. Это ускоряет передачу контекста и снижает риск случайного `COPY` лишних данных, но не заменяет проверку Dockerfile и секретов.

Секреты нельзя передавать через обычные `ARG`, `ENV` или копируемый `.npmrc`: они могут попасть в слои, кэш, метаданные сборки или итоговый JavaScript. Для установки приватного пакета BuildKit временно монтирует secret только в нужную инструкцию, например `RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci`. Этот файл не сохраняется в слое. Любое значение, которое сборщик подставил в клиентскую сборку (`bundle`), всё равно становится публичным.

Build-time переменная действует во время `npm run build` и в статической SPA обычно вшивается в JavaScript. Runtime `ENV` контейнера не изменит уже созданный файл. Если один образ должен работать в staging и production, публичную конфигурацию генерируют при старте в отдельный `config.js` или получают с сервера, а не пересобирают исходники.

Финальный образ должен содержать только необходимое, запускаться предсказуемо и быть проверен в CI. Для production его сканируют на уязвимости, связывают с commit и публикуют под уникальными tag и digest. По возможности процесс работает без root; для Nginx это требует образа и конфигурации, поддерживающих непривилегированный порт и доступ к временным каталогам, а не простого добавления `USER` в случайное место.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Docker image отличается от container?</strong></summary>

<dl>
<dd>
<h2></h2>

Образ - сохранённый шаблон со слоями, файлами и настройками запуска. Контейнер - процесс, запущенный из образа, с собственным изменяемым верхним слоем, сетью и ограничениями ресурсов. Один образ может одновременно запускаться в нескольких контейнерах.

Изменение файлов внутри контейнера не создаёт новую версию приложения и обычно теряется при замене. Production-поставку изменяют новой сборкой образа, а постоянные данные хранят вне эфемерного контейнера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему не оставить Node.js image в production SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузерная SPA после build состоит из статических файлов и не выполняет Node.js на сервере. Runtime image с Nginx или другим статическим сервером меньше и содержит меньше пакетов и инструментов. Build stage остаётся отдельно и предоставляет только `dist`.

Multi-stage не является защитой сам по себе: если секрет попал в `dist`, он будет скопирован. Также кэш сборки может сохранить неосторожно созданные файлы, поэтому учётные данные передают через временно подключаемые secrets.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему сначала копируют <code>package.json</code> и lock-файл, а потом исходники?</strong></summary>

<dl>
<dd>
<h2></h2>

Слой `npm ci` зависит только от файлов зависимостей. Пока они не изменились, Docker переиспользует установку из cache, даже если поменялся компонент. Если выполнить `COPY . .` до установки, любое изменение исходника инвалидирует слой и заставляет скачивать пакеты заново.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>.dockerignore</code>, если лишнее не копируется явно?</strong></summary>

<dl>
<dd>
<h2></h2>

Docker сначала формирует и отправляет build context builder-у. Большой `node_modules` или `.git` замедляет этот шаг и участвует в расчёте cache для широкого `COPY`. Кроме того, будущая правка Dockerfile может случайно скопировать локальный `.env` или токен. `.dockerignore` сокращает доступный набор заранее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>ARG</code> отличается от <code>ENV</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`ARG` доступен инструкциям во время build и не становится обычной переменной запущенного контейнера. `ENV` сохраняется в образе и доступен процессу во время выполнения. Оба механизма не подходят для секретов: значения могут раскрыться через метаданные, кэш, логи или приложение.

Во frontend важен ещё один уровень: сборщик может заменить `import.meta.env.VITE_API_URL` текстом внутри JavaScript. После этого значение находится не в Docker environment, а в публичном файле bundle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как установить приватные npm-пакеты и не сохранить токен в image?</strong></summary>

<dl>
<dd>
<h2></h2>

CI передаёт временный `.npmrc` или token через `docker build --secret`, а Dockerfile использует `RUN --mount=type=secret`. Secret существует только во время этой инструкции и не попадает в созданный слой. После установки проверяют, что `.npmrc` не был скопирован другим `COPY` и токен не напечатан в log.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему изменение <code>docker run -e VITE_API_URL=...</code> не меняет адрес API у готовой SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

Vite заменил `import.meta.env.VITE_API_URL` во время `npm run build`, и в `dist` уже лежит строка. Nginx только отдаёт файл и не выполняет этот код на сервере. Для runtime-настройки entrypoint создаёт отдельный публичный config до старта Nginx или приложение загружает config endpoint до инициализации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда frontend image должен содержать Node.js runtime?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда JavaScript выполняется на сервере после запуска: Next.js SSR, Route Handlers, Server Actions или собственный Node.js backend. Тогда runtime stage копирует автономный сервер (`standalone`), production-зависимости и статические файлы, а контейнер запускает Node.js-процесс. Для полностью статического export или Vite SPA достаточно статического сервера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему одного tag <code>latest</code> недостаточно для deploy и rollback?</strong></summary>

<dl>
<dd>
<h2></h2>

Tag является изменяемой ссылкой и завтра может указывать на другой image. Digest однозначно идентифицирует содержимое. Pipeline публикует image с commit SHA, сохраняет digest в release metadata и развёртывает эту точную версию. Тогда rollback не зависит от текущего значения `latest`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему container желательно запускать без root и почему недостаточно написать <code>USER 1000</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Непривилегированный процесс ограничивает последствия уязвимости внутри container. Но процессу нужны права на порт, cache, PID и временные каталоги. Случайный `USER 1000` может сломать запуск Nginx или оставить часть каталогов недоступной. Используют подготовленный unprivileged image либо явно меняют порт, владельцев и пути и проверяют это в runtime.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Решение |
| --- | --- |
| Vite SPA | Node.js build stage и Nginx runtime stage |
| Next.js SSR | Multi-stage build и Node.js runtime |
| Быстрая пересборка | Manifest до исходников и BuildKit cache mount |
| Приватный npm registry | BuildKit secret, а не `ARG TOKEN` |
| Несколько окружений | Один image и отдельная публичная runtime-конфигурация |
| Точный rollback | Commit tag и сохранённый image digest |

## Связанные темы

- [05 Nginx static serving SPA fallback cache headers](<./05 Nginx static serving SPA fallback cache headers.md>)
- [06 Env variables secrets build-time runtime](<./06 Env variables secrets build-time runtime.md>)
- [02 lock files npm ci и воспроизводимая установка](<../Tooling/02 lock files npm ci и воспроизводимая установка.md>)
- [04 SSR SSG ISR Streaming и hydration](<../Next.js/04 SSR SSG ISR Streaming и hydration.md>)

## Источники

- [Docker: Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker: Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Docker: Build secrets](https://docs.docker.com/build/building/secrets/)
- [Docker: Build cache](https://docs.docker.com/build/cache/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 GitLab CI для frontend](<./03 GitLab CI для frontend.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Nginx static serving SPA fallback cache headers →](<./05 Nginx static serving SPA fallback cache headers.md>)
<!-- CARD-NAV-BOTTOM:END -->
