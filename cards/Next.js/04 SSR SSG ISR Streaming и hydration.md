# 04 SSR SSG ISR Streaming и hydration

<!-- CARD-NAV-TOP:START -->
[← 03 Server Components Client Components и use client](<./03 Server Components Client Components и use client.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Data fetching fetch cache no-store revalidate →](<./05 Data fetching fetch cache no-store revalidate.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются SSR, SSG, ISR, streaming и hydration в Next.js?

<details>
<summary><strong>Показать ответ</strong></summary>

Эти термины описывают разные этапы. SSR, SSG и ISR отвечают, когда сервер формирует маршрут. Streaming, или потоковая передача, определяет, отправляется ли результат целиком или частями. Hydration, или гидратация, отвечает за превращение Client Components в интерактивный интерфейс браузера. React Server Components являются отдельной компонентной моделью и могут участвовать во всех этих вариантах.

**SSR (server-side rendering), или серверный рендеринг,** означает формирование HTML на сервере для конкретного запроса. В App Router точнее говорить о динамическом рендеринге во время запроса. Он нужен для персональных данных, cookies, headers и другой информации, известной только при обращении пользователя. Такой маршрут не хранится в Full Route Cache, хотя отдельные запросы данных всё ещё могут кэшироваться.

**SSG (static site generation), или статическая генерация,** означает формирование маршрута заранее во время `next build`. HTML и RSC Payload попадают в Full Route Cache и переиспользуются между пользователями. Это подходит для документации, статей и публичных страниц, данные которых одинаковы для всех.

**ISR (incremental static regeneration), или инкрементальная статическая регенерация,** позволяет обновлять статический результат после развёртывания. При обновлении по времени первый запрос после истечения интервала в Next.js 14 ещё получает прежний результат, а обновление запускается в фоне. После успешного обновления новые запросы получают свежую версию. Событийная revalidation через path или tag удаляет соответствующие записи, и следующий запрос строит их заново.

**Streaming** означает постепенную отправку интерфейса. Сервер может сначала отправить общую оболочку и быстрые сегменты, а медленные участки позже подставить через Suspense. `loading.tsx` создаёт границу на уровне маршрута, а ручной `Suspense` позволяет разделить страницу точнее. Streaming уменьшает время до первого полезного содержимого, но не ускоряет сам медленный источник данных.

**Hydration**, или гидратация, подключает клиентский React к HTML, сформированному сервером. React использует RSC Payload для согласования дерева, а JavaScript Client Components добавляет состояние и обработчики событий. Server Components сами не гидратируются, потому что их реализация не загружается в браузер.

В Next.js 14 маршрут становится динамическим, если использует данные конкретного запроса, например `cookies()`, `headers()`, свойство page `searchParams`, `cache: "no-store"` или `dynamic = "force-dynamic"`. Статический и динамический рендеринг могут сочетаться с кэшированными и некэшированными источниками данных, поэтому «SSR» не означает автоматически «ничего не кэшируется».

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> SSR и Server Components являются одним и тем же?</summary>

Нет. SSR создаёт HTML на сервере и может включать предварительный рендеринг Client Components. Server Components определяют, какой компонент выполняется только на сервере и передаётся через RSC Payload без своей реализации в клиентском бандле. В Next.js эти механизмы работают вместе, но решают разные задачи.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем SSG отличается от ISR?</summary>

SSG создаёт версию маршрута во время сборки и не задаёт автоматического обновления. ISR добавляет правило revalidation по времени или событию. В обоих случаях пользователь обычно получает сохранённый статический результат, но ISR позволяет менять его без нового полного развёртывания.

</details>

<details>
<summary><strong>Вопрос:</strong> Как работает <code>revalidate: 60</code> в Next.js 14?</summary>

В течение 60 секунд используется сохранённое значение. Первый запрос после истечения интервала получает устаревшую версию и запускает фоновое обновление. Если обновление успешно, кэш заменяется; если источник недоступен, прежнее значение сохраняется. Это поведение похоже на stale-while-revalidate.

</details>

<details>
<summary><strong>Вопрос:</strong> Что даёт streaming пользователю?</summary>

Пользователь раньше видит layout, навигацию и готовые части страницы, не ожидая самого медленного блока. Fallback внутри Suspense показывает временное состояние только для незавершённого участка. Нужно избегать большого числа хаотичных границ, иначе интерфейс появляется фрагментами и скачет.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему возникает hydration mismatch?</summary>

Первый клиентский рендеринг не совпал с серверным HTML. Причиной могут быть `Date.now()`, `Math.random()`, разные локаль или часовой пояс, чтение `window` прямо во время рендеринга, изменившиеся данные и невалидная вложенность HTML. Нужно добиться одинакового первого результата, а значение, доступное только в браузере, прочитать после монтирования или передать с сервера.

</details>

<details>
<summary><strong>Вопрос:</strong> Всегда ли динамический route медленный?</summary>

Нет. Он формируется на запрос, но может выполняться близко к пользователю, использовать Data Cache, кэш базы данных и streaming. Производительность зависит от времени получения данных, объёма серверной работы, сети и платформы развёртывания. Статический маршрут обычно дешевле, но не подходит для персонального содержимого.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли на одной странице сочетать статические и динамические данные?</summary>

В Next.js 14 маршрут с некэшированным запросом выходит из Full Route Cache, но другие `fetch` в нём могут продолжать использовать Data Cache. Streaming позволяет отдельно показать быстрые и медленные части. Полноценная статическая оболочка с динамическими участками в Next.js 14 относилась к экспериментальному PPR.

</details>

## Где это встречается во frontend

| Сценарий | Подход |
| --- | --- |
| Документация | SSG |
| Профиль по cookies | Динамический серверный рендеринг |
| Каталог с редкими изменениями | ISR |
| Dashboard с медленными блоками | Streaming и Suspense |
| Интерактивная форма | HTML с hydration Client Component |

## Связанные темы

- [03 Server Components Client Components и use client](<./03 Server Components Client Components и use client.md>)
- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>)
- [17 Hydration SSR и SSG](<../React/17 Hydration SSR и SSG.md>)

## Источники

- [Next.js 14 docs: Server Rendering Strategies](https://nextjs.org/docs/14/app/building-your-application/rendering/server-components)
- [Next.js 14 docs: Caching](https://nextjs.org/docs/14/app/building-your-application/caching)
- [Next.js 14 docs: Loading UI and Streaming](https://nextjs.org/docs/14/app/building-your-application/routing/loading-ui-and-streaming)
- [React docs: hydrateRoot](https://react.dev/reference/react-dom/client/hydrateRoot)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Server Components Client Components и use client](<./03 Server Components Client Components и use client.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Data fetching fetch cache no-store revalidate →](<./05 Data fetching fetch cache no-store revalidate.md>)
<!-- CARD-NAV-BOTTOM:END -->
