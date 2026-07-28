# 14 Environment variables next config standalone и deployment

<!-- CARD-NAV-TOP:START -->
[← 13 Image Font Link Script и оптимизация](<./13 Image Font Link Script и оптимизация.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как настраивают переменные окружения, `next.config.js`, production-сборку и развёртывание Next.js-приложения?

#### Ответ

Next.js-приложение сначала собирают командой `next build`, а затем запускают через `next start`, standalone-сервер, образ Docker или адаптер выбранной платформы. Способ развёртывания должен соответствовать возможностям приложения: статический export не умеет выполнять Server Components для запроса, Server Actions и динамические Route Handlers.

Environment variables, то есть переменные окружения, по умолчанию доступны только серверному коду через `process.env`. Next.js загружает `.env`, `.env.local` и файлы для конкретного `NODE_ENV`. Локальные файлы с секретами не добавляют в Git; в CI и production значения передают через защищённое хранилище секретов платформы.

Префикс `NEXT_PUBLIC_` делает переменную доступной клиентскому коду. Её значение подставляется в JavaScript во время `next build` и после сборки уже не меняется:

```ts
const apiOrigin = process.env.NEXT_PUBLIC_API_ORIGIN;
```

Это означает, что один и тот же готовый клиентский бандл нельзя перенести из тестового окружения staging в production и ожидать другого `NEXT_PUBLIC_API_ORIGIN`. Для конфигурации, которая должна определяться при запуске, значение получают на сервере и явно передают клиенту. Секреты никогда не помечают `NEXT_PUBLIC_`.

`next.config.js` или `next.config.mjs` выполняется в Node.js во время сборки и задаёт конфигурацию фреймворка: источники изображений, `redirects`, `rewrites`, `headers`, `basePath`, `output` и совместимость сборщика. Настройку `env` в `next.config.js` не используют для секретов, потому что указанные там значения встраиваются в JavaScript-бандл.

`redirects` возвращает браузеру HTTP-перенаправление на новый URL. `rewrites` внутренне сопоставляет входной URL с другим источником, не меняя адресную строку, и подходит для проксирования API или постепенной миграции. `headers` добавляет заголовки ответа, например CSP и HSTS, но заголовки безопасности должны соответствовать архитектуре приложения, а не копироваться вслепую.

`output: "standalone"` создаёт `.next/standalone` с минимальным сервером и необходимыми production-зависимостями, то есть зависимостями для запуска. Это удобно для небольшого образа Docker. Каталоги `public` и `.next/static` не копируются туда автоматически для standalone-сервера, поэтому отдельный этап сборки Docker должен перенести их или настроить раздачу через CDN.

```js
// next.config.js
module.exports = {
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cdn.example.com",
        pathname: "/products/**",
      },
    ],
  },
};
```

При self-hosting, то есть самостоятельном размещении, перед Next.js обычно ставят reverse proxy, или обратный прокси-сервер. Он ограничивает размер и скорость запросов, завершает TLS, может отдавать статические ресурсы и защищает Node.js-сервер от медленных соединений. Если приложение запущено в нескольких экземплярах, общий Data Cache и хранилище ISR нельзя без проверки оставлять локальными: разные экземпляры способны отдавать разные версии данных.

Надёжный CI/CD собирает один неизменяемый артефакт, проверяет его и продвигает между окружениями. Версии Node.js и package manager, то есть менеджера пакетов, фиксируют, зависимости устанавливают через lockfile, а сборку выполняют с теми публичными переменными, которые должны попасть в клиент. После развёртывания нужны проверки состояния, логи, метрики, корректное завершение процесса и стратегия отката.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Чем серверная переменная окружения отличается от `NEXT_PUBLIC_`?
>
> **Ответ:** Обычная переменная читается только серверным кодом и может содержать секрет. Значение с `NEXT_PUBLIC_` встраивается в клиентский JavaScript во время сборки, поэтому его может увидеть любой пользователь. Префикс определяет границу доступности, а не просто соглашение об имени.

> [!followup]
> **Вопрос:** Почему `NEXT_PUBLIC_` не меняется после запуска контейнера?
>
> **Ответ:** Next.js заменяет обращение к этой переменной конкретным значением во время `next build`. Контейнер запускает уже готовые JavaScript-файлы. Чтобы значение стало конфигурацией времени выполнения, сервер должен прочитать его при запросе и передать браузеру через HTML, API или Server Component.

> [!followup]
> **Вопрос:** Можно ли хранить секрет в `next.config.js`?
>
> **Ответ:** Нельзя помещать секрет в поле `env`, потому что Next.js подставляет такие значения в бандл. Сам файл конфигурации может прочитать серверную переменную для задачи сборки, но нужно понимать, куда результат попадёт. Секрет безопаснее читать непосредственно в server-only модуле, Route Handler или Server Action и никогда не возвращать клиенту.

> [!followup]
> **Вопрос:** Чем rewrite отличается от redirect?
>
> **Ответ:** Redirect отправляет статус перенаправления и новый URL, после чего браузер выполняет отдельный запрос и меняет адресную строку. Rewrite незаметно сопоставляет исходный URL с другим внутренним или внешним адресом назначения. Он полезен для проксирования, но публичный URL и правила кэширования остаются отдельной частью контракта.

> [!followup]
> **Вопрос:** Что содержит standalone output?
>
> **Ответ:** Next.js трассирует необходимые файлы и production-зависимости, затем создаёт минимальный `server.js` в `.next/standalone`. Это уменьшает образ Docker, но не означает полностью готовый каталог: `public` и `.next/static` копируют отдельно, если их не раздаёт CDN.

> [!followup]
> **Вопрос:** Когда подходит static export?
>
> **Ответ:** Когда все страницы и данные можно сформировать во время сборки, а на хостинге нужны только HTML, CSS, JavaScript и статические ресурсы. Он не подходит для SSR во время запроса, Server Actions, cookies на сервере и динамического Node.js API. Image Optimization также требует отдельного загрузчика или отказа от серверного оптимизатора.

> [!followup]
> **Вопрос:** Что нужно учесть при нескольких экземплярах Next.js?
>
> **Ответ:** Локальная память и файловый кэш не являются общими. Нужно согласовать Data Cache, ISR, rate limiting, то есть ограничение частоты запросов, сессии и фоновые задачи между экземплярами. Иначе один контейнер обновит страницу, а другой продолжит отдавать прежний результат. Конкретное решение зависит от хостинга и cache handler.

> [!followup]
> **Вопрос:** Зачем собирать артефакт один раз, а не выполнять сборку в каждом окружении?
>
> **Ответ:** Один проверенный артефакт уменьшает расхождение между staging и production и позволяет точно откатить версию. Исключением являются значения `NEXT_PUBLIC_`, которые входят в сборку: либо для окружений собирают отдельные артефакты, либо проектируют конфигурацию времени выполнения через сервер.

#### Где это встречается во frontend

| Задача | Решение |
| --- | --- |
| Пароль базы данных | Серверная переменная окружения |
| Публичный origin API | `NEXT_PUBLIC_`, если допустима фиксация при сборке |
| Развёртывание в Docker | Multi-stage build и `output: "standalone"` |
| Полностью статический сайт | `output: "export"` с проверкой ограничений |
| Постепенная миграция backend | `rewrites` |
| Несколько реплик | Общее хранилище кэша и сессий, наблюдаемость |

#### Связанные темы

- [06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>)
- [08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>)
- [04 Docker для frontend multi-stage build](<../DevOps/04 Docker для frontend multi-stage build.md>)
- [02 CI CD pipeline stages jobs artifacts cache](<../DevOps/02 CI CD pipeline stages jobs artifacts cache.md>)
- [03 GitLab CI для frontend](<../DevOps/03 GitLab CI для frontend.md>)
- [02 lock files npm ci и воспроизводимая установка](<../Tooling/02 lock files npm ci и воспроизводимая установка.md>)
- [03 Semver caret tilde exact versions](<../Tooling/03 Semver caret tilde exact versions.md>)
- [08 Supply chain npm dependencies secrets third-party scripts](<../Security/08 Supply chain npm dependencies secrets third-party scripts.md>)

#### Источники

- [Next.js 14 docs: Environment Variables](https://nextjs.org/docs/14/app/building-your-application/configuring/environment-variables)
- [Next.js 14 docs: next.config.js](https://nextjs.org/docs/14/app/api-reference/next-config-js)
- [Next.js 14 docs: Deploying](https://nextjs.org/docs/14/app/building-your-application/deploying)
- [Next.js 14 docs: output](https://nextjs.org/docs/14/app/api-reference/next-config-js/output)
- [Next.js 14 docs: Static Exports](https://nextjs.org/docs/14/app/building-your-application/deploying/static-exports)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 13 Image Font Link Script и оптимизация](<./13 Image Font Link Script и оптимизация.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
