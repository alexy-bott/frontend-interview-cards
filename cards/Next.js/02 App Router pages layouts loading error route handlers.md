# 02 App Router pages layouts loading error route handlers

<!-- CARD-NAV-TOP:START -->
[← 01 Что такое Next.js и зачем он нужен](<./01 Что такое Next.js и зачем он нужен.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Server Components Client Components и use client →](<./03 Server Components Client Components и use client.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как устроен App Router? Что делают `page.tsx`, `layout.tsx`, `template.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx` и `route.ts`?

#### Ответ

App Router строит маршруты из папок внутри `app`. Каждая папка является route segment, то есть сегментом маршрута. Папка становится публичной страницей только при наличии `page.tsx`; остальные файлы могут задавать оболочку и состояние сегмента, не создавая отдельный URL.

`page.tsx` содержит уникальный интерфейс маршрута. `layout.tsx` оборачивает страницу и дочерние сегменты общим интерфейсом. Layout сохраняется при переходах между своими дочерними страницами, поэтому подходит для навигации, боковой панели и providers. Корневой `app/layout.tsx` обязателен и должен вернуть `html` и `body`.

`template.tsx` похож на layout, но при навигации получает новый экземпляр. Его дочернее дерево размонтируется и монтируется заново, локальное состояние сбрасывается, а эффекты запускаются повторно. Template нужен редко, когда сохранение layout мешает ожидаемому жизненному циклу.

`loading.tsx` автоматически создаёт границу Suspense вокруг страницы и вложенных сегментов. Пока сервер готовит содержимое, Next.js может сразу показать состояние загрузки и продолжить потоковую передачу готовых частей. Общий layout при этом остаётся доступным и интерактивным.

`error.tsx` создаёт React Error Boundary, то есть границу ошибок, для дочернего содержимого сегмента и обязан быть Client Component. Он получает ошибку и функцию `reset` для повторной попытки. Ошибка в `layout.tsx` того же сегмента не попадёт в его `error.tsx`, потому что граница находится ниже layout; её обрабатывает граница родительского сегмента. Для корневого layout существует `global-error.tsx`.

`not-found.tsx` показывает интерфейс для `notFound()` или несовпавшего маршрута. `redirect()` и `permanentRedirect()` прерывают текущий рендеринг и возвращают перенаправление.

`route.ts` является HTTP endpoint на основе Web API `Request` и `Response`, а не React-страницей. Его используют для webhook, callback авторизации, загрузки файла и BFF. В одном сегменте маршрута нельзя одновременно определить `page.tsx` и `route.ts`, потому что они претендуют на один URL.

Layout намеренно не получает `searchParams`: при клиентской навигации он сохраняется и мог бы видеть устаревшее значение. Актуальные параметры читают в `page.tsx` или через `useSearchParams` в Client Component.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Что такое route segment?
>
> **Ответ:** Это часть маршрута, соответствующая папке в `app`. Файл `app/dashboard/settings/page.tsx` создаёт URL `/dashboard/settings` из сегментов `dashboard` и `settings`. Route groups и slots могут участвовать в структуре файлов, но не обязаны добавлять часть URL.

> [!followup]
> **Вопрос:** Чем `layout.tsx` отличается от `template.tsx`?
>
> **Ответ:** Layout сохраняет экземпляр и состояние между переходами внутри сегмента. Template получает уникальный `key`, поэтому его дочернее дерево монтируется заново. Template выбирают, когда при каждой навигации нужно сбросить локальное состояние, повторить эффект или заново показать fallback.

> [!followup]
> **Вопрос:** Почему layout не получает `searchParams`?
>
> **Ответ:** Общий layout не выполняется заново при каждой клиентской навигации. Если бы он получил параметры запроса, они могли бы устареть после изменения URL. Page выполняется для нового маршрута, а Client Component с `useSearchParams` подписан на актуальный URL.

> [!followup]
> **Вопрос:** Как `loading.tsx` связан с Suspense?
>
> **Ответ:** Next.js автоматически использует его как fallback ближайшей границы Suspense для сегмента. При переходе fallback можно показать немедленно, а готовый общий интерфейс сохранить. Для более точной загрузки отдельного блока Suspense добавляют вручную ближе к медленной операции.

> [!followup]
> **Вопрос:** Какие ошибки ловит `error.tsx`?
>
> **Ответ:** Он ловит необработанные ошибки страницы и вложенных сегментов внутри своей границы. Ошибки layout или template того же уровня всплывают к родителю. Ожидаемые ошибки, например неверные данные формы, обычно возвращают как состояние, а не превращают в исключение для Error Boundary.

> [!followup]
> **Вопрос:** Для чего нужна функция `reset` в `error.tsx`?
>
> **Ответ:** Она пытается повторно отрисовать содержимое границы без полной перезагрузки страницы. Это полезно для временного сбоя запроса. Если причина не устранена, ошибка возникнет снова, поэтому её также нужно записать в журнал и показать пользователю понятное состояние.

> [!followup]
> **Вопрос:** Чем `notFound()` отличается от обычного возврата текста «не найдено»?
>
> **Ответ:** `notFound()` прерывает рендеринг сегмента, показывает ближайший `not-found.tsx` и позволяет Next.js сформировать корректный ответ 404. Обычный JSX с сообщением сам по себе не меняет HTTP-статус и семантику маршрута.

#### Где это встречается во frontend

| Файл | Назначение |
| --- | --- |
| `page.tsx` | Уникальный интерфейс URL |
| `layout.tsx` | Сохраняемая общая оболочка |
| `template.tsx` | Оболочка с повторным mount |
| `loading.tsx` | Fallback и потоковая передача сегмента |
| `error.tsx` | Локальная граница ошибок |
| `not-found.tsx` | Интерфейс 404 |
| `route.ts` | HTTP endpoint без React-интерфейса |

#### Связанные темы

- [03 Server Components Client Components и use client](<./03 Server Components Client Components и use client.md>)
- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>)
- [12 Route Groups Parallel и Intercepting Routes](<./12 Route Groups Parallel и Intercepting Routes.md>)
- [15 Suspense lazy и code splitting](<../React/15 Suspense lazy и code splitting.md>)

#### Источники

- [Next.js 14 docs: Pages and Layouts](https://nextjs.org/docs/14/app/building-your-application/routing/pages-and-layouts)
- [Next.js 14 docs: Layout file](https://nextjs.org/docs/14/app/api-reference/file-conventions/layout)
- [Next.js 14 docs: Loading UI and Streaming](https://nextjs.org/docs/14/app/building-your-application/routing/loading-ui-and-streaming)
- [Next.js 14 docs: Error Handling](https://nextjs.org/docs/14/app/building-your-application/routing/error-handling)
- [Next.js 14 docs: Route Handlers](https://nextjs.org/docs/14/app/building-your-application/routing/route-handlers)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Что такое Next.js и зачем он нужен](<./01 Что такое Next.js и зачем он нужен.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Server Components Client Components и use client →](<./03 Server Components Client Components и use client.md>)
<!-- CARD-NAV-BOTTOM:END -->
