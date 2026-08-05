# Server Actions forms mutations revalidatePath revalidateTag

<!-- CARD-NAV-TOP:START -->
[← 06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Route Handlers Middleware Edge и Node runtime →](<./08 Route Handlers Middleware Edge и Node runtime.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Server Actions в Next.js 14? Как через них отправлять формы, изменять данные и обновлять кэш?**

<h2></h2>

<br>
<dl>
<dd>

Server Action — асинхронная серверная функция, которую можно вызвать из React-компонента без самостоятельного Route Handler.

В Next.js 14 Server Actions стали стабильной возможностью.

В современной терминологии React такая функция называется Server Function. Когда она используется как action для изменения серверного состояния, её называют Server Action.

Server Actions предназначены прежде всего для mutations:

- создания данных;
- редактирования;
- удаления;
- отправки формы;
- изменения cookies;
- обновления серверного кэша.

Для обычного чтения данных предпочтительнее Server Components, `fetch` или функция data access layer.

Server Action выполняется только на сервере, поэтому внутри неё можно обращаться:

- к базе данных;
- к закрытым environment variables;
- к внутренним сервисам;
- к server-only SDK.

При этом action наследует runtime страницы или layout, где она используется.

Например, доступ к Node.js API, файловой системе или конкретному database driver возможен только в совместимой среде выполнения.

Server Action помечают директивой:

```ts
"use server";
```

Её можно поставить первой строкой отдельного файла:

```ts
// app/posts/actions.ts
"use server";

import { revalidateTag } from "next/cache";

export async function createPost(formData: FormData) {
  const title = String(
    formData.get("title") ?? "",
  ).trim();

  if (!title) {
    return {
      error: "Введите заголовок",
    };
  }

  await postsRepository.create({
    title,
  });

  revalidateTag("posts");

  return {
    success: true,
  };
}
```

В модуле с верхнеуровневой директивой экспортируемые Server Actions должны быть асинхронными функциями. Несвязанные константы и обычные утилиты лучше хранить в другом модуле.

Inline Server Action можно определить непосредственно внутри Server Component:

```tsx
export default function Page() {
  async function createPost(formData: FormData) {
    "use server";

    // Mutation
  }

  return (
    <form action={createPost}>
      {/* Поля */}
    </form>
  );
}
```

Client Component не может объявить inline Server Action внутри себя.

Он может:

- импортировать action из отдельного модуля с `"use server"`;
- получить Server Action через props от Server Component.

В форме action передают в атрибут `action`.

Браузер собирает поля с `name` в стандартный объект `FormData`, а Next.js вызывает серверную функцию через `POST`:

```tsx
import { createPost } from "./actions";

export function PostForm() {
  return (
    <form action={createPost}>
      <input
        name="title"
        required
      />

      <button type="submit">
        Создать
      </button>
    </form>
  );
}
```

При вызове из обычной формы action автоматически получает `FormData` первым аргументом:

```ts
export async function createPost(
  formData: FormData,
) {
  "use server";

  const title = formData.get("title");
}
```

Форма, объявленная в Server Component, поддерживает progressive enhancement.

Она может отправиться:

- до загрузки клиентского JavaScript;
- при полностью отключённом JavaScript.

Если форма находится в Client Component и вызывает импортированную Server Action, Next.js ставит отправку в очередь, пока загружается JavaScript и выполняется hydration.

После hydration отправка выполняется без полной перезагрузки документа.

В Next.js 14 результат action можно связать с интерфейсом через:

```ts
useFormState
```

из `react-dom`.

Важно: после оборачивания через `useFormState` сигнатура action меняется.

Первым аргументом становится предыдущее состояние, а `FormData` передаётся вторым:

```ts
type FormState = {
  error?: string;
  success?: boolean;
};

export async function createPost(
  previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  "use server";

  const title = String(
    formData.get("title") ?? "",
  ).trim();

  if (!title) {
    return {
      error: "Введите заголовок",
    };
  }

  await postsRepository.create({
    title,
  });

  revalidateTag("posts");

  return {
    success: true,
  };
}
```

Состояние отправки читают через:

```ts
useFormStatus
```

Этот hook должен вызываться в Client Component, расположенном внутри соответствующей `<form>`.

В Next.js 15 с React 19 `useFormState` был заменён рекомендуемым API:

```ts
useActionState
```

Поэтому название hook зависит от версии проекта.

После mutation сохранённый серверный интерфейс не всегда обновляется автоматически.

Для инвалидации данных по метке используют:

```ts
revalidateTag("posts");
```

Запрос должен заранее получить такую метку:

```ts
await fetch("https://api.example.com/posts", {
  next: {
    tags: ["posts"],
  },
});
```

`revalidateTag("posts")` инвалидирует связанные записи Data Cache во всех маршрутах, которые использовали эту метку.

Для конкретного маршрута используют:

```ts
revalidatePath("/posts");
```

`revalidatePath` инвалидирует кэш данных и сохранённый результат рендеринга для указанной page или layout.

Различие:

```text
revalidateTag
→ группа данных независимо от маршрута

revalidatePath
→ конкретная часть route tree
```

В Next.js 14 revalidation не означает немедленную загрузку свежих данных для всех возможных страниц.

Актуальный результат строится, когда затронутый путь снова рендерится.

Если Server Action изменяет данные текущего интерфейса, Next.js может в одном серверном ответе вернуть:

- результат action;
- обновлённый RSC Payload;
- новое серверное дерево.

Браузер согласует его с открытой страницей без полной перезагрузки документа.

Ожидаемые ошибки, например ошибки валидации, обычно возвращают как сериализуемое состояние:

```ts
return {
  error: "Введите заголовок",
};
```

Неожиданную ошибку можно выбросить:

```ts
throw new Error(
  "Failed to create post",
);
```

Тогда её обработает ближайшая подходящая граница `error.tsx`.

Server Action нельзя считать защищённой только потому, что она не выглядит как обычный REST endpoint.

Клиент получает ссылку, через которую action вызывается сетевым `POST`-запросом. Её можно вызвать повторно или передать изменённые аргументы.

Поэтому каждая Server Action должна самостоятельно проверить:

- входные данные;
- текущую сессию;
- authentication;
- authorization;
- принадлежность изменяемого ресурса;
- допустимость операции.

Проверка показа кнопки или защита layout управляют интерфейсом, но не заменяют серверную авторизацию.

Next.js использует дополнительные механизмы защиты, включая проверку origin запроса, но они не определяют, имеет ли конкретный пользователь право изменять конкретный ресурс.

Аргументы и возвращаемое значение Server Action передаются через сетевую границу и должны поддерживать сериализацию React.

Поддерживаются, например:

- строки, числа и boolean;
- `null` и `undefined`;
- массивы;
- plain objects;
- `FormData`;
- `Date`;
- `Map`;
- `Set`;
- некоторые другие встроенные типы;
- Server Functions.

Нельзя передавать:

- обычное замыкание;
- DOM-узел;
- соединение с базой данных;
- экземпляр произвольного класса;
- обычную клиентскую или серверную функцию.

Server Function является специальным поддерживаемым исключением среди функций.

Сериализуемость не означает безопасность.

Закрытые значения нужно читать внутри Server Action:

```ts
const secret = process.env.INTERNAL_API_KEY;
```

а не принимать от клиента или возвращать в интерфейс.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Server Action отличается от Route Handler?</strong></summary>

<dl>
<dd>
<h2></h2>

Server Action тесно связана с React и предназначена прежде всего для mutations из формы или компонента.

Next.js самостоятельно:

- кодирует сетевой вызов;
- вызывает функцию через `POST`;
- сериализует аргументы и результат;
- интегрирует action с revalidation;
- может вернуть обновлённый RSC Payload вместе с результатом.

Route Handler создаёт обычный HTTP endpoint:

```ts
export async function POST(
  request: Request,
) {
  // ...
}
```

Разработчик явно управляет:

- HTTP-методом;
- URL;
- headers;
- status code;
- форматом request и response.

Server Action подходит, когда операция является внутренней частью React-приложения.

Route Handler нужен для:

- webhook;
- callback внешней авторизации;
- мобильного приложения;
- публичного или документированного API;
- внешней системы;
- клиента, не связанного с React.

Server Action не следует использовать как замену стабильному публичному HTTP-контракту.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему проверку авторизации нужно выполнять внутри каждой action?</strong></summary>

<dl>
<dd>
<h2></h2>

Server Action является серверной точкой входа.

Клиент способен:

- вызвать её повторно;
- изменить аргументы;
- подставить другой идентификатор;
- отправить запрос не через отображаемую кнопку.

Скрытая кнопка и проверка в layout управляют только интерфейсом.

Action должна получить текущую сессию и проверить разрешение на конкретную операцию:

```ts
"use server";

export async function deletePost(
  postId: string,
) {
  const session = await getSession();

  if (!session) {
    throw new Error(
      "Authentication required",
    );
  }

  const post = await postsRepository.getById(
    postId,
  );

  if (post.authorId !== session.user.id) {
    throw new Error(
      "Operation is not allowed",
    );
  }

  await postsRepository.delete(postId);
}
```

Нельзя доверять `userId`, role или разрешению, переданному из Client Component.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем валидация отличается от авторизации?</strong></summary>

<dl>
<dd>
<h2></h2>

Валидация проверяет корректность входных данных:

- заполнено ли обязательное поле;
- подходит ли длина;
- имеет ли значение ожидаемый формат;
- существует ли связанная сущность.

Авторизация отвечает на другой вопрос:

```text
Имеет ли текущий пользователь право выполнить эту операцию?
```

Например, корректный `postId` может указывать на реально существующий пост, но пользователь не обязательно имеет право его редактировать.

Для безопасной mutation нужны:

1. authentication;
2. authorization;
3. валидация;
4. выполнение изменения;
5. инвалидация кэша.

Клиентская валидация улучшает UX, но серверная проверка остаётся обязательной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>revalidateTag</code> отличается от <code>revalidatePath</code> после mutation?</strong></summary>

<dl>
<dd>
<h2></h2>

Tag относится к данным.

Например, данные постов могут использоваться:

- в `/posts`;
- на главной странице;
- в профиле автора;
- в боковой панели.

Если все запросы имеют метку:

```ts
next: {
  tags: ["posts"],
}
```

то вызов:

```ts
revalidateTag("posts");
```

инвалидирует всю эту группу данных.

Path относится к конкретной части маршрутов:

```ts
revalidatePath("/posts");
```

Он подходит, когда нужно обновить известную page или layout.

В Next.js 14 обе функции прежде всего инвалидируют кэш. Они не обязаны немедленно выполнять запросы для всех связанных URL.

Свежий результат формируется при следующем серверном рендеринге соответствующего пути.

Tag обычно точнее описывает предметные данные, а path — конкретный участок интерфейса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда после action использовать <code>redirect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`redirect` подходит, если после успешной операции пользователь должен перейти на другой маршрут.

Например, после создания записи:

```ts
"use server";

import { revalidateTag } from "next/cache";
import { redirect } from "next/navigation";

export async function createPost(
  formData: FormData,
) {
  let postId: string;

  try {
    const post = await postsRepository.create({
      title: String(
        formData.get("title") ?? "",
      ),
    });

    postId = post.id;
  } catch {
    return {
      error: "Не удалось создать пост",
    };
  }

  revalidateTag("posts");
  redirect(`/posts/${postId}`);
}
```

Сначала выполняют:

1. mutation;
2. revalidation;
3. redirect.

`redirect()` прерывает выполнение через специальное исключение Next.js. Поэтому его вызывают вне перехватывающего `try/catch`.

В Server Action он формирует ответ:

```text
303 See Other
```

Это переводит браузер с результата `POST` на новый маршрут через `GET`.

Код после `redirect()` не выполняется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как показать состояние отправки формы?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 14 дочерний Client Component вызывает:

```ts
useFormStatus
```

из `react-dom`:

```tsx
"use client";

import { useFormStatus } from "react-dom";

export function SubmitButton() {
  const {
    pending,
  } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
    >
      {pending
        ? "Сохранение..."
        : "Сохранить"}
    </button>
  );
}
```

Компонент размещают внутри формы:

```tsx
<form action={createPost}>
  <input name="title" />
  <SubmitButton />
</form>
```

`useFormStatus` читает состояние ближайшей родительской `<form>`.

Если вызвать hook в том же компоненте, который только создаёт эту форму, он не увидит её отправку, потому что компонент не является её потомком.

Отключение кнопки уменьшает вероятность повторного клика, но не является серверной гарантией от повторного выполнения mutation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли вызвать Server Action не из <code>&lt;form&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

Server Action можно:

- вызвать из event handler;
- передать в `formAction` отдельной кнопки;
- вызвать внутри `startTransition`;
- использовать из стороннего клиентского компонента;
- при необходимости вызвать из `useEffect`.

Например:

```tsx
"use client";

import {
  useTransition,
} from "react";

import {
  toggleLike,
} from "./actions";

export function LikeButton() {
  const [
    isPending,
    startTransition,
  ] = useTransition();

  function handleClick() {
    startTransition(async () => {
      await toggleLike();
    });
  }

  return (
    <button
      onClick={handleClick}
      disabled={isPending}
    >
      {isPending
        ? "Сохранение..."
        : "Нравится"}
    </button>
  );
}
```

Формы автоматически вызывают action внутри transition.

При произвольном вызове `startTransition` позволяет связать операцию с pending- и optimistic-состояниями.

Progressive enhancement без клиентского JavaScript относится прежде всего к форме в Server Component.

Вызовы из `useEffect` используют осторожно: повторный mount, изменение зависимостей или Strict Mode могут вызвать mutation больше одного раза.

Server Action не предназначена для обычного чтения данных при каждом render.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать двойного изменения данных при повторном клике или сетевом повторе?</strong></summary>

<dl>
<dd>
<h2></h2>

Отключение кнопки уменьшает вероятность повторной отправки через конкретный интерфейс:

```tsx
<button disabled={pending}>
  Оплатить
</button>
```

Но это не является серверной гарантией.

Запрос может повториться из-за:

- двойного клика до обновления интерфейса;
- сетевого retry;
- повторного вызова action;
- нескольких вкладок;
- повторной отправки после ошибки клиента.

Для критической операции используют серверную идемпотентность:

- idempotency key;
- уникальное ограничение базы данных;
- проверку текущего состояния сущности;
- транзакцию;
- запись уже обработанных операций.

Например:

```text
первый запрос с operationId
→ создаёт платёж

повторный запрос с тем же operationId
→ возвращает результат первого запроса
```

Клиентское состояние `pending` улучшает UX, а серверная идемпотентность обеспечивает корректность данных.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Подход |
| --- | --- |
| Простая форма внутри приложения | Server Action в `action` формы |
| Ошибки полей | Возвращаемое состояние и `useFormState` в Next.js 14 |
| Индикатор отправки | `useFormStatus` в дочерней кнопке |
| Обновление нескольких представлений ресурса | `revalidateTag` |
| Переход после создания | Обновление кэша, затем `redirect` |
| Webhook или API для мобильного клиента | Route Handler |

## Связанные темы

- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>)
- [08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>)
- [06 Submit lifecycle server errors reset defaultValues](<../Forms/06 Submit lifecycle server errors reset defaultValues.md>)

## Источники

- [Next.js 14 docs: Server Actions and Mutations](https://nextjs.org/docs/14/app/building-your-application/data-fetching/server-actions-and-mutations)
- [Next.js 14 docs: Data Security](https://nextjs.org/docs/14/app/building-your-application/data-fetching/server-actions-and-mutations#security)
- [Next.js 14 docs: revalidatePath](https://nextjs.org/docs/14/app/api-reference/functions/revalidatePath)
- [Next.js 14 docs: revalidateTag](https://nextjs.org/docs/14/app/api-reference/functions/revalidateTag)
- [Next.js 14 docs: Redirecting](https://nextjs.org/docs/14/app/building-your-application/routing/redirecting)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)
- [React docs: use server](https://react.dev/reference/rsc/use-server)
- [React docs: Server Functions](https://react.dev/reference/rsc/server-functions)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Route Handlers Middleware Edge и Node runtime →](<./08 Route Handlers Middleware Edge и Node runtime.md>)
<!-- CARD-NAV-BOTTOM:END -->
