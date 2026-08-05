# Route Handlers Middleware Edge и Node runtime

<!-- CARD-NAV-TOP:START -->
[← 07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Dynamic routes params searchParams metadata →](<./09 Dynamic routes params searchParams metadata.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Route Handlers и Middleware в Next.js 14? Чем отличаются Edge Runtime и Node.js Runtime?**

<h2></h2>

<br>
<dl>
<dd>

Route Handler создаёт HTTP endpoint, то есть точку входа для HTTP-запросов, внутри App Router.

Файл `route.ts` размещают в каталоге `app`, а экспортированные функции обрабатывают соответствующие HTTP-методы:

- `GET`;
- `POST`;
- `PUT`;
- `PATCH`;
- `DELETE`;
- `HEAD`;
- `OPTIONS`.

```ts
// app/api/posts/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const posts = await postsRepository.findAll();

  return NextResponse.json(posts);
}

export async function POST(request: Request) {
  const body: unknown = await request.json();

  // Входные данные нужно проверить перед записью.
  const post = await postsRepository.create(body);

  return NextResponse.json(post, {
    status: 201,
  });
}
```

Route Handler использует стандартные Web API:

- `Request`;
- `Response`;
- `Headers`;
- `FormData`;
- `ReadableStream`.

Next.js дополнительно предоставляет `NextRequest` и `NextResponse` с удобным доступом к cookies, URL и служебным возможностям фреймворка.

Если запрошенный HTTP-метод не поддерживается, Next.js возвращает:

```text
405 Method Not Allowed
```

Если собственный `OPTIONS` не определён, Next.js автоматически создаёт ответ и устанавливает header `Allow` на основе экспортированных методов.

Такой автоматический ответ не является полной настройкой CORS preflight. Для cross-origin API всё равно могут потребоваться собственные `Access-Control-Allow-*` headers.

В Next.js 14 Route Handler кэшируется по умолчанию, когда используется `GET`, возвращающий `Response`, и обработчик не переходит к динамическому режиму.

Например:

```ts
export async function GET() {
  const posts = await postsRepository.findAll();

  return Response.json(posts);
}
```

От автоматического кэширования `GET` можно отказаться:

- принимая и используя объект `Request`;
- используя `cookies()` или `headers()`;
- задавая динамическую route segment config;
- выполняя другой HTTP-метод;
- явно настраивая динамический режим.

Например:

```ts
export const dynamic = "force-dynamic";

export async function GET(
  request: Request,
) {
  const searchParams = new URL(
    request.url,
  ).searchParams;

  return Response.json({
    query: searchParams.get("query"),
  });
}
```

Начиная с Next.js 15 `GET` Route Handlers по умолчанию не кэшируются. Поэтому поведение всегда нужно связывать с версией проекта.

Route Handler является обычной серверной HTTP-точкой входа.

Внутри него нужно проверять:

- формат входных данных;
- authentication;
- authorization;
- право на конкретный ресурс;
- допустимость операции;
- ожидаемые ошибки.

Middleware запускается до сопоставления запроса с файловым маршрутом и может:

- перенаправить запрос;
- переписать URL;
- изменить request headers;
- изменить response headers;
- установить или удалить cookie;
- вернуть ответ без выполнения маршрута;
- пропустить запрос дальше через `NextResponse.next()`.

В Next.js 14 используется единственный файл:

```text
middleware.ts
```

Его размещают:

- в корне проекта рядом с `app`;
- либо внутри `src`, если приложение использует `src/app`.

Логику можно разбивать на импортируемые модули, но специальный файл Middleware остаётся один.

Область запуска задаётся через `matcher`:

```ts
// middleware.ts
import {
  NextResponse,
  type NextRequest,
} from "next/server";

export function middleware(
  request: NextRequest,
) {
  if (!request.cookies.has("session")) {
    return NextResponse.redirect(
      new URL("/login", request.url),
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/account/:path*"],
};
```

Значения `matcher` должны быть константами, которые Next.js может проанализировать во время сборки.

Middleware подходит для быстрых решений на границе запроса:

- перенаправления по локали;
- A/B-теста;
- общих security headers;
- rewrite на другой маршрут;
- ранней проверки наличия session cookie;
- исключения очевидно недоступных маршрутов.

Middleware не следует использовать для:

- тяжёлых запросов к базе данных;
- длительных вычислений;
- основной предметной логики;
- полной проверки доступа к каждой сущности.

Наличие cookie само по себе не доказывает:

- действительность сессии;
- актуальность роли;
- право пользователя читать или изменять конкретный ресурс.

Поэтому защищённую операцию повторно проверяют рядом с данными:

- в Server Component;
- в Route Handler;
- в Server Action;
- в data access layer.

**Node.js Runtime** является стандартной средой выполнения серверных маршрутов Next.js.

Он предоставляет:

- Node.js API;
- совместимость с большинством npm packages;
- драйверы баз данных;
- native modules, если их поддерживает платформа;
- файловые операции;
- привычные серверные библиотеки.

Доступность постоянной записываемой файловой системы всё равно зависит от платформы. Например, в serverless-среде файловая система может быть временной или частично доступной только для чтения.

**Edge Runtime** основан преимущественно на Web API.

Он предоставляет, например:

- `fetch`;
- `Request`;
- `Response`;
- `Headers`;
- Web Crypto;
- Streams;
- URL API.

При этом Edge Runtime не предоставляет полный набор Node.js API и может не поддерживать:

- `fs`;
- часть `crypto` из Node.js;
- native modules;
- некоторые database drivers;
- packages с динамической генерацией кода;
- библиотеки, зависящие от Node.js globals.

В Next.js 14 Middleware работает в Edge Runtime.

Route Handlers, pages и layouts по умолчанию используют Node.js Runtime, но совместимый route segment можно переключить:

```ts
export const runtime = "edge";
```

или явно оставить в Node.js:

```ts
export const runtime = "nodejs";
```

Перед переносом в Edge нужно проверять всю цепочку imports, а не только код самого handler.

Название Edge Runtime не гарантирует, что функция физически выполняется рядом с каждым пользователем.

Реальные:

- регионы;
- лимиты выполнения;
- cold starts;
- доступность runtime;
- расположение относительно базы данных;

определяются платформой развёртывания.

Между версиями Next.js модель изменилась:

```text
Next.js 14
→ Middleware работает в Edge Runtime

Next.js 15.5
→ Node.js Runtime для Middleware стал стабильным

Next.js 16
→ middleware.ts deprecated в пользу proxy.ts
→ Proxy работает только в Node.js Runtime
```

В Next.js 16 Edge Runtime не поддерживается для `proxy.ts`. Если проект пока должен сохранить Edge Runtime, upgrade guide разрешает продолжать использовать старый Middleware convention до дальнейших изменений.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда нужен Route Handler, а когда Server Action?</strong></summary>

<dl>
<dd>
<h2></h2>

Route Handler нужен, когда требуется явный HTTP-контракт:

- endpoint для мобильного клиента;
- webhook;
- OAuth callback;
- CORS;
- загрузка или выдача файла;
- публичный API;
- интеграция с внешней системой.

Разработчик управляет:

- URL;
- HTTP-методом;
- status code;
- headers;
- форматом request;
- форматом response.

Server Action удобна для mutation, инициированной React-формой или компонентом внутри того же приложения.

Next.js сам связывает её с React, сериализует вызов и может вернуть обновлённый RSC Payload.

Server Action не предназначена как стабильный публичный API для независимых клиентов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Следует ли Server Component получать данные через собственный Route Handler?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет.

Server Component уже выполняется на сервере и может напрямую вызвать:

- repository;
- database client;
- CMS SDK;
- функцию data access layer.

```tsx
import {
  getPosts,
} from "@/server/posts";

export default async function Page() {
  const posts = await getPosts();

  return <PostsList posts={posts} />;
}
```

Внутренний HTTP-запрос добавляет:

- сериализацию;
- сетевой переход;
- задержку;
- отдельную обработку ошибок;
- повторную передачу авторизации;
- необходимость формировать абсолютный URL.

Во время build собственный endpoint может ещё не быть запущен, поэтому такой запрос способен сломать prerendering.

Route Handler оставляют для настоящей HTTP-границы, когда endpoint нужен браузеру, внешней системе или другому независимому клиенту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли разместить <code>page.tsx</code> и <code>route.ts</code> в одном сегменте?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Оба файла претендуют на один URL:

```text
app/posts/page.tsx
app/posts/route.ts
```

Next.js считает такую структуру конфликтом.

HTTP endpoint выносят в другой segment.

Например:

```text
app/posts/page.tsx
→ /posts

app/posts/export/route.ts
→ /posts/export
```

Или используют отдельную API-область:

```text
app/api/posts/route.ts
→ /api/posts
```

Префикс `/api` является соглашением проекта, а не обязательным требованием Route Handlers.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обработать динамический сегмент в Route Handler?</strong></summary>

<dl>
<dd>
<h2></h2>

Файл размещают в папке с динамическим segment:

```text
app/api/posts/[id]/route.ts
```

В Next.js 14 `params` является обычным объектом второго аргумента handler:

```ts
export async function GET(
  request: Request,
  {
    params,
  }: {
    params: {
      id: string;
    };
  },
) {
  return Response.json({
    id: params.id,
  });
}
```

Начиная с Next.js 15 `params` стал асинхронным:

```ts
export async function GET(
  request: Request,
  {
    params,
  }: {
    params: Promise<{
      id: string;
    }>;
  },
) {
  const {
    id,
  } = await params;

  return Response.json({
    id,
  });
}
```

При обновлении версии нужно проверить сигнатуры:

- pages;
- layouts;
- Route Handlers;
- `generateMetadata`;
- другие Dynamic APIs.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему полноценную авторизацию нельзя оставить только в Middleware?</strong></summary>

<dl>
<dd>
<h2></h2>

Middleware находится до конкретного маршрута и обычно выполняет только дешёвую предварительную проверку.

Например, оно может определить:

```text
session cookie отсутствует
→ перенаправить на /login
```

Но наличие cookie не отвечает на вопросы:

- действительна ли сессия;
- не был ли пользователь заблокирован;
- имеет ли он нужную роль;
- принадлежит ли ему конкретная запись;
- разрешена ли операция над текущим состоянием сущности.

Поэтому Route Handler или Server Action повторно проверяет доступ непосредственно перед чтением или mutation:

```text
Middleware
→ ранняя фильтрация запроса

Route Handler / Server Action / DAL
→ окончательная authentication и authorization
```

Проверки могут использовать общий модуль авторизации, но должны выполняться на защищённой серверной границе.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что чаще всего ломается при переносе кода в Edge Runtime?</strong></summary>

<dl>
<dd>
<h2></h2>

Чаще всего ломаются зависимости от:

- `fs`;
- Node.js `net` и `tls`;
- части Node.js `crypto`;
- native modules;
- традиционных database drivers;
- Node.js globals;
- динамической генерации кода;
- packages, которые импортируют неподдерживаемые модули косвенно.

Проверять нужно всю цепочку imports:

```text
Route Handler
  → repository
    → database driver
      → native или Node.js dependency
```

Даже если собственный файл использует только `fetch`, вложенная библиотека может требовать Node.js.

Для Edge выбирают совместимые HTTP-based SDK и Web API.

Если библиотека требует Node.js, маршрут оставляют в runtime:

```ts
export const runtime = "nodejs";
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как реализовать CORS в Route Handler?</strong></summary>

<dl>
<dd>
<h2></h2>

CORS headers добавляют в response:

```ts
const allowedOrigins = new Set([
  "https://app.example.com",
]);

export async function GET(
  request: Request,
) {
  const origin =
    request.headers.get("origin");

  if (
    !origin ||
    !allowedOrigins.has(origin)
  ) {
    return new Response(null, {
      status: 403,
    });
  }

  return Response.json(
    {
      status: "ok",
    },
    {
      headers: {
        "Access-Control-Allow-Origin":
          origin,
        "Vary": "Origin",
      },
    },
  );
}
```

Для preflight реализуют `OPTIONS`:

```ts
export async function OPTIONS(
  request: Request,
) {
  const origin =
    request.headers.get("origin");

  if (
    !origin ||
    !allowedOrigins.has(origin)
  ) {
    return new Response(null, {
      status: 403,
    });
  }

  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin":
        origin,
      "Access-Control-Allow-Methods":
        "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers":
        "Content-Type, Authorization",
      "Access-Control-Max-Age": "86400",
      "Vary": "Origin",
    },
  });
}
```

Автоматический `OPTIONS` Next.js устанавливает `Allow`, но не обязан сформировать все CORS headers приложения.

Нельзя бездумно отражать любой входящий `Origin`.

Если запрос использует credentials:

```text
cookies или Authorization
```

нельзя сочетать их с:

```text
Access-Control-Allow-Origin: *
```

Нужен явно разрешённый origin и, для cookie-запросов:

```text
Access-Control-Allow-Credentials: true
```

Для API того же origin CORS обычно не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как принимать webhook безопасно?</strong></summary>

<dl>
<dd>
<h2></h2>

Webhook обычно подписывается провайдером по исходному телу запроса.

Поэтому body сначала читают без преобразования:

```ts
export async function POST(
  request: Request,
) {
  const rawBody = await request.text();
  const signature =
    request.headers.get(
      "x-webhook-signature",
    );

  verifyWebhookSignature({
    rawBody,
    signature,
  });

  const event = JSON.parse(rawBody);

  await processWebhook(event);

  return new Response(null, {
    status: 204,
  });
}
```

Если провайдер подписывает bytes, используют:

```ts
await request.arrayBuffer();
```

Нельзя сначала вызвать:

```ts
await request.json();
```

а затем пытаться прочитать исходное тело. Body является stream и обычным способом читается один раз. Кроме того, повторная сериализация JSON может изменить представление, по которому рассчитывалась подпись.

Безопасная обработка включает:

- проверку подписи;
- проверку timestamp;
- защиту от replay;
- idempotency по идентификатору события;
- проверку типа события;
- безопасное логирование;
- ограничение размера body.

Если обработка долгая, событие сохраняют в очередь, а провайдеру быстро возвращают успешный HTTP-статус. Это уменьшает вероятность повторной доставки из-за timeout.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Механизм |
| --- | --- |
| Webhook платёжной системы | Route Handler |
| BFF endpoint для клиентского приложения | Route Handler |
| Изменение данных из React-формы | Server Action |
| Перенаправление по локали | Middleware в Next.js 14 |
| Тяжёлый драйвер базы данных | Node.js Runtime |
| Короткий handler на основе Web API | Edge Runtime, если код и платформа совместимы |

## Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)

## Источники

- [Next.js 14 docs: Route Handlers](https://nextjs.org/docs/14/app/building-your-application/routing/route-handlers)
- [Next.js 14 docs: Middleware](https://nextjs.org/docs/14/app/building-your-application/routing/middleware)
- [Next.js 14 docs: Route Segment Config](https://nextjs.org/docs/14/app/api-reference/file-conventions/route-segment-config)
- [Next.js 14 docs: Edge and Node.js Runtimes](https://nextjs.org/docs/14/app/building-your-application/rendering/edge-and-nodejs-runtimes)
- [Next.js 14 docs: Edge Runtime API](https://nextjs.org/docs/14/pages/api-reference/edge)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)
- [Next.js docs: Upgrading to version 16](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Next.js docs: Proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Dynamic routes params searchParams metadata →](<./09 Dynamic routes params searchParams metadata.md>)
<!-- CARD-NAV-BOTTOM:END -->
