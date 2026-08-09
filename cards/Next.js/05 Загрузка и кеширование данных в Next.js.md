# Загрузка и кеширование данных в Next.js

<!-- CARD-NAV-TOP:START -->
[← 04 Рендеринг в Next.js](<./04 Рендеринг в Next.js.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Уровни кеширования в Next.js →](<./06 Уровни кеширования в Next.js.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как в Next.js 14 загружают данные через `fetch`? Что делают `force-cache`, `no-store`, `revalidate` и как обновлять кэш по меткам и путям?**

<h2></h2>

<br>
<dl>
<dd>

В App Router Server Component может быть `async` и получать данные непосредственно перед рендерингом.

Next.js 14 расширяет серверный `fetch`: кроме обычного HTTP-запроса он управляет Data Cache, то есть постоянным серверным кэшем данных, и позволяет настроить срок и способ обновления результата.

В Next.js 14 `fetch` без явной настройки по умолчанию использует:

```ts
cache: "force-cache"
```

и сохраняет ответ в Data Cache.

Однако значение по умолчанию зависит от контекста. Если неявный `fetch` выполняется после request-time API, например `cookies()` или `headers()`, для него используется `no-store`.

Порядок имеет значение:

```text
fetch до cookies()  → может кэшироваться
cookies()
fetch после cookies() → по умолчанию no-store
```

Чтобы поведение не зависело от неочевидной эвристики и порядка вызовов, важные запросы лучше настраивать явно.

`cache: "force-cache"` разрешает Next.js сохранить ответ в Data Cache и переиспользовать его между серверными запросами:

```ts
const response = await fetch(
  "https://api.example.com/products",
  {
    cache: "force-cache",
  },
);
```

Если записи ещё нет, Next.js получает данные из источника и сохраняет результат.

`cache: "no-store"` отключает Data Cache для конкретного запроса:

```ts
const response = await fetch(
  "https://api.example.com/profile",
  {
    cache: "no-store",
  },
);
```

Next.js обращается к источнику при каждом серверном рендеринге, где нужен этот запрос, и не сохраняет ответ в Data Cache.

При этом `no-store` не обязательно означает два реальных HTTP-запроса при двух одинаковых вызовах внутри одного прохода рендеринга. React Request Memoization всё ещё может объединить одинаковые GET-запросы до завершения текущего React-дерева.

Некэшированный `fetch` делает маршрут динамическим и исключает его результат из Full Route Cache.

Другие явно кэшируемые запросы того же маршрута могут продолжать использовать Data Cache:

```text
динамический route
  ├── персональный fetch с no-store
  └── общий каталог с force-cache
```

Нельзя помещать персональные данные под общий ключ Data Cache.

Для обновления кэша по времени используют:

```ts
const response = await fetch(
  "https://api.example.com/posts",
  {
    next: {
      revalidate: 60,
    },
  },
);
```

`next: { revalidate: 60 }` сохраняет ответ и разрешает повторную проверку не раньше чем через 60 секунд.

Это не означает, что запрос обязательно выполнится ровно через минуту. Если после истечения интервала никто не запрашивает данные, обновление не запускается.

В Next.js 14 первый запрос после истечения интервала обычно получает прежнее сохранённое значение и запускает обновление в фоне.

Если обновление успешно, Data Cache заменяется свежим результатом. Если источник завершился ошибкой, Next.js продолжает использовать последнее успешное значение и повторяет попытку при следующем запросе.

Для статического маршрута наименьший интервал среди его layouts, pages и `fetch` влияет на частоту revalidation всего маршрута.

Для динамически сформированного маршрута отдельные кэшированные `fetch` обновляются согласно собственным правилам.

Нельзя задавать конфликтующие настройки:

```ts
fetch(url, {
  cache: "no-store",
  next: {
    revalidate: 60,
  },
});
```

`no-store` требует каждый раз получать данные заново, а положительный `revalidate` предполагает сохранение ответа. Нужно выбрать одну модель.

Для событийного обновления запросу назначают tags, то есть метки:

```ts
await fetch("https://api.example.com/posts", {
  next: {
    tags: ["posts"],
  },
});
```

После изменения данных вызывают:

```ts
revalidateTag("posts");
```

В Next.js 14 `revalidateTag()` инвалидирует записи Data Cache, связанные с указанной меткой.

Метку удобно использовать, когда один набор данных отображается в нескольких местах:

```text
posts
  ├── /posts
  ├── /
  └── /dashboard
```

Для конкретного пути используют:

```ts
revalidatePath("/posts");
```

`revalidatePath()` инвалидирует кэш, связанный с указанной page или layout.

В Next.js 14 обе функции не обязаны немедленно выполнять все запросы и перестраивать все маршруты. Обновление происходит при следующем посещении затронутого пути.

Различие:

```text
revalidateTag → группа данных во всех использующих её маршрутах
revalidatePath → конкретный путь или группа путей
```

React отдельно выполняет Request Memoization, или мемоизацию запросов.

Одинаковые GET-вызовы `fetch` с одинаковыми URL и настройками внутри одного прохода React-рендеринга выполняются один раз:

```text
первый вызов  → реальный запрос или Data Cache
следующий     → результат из памяти текущего рендеринга
```

Request Memoization:

- относится к React, а не к постоянному Data Cache;
- действует только для GET-запросов;
- живёт до завершения текущего серверного рендеринга;
- не переиспользуется между отдельными запросами пользователей;
- не требует revalidation.

Она действует внутри React-дерева, включая:

- pages;
- layouts;
- Server Components;
- `generateMetadata`;
- `generateStaticParams`.

Route Handlers не входят в React-дерево, поэтому их `fetch` автоматически не мемоизируется этим механизмом.

Передача `AbortSignal` отключает автоматическую мемоизацию конкретного `fetch`:

```ts
const controller = new AbortController();

await fetch(url, {
  signal: controller.signal,
});
```

Если данные читаются через ORM, CMS SDK или клиент базы данных без `fetch`, React `cache` может устранить повторный вызов одной функции в рамках серверного рендеринга:

```ts
import { cache } from "react";

export const getUser = cache(async (id: string) => {
  return database.user.findUnique({
    where: {
      id,
    },
  });
});
```

React `cache` не является постоянным хранилищем между запросами.

Для постоянного кэширования результата произвольной серверной функции в Next.js 14 использовали:

```ts
unstable_cache
```

Например:

```ts
import { unstable_cache } from "next/cache";

export const getPosts = unstable_cache(
  async () => {
    return database.post.findMany();
  },
  ["posts"],
  {
    revalidate: 60,
    tags: ["posts"],
  },
);
```

Эти механизмы решают разные задачи:

```text
Request Memoization / React cache
→ устраняет повторы внутри одного серверного рендеринга

Data Cache / unstable_cache
→ переиспользует результат между серверными запросами
```

Server Component не нужно заставлять обращаться к собственному Route Handler по HTTP.

Он уже находится на сервере и может напрямую вызвать функцию доступа к данным:

```ts
import { getPosts } from "@/server/posts";

export default async function Page() {
  const posts = await getPosts();

  return <PostsList posts={posts} />;
}
```

Внутренний HTTP-запрос:

- добавляет лишний сетевой переход;
- повторно сериализует данные;
- усложняет передачу авторизации;
- требует абсолютного URL;
- может провалить prerendering во время build, когда Next.js-сервер ещё не запущен.

Route Handler нужен, когда существует реальная HTTP-граница:

- запрос приходит из Client Component;
- endpoint используется внешней системой;
- нужен webhook;
- API используют несколько клиентов.

Значения по умолчанию зависят от версии Next.js.

Начиная с Next.js 15 серверный `fetch` больше не кэшируется по умолчанию:

```ts
fetch(url); // по умолчанию не сохраняется в Data Cache
```

Для включения кэширования указывают:

```ts
fetch(url, {
  cache: "force-cache",
});
```

Либо меняют значение по умолчанию сегмента:

```ts
export const fetchCache = "default-cache";
```

В Next.js 16 Cache Components доступны как отдельная opt-in модель через:

```ts
cacheComponents: true
```

При её использовании кэширование выражается через:

- `"use cache"`;
- `cacheLife`;
- `cacheTag`.

Поэтому ответ о поведении `fetch` всегда должен начинаться с версии проекта. Правила этой карточки относятся прежде всего к Next.js 14.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>force-cache</code> отличается от <code>no-store</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`force-cache` разрешает использовать серверный Data Cache:

```ts
fetch(url, {
  cache: "force-cache",
});
```

Next.js сначала ищет сохранённый ответ. При отсутствии записи он получает данные из источника и сохраняет результат.

`no-store` пропускает Data Cache:

```ts
fetch(url, {
  cache: "no-store",
});
```

Ответ не сохраняется между отдельными серверными рендерами.

Это не те же настройки, что HTTP-кэш браузера.

В браузере свойство `cache` управляет взаимодействием с HTTP-кэшем браузера. В серверном `fetch` Next.js 14 оно управляет Data Cache Next.js.

При этом React Request Memoization всё ещё может объединить одинаковые GET-вызовы с `no-store` в рамках одного прохода рендеринга.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>revalidate: 60</code> отличается от <code>no-store</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`revalidate: 60` сохраняет ответ и разрешает считать его актуальным в течение заданного интервала:

```ts
fetch(url, {
  next: {
    revalidate: 60,
  },
});
```

После истечения интервала обновление запускается при следующем обращении. Пользователь при этом обычно сначала получает последнее сохранённое значение.

`no-store` не использует Data Cache:

```ts
fetch(url, {
  cache: "no-store",
});
```

Источник вызывается при каждом отдельном серверном рендеринге.

Выбор зависит не просто от частоты изменений:

- общие данные с допустимой задержкой — `revalidate`;
- данные конкретного пользователя — обычно `no-store`;
- данные, которые должны измениться сразу после mutation, — tag- или path-based revalidation;
- секретные персональные ответы нельзя помещать в общий кэш.

Положительный `revalidate` и `cache: "no-store"` не следует задавать одновременно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>revalidateTag</code> отличается от <code>revalidatePath</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Tag связывается с конкретными кэшированными данными:

```ts
fetch(url, {
  next: {
    tags: ["posts"],
  },
});
```

Вызов:

```ts
revalidateTag("posts");
```

инвалидирует все записи Data Cache с этой меткой независимо от маршрута, где они использовались.

Path адресует участок route tree:

```ts
revalidatePath("/posts");
```

Он подходит, когда нужно обновить конкретную page или layout.

Пример:

```text
revalidateTag("posts")
→ данные списка постов на главной, в каталоге и sidebar

revalidatePath("/posts")
→ кэш, связанный с маршрутом /posts
```

В Next.js 14 инвалидация не означает немедленный массовый запрос ко всем источникам. Актуальное содержимое строится при следующем посещении соответствующих маршрутов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Являются ли Data Cache и мемоизация запросов (Request Memoization) одним механизмом?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Data Cache принадлежит Next.js и может хранить результат между:

- отдельными серверными запросами;
- разными пользователями;
- повторными рендерами;
- deployment, если это поддерживает конфигурация платформы.

Request Memoization принадлежит React и действует только во время рендеринга одного серверного React-дерева.

После завершения рендеринга записи мемоизации очищаются.

Один вызов `fetch` может пройти через оба механизма:

```text
повтор внутри render
        ↓
Request Memoization
        ↓
Data Cache
        ↓
внешний источник
```

Если Data Cache содержит значение, первый вызов рендеринга получает его оттуда, а последующие одинаковые вызовы получают уже мемоизированный результат.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему два одинаковых запроса иногда всё равно выполняются дважды?</strong></summary>

<dl>
<dd>
<h2></h2>

Request Memoization учитывает URL и настройки запроса.

Запросы считаются разными, если отличаются, например:

- URL;
- headers;
- method;
- параметры `cache`;
- параметры `next`;
- другие options.

Мемоизация применяется только к GET-запросам внутри React-дерева.

Она не действует для `fetch` в Route Handler, потому что Route Handler не участвует в рендеринге React Component tree.

Переданный `AbortSignal` также отключает автоматическую мемоизацию:

```ts
const controller = new AbortController();

fetch(url, {
  signal: controller.signal,
});
```

Два одинаковых запроса, выполненные в разных серверных обращениях пользователя, также не объединяются Request Memoization. Для их переиспользования нужен Data Cache или другой постоянный кэш.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли <code>cookies()</code> все данные некэшируемыми?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

В Next.js 14 `cookies()` использует данные конкретного запроса и переводит маршрут в динамический режим.

Неявные `fetch`, расположенные после него, по умолчанию получают `no-store`.

Но это не запрещает явно кэшировать общие данные:

```ts
const catalog = await fetch(
  "https://api.example.com/catalog",
  {
    cache: "force-cache",
  },
);

const cookieStore = cookies();

const profile = await fetch(
  "https://api.example.com/profile",
  {
    cache: "no-store",
    headers: {
      Authorization: cookieStore.get("token")?.value ?? "",
    },
  },
);
```

В этом примере:

- каталог может переиспользоваться между пользователями;
- профиль формируется для конкретного запроса.

Нельзя кэшировать персональный ответ под общим ключом или случайно включать пользовательские credentials в разделяемую запись.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли проверять <code>response.ok</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

`fetch` отклоняет Promise при сетевой ошибке, невозможности установить соединение или отмене запроса.

Ответы `404`, `403` и `500` сами по себе не отклоняют Promise:

```ts
const response = await fetch(url);

if (!response.ok) {
  throw new Error(
    `Request failed: ${response.status}`,
  );
}
```

Дальнейшее поведение зависит от вида ошибки:

- отсутствующий ресурс может вызвать `notFound()`;
- ожидаемая ошибка формы возвращается как состояние;
- временная ошибка может показываться рядом с интерфейсом;
- неожиданное исключение может обработать ближайший `error.tsx`.

Нельзя автоматически показывать пользователю текст внутреннего серверного исключения, если он может содержать технические или секретные данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что изменилось в Next.js 15?</strong></summary>

<dl>
<dd>
<h2></h2>

Начиная с Next.js 15 `fetch` больше не кэшируется по умолчанию.

Запрос:

```ts
fetch("https://api.example.com/posts");
```

по умолчанию не сохраняется в Data Cache.

Для отдельного запроса кэширование включают явно:

```ts
fetch("https://api.example.com/posts", {
  cache: "force-cache",
});
```

Для layout или page можно изменить значение по умолчанию:

```ts
export const fetchCache = "default-cache";
```

Явные настройки конкретного `fetch` имеют приоритет.

При переносе приложения с Next.js 14 на Next.js 15 число запросов может увеличиться, если код полагался на неявный `force-cache`.

В Next.js 16 дополнительно появилась opt-in модель Cache Components:

```ts
const nextConfig = {
  cacheComponents: true,
};
```

В ней вместо части старых route segment options используются:

- `"use cache"`;
- `cacheLife`;
- `cacheTag`.

Поэтому документацию по кэшированию нужно читать для точной версии и конфигурации проекта.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Данные | Настройка Next.js 14 |
| --- | --- |
| Общий каталог | `force-cache` и правило обновления кэша |
| Личный кабинет | `cookies()` и `no-store` для персональных данных |
| Новости с минутным допуском | `next: { revalidate: 60 }` |
| Обновление после формы | `revalidateTag` или `revalidatePath` |
| Прямой запрос к базе данных | Функция доступа к данным без внутреннего Route Handler |

## Связанные темы

- [04 Рендеринг в Next.js](<./04 Рендеринг в Next.js.md>)
- [06 Уровни кеширования в Next.js](<./06 Уровни кеширования в Next.js.md>)
- [07 Server Actions и изменение данных](<./07 Server Actions и изменение данных.md>)
- [01 Виды состояния во frontend](<../State Management/01 Виды состояния во frontend.md>)

## Источники

- [Next.js 14 docs: Fetching, Caching, and Revalidating](https://nextjs.org/docs/14/app/building-your-application/data-fetching/fetching-caching-and-revalidating)
- [Next.js 14 docs: fetch](https://nextjs.org/docs/14/app/api-reference/functions/fetch)
- [Next.js 14 docs: Caching](https://nextjs.org/docs/14/app/building-your-application/caching)
- [Next.js 14 docs: revalidateTag](https://nextjs.org/docs/14/app/api-reference/functions/revalidateTag)
- [Next.js 14 docs: revalidatePath](https://nextjs.org/docs/14/app/api-reference/functions/revalidatePath)
- [Next.js docs: Backend for Frontend](https://nextjs.org/docs/app/guides/backend-for-frontend)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)
- [Next.js docs: Cache Components](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents)
- [Next.js docs: Migrating to Cache Components](https://nextjs.org/docs/app/guides/migrating-to-cache-components)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Рендеринг в Next.js](<./04 Рендеринг в Next.js.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Уровни кеширования в Next.js →](<./06 Уровни кеширования в Next.js.md>)
<!-- CARD-NAV-BOTTOM:END -->
