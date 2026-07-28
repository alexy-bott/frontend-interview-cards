# 08 Route Handlers Middleware Edge и Node runtime

<!-- CARD-NAV-TOP:START -->
[← 07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Dynamic routes params searchParams metadata →](<./09 Dynamic routes params searchParams metadata.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое Route Handlers и Middleware в Next.js 14? Чем отличаются Edge Runtime и Node.js Runtime?

<details>
<summary><strong>Показать ответ</strong></summary>

Route Handler создаёт HTTP endpoint, то есть точку входа для HTTP-запросов, внутри App Router. Файл `route.ts` размещают в каталоге `app`, а экспортированные функции `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD` и `OPTIONS` обрабатывают соответствующие HTTP-методы.

```ts
// app/api/posts/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const posts = await postsRepository.findAll();
  return NextResponse.json(posts);
}

export async function POST(request: Request) {
  const body = await request.json();
  const post = await postsRepository.create(body);
  return NextResponse.json(post, { status: 201 });
}
```

Handler использует стандартные Web API `Request` и `Response`. Next.js добавляет `NextRequest` и `NextResponse` с удобным доступом к cookies, URL и служебным возможностям фреймворка. Для неподдерживаемого метода Next.js возвращает `405 Method Not Allowed`, а ответ на `OPTIONS` может сформировать автоматически.

В Next.js 14 `GET`, который возвращает `Response` без динамических API, кэшируется по умолчанию. Использование входного `Request`, `cookies`, `headers`, другого HTTP-метода или явной динамической настройки отключает этот режим. Начиная с Next.js 15 GET Route Handlers по умолчанию не кэшируются, поэтому поведение всегда нужно связывать с версией.

Middleware запускается до выбора маршрута и может переписать URL, перенаправить запрос, изменить headers запроса или ответа либо вернуть ответ сразу. В Next.js 14 это корневой файл `middleware.ts`, а область запуска задаётся `matcher`:

```ts
// middleware.ts
import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  if (!request.cookies.has("session")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/account/:path*"],
};
```

Middleware подходит для дешёвых решений на границе запроса: перенаправления по локали, выбора группы A/B-теста, общих headers и ранней проверки session cookie. Оно не должно выполнять тяжёлые запросы к базе и не заменяет авторизацию внутри страницы, Route Handler или Server Action. Cookie может быть подделана или устареть, а защищённую операцию всё равно нужно проверить рядом с данными.

Node.js Runtime предоставляет обычные Node.js API и совместим с большинством npm packages, драйверов баз данных и файловых операций. Edge Runtime основан на Web API и рассчитан на короткое выполнение ближе к пользователю, но не предоставляет полный набор Node.js API и поддерживает не все библиотеки.

В Next.js 14 Middleware работает только в Edge Runtime. Route Handlers и серверные маршруты по умолчанию работают в Node.js Runtime, но для совместимого кода можно указать `export const runtime = "edge"`. Слово edge описывает среду выполнения, а не обещание минимальной задержки: реальное расположение и ограничения зависят от платформы развёртывания.

В Next.js 16 `middleware.ts` переименован в `proxy.ts`, а Proxy работает в Node.js Runtime. Поэтому утверждение «Middleware всегда Edge» верно для Next.js 14, но уже не описывает текущую модель Next.js 16.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Когда нужен Route Handler, а когда Server Action?</summary>

Route Handler нужен, когда требуется явный HTTP-контракт: endpoint для мобильного клиента, webhook, OAuth callback, CORS или выдача файла. Server Action удобна для изменения данных, инициированного React-формой или компонентом внутри того же приложения. Она не предназначена как публичный API для независимых клиентов.

</details>

<details>
<summary><strong>Вопрос:</strong> Следует ли Server Component получать данные через собственный Route Handler?</summary>

Обычно нет. Server Component уже выполняется на сервере и может напрямую вызвать repository или функцию доступа к данным. Внутренний HTTP добавляет сериализацию, задержку и отдельную обработку авторизации, а во время сборки endpoint может ещё не быть запущен. Route Handler оставляют для настоящей HTTP-границы.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли разместить <code>page.tsx</code> и <code>route.ts</code> в одном сегменте?</summary>

Нет. Они претендуют на один и тот же URL, поэтому Next.js считает такую структуру конфликтом. API endpoint выносят в дочерний сегмент, например страница `/posts` и handler `/posts/export`.

</details>

<details>
<summary><strong>Вопрос:</strong> Как обработать динамический сегмент в Route Handler?</summary>

Файл размещают, например, как `app/api/posts/[id]/route.ts`. Значение `id` приходит в объекте `params` второго аргумента handler. В Next.js 14 `params` является обычным объектом, а в Next.js 15 API запроса и параметры маршрута переходят к асинхронной форме.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему полноценную авторизацию нельзя оставить только в Middleware?</summary>

Middleware находится далеко от конкретной операции и обычно видит лишь cookie или token. Оно может рано отклонить явно неавторизованный запрос, но не всегда знает, имеет ли пользователь доступ к конкретной записи. Проверку владельца и разрешения выполняют в Server Action, Route Handler или слое доступа к данным непосредственно перед чтением или изменением.

</details>

<details>
<summary><strong>Вопрос:</strong> Что чаще всего ломается при переносе кода в Edge Runtime?</summary>

Ломаются зависимости от Node.js API, native modules, неподдерживаемых драйверов баз данных и packages с динамической генерацией кода. Перед переключением нужно проверить всю цепочку imports, а не только собственный файл. Если библиотека требует Node.js, маршрут следует оставить в `nodejs` runtime.

</details>

<details>
<summary><strong>Вопрос:</strong> Как реализовать CORS в Route Handler?</summary>

Handler возвращает `Access-Control-Allow-Origin` и другие разрешённые headers, а для preflight, то есть предварительного запроса, реализует `OPTIONS`. Origin нельзя бездумно отражать из запроса вместе с credentials: разрешённые origins сравнивают с явным списком. Для API того же origin CORS обычно не нужен.

</details>

<details>
<summary><strong>Вопрос:</strong> Как принимать webhook безопасно?</summary>

Handler читает исходное тело запроса в формате, который требует провайдер, проверяет подпись и timestamp, а затем обеспечивает идемпотентность обработки. JSON нельзя преобразовывать до проверки, если подпись вычислена от исходных bytes. Медленную работу лучше передать в очередь, а провайдеру быстро вернуть успешный HTTP-статус.

</details>

## Где это встречается во frontend

| Задача | Механизм |
| --- | --- |
| Webhook платёжной системы | Route Handler |
| BFF endpoint для клиентского приложения | Route Handler |
| Изменение данных из React-формы | Server Action |
| Перенаправление по локали | Middleware в Next.js 14 |
| Тяжёлый драйвер базы данных | Node.js Runtime |
| Короткий handler на основе Web API | Edge Runtime, если это поддерживает платформа |

## Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)

## Источники

- [Next.js 14 docs: Route Handlers](https://nextjs.org/docs/14/app/building-your-application/routing/route-handlers)
- [Next.js 14 docs: Middleware](https://nextjs.org/docs/14/app/building-your-application/routing/middleware)
- [Next.js 14 docs: Edge and Node.js Runtimes](https://nextjs.org/docs/14/app/building-your-application/rendering/edge-and-nodejs-runtimes)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)
- [Next.js docs: Upgrading to version 16](https://nextjs.org/docs/app/guides/upgrading/version-16)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Dynamic routes params searchParams metadata →](<./09 Dynamic routes params searchParams metadata.md>)
<!-- CARD-NAV-BOTTOM:END -->
