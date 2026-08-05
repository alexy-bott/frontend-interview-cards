# App Router pages layouts loading error route handlers

<!-- CARD-NAV-TOP:START -->
[← 01 Что такое Next.js и зачем он нужен](<./01 Что такое Next.js и зачем он нужен.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Server Components Client Components и use client →](<./03 Server Components Client Components и use client.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как устроен App Router? Что делают `page.tsx`, `layout.tsx`, `template.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx` и `route.ts`?**

<h2></h2>

<br>
<dl>
<dd>

App Router строит маршруты из папок внутри `app`. Каждая папка представляет route segment, то есть сегмент маршрута.

Папка становится публичным UI-маршрутом при наличии `page.tsx`. Остальные специальные файлы могут задавать оболочку и состояния сегмента, не создавая отдельную страницу.

Исключение — `route.ts`: он создаёт HTTP endpoint без React-интерфейса.

`page.tsx` содержит уникальный интерфейс конкретного URL.

Page может получать:

- `params` — параметры динамических сегментов;
- `searchParams` — параметры query string.

В актуальных версиях App Router эти значения являются асинхронными:

```tsx
export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { id } = await params;
  const query = await searchParams;

  return <div>{id}</div>;
}
```

`layout.tsx` оборачивает страницу и вложенные сегменты общим интерфейсом.

При клиентских переходах внутри своей части дерева layout:

- сохраняет экземпляр;
- сохраняет локальное состояние Client Components;
- остаётся на экране;
- не выполняется заново только из-за изменения дочерней страницы.

Поэтому layout подходит для:

- навигации;
- боковой панели;
- общей оболочки;
- providers;
- интерфейса, общего для нескольких страниц.

Каждый маршрут должен находиться под root layout, который возвращает `<html>` и `<body>`.

Обычно это:

```text
app/layout.tsx
```

Но приложение может иметь несколько root layouts внутри route groups:

```text
app/
  (shop)/
    layout.tsx
  (admin)/
    layout.tsx
```

В таком случае общий верхнеуровневый `app/layout.tsx` может отсутствовать. Переход между страницами, принадлежащими разным root layouts, выполняет полную загрузку документа.

`template.tsx` похож на layout, но получает новый экземпляр при соответствующей навигации.

Его дочернее дерево:

- размонтируется;
- монтируется заново;
- теряет локальное состояние;
- повторно запускает эффекты;
- заново показывает вложенные Suspense fallbacks.

Template нужен редко, например когда сохранение состояния layout мешает ожидаемому жизненному циклу.

Область перемонтирования зависит от уровня template. Навигация только внутри более глубокого сегмента не перемонтирует template, расположенный выше этого сегмента.

`loading.tsx` создаёт состояние загрузки на основе React Suspense.

Next.js автоматически оборачивает страницу и вложенное содержимое сегмента в Suspense Boundary с `loading.tsx` в качестве fallback.

Пока сервер готовит содержимое, Next.js может:

- сразу показать fallback;
- сохранить общую оболочку маршрута;
- передавать готовые части через streaming;
- заменить fallback готовым интерфейсом без полной перезагрузки.

Для более точного состояния загрузки отдельного блока добавляют ручную Suspense Boundary ближе к медленной операции.

При streaming заголовки ответа могут быть отправлены до завершения всего дерева. Поэтому поздний `notFound()` или redirect не всегда может изменить уже отправленный HTTP-статус.

`error.tsx` создаёт Error Boundary для необработанных исключений в дочернем содержимом сегмента.

Он обязан быть Client Component:

```tsx
"use client";
```

Граница обрабатывает ошибки:

- страницы этого сегмента;
- вложенных компонентов;
- дочерних сегментов без собственной подходящей границы.

Ошибка из `layout.tsx` или `template.tsx` того же сегмента не попадёт в его `error.tsx`, потому что граница находится ниже них. Такая ошибка поднимается к родительскому сегменту.

Для ошибок root layout или root template используют:

```text
app/global-error.tsx
```

`global-error.tsx` заменяет root layout и поэтому должен самостоятельно вернуть `<html>` и `<body>`.

В Next.js 14 компонент `error.tsx` получал `error` и `reset`:

```tsx
"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <button onClick={reset}>
      Повторить
    </button>
  );
}
```

`reset()` очищает состояние границы и пытается повторно отрисовать её содержимое.

В современных версиях Next.js дополнительно доступен `unstable_retry()`, который повторно получает и рендерит серверные данные сегмента. Для временной ошибки Server Components он обычно полезнее простого `reset()`.

Error Boundary предназначен для неожиданных исключений во время render.

Ожидаемые ошибки — например, неуспешную валидацию формы или известный ответ API — обычно возвращают как состояние интерфейса.

Граница также не перехватывает обычную ошибку асинхронного event handler, возникшую после render. Такую ошибку обрабатывают непосредственно в сценарии события.

`not-found.tsx` задаёт интерфейс отсутствующего ресурса.

Вызов:

```tsx
notFound();
```

прерывает рендеринг текущего сегмента и показывает ближайший `not-found.tsx`.

Корневой:

```text
app/not-found.tsx
```

также может обслуживать URL, для которых не найден маршрут.

В современных версиях доступен экспериментальный:

```text
app/global-not-found.tsx
```

Он обрабатывает неизвестные URL на уровне маршрутизатора и не использует обычные layouts приложения. Это полезно при нескольких root layouts.

Для non-streamed ответа `notFound()` позволяет вернуть статус `404`.

Если streaming уже начался и заголовки отправлены, ответ может сохранить статус `200`. В таком случае Next.js добавляет `noindex`, чтобы поисковые системы не индексировали отсутствующий ресурс.

Обычный JSX:

```tsx
return <div>Не найдено</div>;
```

сам по себе не сообщает Next.js, что ресурс отсутствует, и не задаёт семантику `notFound()`.

`redirect()` и `permanentRedirect()` прерывают текущий рендеринг и передают управление механизму перенаправления Next.js.

`route.ts` создаёт Route Handler — HTTP endpoint на основе Web API `Request` и `Response`.

Поддерживаются методы:

- `GET`;
- `POST`;
- `PUT`;
- `PATCH`;
- `DELETE`;
- `HEAD`;
- `OPTIONS`.

Например:

```ts
export async function GET() {
  return Response.json({
    status: "ok",
  });
}
```

Если запрошенный HTTP-метод не реализован, Next.js возвращает `405 Method Not Allowed`.

Route Handler используют для:

- webhook;
- callback авторизации;
- загрузки файла;
- BFF;
- RSS;
- программного HTTP API.

В одном route segment нельзя одновременно определить `page.tsx` и `route.ts`, потому что они претендуют на один URL.

Layout намеренно не получает `searchParams`.

При клиентской навигации общий layout сохраняется и не выполняется заново, поэтому переданное ему значение могло бы устареть.

Актуальные query-параметры читают:

- через `searchParams` в `page.tsx`;
- через `useSearchParams()` в Client Component.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое route segment?</strong></summary>

<dl>
<dd>
<h2></h2>

Route segment — часть маршрута, соответствующая уровню папок внутри `app`.

Например:

```text
app/dashboard/settings/page.tsx
```

создаёт URL:

```text
/dashboard/settings
```

из сегментов:

```text
dashboard
settings
```

Динамический сегмент записывают в квадратных скобках:

```text
app/users/[id]/page.tsx
```

Он соответствует URL вроде:

```text
/users/42
```

Не каждая папка добавляет часть URL.

Route group:

```text
(marketing)
```

используется для организации маршрутов и layouts, но не входит в адрес.

Папка slot для Parallel Routes:

```text
@analytics
```

также участвует в структуре дерева, но не добавляет сегмент URL.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>layout.tsx</code> отличается от <code>template.tsx</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Layout сохраняет экземпляр и состояние между клиентскими переходами внутри своей части дерева.

Template получает уникальный `key`, поэтому его дочернее дерево монтируется заново при соответствующей навигации.

Template выбирают, когда нужно:

- сбросить локальное состояние дочерних Client Components;
- повторно запустить `useEffect`;
- заново показать Suspense fallback;
- начать новый жизненный цикл части интерфейса.

При этом template перемонтируется только в области своего сегмента. Навигация внутри более глубокого дочернего сегмента не обязательно перемонтирует templates, находящиеся выше.

Если сброс состояния не нужен, используют layout.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему layout не получает <code>searchParams</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Общий layout сохраняется и не выполняется заново при каждой клиентской навигации внутри своего дерева.

Если бы Server Component layout получил `searchParams`, после изменения query string он мог бы продолжить показывать устаревшее значение.

Актуальные параметры читают в page:

```tsx
export default async function Page({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = await searchParams;

  return <div>{query.search}</div>;
}
```

Либо в Client Component:

```tsx
"use client";

import { useSearchParams } from "next/navigation";

export function Filters() {
  const searchParams = useSearchParams();

  return <span>{searchParams.get("search")}</span>;
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>loading.tsx</code> связан с Suspense?</strong></summary>

<dl>
<dd>
<h2></h2>

Next.js автоматически использует `loading.tsx` как fallback Suspense Boundary для страницы и вложенного содержимого сегмента.

При переходе fallback можно показать до завершения медленных Server Components, а готовые части передавать через streaming.

Например:

```text
layout
  └── loading fallback
        └── page и вложенные сегменты
```

Для более точной загрузки отдельного участка используют ручную Suspense Boundary:

```tsx
import { Suspense } from "react";

export default function Page() {
  return (
    <>
      <Header />

      <Suspense fallback={<ListSkeleton />}>
        <SlowList />
      </Suspense>
    </>
  );
}
```

Так быстрый интерфейс не скрывается общим fallback из-за одного медленного блока.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие ошибки ловит <code>error.tsx</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он ловит необработанные исключения страницы и вложенного содержимого внутри своей Error Boundary.

Ошибка из дочернего сегмента сначала попадает в ближайший подходящий `error.tsx`. Если его нет, она поднимается выше по route tree.

Граница того же сегмента не ловит ошибку из его собственного:

- `layout.tsx`;
- `template.tsx`.

Она также не предназначена для обычных ожидаемых ошибок:

- ошибки валидации;
- неверных данных формы;
- ожидаемого ответа `404`;
- известного отказа API.

Такие состояния обрабатывают явно через возвращаемые данные, `notFound()` или пользовательский интерфейс.

Обычные исключения event handlers и асинхронного кода после render Error Boundary также автоматически не перехватывает.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужна функция <code>reset</code> в <code>error.tsx</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 14 функция `reset()` очищает состояние Error Boundary и пытается повторно отрисовать её дочернее содержимое без полной перезагрузки страницы.

Это может помочь, если ошибка была временной и следующий render завершится успешно.

Если причина не устранена, ошибка возникнет снова.

В современных версиях также появился `unstable_retry()`:

```tsx
"use client";

export default function Error({
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  return (
    <button onClick={unstable_retry}>
      Повторить
    </button>
  );
}
```

Он не только сбрасывает Error Boundary, но и повторно получает Server Components, поэтому лучше подходит для сбоев серверной загрузки данных.

Независимо от способа восстановления ошибку нужно логировать, а пользователю показывать безопасное и понятное сообщение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>notFound()</code> отличается от обычного возврата текста «не найдено»?</strong></summary>

<dl>
<dd>
<h2></h2>

`notFound()`:

- прерывает рендеринг текущего сегмента;
- показывает ближайший `not-found.tsx`;
- добавляет семантику отсутствующего ресурса;
- добавляет `noindex`;
- возвращает `404`, если HTTP-заголовки ещё можно изменить.

При уже начавшемся streaming статус ответа может остаться `200`, потому что заголовки отправлены раньше. `noindex` при этом предотвращает индексирование отсутствующего ресурса.

Обычный JSX:

```tsx
return <div>Не найдено</div>;
```

только отображает текст. Он сам по себе не активирует `not-found.tsx` и не сообщает маршрутизатору, что ресурс отсутствует.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Файл | Назначение |
| --- | --- |
| `page.tsx` | Уникальный интерфейс URL |
| `layout.tsx` | Сохраняемая общая оболочка |
| `template.tsx` | Оболочка с повторным mount |
| `loading.tsx` | Suspense fallback и streaming сегмента |
| `error.tsx` | Локальная граница необработанных ошибок |
| `not-found.tsx` | Интерфейс отсутствующего ресурса |
| `route.ts` | HTTP endpoint без React-интерфейса |

## Связанные темы

- [01 Что такое Next.js и зачем он нужен](<./01 Что такое Next.js и зачем он нужен.md>)
- [03 Server Components Client Components и use client](<./03 Server Components Client Components и use client.md>)
- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>)
- [12 Route Groups Parallel и Intercepting Routes](<./12 Route Groups Parallel и Intercepting Routes.md>)
- [11 Pages Router getServerSideProps getStaticProps getStaticPaths](<./11 Pages Router getServerSideProps getStaticProps getStaticPaths.md>)
- [15 Suspense lazy и code splitting](<../React/15 Suspense lazy и code splitting.md>)

## Источники

- [Next.js docs: Layouts and Pages](https://nextjs.org/docs/app/getting-started/layouts-and-pages)
- [Next.js docs: Project Structure](https://nextjs.org/docs/app/getting-started/project-structure)
- [Next.js docs: Page file](https://nextjs.org/docs/app/api-reference/file-conventions/page)
- [Next.js docs: Layout file](https://nextjs.org/docs/app/api-reference/file-conventions/layout)
- [Next.js docs: Template file](https://nextjs.org/docs/app/api-reference/file-conventions/template)
- [Next.js docs: Loading file](https://nextjs.org/docs/app/api-reference/file-conventions/loading)
- [Next.js docs: Error file](https://nextjs.org/docs/app/api-reference/file-conventions/error)
- [Next.js docs: Error Handling](https://nextjs.org/docs/app/getting-started/error-handling)
- [Next.js docs: Not Found file](https://nextjs.org/docs/app/api-reference/file-conventions/not-found)
- [Next.js docs: Route Handlers](https://nextjs.org/docs/app/getting-started/route-handlers)
- [Next.js docs: Route Groups](https://nextjs.org/docs/app/api-reference/file-conventions/route-groups)
- [Next.js docs: useSearchParams](https://nextjs.org/docs/app/api-reference/functions/use-search-params)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Что такое Next.js и зачем он нужен](<./01 Что такое Next.js и зачем он нужен.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Server Components Client Components и use client →](<./03 Server Components Client Components и use client.md>)
<!-- CARD-NAV-BOTTOM:END -->
