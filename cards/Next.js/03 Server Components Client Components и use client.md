# Server Components Client Components и use client

<!-- CARD-NAV-TOP:START -->
[← 02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 SSR SSG ISR Streaming и hydration →](<./04 SSR SSG ISR Streaming и hydration.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются Server Components и Client Components в App Router? Что делает `"use client"`?**

<h2></h2>

<br>
<dl>
<dd>

Server Components выполняются в серверной среде во время сборки или обработки запроса. В App Router это тип компонентов по умолчанию.

Они могут:

- напрямую получать данные из базы или внутреннего API;
- читать файловую систему;
- использовать server-only SDK;
- обращаться к закрытым environment variables, то есть переменным окружения;
- выполнять тяжёлые преобразования без отправки соответствующих библиотек браузеру.

Реализация Server Component и его серверные зависимости не попадают в клиентский bundle. Браузер получает результат рендеринга через RSC Payload, а не исходный код компонента.

В Server Components нельзя использовать возможности, требующие интерактивного экземпляра в браузере:

- `useState`;
- `useEffect`;
- DOM event handlers вроде `onClick`;
- `window`, `document`, `localStorage`;
- большинство клиентских hooks.

Client Components нужны для:

- локального состояния;
- эффектов;
- событий;
- API браузера;
- клиентских подписок;
- Context Providers;
- интерактивных сторонних библиотек.

Название Client Component не означает, что при первом открытии он вообще не участвует в серверном формировании страницы.

При первом полном открытии Next.js:

1. формирует RSC Payload;
2. использует Server и Client Components для предварительного HTML;
3. отправляет HTML браузеру;
4. загружает JavaScript Client Components;
5. гидратирует их, подключая состояние и события.

Server Components не гидратируются, потому что их реализация не выполняется в браузере.

При последующей клиентской навигации сервер формирует новый RSC Payload, а браузер использует его для обновления дерева без полной перезагрузки документа. Client Components при этом рендерятся и сохраняют интерактивность на клиенте.

Директива:

```tsx
"use client";
```

задаёт границу в графе модулей.

Её ставят в начале файла до imports:

```tsx
"use client";

import { useState } from "react";

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}
```

Сам файл и его транзитивные imports становятся частью клиентского графа зависимостей.

Поэтому директиву не нужно добавлять в каждый вложенный файл.

Важно различать:

- граф imports;
- визуальное React-дерево.

Компонент не становится клиентским только потому, что визуально находится внутри Client Component. Если Server Component был создан выше и передан через `children` или другой React-prop, его реализация остаётся серверной.

Границу `"use client"` обычно располагают как можно ниже.

Если вся page помечена `"use client"` ради одной кнопки, в клиентский bundle могут попасть:

- сама страница;
- её imports;
- утилиты;
- библиотеки;
- компоненты, которые могли бы остаться серверными.

Обычный подход:

```text
Server Component
  ├── получает данные
  ├── рендерит статический интерфейс
  └── передаёт нужные данные небольшому Client Component
```

Server Component может импортировать Client Component и передавать ему props.

Значения, пересекающие серверно-клиентскую границу, должны поддерживаться сериализацией React.

К поддерживаемым значениям относятся, например:

- primitives;
- массивы и plain objects;
- `Date`;
- `Map`;
- `Set`;
- некоторые другие встроенные структуры;
- Promises;
- React-элементы;
- Server Functions.

Нельзя передать:

- обычное замыкание;
- DOM-узел;
- соединение с базой;
- экземпляр произвольного класса;
- server-only SDK;
- secret, который не должен попасть пользователю.

Сериализуемость не означает безопасность. Например, строка с секретным токеном технически сериализуема, но передавать её Client Component нельзя.

Server Function является специальной серверной ссылкой, которую React умеет передавать через границу отдельно от обычных функций.

Client Component не может импортировать server-only модуль и сохранить его серверное выполнение.

Если клиентский модуль импортирует обычный универсальный компонент, его использование становится частью клиентского графа. Если модулю нужны база данных, файловая система или secrets, такой импорт должен завершиться ошибкой.

Чтобы визуально разместить настоящий Server Component внутри Client Component, используют композицию.

Server Component создаёт дерево выше:

```tsx
import { Modal } from "./Modal";
import { Cart } from "./Cart";

export default function Page() {
  return (
    <Modal>
      <Cart />
    </Modal>
  );
}
```

`Modal` является Client Component:

```tsx
"use client";

import type { ReactNode } from "react";

export function Modal({
  children,
}: {
  children: ReactNode;
}) {
  return <div>{children}</div>;
}
```

`Cart` остаётся Server Component, потому что его импортирует и создаёт `Page`, а `Modal` получает только место для уже сформированного серверного содержимого в RSC Payload.

Директива:

```tsx
"use server";
```

не помечает Server Component.

Она объявляет async Server Function:

```tsx
"use server";

export async function saveProfile(formData: FormData) {
  // Серверная mutation
}
```

Server Action — это Server Function, используемая как action, например для отправки формы или другой mutation.

Аргументы Server Function приходят от клиента и считаются недоверенными. Внутри неё всегда нужны:

- валидация;
- authentication;
- authorization;
- проверка права на конкретную операцию.

Для защиты от случайного импорта серверного модуля в клиентский код используют:

```ts
import "server-only";
```

Такой импорт заставляет Next.js завершить сборку ошибкой, если модуль попадёт в клиентский граф.

Аналогично модуль с обязательными API браузера можно пометить:

```ts
import "client-only";
```

`server-only` защищает границу imports, но не фильтрует данные. Если Server Component явно передаст secret в props Client Component, значение всё равно может попасть клиенту.

Environment variables без `NEXT_PUBLIC_` по умолчанию остаются серверными.

Переменные с префиксом:

```text
NEXT_PUBLIC_
```

предназначены для клиентского кода и должны считаться публичными.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Выполняется ли Client Component на сервере?</strong></summary>

<dl>
<dd>
<h2></h2>

При первом полном открытии Next.js использует Client Components при предварительном формировании HTML на сервере.

Однако такой HTML ещё не интерактивен.

После загрузки JavaScript браузер гидратирует Client Components:

- создаёт клиентские экземпляры;
- подключает обработчики событий;
- активирует состояние;
- запускает эффекты.

Следовательно, Client Component может предварительно рендериться на сервере, но его интерактивный код обязательно должен уметь выполняться в браузере.

Поэтому во время render нельзя без проверки обращаться к API, существующему только после загрузки страницы:

```tsx
"use client";

import { useEffect } from "react";

export function StorageReader() {
  useEffect(() => {
    const value = localStorage.getItem("theme");
  }, []);

  return null;
}
```

При последующей навигации Next.js получает RSC Payload нового маршрута, а Client Components обновляются в браузере без загрузки нового полного HTML-документа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в Server Component нельзя использовать <code>useState</code> и <code>onClick</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Server Component выполняется заранее и не сохраняет интерактивный экземпляр в браузере.

`useState` требует состояния, которое живёт между клиентскими render.

`onClick` требует обработчика DOM-события, который должен быть загружен и зарегистрирован в браузере.

Код Server Component туда не отправляется, поэтому интерактивный участок выносят за границу `"use client"`:

```tsx
import { LikeButton } from "./LikeButton";

export default async function Product() {
  const product = await getProduct();

  return (
    <>
      <h1>{product.name}</h1>
      <LikeButton productId={product.id} />
    </>
  );
}
```

Server Component получает данные, а Client Component отвечает только за интерактивность.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>"use client"</code> влияет на bundle?</strong></summary>

<dl>
<dd>
<h2></h2>

`"use client"` создаёт корень клиентского графа модулей.

Все его транзитивные статические imports становятся кандидатами на включение в клиентские chunks.

Чем выше находится граница и чем больше зависимостей она охватывает, тем больше JavaScript браузеру нужно:

- скачать;
- разобрать;
- скомпилировать;
- выполнить;
- гидратировать.

Поэтому вместо client layout:

```tsx
"use client";

import { Logo } from "./Logo";
import { Navigation } from "./Navigation";
import { Search } from "./Search";
```

обычно оставляют layout серверным, а клиентским делают только `Search`.

При этом Server Components, созданные выше и переданные через `children` или другой React-prop, не становятся imports клиентского модуля и не включаются в его bundle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему props из Server Component должны сериализоваться?</strong></summary>

<dl>
<dd>
<h2></h2>

React передаёт значения через серверно-клиентскую границу в RSC Payload.

Поэтому значение должно иметь представление, которое React умеет восстановить на другой стороне.

Поддержка шире обычного JSON. React может передавать, например:

- primitives;
- массивы;
- plain objects;
- `Date`;
- `Map`;
- `Set`;
- Promises;
- React-элементы;
- Server Functions.

Обычное замыкание не имеет переносимого представления:

```tsx
<ClientButton
  onSave={() => database.save()}
/>
```

Так передать функцию из Server Component нельзя.

Экземпляр произвольного класса или подключение к базе также содержит поведение и внутреннее состояние, которое нельзя безопасно восстановить в браузере.

Server Function является отдельным поддерживаемым типом ссылки, поэтому её можно передать Client Component:

```tsx
<ClientForm action={saveProfile} />
```

Сериализуемые данные всё равно нужно фильтровать. Нельзя передавать весь объект пользователя или базы только потому, что React технически способен сериализовать часть его полей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли передать Server Component внутрь Client Component?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, через композицию.

Server Component должен создать оба элемента и передать серверное содержимое через `children` или другой React-prop:

```tsx
export default function Page() {
  return (
    <ClientModal>
      <ServerCart />
    </ClientModal>
  );
}
```

Client Component не импортирует реализацию `ServerCart`:

```tsx
"use client";

import type { ReactNode } from "react";

export function ClientModal({
  children,
}: {
  children: ReactNode;
}) {
  return <div>{children}</div>;
}
```

`ServerCart` заранее выполняется на сервере, а RSC Payload содержит указание, где его результат нужно разместить внутри клиентской оболочки.

Если импортировать тот же универсальный компонент непосредственно из client-модуля, его использование станет клиентским. Если модуль действительно server-only, такой импорт должен быть запрещён.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где размещать Context Provider?</strong></summary>

<dl>
<dd>
<h2></h2>

React Context для клиентского состояния используют через Client Component:

```tsx
"use client";

import { createContext } from "react";

export const ThemeContext = createContext("light");

export function ThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ThemeContext.Provider value="dark">
      {children}
    </ThemeContext.Provider>
  );
}
```

Server Component может импортировать и отрисовать Provider:

```tsx
import { ThemeProvider } from "./ThemeProvider";

export default function Layout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
```

Client Components внутри смогут прочитать `ThemeContext`.

Server Components, переданные через `children`, не получают доступ к клиентскому Context. Они выполняются на сервере до того, как Provider начинает работать в браузере.

Provider размещают как можно глубже — вокруг только той части дерева, которой действительно нужно клиентское состояние. Это уменьшает клиентскую границу и позволяет большей части интерфейса оставаться серверной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как не допустить попадания серверного кода в клиентский бандл?</strong></summary>

<dl>
<dd>
<h2></h2>

Доступ к данным, secrets и server SDK держат в отдельных модулях:

```ts
import "server-only";

export async function getUser() {
  return database.user.findFirst();
}
```

Если этот модуль импортировать из клиентского графа, Next.js выдаст ошибку сборки.

Также важно:

- не добавлять `"use client"` слишком высоко;
- не импортировать server SDK из client entry;
- не передавать приватные данные через props;
- возвращать из data access layer только необходимые публичные поля;
- не считать сериализуемость доказательством безопасности.

Переменные без `NEXT_PUBLIC_` по умолчанию не предназначены для браузера.

Переменные с префиксом:

```text
NEXT_PUBLIC_
```

включаются в клиентский код и должны считаться публичными.

`server-only` предотвращает неправильный импорт, но не защищает от явной передачи секрета:

```tsx
<ClientComponent token={process.env.SECRET_TOKEN} />
```

Такой код архитектурно неверен, даже если модуль остаётся серверным.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Тип компонента |
| --- | --- |
| Получить данные напрямую из базы данных или CMS | Server Component |
| Использовать `onClick` или `useState` | Client Component |
| Показать серверные данные внутри интерактивной модалки | Server Component, переданный в Client Component через композицию |
| Подключить Theme Provider | Client Component |
| Скрыть secret и server SDK | Server module с `server-only` и фильтрацией возвращаемых данных |

## Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [18 Server Components и Server Actions](<../React/18 Server Components и Server Actions.md>)

## Источники

- [Next.js docs: Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components)
- [Next.js docs: use client](https://nextjs.org/docs/app/api-reference/directives/use-client)
- [Next.js docs: Data Security](https://nextjs.org/docs/app/guides/data-security)
- [Next.js docs: Environment Variables](https://nextjs.org/docs/app/guides/environment-variables)
- [React docs: Server Components](https://react.dev/reference/rsc/server-components)
- [React docs: use client](https://react.dev/reference/rsc/use-client)
- [React docs: use server](https://react.dev/reference/rsc/use-server)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 SSR SSG ISR Streaming и hydration →](<./04 SSR SSG ISR Streaming и hydration.md>)
<!-- CARD-NAV-BOTTOM:END -->
