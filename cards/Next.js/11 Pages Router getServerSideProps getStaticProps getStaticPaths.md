# 11 Pages Router getServerSideProps getStaticProps getStaticPaths

<!-- CARD-NAV-TOP:START -->
[← 10 Next.js 14 15 16 версии Turbopack Cache Components PPR](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Route Groups Parallel и Intercepting Routes →](<./12 Route Groups Parallel и Intercepting Routes.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как работает Pages Router и для чего нужны `getServerSideProps`, `getStaticProps` и `getStaticPaths`?

#### Ответ

Pages Router является файловой системой маршрутизации Next.js на основе каталога `pages`. `pages/index.tsx` создаёт `/`, `pages/users/[id].tsx` создаёт динамический маршрут, а файлы в `pages/api` создают API Routes. Модель появилась раньше App Router, но остаётся поддерживаемой и часто встречается в существующих production-проектах.

`getServerSideProps` выполняется на сервере при каждом запросе страницы. Функция получает `context` с `params`, `query`, `req`, `res` и cookies, затем возвращает `props`, `redirect` или `notFound`:

```ts
export async function getServerSideProps(context) {
  const user = await getUser(context.params.id, context.req.cookies.session);

  if (!user) {
    return { notFound: true };
  }

  return { props: { user } };
}
```

Этот вариант подходит, когда HTML зависит от конкретного запроса: текущей сессии, прав, заголовков или данных, которые нельзя отдавать с задержкой. Цена состоит в серверной работе и ожидании источника данных на каждый запрос. Возвращаемые props, то есть свойства страницы, сериализуются в HTML и доступны клиенту, поэтому секреты в них помещать нельзя.

`getStaticProps` формирует страницу заранее во время сборки. Результат можно раздавать как статический файл через CDN. Если вернуть `revalidate: 60`, включается ISR: после истечения интервала Next.js может сформировать новую версию в фоне и заменить сохранённую страницу.

```ts
export async function getStaticProps() {
  const posts = await getPosts();

  return {
    props: { posts },
    revalidate: 60,
  };
}
```

`getStaticPaths` используется вместе с `getStaticProps` в динамическом файле, например `pages/posts/[slug].tsx`. Он перечисляет значения, которые следует построить заранее, и задаёт `fallback` для остальных:

| `fallback` | Поведение неизвестного пути |
| --- | --- |
| `false` | Сразу вернуть 404 |
| `true` | Сначала показать fallback, то есть временный интерфейс, затем сформировать страницу |
| `"blocking"` | Дождаться серверного рендеринга, затем сохранить страницу без fallback |

В режиме `fallback: true` компонент должен проверять `router.isFallback`, иначе он попытается прочитать ещё не загруженные props. `"blocking"` проще для интерфейса, но первый посетитель нового пути ждёт генерацию целиком.

В App Router этих трёх функций нет. `getServerSideProps` заменяется Server Components с динамическим получением данных, `getStaticProps` и ISR выражаются через настройки кэша и revalidate, а роль `getStaticPaths` выполняет `generateStaticParams`. Это сопоставление приблизительное: App Router использует другую модель layouts, Server Components, streaming и кэшей.

Каталоги `pages` и `app` можно держать в одном проекте во время постепенной миграции, но один URL не должен определяться сразу в обоих. Переход выполняют по маршрутам, а не обязательным переписыванием всего приложения за один раз.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Когда использовать `getServerSideProps`?
>
> **Ответ:** Когда результат должен учитывать конкретный запрос и не может быть безопасно общим: закрытая страница с серверной проверкой сессии, данные из headers запроса или информация, требующая актуальности на каждое открытие. Если страница публичная и допускает небольшую задержку обновления, SSG или ISR обычно дешевле и быстрее.

> [!followup]
> **Вопрос:** Видит ли браузер код и данные из `getServerSideProps`?
>
> **Ответ:** Тело функции выполняется только на сервере и не входит в клиентский бандл. Однако возвращённые props сериализуются и отправляются браузеру, поэтому пользователь способен их прочитать. Закрытый token можно использовать для серверного запроса, но нельзя вернуть в props.

> [!followup]
> **Вопрос:** Можно ли вызвать собственный API Route из `getServerSideProps`?
>
> **Ответ:** Технически можно, но обычно не нужно. Обе функции работают на сервере, поэтому лучше напрямую вызвать общий service или repository, то есть слой получения данных. Внутренний HTTP создаёт лишнюю задержку и дублирует сериализацию, а относительный URL на сервере требует дополнительной настройки origin.

> [!followup]
> **Вопрос:** Чем SSG с `getStaticProps` отличается от ISR?
>
> **Ответ:** Без `revalidate` страница меняется только после новой сборки. ISR добавляет срок, после которого посещение может запустить regeneration, то есть повторное формирование сохранённой страницы. До успешного обновления пользователи продолжают получать предыдущую версию.

> [!followup]
> **Вопрос:** Зачем нужен `getStaticPaths`?
>
> **Ответ:** Во время сборки Next.js не знает все допустимые значения динамического `[slug]`. `getStaticPaths` перечисляет пути для предварительной генерации, а `fallback` определяет судьбу остальных. Без этой функции динамическая page с `getStaticProps` не знает, какие файлы создать.

> [!followup]
> **Вопрос:** Чем `fallback: true` отличается от `fallback: "blocking"`?
>
> **Ответ:** При `true` обычная клиентская навигация может сначала получить страницу без готовых props, поэтому компонент показывает fallback через `router.isFallback`. При `"blocking"` первый запрос ждёт готовый HTML и не видит промежуточное состояние. Оба варианта затем сохраняют сформированную страницу.

> [!followup]
> **Вопрос:** Чем `getInitialProps` отличается от этих функций?
>
> **Ответ:** Это более старый API. На первом открытии он выполняется на сервере, а при клиентской навигации может выполняться в браузере. Использование `getInitialProps` в пользовательском `_app` отключает автоматическую статическую оптимизацию для страниц без собственных API статической загрузки данных, поэтому в новом коде обычно выбирают более конкретные функции.

> [!followup]
> **Вопрос:** Можно ли постепенно мигрировать с Pages Router на App Router?
>
> **Ответ:** Да. Каталоги `pages` и `app` могут сосуществовать, пока разные файлы не определяют один URL. Обычно переносят один маршрут или группу маршрутов, отдельно проверяя загрузку данных, layouts, границы клиентских компонентов, SEO и кэширование, потому что прямой замены API один к одному нет.

#### Где это встречается во frontend

| Сценарий | Pages Router API |
| --- | --- |
| Персональная SSR-страница | `getServerSideProps` |
| Публичная статья | `getStaticProps` |
| Периодически обновляемый каталог | `getStaticProps` с `revalidate` |
| Статьи по `[slug]` | `getStaticPaths` и `getStaticProps` |
| Backend endpoint | `pages/api/*` |
| Постепенная миграция | Одновременные `pages` и `app` без конфликта URL |

#### Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>)
- [17 Hydration SSR и SSG](<../React/17 Hydration SSR и SSG.md>)

#### Источники

- [Next.js docs: Pages Router](https://nextjs.org/docs/pages)
- [Next.js docs: getServerSideProps](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-server-side-props)
- [Next.js docs: getStaticProps](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-static-props)
- [Next.js docs: getStaticPaths](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-static-paths)
- [Next.js docs: Incremental Static Regeneration](https://nextjs.org/docs/pages/building-your-application/data-fetching/incremental-static-regeneration)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 10 Next.js 14 15 16 версии Turbopack Cache Components PPR](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Route Groups Parallel и Intercepting Routes →](<./12 Route Groups Parallel и Intercepting Routes.md>)
<!-- CARD-NAV-BOTTOM:END -->
