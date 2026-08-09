# Server Components и Server Actions

<!-- CARD-NAV-TOP:START -->
[← 17 SSR SSG и hydration в React](<./17 SSR SSG и hydration в React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [19 Версии React 18 19 и 19.2 →](<./19 Версии React 18 19 и 19.2.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое React Server Components и Server Functions? Чем они отличаются от SSR и Client Components?**

<h2></h2>

<br>
<dl>
<dd>

React Server Components, или RSC, являются компонентами, которые выполняются в серверной среде или во время сборки. Они не отправляют собственный код и чисто серверные зависимости в клиентский бандл.

Server Components могут напрямую читать серверные данные и формируют сериализованное описание React-дерева. Фреймворк объединяет этот результат с интерактивными Client Components.

В зависимости от фреймворка Server Component может выполняться:

- один раз во время сборки;
- для каждого запроса;
- во время повторного получения серверного дерева при клиентской навигации.

Server Component может быть асинхронным, обращаться к базе данных или внутреннему API и импортировать серверную библиотеку:

```tsx
export default async function ProductPage() {
  const product = await db.product.findFirst();

  return <h1>{product?.name}</h1>;
}
```

Он не может использовать:

- `useState`;
- `useEffect`;
- DOM;
- `window`;
- обычные обработчики событий DOM-элементов.

Например, следующая функция должна выполняться в браузере и не может быть обычным callback внутри Server Component:

```tsx
<button onClick={() => console.log("click")}>
  Купить
</button>
```

Исключением является Server Function. React может закодировать специальную ссылку на неё и передать эту ссылку Client Component.

Client Component нужен для интерактивности:

- состояния;
- эффектов;
- обработчиков событий;
- браузерных API;
- клиентских библиотек.

В Next.js файл помечается директивой:

```tsx
"use client";
```

Она создаёт границу в графе модулей, а не границу в визуальном дереве компонентов.

Экспортируемые из файла компоненты и транзитивно импортируемые им модули становятся частью клиентского кода:

```tsx
"use client";

import { useState } from "react";
import { formatCount } from "./formatCount";

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      {formatCount(count)}
    </button>
  );
}
```

В клиентский граф попадут и `Counter`, и `formatCount`.

Директиву не требуется повторять в каждом дочернем файле.

Название Client Component не означает, что его первоначальная разметка обязательно создаётся только в браузере. При первой загрузке фреймворк может сформировать для него HTML на сервере, а затем гидрировать компонент в браузере.

RSC и SSR отвечают на разные вопросы:

| Механизм | Результат | Задача |
| --- | --- | --- |
| RSC | Сериализованный результат Server Components и ссылки на Client Components | Разделить серверный и клиентский код в React-дереве |
| SSR | HTML | Дать браузеру первоначальную разметку |
| Гидратация | Связь Client Components с существующим DOM | Добавить интерактивность в браузере |

При первом открытии фреймворк может:

```text
1. Выполнить Server Components
2. Получить RSC Payload
3. Создать из него и Client Components первоначальный HTML
4. Отправить HTML и RSC Payload браузеру
5. Загрузить JavaScript Client Components
6. Гидратировать Client Components
```

При клиентской навигации фреймворк может запросить новый RSC Payload без полной HTML-страницы и использовать его для обновления существующего React-дерева.

Поэтому фраза «компонент выполнился на сервере» ещё не объясняет, идёт ли речь о RSC или SSR.

Server Component может импортировать и рендерить Client Component:

```tsx
import { Counter } from "./Counter";

export default function Page() {
  return (
    <>
      <h1>Товар</h1>
      <Counter />
    </>
  );
}
```

Props, передаваемые через серверно-клиентскую границу, должны поддерживать сериализацию React.

К поддерживаемым значениям относятся:

- строки, числа, `bigint`, boolean, `null` и `undefined`;
- глобальные символы, созданные через `Symbol.for`;
- обычные объекты;
- массивы;
- `Map` и `Set`;
- `Date`;
- `ArrayBuffer` и типизированные массивы;
- сериализуемые JSX-элементы;
- `Promise`;
- ссылки на Server Functions.

Нельзя передать:

- произвольную функцию;
- экземпляр пользовательского класса;
- объект с `null`-прототипом;
- локальный символ, созданный через `Symbol()`;
- значение, внутри которого находится неподдерживаемый объект.

Например, обычный callback передать нельзя:

```tsx
<ClientButton
  onClick={() => {
    console.log("click");
  }}
/>
```

Но можно передать специальную Server Function, которую React сериализует как ссылку.

Client Component не может напрямую импортировать модуль, который должен оставаться Server Component и использует серверные возможности:

```tsx
"use client";

import { ServerCart } from "./ServerCart";
```

Если обычный универсальный компонент без серверных зависимостей импортируется из клиентского графа, его конкретное использование становится клиентским, а исходный код попадает в клиентский бандл.

Поэтому отсутствие `"use client"` само по себе не гарантирует, что любой импорт компонента всегда будет выполняться на сервере.

Чтобы сохранить серверное выполнение, Server Component создают выше в серверном дереве и передают Client Component через `children` или другой prop:

```tsx
// Server Component
export default function Page() {
  return (
    <ClientModal>
      <ServerCart />
    </ClientModal>
  );
}
```

```tsx
"use client";

export function ClientModal({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div role="dialog">{children}</div>;
}
```

`ClientModal` не импортирует реализацию `ServerCart`. Он только определяет место, в котором React покажет уже подготовленное серверное содержимое.

Server Functions являются асинхронными функциями, выполняемыми на сервере и доступными клиентскому коду через интеграцию React-фреймворка.

Директива:

```tsx
"use server";
```

помечает отдельную асинхронную функцию:

```tsx
export default function Page() {
  async function createOrder() {
    "use server";

    await db.order.create({
      data: {},
    });
  }

  return <OrderButton action={createOrder} />;
}
```

Директиву также можно поставить в начале отдельного модуля:

```tsx
"use server";

export async function createOrder() {
  await db.order.create({
    data: {},
  });
}
```

Все экспортируемые асинхронные функции такого модуля становятся Server Functions.

Client Component может напрямую импортировать Server Function только из модуля с `"use server"` на верхнем уровне:

```tsx
"use client";

import { createOrder } from "./actions";

export function OrderButton() {
  return (
    <button onClick={() => createOrder()}>
      Создать заказ
    </button>
  );
}
```

Server Function, объявленную внутри Server Component, передают в Client Component через prop.

Директива `"use server"` не обозначает Server Component. Отдельной директивы `"use server component"` нет.

Server Components определяются положением в серверной части графа модулей.

Понятия Server Function и Server Action связаны, но не полностью равнозначны.

Server Function называют Server Action, когда она:

- передана в `action` или `formAction`;
- вызывается внутри React Action;
- участвует в мутации состояния через интеграцию фреймворка.

Не каждая Server Function обязательно используется как Server Action.

Вызов Server Function из браузера является сетевым запросом, а не прямым вызовом доверенного серверного кода:

```text
Client Component
→ сериализация аргументов
→ сетевой запрос
→ выполнение функции на сервере
→ сериализация результата
→ ответ клиенту
```

Аргументы и возвращаемое значение должны поддерживать сериализацию React.

Server Functions предназначены преимущественно для мутаций серверного состояния. Их не следует использовать как универсальную замену чтению данных через Server Components, API или клиентскую библиотеку запросов.

Фреймворк может выполнять вызовы Server Functions последовательно и не обязан кешировать их возвращаемые значения.

Любой аргумент Server Function считается пользовательским вводом.

Функция должна заново проверить:

- аутентификацию;
- право пользователя на конкретный объект;
- схему входных данных;
- допустимость изменения состояния;
- бизнес-ограничения.

Например:

```tsx
"use server";

export async function deleteOrder(orderId: string) {
  const session = await getSession();

  if (!session) {
    throw new Error("Unauthenticated");
  }

  const order = await db.order.findUnique({
    where: {
      id: orderId,
    },
  });

  if (order?.userId !== session.user.id) {
    throw new Error("Forbidden");
  }

  await db.order.delete({
    where: {
      id: orderId,
    },
  });
}
```

Не являются авторизацией:

- скрытое поле формы;
- недоступная кнопка;
- отсутствие ссылки в интерфейсе;
- факт импорта Server Function;
- идентификатор, ранее сформированный сервером.

Защита фреймворка от CSRF и проверка origin дополняют, но не заменяют аутентификацию, авторизацию и валидацию аргументов.

Серверная среда также не означает, что любое значение автоматически остаётся секретным. Данные, переданные в Client Component, возвращённые Server Function или попавшие в RSC Payload, могут стать доступны пользователю.

React 19 стабилизировал публичные возможности Server Components и Server Functions.

При этом низкоуровневые API, через которые сборщик или фреймворк реализует RSC-протокол, не следуют SemVer и могут изменяться между минорными версиями React 19.x.

Поэтому приложение обычно использует поддерживаемую версию Next.js или другого фреймворка, а не реализует собственный RSC-протокол без отдельной необходимости.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Server Component является просто SSR-компонентом?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

SSR создаёт HTML и может использовать результат как Server Components, так и Client Components для формирования первоначальной разметки.

RSC определяет:

- какие компоненты выполняются в серверной среде;
- какой код не должен попадать в клиентский бандл;
- какой сериализованный результат получит клиент;
- где в дереве находятся Client Components.

Механизмы часто работают вместе:

```text
Server Components
→ RSC Payload
→ SSR
→ HTML
```

Но их результаты и границы различаются.

При последующей клиентской навигации фреймворк также может получить новый RSC Payload без новой полной HTML-страницы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>"use client"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Директива объявляет точку входа в граф клиентских модулей.

Экспортированные компоненты могут использовать:

- состояние;
- эффекты;
- обработчики событий;
- браузерные API.

Их код и транзитивные клиентские зависимости войдут в бандл.

Директива определяет границу графа модулей, а не всего маршрута или визуального дерева.

Её не требуется указывать в каждом вложенном компоненте. Достаточно поставить `"use client"` в точке входа нужной интерактивной области.

Это не означает, что весь маршрут становится CSR. При первоначальной загрузке Client Component может участвовать в серверном создании HTML, а затем гидратироваться в браузере.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли <code>"use server"</code> компонент серверным?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Директива `"use server"` создаёт Server Function, которую фреймворк может вызвать из клиентского кода.

Она применяется:

- в начале тела отдельной асинхронной функции;
- либо в начале модуля для всех его экспортируемых асинхронных функций.

Server Components определяются серверной частью графа модулей без такой директивы.

Отдельной директивы:

```text
"use server component"
```

не существует.

Чтобы Server Function можно было напрямую импортировать в Client Component, `"use server"` должна находиться на уровне её модуля.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли передать функцию из Server Component в Client Component?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычную функцию-замыкание передать нельзя:

```tsx
<ClientButton
  onClick={() => console.log("click")}
/>
```

React не может сериализовать её код и окружение как обычный prop.

Функцию обратного вызова можно создать уже внутри Client Component.

Также можно передать специальную ссылку на Server Function:

```tsx
async function save() {
  "use server";

  // Изменение данных
}

return <ClientButton action={save} />;
```

React и фреймворк кодируют её не как обычную JavaScript-функцию, а как ссылку на серверную операцию.

Даже в этом случае вызов остаётся асинхронной сетевой операцией с обязательной серверной проверкой аргументов и прав доступа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли Client Component показать Server Component внутри себя?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если Server Component был создан выше в серверном дереве и передан как `children` или другой React prop:

```tsx
<ClientModal>
  <ServerCart />
</ClientModal>
```

Client Component не импортирует серверную реализацию. Он только определяет место для уже описанного серверного содержимого:

```tsx
"use client";

export function ClientModal({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div>{children}</div>;
}
```

Прямой импорт модуля, который должен остаться Server Component, из клиентского графа не поддерживается.

Если же импортированный компонент не использует серверные возможности и может выполняться в обеих средах, его использование внутри клиентского графа становится Client Component, а код попадает в клиентский бандл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Уменьшают ли Server Components клиентский бандл автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

Код Server Component и его чисто серверных зависимостей не отправляется в браузер.

Например, библиотека для обработки Markdown, импортированная только Server Component, может полностью остаться на сервере.

Но Server Components не уменьшают любой бандл автоматически.

Если тяжёлая библиотека импортируется из Client Component, она входит в клиентский граф:

```text
"use client"
→ компонент
→ его imports
→ транзитивные dependencies
→ клиентский bundle
```

Слишком высокая граница `"use client"` затягивает в клиентский код больше модулей.

Поэтому интерактивные области стараются держать как можно глубже и уже:

```text
Server Layout
├── Server Logo
├── Server Navigation
└── Client Search
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли доверять данным Server Function?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Аргументы Server Function пришли по сети и полностью контролируются клиентом:

```ts
deleteOrder(orderId);
```

Пользователь может заменить `orderId`, повторить запрос или вызвать функцию без предусмотренного интерфейса.

На каждом вызове проверяются:

- действительность сессии;
- право на конкретный ресурс;
- типы и схема данных;
- бизнес-ограничения;
- допустимость перехода состояния.

Скрытие кнопки защищает интерфейс, но не серверную операцию.

После изменения данных фреймворк также должен обновить или пометить устаревшим соответствующий кеш.

Механизмы same-origin и CSRF-защиты не заменяют проверку прав пользователя на конкретную операцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что может вызвать каскадную загрузку в Server Components?</strong></summary>

<dl>
<dd>
<h2></h2>

Каскадную загрузку создают последовательные `await`, когда следующий независимый запрос начинается только после завершения предыдущего:

```text
Запрос пользователя
→ запрос заказов
→ запрос товаров
```

Независимые операции запускают параллельно:

```tsx
const userPromise = getUser();
const ordersPromise = getOrders();

const [user, orders] = await Promise.all([
  userPromise,
  ordersPromise,
]);
```

Если дочерний запрос действительно зависит от результата родительского, последовательность является необходимой.

Границы Suspense позволяют не блокировать всю страницу и потоково раскрывать готовые части.

Кеширование и устранение одинаковых запросов зависят от фреймворка и его версии. Их нельзя предполагать для произвольного запроса без проверки конкретного API.

Server Functions также не следует использовать для первоначального чтения независимых данных: они предназначены преимущественно для мутаций и могут обрабатываться фреймворком последовательно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Выбор |
| --- | --- |
| Чтение данных без интерактивности | Server Component |
| `useState`, обработчик клика или браузерный API | Client Component |
| Первоначальный HTML | SSR поверх результата RSC-дерева и Client Components |
| Изменение данных из формы | Server Function с полной проверкой входа |
| Обычное чтение данных клиентом | API, Server Component или клиентская библиотека запросов |
| Тяжёлая серверная зависимость | Не пересекать границу `"use client"` |
| Интерактивная оболочка с серверным содержимым | Передать Server Component через `children` |
| Прямой импорт Server Function в Client Component | Отдельный модуль с `"use server"` |

## Связанные темы

- [17 SSR SSG и hydration в React](<./17 SSR SSG и hydration в React.md>)
- [19 Версии React 18 19 и 19.2](<./19 Версии React 18 19 и 19.2.md>)
- [27 Формы и actions в React 19](<./27 Формы и actions в React 19.md>)
- [03 Server и Client Components](<../Next.js/03 Server и Client Components.md>)
- [18 Проверка данных с backend](<../TypeScript/18 Проверка данных с backend.md>)

## Источники

- [React: Server Components](https://react.dev/reference/rsc/server-components)
- [React: Server Functions](https://react.dev/reference/rsc/server-functions)
- [React: `use client`](https://react.dev/reference/rsc/use-client)
- [React: `use server`](https://react.dev/reference/rsc/use-server)
- [React 19: React Server Components](https://react.dev/blog/2024/12/05/react-19)
- [Next.js: Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components)
- [Next.js 14: Server Components](https://nextjs.org/docs/14/app/building-your-application/rendering/server-components)
- [Next.js 14: Client Components](https://nextjs.org/docs/14/app/building-your-application/rendering/client-components)
- [Next.js 14: Composition Patterns](https://nextjs.org/docs/14/app/building-your-application/rendering/composition-patterns)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 17 SSR SSG и hydration в React](<./17 SSR SSG и hydration в React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [19 Версии React 18 19 и 19.2 →](<./19 Версии React 18 19 и 19.2.md>)
<!-- CARD-NAV-BOTTOM:END -->
