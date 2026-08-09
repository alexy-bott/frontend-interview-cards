# Уровни кеширования в Next.js

<!-- CARD-NAV-TOP:START -->
[← 05 Загрузка и кеширование данных в Next.js](<./05 Загрузка и кеширование данных в Next.js.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Server Actions и изменение данных →](<./07 Server Actions и изменение данных.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Какие уровни кэширования есть в Next.js 14 App Router и как они связаны?**

<h2></h2>

<br>
<dl>
<dd>

В Next.js 14 нужно различать четыре механизма. Они хранят разные результаты, находятся в разных местах и обновляются разными API.

| Механизм | Что хранит | Где | Срок |
| --- | --- | --- | --- |
| Request Memoization | Результат одинакового GET `fetch` | Память серверного рендеринга | Один проход рендеринга |
| Data Cache | Результаты загрузки данных | Сервер или платформа | Между запросами и развёртываниями |
| Full Route Cache | HTML и RSC Payload статического маршрута | Сервер или платформа | До revalidation или нового развёртывания |
| Router Cache | RSC Payload посещённых и предварительно загруженных сегментов | Память браузера | Сессия или автоматический срок |

Request Memoization, или мемоизация запроса, является возможностью React.

Во время рендеринга дерева одинаковый GET `fetch` с теми же URL и options выполняется один раз. После завершения серверного рендеринга запись исчезает.

Механизм работает внутри React-дерева:

- Server Components;
- pages;
- layouts;
- `generateMetadata`;
- `generateStaticParams`.

Он не применяется к Route Handlers, потому что они не участвуют в рендеринге React-дерева.

Data Cache хранит результаты получения данных между отдельными серверными запросами.

В Next.js 14 серверный `fetch` по умолчанию кэшируется, пока код явно не отключил кэширование или запрос не оказался в динамическом контексте.

Data Cache настраивают через:

- `cache: "force-cache"`;
- `cache: "no-store"`;
- `next.revalidate`;
- tags;
- `revalidateTag`;
- `revalidatePath`.

Full Route Cache хранит уже сформированный результат статического маршрута:

- HTML;
- RSC Payload.

Динамически формируемые маршруты в него не попадают, но могут продолжать использовать Data Cache для отдельных общих данных.

Связь между серверными кэшами односторонняя:

```text
Data Cache обновлён или очищен
              ↓
зависимый маршрут рендерится заново
              ↓
Full Route Cache обновляется
```

Обратное неверно.

Если маршрут стал динамическим или его Full Route Cache был очищен, это само по себе не удаляет записи Data Cache. Поэтому динамический маршрут может сочетать кэшированные и некэшированные данные.

Новое развёртывание очищает Full Route Cache, потому что сохранённый результат относится к конкретной сборке.

Data Cache по модели Next.js 14 может сохраняться между развёртываниями. При самостоятельном размещении реальное поведение зависит от cache handler, файловой системы и наличия общего хранилища между экземплярами приложения.

Router Cache находится в памяти браузера и разбит по сегментам route tree.

Он хранит RSC Payload:

- посещённых маршрутов;
- предварительно загруженных маршрутов;
- общих layouts;
- loading states;
- страниц.

Router Cache применяется и к статическим, и к динамическим маршрутам.

Он ускоряет:

- переходы между страницами;
- prefetch;
- возврат назад и вперёд;
- сохранение общих layouts;
- частичное обновление дерева без полной загрузки документа.

В Next.js 14 автоматический срок зависит от типа маршрута:

```text
динамический сегмент → 30 секунд
статический сегмент → 5 минут
```

Срок отсчитывается для отдельного сегмента с момента его создания или последнего доступа.

Полный prefetch через:

```tsx
<Link href="/dashboard" prefetch={true}>
  Dashboard
</Link>
```

или:

```ts
router.prefetch("/dashboard");
```

может сохранить даже динамический маршрут на 5 минут.

Полная перезагрузка документа очищает Router Cache, потому что он находится во временной памяти браузера.

`router.refresh()` обновляет клиентскую сторону текущего интерфейса:

```ts
router.refresh();
```

В модели Next.js 14 команда:

1. очищает Router Cache;
2. запрашивает новый RSC Payload текущего маршрута;
3. объединяет результат с существующим клиентским деревом;
4. сохраняет незатронутое состояние Client Components и состояние браузера.

Она не очищает:

- Data Cache;
- Full Route Cache.

Если сервер снова получил старые данные из Data Cache, новый RSC Payload также будет содержать старое значение.

Для серверной инвалидации используют:

```ts
revalidateTag("posts");
```

или:

```ts
revalidatePath("/posts");
```

Вызов из Server Action связывается с текущим клиентским взаимодействием, поэтому может обновить:

- Data Cache;
- зависимый Full Route Cache;
- Router Cache текущей клиентской сессии.

В Next.js 14 `revalidatePath()` из Server Action мог очищать клиентский Router Cache шире указанного пути. Сам серверный Data Cache и Full Route Cache при этом инвалидируются в соответствии с переданным path.

Вызов тех же функций из Route Handler обновляет серверные кэши, но Route Handler не связан с конкретной открытой страницей.

Поэтому уже загруженный Router Cache может продолжать показывать прежний RSC Payload до:

- `router.refresh()`;
- новой навигации после истечения срока;
- полной перезагрузки;
- другой клиентской инвалидации.

Изменение cookie внутри Server Action:

```ts
cookies().set(...);
cookies().delete(...);
```

также инвалидирует Router Cache. Это нужно, чтобы layouts и страницы не сохраняли устаревшее состояние авторизации.

Кэш Next.js не заменяет:

- HTTP-кэш браузера;
- CDN-кэш;
- кэш базы данных;
- клиентский кэш RTK Query;
- browser back/forward cache.

Каждому уровню нужны собственные правила хранения и инвалидации.

Частые ошибки:

- вызывать только `router.refresh()` при устаревшем Data Cache;
- ожидать мгновенного обновления открытой страницы после revalidation из Route Handler;
- считать динамический маршрут полностью некэшируемым;
- хранить персональные данные под общим ключом Data Cache;
- не синхронизировать серверный кэш между несколькими containers.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Data Cache отличается от Full Route Cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Data Cache хранит результат получения данных:

```text
fetch или серверная функция → данные
```

Full Route Cache хранит результат рендеринга маршрута:

```text
данные + React-дерево → HTML и RSC Payload
```

Динамический маршрут может использовать Data Cache без Full Route Cache.

Например:

```text
динамический профиль
  ├── персональные данные с no-store
  └── общий список стран из Data Cache
```

Обновление Data Cache приводит к повторному рендерингу зависимого статического маршрута и обновлению Full Route Cache.

Очистка или отключение Full Route Cache не удаляет Data Cache автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Request Memoization отличается от Data Cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Request Memoization устраняет повтор одинаковой работы только внутри текущего React-рендеринга.

После завершения рендеринга запись исчезает:

```text
один render
  ├── первый fetch → запрос
  └── второй fetch → результат из памяти
```

Data Cache сохраняется между отдельными серверными запросами:

```text
первый пользователь → данные сохранены
второй пользователь → данные переиспользованы
```

Request Memoization:

- не требует revalidation;
- применяется только внутри React-дерева;
- относится к GET `fetch`;
- не является постоянным хранилищем.

Data Cache должен иметь понятное правило:

- срока жизни;
- событийной инвалидации;
- либо явного отказа от кэширования.

Один запрос может одновременно использовать оба механизма.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что хранит Router Cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Router Cache хранит RSC Payload посещённых и предварительно загруженных route segments в памяти браузера.

Он не хранит исходные backend-данные как самостоятельное клиентское хранилище.

RSC Payload описывает результат Server Components и места Client Components в React-дереве.

Кэш позволяет:

- запрашивать только отсутствующие сегменты;
- сохранять общие layouts;
- выполнять частичную навигацию;
- быстро возвращаться на посещённые маршруты;
- не загружать новый HTML-документ при каждом переходе.

Router Cache отличается от Full Route Cache:

```text
Full Route Cache → сервер, только статические маршруты

Router Cache → браузер, статические и динамические маршруты
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>router.refresh()</code> может не показать новые данные?</strong></summary>

<dl>
<dd>
<h2></h2>

`router.refresh()` запрашивает новый результат серверного рендеринга, но не очищает серверные кэши.

Например:

```text
router.refresh()
      ↓
новый серверный render
      ↓
fetch получает старое значение из Data Cache
      ↓
новый RSC Payload содержит прежние данные
```

Сначала нужно правильно обновить источник серверных данных:

```ts
revalidateTag("posts");
```

или:

```ts
revalidatePath("/posts");
```

Либо не помещать запрос в Data Cache:

```ts
fetch(url, {
  cache: "no-store",
});
```

После корректной серверной инвалидации `router.refresh()` может быть нужен, если mutation выполнялась через обычный клиентский запрос или Route Handler и уже открытый Router Cache не был обновлён автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли динамический route все его <code>fetch</code> динамическими?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Динамический маршрут:

- не сохраняется в Full Route Cache;
- выполняется на каждый серверный запрос.

Но отдельный общий `fetch` может явно использовать Data Cache:

```ts
const catalog = await fetch(
  "https://api.example.com/catalog",
  {
    cache: "force-cache",
  },
);
```

Одновременно персональные данные получают без кэша:

```ts
const profile = await fetch(
  "https://api.example.com/profile",
  {
    cache: "no-store",
  },
);
```

Так можно сочетать:

```text
персональный динамический интерфейс
+
общие кэшируемые справочники
```

Важно не сохранять пользовательские данные в общем Data Cache.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит с кэшем после deployment?</strong></summary>

<dl>
<dd>
<h2></h2>

Full Route Cache очищается при новой сборке, потому что HTML и RSC Payload зависят от версии приложения.

Data Cache по модели Next.js 14 может переживать deployment.

На управляемой платформе постоянство и распределение кэша обеспечивает сама платформа.

При self-hosting по умолчанию кэш может находиться на диске отдельного Next.js-сервера.

Если приложение запущено в нескольких containers, каждый экземпляр без дополнительной настройки может иметь собственное состояние.

Для согласованного кэша используют:

- общий cache handler;
- Redis или другое внешнее хранилище;
- общую файловую систему;
- платформенный Data Cache.

Нужно отдельно проверить:

- сохраняется ли кэш при замене container;
- видят ли экземпляры инвалидации друг друга;
- не обслуживают ли разные instances разные версии данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли отключить Router Cache?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 14 полностью отключить Router Cache нельзя.

Можно отключить автоматический prefetch ссылки:

```tsx
<Link
  href="/dashboard"
  prefetch={false}
>
  Dashboard
</Link>
```

Но после фактического посещения route segments всё равно временно сохраняются для:

- вложенной навигации;
- возврата назад и вперёд;
- повторного перехода;
- сохранения layouts.

Для принудительного обновления используют:

```ts
router.refresh();
```

При этом команда не очищает Data Cache или Full Route Cache.

Автоматические сроки Router Cache в Next.js 14 можно было изменять через экспериментальную настройку `staleTimes`, но это не превращало Router Cache в полностью отключаемый механизм.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем кэш Next.js отличается от RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Next.js кэширует данные и результат рендеринга на серверной и маршрутизаторной границе.

RTK Query работает после загрузки клиентского JavaScript и хранит server state в Redux store:

- результаты запросов;
- статусы загрузки;
- ошибки;
- подписки компонентов;
- client-side tags;
- время жизни неиспользуемых данных.

Пример разделения:

```text
Next.js Data Cache
→ общие данные для серверного рендеринга

RTK Query
→ данные интерактивного клиентского экрана
```

Один ресурс может присутствовать на нескольких уровнях, но тогда нужно определить:

- какой кэш является источником актуального состояния;
- что инвалидируется после mutation;
- как серверные данные передаются клиенту;
- не выполняется ли один запрос повторно без необходимости.

Tags RTK Query и tags Next.js не связаны автоматически. Это разные системы инвалидации.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Симптом | Что проверить |
| --- | --- |
| Один GET повторяется внутри page и layout | Request Memoization |
| Backend вызывается на каждый серверный запрос | Data Cache и `no-store` |
| Маршрут не выполняется заново | Full Route Cache |
| После навигации виден прежний сегмент | Router Cache |
| `router.refresh()` не обновил данные | Data Cache |
| После webhook открытая страница показывает старые данные | Router Cache после revalidation из Route Handler |
| Разные containers показывают разные версии | Общее хранилище и cache handler |

## Связанные темы

- [05 Загрузка и кеширование данных в Next.js](<./05 Загрузка и кеширование данных в Next.js.md>)
- [07 Server Actions и изменение данных](<./07 Server Actions и изменение данных.md>)
- [10 Версии Next.js 14 15 и 16](<./10 Версии Next.js 14 15 и 16.md>)
- [06 Основы RTK Query](<../State Management/06 Основы RTK Query.md>)

## Источники

- [Next.js 14 docs: Caching](https://nextjs.org/docs/14/app/building-your-application/caching)
- [Next.js 14 docs: Fetching, Caching, and Revalidating](https://nextjs.org/docs/14/app/building-your-application/data-fetching/fetching-caching-and-revalidating)
- [Next.js 14 docs: useRouter](https://nextjs.org/docs/14/app/api-reference/functions/use-router)
- [Next.js 14 docs: revalidatePath](https://nextjs.org/docs/14/app/api-reference/functions/revalidatePath)
- [Next.js 14 docs: revalidateTag](https://nextjs.org/docs/14/app/api-reference/functions/revalidateTag)
- [Next.js 14 docs: staleTimes](https://nextjs.org/docs/14/app/api-reference/next-config-js/staleTimes)
- [Next.js 14 docs: Deploying](https://nextjs.org/docs/14/app/building-your-application/deploying)
- [Next.js 14 docs: Custom Cache Handler](https://nextjs.org/docs/14/app/api-reference/next-config-js/incrementalCacheHandlerPath)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Загрузка и кеширование данных в Next.js](<./05 Загрузка и кеширование данных в Next.js.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Server Actions и изменение данных →](<./07 Server Actions и изменение данных.md>)
<!-- CARD-NAV-BOTTOM:END -->
