# Dynamic routes params searchParams metadata

<!-- CARD-NAV-TOP:START -->
[← 08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Next.js 14 15 16 версии Turbopack Cache Components PPR →](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как в App Router работают динамические маршруты, `params`, `searchParams`, `generateStaticParams` и метаданные?**

<h2></h2>

<br>
<dl>
<dd>

Динамический маршрут содержит часть URL, значение которой заранее неизвестно.

В App Router такой сегмент обозначают квадратными скобками:

```text
app/products/[id]/page.tsx
```

Этот файл обрабатывает URL:

```text
/products/42
```

а `params.id` содержит строку:

```text
"42"
```

Есть три основных вида динамических сегментов:

| Каталог | Подходящий URL | Значение |
| --- | --- | --- |
| `[id]` | `/products/42` | `{ id: "42" }` |
| `[...slug]` | `/docs/react/hooks` | `{ slug: ["react", "hooks"] }` |
| `[[...slug]]` | `/docs` и `/docs/react` | `{ slug: undefined }` либо `{ slug: ["react"] }` |

`params` описывает динамические сегменты пути.

Обычно через них определяют конкретный ресурс:

- идентификатор пользователя;
- идентификатор товара;
- slug, то есть читаемый идентификатор статьи в URL;
- вложенный путь документации.

В Next.js 14 page и layout получают `params` как обычный объект:

```tsx
type PageProps = {
  params: {
    id: string;
  };
};

export default function Page({
  params,
}: PageProps) {
  return <div>{params.id}</div>;
}
```

В Client Component текущие значения можно прочитать через:

```ts
useParams()
```

`searchParams` описывает query string после `?`.

Например:

```text
/products?page=2&sort=price
```

В Next.js 14 page получает объект следующего вида:

```ts
type SearchParams = {
  [key: string]:
    | string
    | string[]
    | undefined;
};
```

Повторяющиеся параметры превращаются в массив:

```text
/products?brand=sony&brand=lg
```

```ts
{
  brand: ["sony", "lg"];
}
```

`searchParams` подходят для состояния представления, которое полезно сохранить в URL:

- фильтра;
- сортировки;
- поиска;
- активной вкладки;
- пагинации.

В Next.js 14 использование свойства page `searchParams` переводит маршрут к динамическому рендерингу, потому что query string известна только во время запроса.

Client Component читает актуальную query string через:

```ts
useSearchParams()
```

Layout не получает `searchParams`.

Общий layout сохраняется при клиентских переходах и не выполняется заново при каждом изменении query string. Поэтому полученное им значение могло бы устареть.

Если параметр нужен нескольким Client Components, каждый из них может прочитать его через `useSearchParams`.

Если параметр влияет на серверные данные, его читают в page и передают в нужный Server или Client Component.

`generateStaticParams` возвращает значения `params`, для которых динамические страницы нужно сформировать заранее:

```ts
export async function generateStaticParams() {
  const posts = await getPosts();

  return posts.map((post) => ({
    slug: post.slug,
  }));
}
```

Для маршрута:

```text
app/posts/[slug]/page.tsx
```

функция должна вернуть:

```ts
[
  {
    slug: "react-server-components",
  },
  {
    slug: "nextjs-caching",
  },
]
```

В production-сборке `generateStaticParams` выполняется до генерации соответствующих layouts и pages.

По умолчанию используется:

```ts
export const dynamicParams = true;
```

Поэтому значения, не возвращённые из `generateStaticParams`, могут быть сформированы при первом обращении.

Если маршрут остаётся статическим, Next.js сохраняет сформированные HTML и RSC Payload в Full Route Cache.

Чтобы разрешить только заранее известные параметры, используют:

```ts
export const dynamicParams = false;
```

Тогда запрос неизвестного значения приводит к not found:

```text
params отсутствуют в generateStaticParams
→ 404
```

`generateStaticParams` не запускается повторно во время ISR.

Поэтому функция не является автоматически обновляемым реестром всех существующих slug. Если после deployment появляются новые записи, нужно заранее определить:

- разрешены ли runtime-параметры через `dynamicParams`;
- как будет формироваться новый маршрут;
- какое правило revalidation он использует;
- должен ли неизвестный slug возвращать 404.

Metadata, то есть метаданные документа, задаёт:

- `title`;
- `description`;
- `robots`;
- canonical URL, то есть основной адрес страницы;
- Open Graph;
- Twitter Card;
- другие сведения для браузеров и поисковых систем.

Постоянные значения экспортируют через объект:

```tsx
import type {
  Metadata,
} from "next";

export const metadata: Metadata = {
  title: "Каталог",
  description: "Каталог товаров",
};
```

Значения, зависящие от `params`, `searchParams` или загружаемых данных, вычисляют через `generateMetadata`.

В Next.js 14 параметры являются синхронными:

```tsx
import type {
  Metadata,
} from "next";

type PageProps = {
  params: {
    slug: string;
  };
};

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const post = await getPost(
    params.slug,
  );

  return {
    title: post.title,
    description: post.summary,
  };
}
```

Статический `metadata` и `generateMetadata` нельзя одновременно экспортировать из одного route segment.

Оба API поддерживаются только в Server Components и не экспортируются из файла с:

```ts
"use client";
```

Metadata вычисляется от корневого layout к более глубоким сегментам.

Простые поля более глубокого сегмента могут заменить родительские значения.

Важно: вложенные объекты не объединяются глубоко автоматически.

Например, если root layout содержит:

```ts
export const metadata = {
  openGraph: {
    title: "Магазин",
    description: "Общее описание",
    images: ["/default.png"],
  },
};
```

а page возвращает:

```ts
return {
  openGraph: {
    title: post.title,
  },
};
```

то родительские `description` и `images` внутри `openGraph` будут заменены вместе со всем объектом.

Если их нужно сохранить, значения объединяют явно, например через parent metadata:

```tsx
import type {
  Metadata,
  ResolvingMetadata,
} from "next";

export async function generateMetadata(
  {
    params,
  }: PageProps,
  parent: ResolvingMetadata,
): Promise<Metadata> {
  const post = await getPost(
    params.slug,
  );

  const previousImages =
    (await parent).openGraph?.images ??
    [];

  return {
    title: post.title,
    openGraph: {
      title: post.title,
      images: [
        post.image,
        ...previousImages,
      ],
    },
  };
}
```

`searchParams` доступны в `generateMetadata` только для page-сегмента, потому что layouts не получают query string.

Если `generateMetadata` и page получают одни данные через одинаковый GET `fetch`, React может мемоизировать запрос на время серверного рендеринга.

Если данные читаются через ORM или SDK без `fetch`, функцию можно обернуть в React `cache`, чтобы не выполнять одинаковое чтение повторно в рамках одного серверного рендеринга.

Для favicon, manifest, robots, sitemap, Open Graph и Twitter images App Router также поддерживает специальные metadata-файлы.

Например:

```text
app/favicon.ico
app/robots.ts
app/sitemap.ts
app/opengraph-image.tsx
app/twitter-image.tsx
```

Файловые metadata conventions автоматически создают необходимые endpoints и элементы документа.

В Next.js 15 request-time API стали асинхронными:

- `params`;
- page `searchParams`;
- `cookies()`;
- `headers()`;
- `draftMode()`.

Поэтому пример для Next.js 15 выглядит иначе:

```tsx
type PageProps = {
  params: Promise<{
    slug: string;
  }>;
};

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const {
    slug,
  } = await params;

  const post = await getPost(slug);

  return {
    title: post.title,
  };
}
```

Свежий пример с `await params` не описывает Next.js 14. Для собеседования и документации сначала нужно назвать версию проекта.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>params</code> отличаются от <code>searchParams</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`params` являются частью структуры пути и обычно идентифицируют страницу или ресурс:

```text
/users/42
```

```ts
{
  id: "42";
}
```

`searchParams` идут после `?` и описывают вариант представления:

```text
/users?role=admin&page=2
```

```ts
{
  role: "admin";
  page: "2";
}
```

Удаление или изменение `params` обычно приводит к другому ресурсу или маршруту:

```text
/users/42
/users/43
```

Удаление `searchParams` оставляет тот же тип страницы, но возвращает настройки представления по умолчанию:

```text
/users
```

В Next.js 14 использование page `searchParams` переводит маршрут к динамическому рендерингу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда состояние интерфейса стоит хранить в <code>searchParams</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда состояние полезно:

- сохранить в истории браузера;
- передать ссылкой;
- восстановить после перезагрузки;
- использовать при серверной загрузке данных;
- индексировать как отдельный вариант страницы, если это предусмотрено SEO.

Примеры:

- поисковый запрос;
- выбранный фильтр;
- сортировка;
- номер страницы;
- активный раздел каталога.

Временное состояние обычно оставляют локальным:

- открыт ли dropdown;
- наведён ли курсор;
- введённый, но ещё не отправленный текст;
- локальное состояние анимации.

Нельзя помещать в URL:

- secrets;
- access tokens;
- чувствительные персональные данные.

Query string попадает в историю браузера, логи, аналитику и может быть передана вместе со ссылкой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему layout не получает <code>searchParams</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Layout переиспользуется при клиентских переходах и не выполняется заново при каждом изменении query string.

Если бы Server Component layout получил `searchParams`, переданное значение могло бы устареть после навигации.

Page получает актуальные параметры для нового серверного рендеринга:

```tsx
type PageProps = {
  searchParams: {
    search?: string;
  };
};

export default function Page({
  searchParams,
}: PageProps) {
  return (
    <div>{searchParams.search}</div>
  );
}
```

Client Component может подписаться на актуальный URL через:

```ts
useSearchParams()
```

Если query-параметр нужен интерфейсу layout, обычно внутрь layout помещают небольшой Client Component, который использует этот hook.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>useSearchParams</code> может потребовать <code>Suspense</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useSearchParams` является Client Component hook.

На статически сформированном маршруте актуальная query string может быть известна только на клиентской границе.

Поэтому Client Component с `useSearchParams` переводит дерево до ближайшей Suspense Boundary в клиентский рендеринг.

Граница позволяет сохранить внешнюю часть страницы статической:

```tsx
import {
  Suspense,
} from "react";

import {
  SearchFilters,
} from "./SearchFilters";

export default function Page() {
  return (
    <>
      <Header />

      <Suspense
        fallback={<FiltersSkeleton />}
      >
        <SearchFilters />
      </Suspense>
    </>
  );
}
```

На статическом маршруте production-сборка может завершиться ошибкой, если компонент с `useSearchParams` не находится под подходящей Suspense Boundary.

Если маршрут динамически формируется во время запроса, значение доступно при начальном серверном рендеринге Client Component, но последующие изменения URL всё равно читаются через client hook.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>[...slug]</code> отличается от <code>[[...slug]]</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Catch-all segment:

```text
[...slug]
```

требует хотя бы один сегмент.

Для маршрута:

```text
app/docs/[...slug]/page.tsx
```

подходит:

```text
/docs/react
/docs/react/hooks
```

но не подходит:

```text
/docs
```

Optional catch-all:

```text
[[...slug]]
```

делает эту часть необязательной.

Для маршрута:

```text
app/docs/[[...slug]]/page.tsx
```

подходят:

```text
/docs
/docs/react
/docs/react/hooks
```

Значения:

```text
/docs
→ { slug: undefined }

/docs/react/hooks
→ { slug: ["react", "hooks"] }
```

В обоих вариантах присутствующие сегменты передаются массивом строк.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>generateStaticParams</code> и заменяет ли он <code>getStaticPaths</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`generateStaticParams` перечисляет динамические параметры для предварительной генерации маршрутов App Router.

По назначению это ближайший аналог `getStaticPaths` из Pages Router, но его API отличается.

`getStaticPaths` возвращает объект с `paths` и `fallback`.

`generateStaticParams` возвращает обычный массив параметров:

```ts
return [
  {
    slug: "react",
  },
  {
    slug: "nextjs",
  },
];
```

Поведение для значений, отсутствующих в массиве, задаёт:

```ts
export const dynamicParams =
  true;
```

или:

```ts
export const dynamicParams =
  false;
```

При `true`, который используется по умолчанию, неизвестный путь может быть сформирован при первом запросе.

При `false` он возвращает 404.

Функция запускается:

- во время `next build`;
- в development при переходе к соответствующему маршруту.

Она не запускается повторно во время ISR.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>metadata</code>, а когда <code>generateMetadata</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Статический объект `metadata` подходит для постоянных значений:

```tsx
export const metadata = {
  title: "Документация",
};
```

`generateMetadata` нужен, если данные зависят от:

- `params`;
- page `searchParams`;
- API;
- базы данных;
- metadata родительского сегмента.

```tsx
export async function generateMetadata({
  params,
}: PageProps) {
  const post = await getPost(
    params.slug,
  );

  return {
    title: post.title,
  };
}
```

В одном route segment экспортируют только один вариант:

- `metadata`;
- либо `generateMetadata`.

Оба API доступны только в Server Components.

Если динамические данные не нужны, статический объект проще и позволяет Next.js определить metadata заранее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обработать несуществующий <code>id</code> или <code>slug</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

После получения данных page вызывает:

```ts
notFound();
```

если ресурс отсутствует:

```tsx
import {
  notFound,
} from "next/navigation";

export default async function Page({
  params,
}: PageProps) {
  const post = await getPost(
    params.slug,
  );

  if (!post) {
    notFound();
  }

  return <Post post={post} />;
}
```

Next.js:

- прерывает рендеринг сегмента;
- показывает ближайший `not-found.tsx`;
- добавляет `noindex`.

Для non-streamed ответа устанавливается статус:

```text
404 Not Found
```

Если streaming уже начался и headers отправлены, HTTP-статус может остаться `200`. Отсутствующий ресурс всё равно помечается через `noindex`.

Это отличается от временной ошибки backend.

Если ресурс должен существовать, но API или база данных недоступны, ошибку обычно выбрасывают и передают ближайшему `error.tsx`, а не превращают в 404.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Механизм |
| --- | --- |
| Страница товара | `[id]` и `params.id` |
| Вложенная документация | `[...slug]` |
| Фильтры каталога | `searchParams` |
| Статическая генерация популярных статей | `generateStaticParams` |
| 404 для неизвестного slug | `notFound()` или `dynamicParams = false` |
| Title карточки товара | `generateMetadata` |

## Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [12 Route Groups Parallel и Intercepting Routes](<./12 Route Groups Parallel и Intercepting Routes.md>)
- [04 URL origin domain path query fragment](<../Web Basics/04 URL origin domain path query fragment.md>)

## Источники

- [Next.js 14 docs: Dynamic Routes](https://nextjs.org/docs/14/app/building-your-application/routing/dynamic-routes)
- [Next.js 14 docs: Page file](https://nextjs.org/docs/14/app/api-reference/file-conventions/page)
- [Next.js 14 docs: Layout file](https://nextjs.org/docs/14/app/api-reference/file-conventions/layout)
- [Next.js 14 docs: Route Segment Config](https://nextjs.org/docs/14/app/api-reference/file-conventions/route-segment-config)
- [Next.js 14 docs: generateStaticParams](https://nextjs.org/docs/14/app/api-reference/functions/generate-static-params)
- [Next.js 14 docs: generateMetadata](https://nextjs.org/docs/14/app/api-reference/functions/generate-metadata)
- [Next.js 14 docs: Metadata](https://nextjs.org/docs/14/app/building-your-application/optimizing/metadata)
- [Next.js 14 docs: Metadata Files](https://nextjs.org/docs/14/app/api-reference/file-conventions/metadata)
- [Next.js 14 docs: useParams](https://nextjs.org/docs/14/app/api-reference/functions/use-params)
- [Next.js 14 docs: useSearchParams](https://nextjs.org/docs/14/app/api-reference/functions/use-search-params)
- [Next.js 14 docs: notFound](https://nextjs.org/docs/14/app/api-reference/functions/not-found)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Next.js 14 15 16 версии Turbopack Cache Components PPR →](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>)
<!-- CARD-NAV-BOTTOM:END -->
