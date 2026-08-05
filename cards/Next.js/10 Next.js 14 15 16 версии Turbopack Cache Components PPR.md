# Next.js 14 15 16 версии Turbopack Cache Components PPR

<!-- CARD-NAV-TOP:START -->
[← 09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Pages Router getServerSideProps getStaticProps getStaticPaths →](<./11 Pages Router getServerSideProps getStaticProps getStaticPaths.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что важно знать о Next.js 14 и какие изменения в Next.js 15 и 16 нельзя смешивать с этой версией?**

<h2></h2>

<br>
<dl>
<dd>

Ответ о Next.js должен быть привязан к версии, потому что между 14, 15 и 16 изменились:

- значения по умолчанию;
- серверные API;
- сборщик модулей;
- модель кэширования;
- runtime Middleware;
- поддерживаемые версии React и Node.js.

Для проекта на Next.js 14 основной ответ строится вокруг поведения этой версии, а более новые возможности называются отдельно.

| Тема | Next.js 14 | Next.js 15 | Next.js 16 |
| --- | --- | --- | --- |
| Server Actions | Стабильны | Интегрированы с API форм React 19 | Поддерживаются |
| Серверный `fetch` | Обычно кэшируется | Не кэшируется по умолчанию | Не кэшируется по умолчанию; Cache Components включаются отдельно |
| GET Route Handler | Кэшируется при выполнении условий | Не кэшируется по умолчанию | Не кэшируется по умолчанию без Cache Components |
| `params`, `searchParams`, `cookies`, `headers` | Синхронные API | Переходят к `Promise`, временно доступна совместимость | Синхронный доступ удалён |
| Turbopack | В основном `next dev --turbo` | Стабилен для разработки; build появился позднее и не был default | По умолчанию для `dev` и `build` |
| PPR | Экспериментальная preview-возможность | Остаётся экспериментальным | Opt-in часть модели Cache Components |
| Middleware | `middleware.ts`, Edge Runtime | `middleware.ts`; Node.js Runtime стабилен с 15.5 | `proxy.ts`, только Node.js Runtime; `middleware.ts` deprecated |
| React Compiler | Нет встроенной интеграции | Экспериментальная интеграция | Стабильная настройка, выключенная по умолчанию |

В Next.js 14 App Router уже поддерживает:

- React Server Components;
- вложенные layouts;
- streaming;
- Route Handlers;
- стабильные Server Actions.

Кэширование описывается четырьмя отдельными механизмами:

- Request Memoization;
- Data Cache;
- Full Route Cache;
- Router Cache.

Серверный `fetch` обычно участвует в Data Cache, если код не перешёл в динамический контекст и кэширование явно не отключено.

Для отказа от кэша используют:

```ts
fetch(url, {
  cache: "no-store",
});
```

Для сохранения ответа указывают:

```ts
fetch(url, {
  cache: "force-cache",
});
```

Для обновления по времени:

```ts
fetch(url, {
  next: {
    revalidate: 60,
  },
});
```

Эта модель относится к Next.js 14 и не должна автоматически переноситься на современные версии.

Turbopack — incremental bundler, то есть инкрементальный сборщик модулей, написанный на Rust.

В Next.js 14 его прежде всего включали для локальной разработки:

```json
{
  "scripts": {
    "dev": "next dev --turbo"
  }
}
```

Production-сборка продолжала использовать webpack.

Поэтому в Next.js 14 нельзя считать, что успешная работа проекта через:

```bash
next dev --turbo
```

доказывает полную совместимость production build с Turbopack.

Конфигурация Turbopack также не является полной копией webpack-конфигурации. Совместимость loaders, plugins, aliases и нестандартной обработки файлов нужно проверять отдельно.

PPR, Partial Prerendering, или частичный предварительный рендеринг, объединяет:

- заранее подготовленную статическую оболочку;
- динамические участки под Suspense;
- streaming динамического результата во время запроса.

Упрощённо:

```text
статический layout и оболочка
              +
динамические участки под Suspense
              ↓
единая страница
```

Оболочка быстро отдаётся из статического результата, а динамические части формируются для конкретного запроса и передаются потоком.

В Next.js 14 PPR был экспериментальной preview-возможностью и не должен описываться как обычное поведение любого маршрута App Router.

Обычный streaming сам по себе не означает PPR.

Streaming может постепенно отправлять полностью динамически сформированный ответ. PPR дополнительно предполагает сохранённую статическую оболочку, которая сочетается с request-time участками.

Next.js 15 добавил поддержку React 19 и перевёл App Router на React-модель, необходимую для новых API форм и серверных функций.

В React 19:

```ts
useFormState
```

был заменён рекомендуемым hook:

```ts
useActionState
```

Next.js 15 также сделал request-time API асинхронными:

- `params`;
- page `searchParams`;
- `cookies()`;
- `headers()`;
- `draftMode()`.

В Next.js 14 код выглядел так:

```tsx
export default function Page({
  params,
}: {
  params: {
    id: string;
  };
}) {
  return <div>{params.id}</div>;
}
```

В Next.js 15 используется асинхронная форма:

```tsx
export default async function Page({
  params,
}: {
  params: Promise<{
    id: string;
  }>;
}) {
  const {
    id,
  } = await params;

  return <div>{id}</div>;
}
```

Версия 15 временно сохраняла синхронный доступ для облегчения миграции, но он сопровождался предупреждениями и не являлся новой рекомендуемой моделью.

Серверный `fetch` и `GET` Route Handlers в Next.js 15 перестали кэшироваться по умолчанию.

Для отдельного запроса кэш включают явно:

```ts
fetch(url, {
  cache: "force-cache",
});
```

Для `GET` Route Handler можно явно выбрать статический режим:

```ts
export const dynamic = "force-static";

export async function GET() {
  return Response.json({
    status: "ok",
  });
}
```

При миграции с Next.js 14 эти изменения могут увеличить число запросов и нагрузку на backend, даже если бизнес-логика приложения не менялась.

В Next.js 15 Turbopack стал стабильным для development.

Production build через Turbopack появился позднее в ветке Next.js 15, но не являлся стандартным сборщиком для всех проектов. Поэтому утверждение «Next.js 15 полностью заменил webpack» неверно.

В Next.js 16 Turbopack стал стандартным сборщиком для:

```bash
next dev
```

и:

```bash
next build
```

Дополнительный флаг больше не нужен:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build"
  }
}
```

Если проект зависит от webpack, его выбирают явно:

```bash
next dev --webpack
next build --webpack
```

Если в `next.config` присутствует пользовательская webpack-конфигурация, обычный `next build`, использующий Turbopack, может завершиться ошибкой, чтобы конфигурация не была молча проигнорирована.

Next.js 16 требует минимум:

```text
Node.js 20.9.0
```

Поддержка Node.js 18 удалена.

В Next.js 16 синхронная совместимость request-time API также удалена.

Нужно обязательно использовать асинхронную форму:

```tsx
const {
  id,
} = await params;
```

Next.js 16 ввёл Cache Components как новую opt-in модель кэширования и Partial Prerendering.

Её включают через:

```ts
import type {
  NextConfig,
} from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
};

export default nextConfig;
```

Включение `cacheComponents` объединяет несколько связанных возможностей:

- Partial Prerendering;
- директиву `"use cache"`;
- динамический request-time код;
- `cacheLife`;
- `cacheTag`;
- автоматическое выделение статической оболочки.

По умолчанию данные не становятся постоянными только из-за обычного вызова `fetch`.

Кэшируемую функцию или компонент отмечают явно:

```ts
import {
  cacheLife,
  cacheTag,
} from "next/cache";

export async function getProducts() {
  "use cache";

  cacheLife("hours");
  cacheTag("products");

  return database.product.findMany();
}
```

`cacheLife` определяет cache profile.

Профиль может описывать:

- `stale` — сколько времени значение можно использовать на клиенте без обращения к серверу;
- `revalidate` — когда кэш следует обновлять в фоне;
- `expire` — когда устаревшее значение больше нельзя использовать.

Поэтому `cacheLife` не является просто одним TTL.

`cacheTag` связывает кэшируемый результат с меткой для последующей инвалидации.

При включённых Cache Components старые route segment options:

- `dynamic`;
- `revalidate`;
- `fetchCache`;

заменяются более явной моделью:

- `"use cache"`;
- `cacheLife`;
- Suspense для request-time участков.

Cache Components требуют Node.js Runtime.

Такой segment нельзя переключить на:

```ts
export const runtime = "edge";
```

Это важное отличие от обычного App Router, где отдельный маршрут может поддерживать Edge Runtime.

Динамические данные, не помещённые в кэш, располагают под Suspense:

```tsx
import {
  Suspense,
} from "react";

export default function Page() {
  return (
    <>
      <CachedCatalog />

      <Suspense
        fallback={<CartSkeleton />}
      >
        <DynamicCart />
      </Suspense>
    </>
  );
}
```

При prerendering Next.js формирует статическую оболочку, а динамическую часть выполняет во время запроса.

В Next.js 16 изменились и API инвалидации.

Для контента, допускающего eventual consistency, используют:

```ts
revalidateTag("posts", "max");
```

Профиль `"max"` применяет stale-while-revalidate:

```text
пользователь получает старое значение
              +
обновление выполняется в фоне
```

Одноаргументная форма:

```ts
revalidateTag("posts");
```

в Next.js 16 deprecated.

Для сценария read-your-writes используют:

```ts
updateTag("posts");
```

`updateTag` доступен только внутри Server Action.

Он немедленно помечает tag истёкшим, чтобы последующее чтение после mutation ожидало свежие данные вместо показа прежнего результата:

```ts
"use server";

import {
  updateTag,
} from "next/cache";

export async function updatePost(
  postId: string,
  title: string,
) {
  await database.post.update({
    where: {
      id: postId,
    },
    data: {
      title,
    },
  });

  updateTag(`post-${postId}`);
}
```

Упрощённое различие:

```text
revalidateTag(tag, "max")
→ stale-while-revalidate
→ допустима временная устарелость

updateTag(tag)
→ только Server Actions
→ read-your-writes после mutation
```

Эти правила относятся к новой модели Next.js 16 и не должны использоваться для объяснения поведения `revalidateTag` в Next.js 14 без оговорки.

В Next.js 16 convention:

```text
middleware.ts
```

deprecated в пользу:

```text
proxy.ts
```

Название Proxy подчёркивает, что код выполняется на сетевой границе до маршрута и не должен превращаться в универсальный слой бизнес-логики.

Proxy использует только Node.js Runtime:

```text
proxy.ts → Node.js Runtime
```

В `proxy.ts` нельзя настроить:

```ts
export const runtime = "edge";
```

Если проект на Next.js 16 временно должен сохранить Edge Runtime, документация разрешает продолжить использовать старый `middleware.ts`, пока convention ещё поддерживается.

Исторически модель развивалась так:

```text
Next.js 14
→ middleware.ts
→ Edge Runtime

Next.js 15.5
→ Node.js Runtime для Middleware стал стабильным

Next.js 16
→ middleware.ts deprecated
→ proxy.ts
→ только Node.js Runtime
```

React Compiler анализирует React-код во время сборки и автоматически добавляет оптимизации, эквивалентные мемоизации, когда может доказать их безопасность.

В Next.js 15 интеграция была экспериментальной.

В Next.js 16 настройка стала стабильной:

```ts
import type {
  NextConfig,
} from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
};

export default nextConfig;
```

Но она выключена по умолчанию.

Также устанавливают compiler plugin:

```bash
pnpm add -D babel-plugin-react-compiler
```

React Compiler использует Babel, поэтому его включение может увеличить время development- и production-компиляции.

Compiler может уменьшить необходимость в ручных:

- `useMemo`;
- `useCallback`;
- `React.memo`.

Но он не исправляет:

- неправильную архитектуру состояния;
- мутацию данных;
- побочные эффекты во время render;
- ошибочные зависимости эффектов;
- слишком высокие Client Component boundaries.

React Compiler не является частью Next.js 14 и не должен упоминаться как встроенная возможность проекта этой версии.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему ответы о кэшировании <code>fetch</code> в Next.js 14 и 15 различаются?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 14 серверный `fetch` обычно кэшируется в Data Cache, если код не перешёл в динамический контекст:

```ts
fetch(url);
```

обычно эквивалентен:

```ts
fetch(url, {
  cache: "force-cache",
});
```

В Next.js 15 запрос не кэшируется по умолчанию.

Для сохранения результата нужно указать:

```ts
fetch(url, {
  cache: "force-cache",
});
```

или изменить значение по умолчанию для сегмента:

```ts
export const fetchCache =
  "default-cache";
```

Поэтому один и тот же код после обновления с Next.js 14 до 15 может начать выполнять больше обращений к backend.

Next.js 16 без Cache Components продолжает использовать модель с некэшируемым по умолчанию `fetch`.

При включении Cache Components кэширование выражают прежде всего через:

```ts
"use cache";
```

Поэтому совет без названной версии и конфигурации может быть прямо противоположным нужному поведению.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в новых примерах <code>params</code> нужно <code>await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 15 API, зависящие от запроса, стали асинхронными:

- `params`;
- page `searchParams`;
- `cookies()`;
- `headers()`;
- `draftMode()`.

Поэтому новый тип выглядит так:

```ts
type PageProps = {
  params: Promise<{
    id: string;
  }>;
};
```

Значение получают через:

```ts
const {
  id,
} = await params;
```

В Next.js 14 `params` и `searchParams` являются обычными объектами.

Next.js 15 временно поддерживал синхронный доступ для миграции, но выводил предупреждения.

В Next.js 16 эта совместимость удалена, и асинхронный доступ стал обязательным.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Turbopack и полностью ли он заменил webpack?</strong></summary>

<dl>
<dd>
<h2></h2>

Turbopack — инкрементальный сборщик модулей, написанный на Rust и оптимизированный для быстрой разработки и повторной компиляции.

В Next.js 14 он использовался прежде всего через:

```bash
next dev --turbo
```

Production build продолжал использовать webpack.

В Next.js 15 Turbopack стал стабильным для разработки. Поддержка production build появилась позднее, но не была стандартным режимом для всех проектов.

В Next.js 16 Turbopack стал сборщиком по умолчанию:

```bash
next dev
next build
```

Webpack не удалён.

Его можно выбрать явно:

```bash
next dev --webpack
next build --webpack
```

Это может понадобиться, если проект зависит от:

- пользовательских webpack plugins;
- нестандартных loaders;
- особенностей webpack resolution;
- конфигурации, которую Turbopack пока не поддерживает.

Следовательно, Turbopack заменил webpack как default, но не удалил возможность использовать webpack.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое PPR и чем он отличается от обычного streaming?</strong></summary>

<dl>
<dd>
<h2></h2>

Streaming — способ доставки серверного результата.

Готовые части ответа передаются браузеру по мере выполнения:

```text
layout → сразу
быстрый блок → следом
медленный блок → позже
```

PPR — стратегия формирования маршрута.

Она объединяет:

- заранее сохранённую статическую оболочку;
- динамические участки;
- Suspense;
- streaming request-time содержимого.

Упрощённо:

```text
PPR
  ├── static shell из кэша
  └── dynamic holes во время запроса
          ↓
       streaming
```

Можно использовать streaming без PPR — например, когда вся страница динамически формируется во время запроса.

PPR использует streaming как способ доставки динамических участков, но дополнительно сохраняет статическую оболочку заранее.

В Next.js 14 и 15 PPR был экспериментальным.

В Next.js 16 он входит в opt-in модель Cache Components:

```ts
cacheComponents: true
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Cache Components в Next.js 16?</strong></summary>

<dl>
<dd>
<h2></h2>

Cache Components — opt-in модель, позволяющая сочетать в одном маршруте:

- статическую оболочку;
- явно кэшируемые данные;
- request-time данные;
- динамические участки под Suspense.

Её включают:

```ts
const nextConfig = {
  cacheComponents: true,
};
```

Кэшируемую функцию или компонент помечают:

```ts
"use cache";
```

Время жизни и revalidation определяют через:

```ts
cacheLife()
```

Метки задают через:

```ts
cacheTag()
```

Динамический участок, который нельзя выполнить во время prerendering, располагают под Suspense.

При включённых Cache Components прежние route segment options:

- `dynamic`;
- `revalidate`;
- `fetchCache`;

заменяются новой моделью.

Cache Components требуют Node.js Runtime и несовместимы с:

```ts
export const runtime = "edge";
```

Эта модель не относится к Next.js 14.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>revalidateTag</code> и <code>updateTag</code> в Next.js 16 отличаются по назначению?</strong></summary>

<dl>
<dd>
<h2></h2>

`revalidateTag` с cache profile применяет stale-while-revalidate:

```ts
revalidateTag("posts", "max");
```

Кэшированное значение становится устаревшим, но пользователь ещё может получить его, пока новое значение загружается в фоне.

Это подходит для:

- статей;
- документации;
- каталога;
- общих данных, где допустима eventual consistency.

`updateTag` разрешён только внутри Server Actions:

```ts
updateTag("posts");
```

Он немедленно помечает запись истёкшей, а следующее чтение ожидает свежий результат.

Это подходит для read-your-writes:

```text
пользователь изменил профиль
              ↓
следующий интерфейс должен сразу показать изменение
```

Одноаргументная форма:

```ts
revalidateTag("posts");
```

в Next.js 16 deprecated.

Это различие появилось в новой модели и не описывает поведение Next.js 14.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>middleware.ts</code> переименовали в <code>proxy.ts</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Название Middleware было слишком широким и создавало впечатление универсального слоя приложения.

Название Proxy подчёркивает, что код работает на сетевой границе до маршрута и предназначен прежде всего для:

- redirects;
- rewrites;
- изменения headers;
- ранней фильтрации запросов;
- маршрутизации.

Он не должен заменять:

- data access layer;
- бизнес-логику;
- окончательную authentication;
- authorization конкретной операции.

Для Next.js 14 корректно говорить:

```text
middleware.ts
Edge Runtime
```

В Next.js 15.5 Middleware получил стабильную поддержку Node.js Runtime.

В Next.js 16 `middleware.ts` deprecated, а новый:

```text
proxy.ts
```

выполняется только в Node.js Runtime.

Конфигурация runtime внутри Proxy недоступна.

Старый Middleware convention в Next.js 16 пока можно сохранить, если проекту необходим Edge Runtime.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли React Compiler частью Next.js 14?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

В Next.js 15 появилась экспериментальная интеграция React Compiler.

В Next.js 16 настройка стала стабильной:

```ts
const nextConfig = {
  reactCompiler: true,
};
```

Но она выключена по умолчанию.

Для работы устанавливают:

```bash
pnpm add -D babel-plugin-react-compiler
```

Compiler выполняет статический анализ и может сократить необходимость в ручных:

- `useMemo`;
- `useCallback`;
- `React.memo`.

При этом он:

- не исправляет неправильные эффекты;
- не устраняет мутацию состояния;
- не заменяет правильные границы Server и Client Components;
- не гарантирует оптимальную архитектуру;
- может увеличить время компиляции из-за использования Babel.

Для проекта на Next.js 14 React Compiler не следует описывать как встроенную возможность фреймворка.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что проверить первым |
| --- | --- |
| Пример из свежей документации не собирается в проекте | Версию Next.js и включённые experimental или opt-in возможности |
| После миграции выросло число запросов | Значения по умолчанию у `fetch` и GET handlers |
| TypeScript требует `await params` | Переход на Next.js 15/16 |
| Пользовательская webpack config перестала работать | Фактический сборщик и наличие флага `--webpack` |
| В статье используется `"use cache"` | Это модель Next.js 16 с Cache Components |
| Проект содержит `middleware.ts` | Для Next.js 14 это ожидаемо; в Next.js 16 convention deprecated |
| `revalidateTag` требует второй аргумент | Новая сигнатура Next.js 16 |
| Cache Components не работают в Edge | Эта модель требует Node.js Runtime |

## Связанные темы

- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>)
- [19 React 18 19 и 19.2](<../React/19 React 18 19 и 19.2.md>)

## Источники

- [Next.js 14 announcement](https://nextjs.org/blog/next-14)
- [Next.js 15 announcement](https://nextjs.org/blog/next-15)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)
- [Next.js 16 announcement](https://nextjs.org/blog/next-16)
- [Next.js docs: Upgrading to version 16](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Next.js docs: Turbopack](https://nextjs.org/docs/app/api-reference/turbopack)
- [Next.js docs: Cache Components](https://nextjs.org/docs/app/getting-started/cache-components)
- [Next.js docs: Migrating to Cache Components](https://nextjs.org/docs/app/guides/migrating-to-cache-components)
- [Next.js docs: use cache](https://nextjs.org/docs/app/api-reference/directives/use-cache)
- [Next.js docs: cacheLife](https://nextjs.org/docs/app/api-reference/functions/cacheLife)
- [Next.js docs: cacheTag](https://nextjs.org/docs/app/api-reference/functions/cacheTag)
- [Next.js docs: revalidateTag](https://nextjs.org/docs/app/api-reference/functions/revalidateTag)
- [Next.js docs: updateTag](https://nextjs.org/docs/app/api-reference/functions/updateTag)
- [Next.js docs: Proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy)
- [Next.js docs: React Compiler](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactCompiler)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Pages Router getServerSideProps getStaticProps getStaticPaths →](<./11 Pages Router getServerSideProps getStaticProps getStaticPaths.md>)
<!-- CARD-NAV-BOTTOM:END -->
