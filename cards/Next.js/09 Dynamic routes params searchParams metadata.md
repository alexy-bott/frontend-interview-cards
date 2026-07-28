# 09 Dynamic routes params searchParams metadata

<!-- CARD-NAV-TOP:START -->
[← 08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Next.js 14 15 16 версии Turbopack Cache Components PPR →](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как в App Router работают динамические маршруты, `params`, `searchParams`, `generateStaticParams` и метаданные?

#### Ответ

Динамический маршрут содержит часть URL, значение которой заранее неизвестно. В App Router такой сегмент обозначают квадратными скобками: файл `app/products/[id]/page.tsx` обрабатывает `/products/42`, а `params.id` содержит строку `"42"`.

Есть три основных вида динамических сегментов:

| Каталог | Подходящий URL | Значение |
| --- | --- | --- |
| `[id]` | `/products/42` | `{ id: "42" }` |
| `[...slug]` | `/docs/react/hooks` | `{ slug: ["react", "hooks"] }` |
| `[[...slug]]` | `/docs` и `/docs/react` | `slug` отсутствует либо содержит массив |

`params` описывает сегменты пути. Обычно через них определяют ресурс: идентификатор пользователя, slug, то есть читаемый идентификатор статьи в URL, или вложенный путь документации. В Next.js 14 page и layout получают `params` как обычный объект. В Client Component текущие значения можно прочитать через `useParams`.

`searchParams` описывает строку параметров запроса после `?`, например `/products?page=2&sort=price`. Она подходит для фильтра, сортировки, поиска, активной вкладки и пагинации. Page в Next.js 14 получает `searchParams` как объект, а Client Component читает их через `useSearchParams`.

Layout не получает `searchParams`. Общий layout сохраняется при переходах и не выполняется заново для каждой смены строки запроса, поэтому его значение могло бы устареть. Если параметр нужен нескольким клиентским компонентам, его читают через `useSearchParams`; если он влияет на серверные данные страницы, его передают из page в нужный компонент.

`generateStaticParams` возвращает значения `params`, для которых динамические страницы следует сгенерировать заранее:

```ts
export async function generateStaticParams() {
  const posts = await getPosts();

  return posts.map((post) => ({
    slug: post.slug,
  }));
}
```

Остальные значения по умолчанию могут быть сформированы при первом обращении. `export const dynamicParams = false` запрещает неизвестные значения и приводит к 404. `generateStaticParams` выполняется во время сборки и не вызывается повторно при ISR, поэтому обновление списка доступных slug нужно проектировать отдельно.

Metadata, то есть метаданные документа, задаёт `title`, `description`, `robots`, canonical URL, то есть основной адрес страницы, Open Graph и другие сведения для браузера и поисковых систем. Постоянные значения экспортируют через `metadata`, а значения, зависящие от `params` или данных, вычисляют в `generateMetadata`:

```ts
export async function generateMetadata({ params }) {
  const post = await getPost(params.slug);

  return {
    title: post.title,
    description: post.summary,
  };
}
```

Metadata наследуется от корневого layout к дочерним сегментам, а более глубокий сегмент может заменить поля. Для favicon, robots, sitemap и изображений Open Graph App Router также поддерживает специальные файлы. Если `generateMetadata` и page запрашивают одни данные через одинаковый GET `fetch`, React может мемоизировать запрос на время серверного рендеринга.

В Next.js 15 `params`, `searchParams`, `cookies()` и другие API, зависящие от запроса, стали асинхронными. Поэтому свежий пример с `await params` не описывает Next.js 14: для собеседования сначала следует назвать версию.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Чем `params` отличаются от `searchParams`?
>
> **Ответ:** `params` являются частью структуры пути и обычно идентифицируют страницу или ресурс: `/users/42`. `searchParams` идут после `?` и описывают вариант представления: `/users?role=admin&page=2`. Удаление `params` обычно приводит к другому маршруту, а удаление `searchParams` оставляет тот же тип страницы с настройками по умолчанию.

> [!followup]
> **Вопрос:** Когда состояние интерфейса стоит хранить в `searchParams`?
>
> **Ответ:** Когда его полезно сохранить в истории браузера, передать ссылкой или восстановить после перезагрузки: поисковый запрос, фильтр, сортировка, номер страницы. Временное состояние открытого выпадающего списка или текст ещё не отправленной формы обычно остаётся локальным, чтобы не засорять URL и историю.

> [!followup]
> **Вопрос:** Почему layout не получает `searchParams`?
>
> **Ответ:** Layout переиспользуется при клиентских переходах и не выполняется заново при каждом изменении строки параметров запроса. Переданное один раз значение стало бы устаревшим. Page получает актуальные параметры для серверного рендеринга, а клиентский компонент может подписаться на URL через `useSearchParams`.

> [!followup]
> **Вопрос:** Почему `useSearchParams` может потребовать `Suspense`?
>
> **Ответ:** На статически сформированной странице участок с `useSearchParams` должен быть дорендерен на клиенте, потому что актуальная строка запроса известна во время навигации. Граница `Suspense` позволяет оставить внешнюю часть страницы статической. В production-сборке отсутствие такой границы для статического маршрута может привести к ошибке.

> [!followup]
> **Вопрос:** Чем `[...slug]` отличается от `[[...slug]]`?
>
> **Ответ:** Catch-all, то есть маршрут, захватывающий все оставшиеся сегменты, `[...slug]` требует хотя бы один сегмент: `/docs/react` подходит, а `/docs` нет. Optional catch-all `[[...slug]]` делает эту часть необязательной и допускает корневой путь `/docs`; в этом случае `slug` отсутствует. В обоих вариантах несколько сегментов приходят массивом строк.

> [!followup]
> **Вопрос:** Что делает `generateStaticParams` и заменяет ли он `getStaticPaths`?
>
> **Ответ:** Он перечисляет динамические параметры для предварительной генерации страниц App Router. По назначению это ближайший аналог `getStaticPaths`, но работает в модели Server Components и сегментов маршрута. Поведение для неуказанных значений дополнительно регулирует `dynamicParams`.

> [!followup]
> **Вопрос:** Когда использовать `metadata`, а когда `generateMetadata`?
>
> **Ответ:** Статический `metadata` подходит для постоянных значений раздела. `generateMetadata` нужен, если `title`, `description` или изображение для социальных сетей зависят от URL и загруженных данных. Оба варианта являются серверными API и не экспортируются из файла с `"use client"`.

> [!followup]
> **Вопрос:** Как обработать несуществующий `id` или `slug`?
>
> **Ответ:** После получения данных page вызывает `notFound()`, если ресурс отсутствует. Next.js показывает ближайший `not-found.tsx` и возвращает ответ 404. Это отличается от временной ошибки backend: её следует выбросить и передать ближайшему `error.tsx`.

#### Где это встречается во frontend

| Сценарий | Механизм |
| --- | --- |
| Страница товара | `[id]` и `params.id` |
| Вложенная документация | `[...slug]` |
| Фильтры каталога | `searchParams` |
| Статическая генерация популярных статей | `generateStaticParams` |
| 404 для неизвестного slug | `notFound()` или `dynamicParams = false` |
| Title карточки товара | `generateMetadata` |

#### Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [12 Route Groups Parallel и Intercepting Routes](<./12 Route Groups Parallel и Intercepting Routes.md>)
- [04 URL origin domain path query fragment](<../Web Basics/04 URL origin domain path query fragment.md>)

#### Источники

- [Next.js 14 docs: Dynamic Routes](https://nextjs.org/docs/14/app/building-your-application/routing/dynamic-routes)
- [Next.js 14 docs: generateStaticParams](https://nextjs.org/docs/14/app/api-reference/functions/generate-static-params)
- [Next.js 14 docs: Metadata](https://nextjs.org/docs/14/app/building-your-application/optimizing/metadata)
- [Next.js 14 docs: useSearchParams](https://nextjs.org/docs/14/app/api-reference/functions/use-search-params)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Next.js 14 15 16 версии Turbopack Cache Components PPR →](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>)
<!-- CARD-NAV-BOTTOM:END -->
