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

Server Action представляет собой асинхронную серверную функцию, которую можно вызвать из React-компонента без самостоятельного Route Handler. В Next.js 14 эта возможность стала стабильной. Функция выполняется только на сервере, поэтому внутри неё можно обращаться к базе данных, закрытым переменным окружения и внутренним сервисам.

Server Action помечают директивой `"use server"`. Её можно поставить первой строкой отдельного файла, чтобы экспортировать несколько Server Actions, либо внутри Server Component перед конкретной функцией:

```ts
// app/posts/actions.ts
"use server";

import { revalidateTag } from "next/cache";

export async function createPost(formData: FormData) {
  const title = String(formData.get("title") ?? "").trim();

  if (!title) {
    return { error: "Введите заголовок" };
  }

  await postsRepository.create({ title });
  revalidateTag("posts");

  return { success: true };
}
```

В форме action передают в атрибут `action`. Браузер собирает поля формы в `FormData`, то есть в стандартный объект с парами имя-значение, и Next.js вызывает серверную функцию:

```tsx
import { createPost } from "./actions";

export function PostForm() {
  return (
    <form action={createPost}>
      <input name="title" />
      <button type="submit">Создать</button>
    </form>
  );
}
```

Форма в Server Component поддерживает progressive enhancement, то есть базовая отправка может сработать ещё до загрузки клиентского JavaScript. Если Server Action передана из Client Component, Next.js ставит отправку в очередь до завершения гидратации.

В Next.js 14 состояние результата удобно связывать с формой через `useFormState` из `react-dom`, а состояние отправки читать через `useFormStatus`. `useFormStatus` должен вызываться в дочернем компоненте формы. В Next.js 15 с React 19 `useFormState` заменён на `useActionState`, поэтому название API зависит от версии проекта.

После mutation, то есть операции изменения данных, интерфейс не всегда обновится сам. `revalidateTag("posts")` помечает устаревшими все записи Data Cache с tag `posts`. `revalidatePath("/posts")` обновляет данные и результат рендеринга для конкретного пути. После этого Next.js может вернуть обновлённый RSC Payload в том же ответе Server Action и согласовать серверное дерево с открытой страницей.

Server Action нельзя считать защищённой только потому, что она не видна как обычный REST endpoint. Клиент получает ссылку, по которой функцию можно вызвать отдельно. Поэтому каждая Server Action должна заново проверить сессию, права пользователя и входные данные. Проверка показа кнопки в интерфейсе не заменяет серверную авторизацию.

Аргументы и возвращаемое значение передаются через сетевую границу и должны поддерживать сериализацию React. Сложные экземпляры классов, соединение с базой данных или функции передавать нельзя. Закрытые значения следует читать внутри Server Action, а не принимать от клиента.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Server Action отличается от Route Handler?</strong></summary>

<dl>
<dd>
<h2></h2>

Server Action тесно связана с React и удобна для изменения данных из формы или компонента. Next.js сам кодирует вызов, возвращает результат и может совместить обновлённый RSC Payload с текущей страницей. Route Handler создаёт обычный HTTP endpoint с явными HTTP-методом, headers и status. Он нужен для внешних клиентов, webhook, публичного API или протокола, который не связан с React-интерфейсом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему проверку авторизации нужно выполнять внутри каждой action?</strong></summary>

<dl>
<dd>
<h2></h2>

Server Action является серверной точкой входа, которую клиент способен вызвать повторно или с изменёнными аргументами. Скрытая кнопка и проверка в layout управляют только интерфейсом. Функция должна получить текущую сессию, проверить разрешение на конкретную операцию и лишь затем изменять данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем валидация отличается от авторизации?</strong></summary>

<dl>
<dd>
<h2></h2>

Валидация проверяет форму и допустимость данных, например обязательность заголовка и длину строки. Авторизация отвечает на другой вопрос: имеет ли текущий пользователь право создавать или редактировать этот ресурс. Для безопасного изменения данных нужны обе проверки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>revalidateTag</code> отличается от <code>revalidatePath</code> после mutation?</strong></summary>

<dl>
<dd>
<h2></h2>

Tag относится к данным и может обновить все страницы, которые используют одну группу данных. Path относится к конкретному участку маршрутов. Если пост отображается в списке, профиле автора и на главной, tag обычно точнее. Если изменился только один известный экран, можно обновить конкретный path.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда после action использовать <code>redirect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`redirect` подходит, если после успешной операции пользователь должен перейти на другой маршрут, например со страницы создания на страницу записи. Функция `redirect` прерывает выполнение через специальное исключение Next.js, поэтому её вызывают вне `try/catch` либо не перехватывают это исключение. Revalidation обычно выполняют до перенаправления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как показать состояние отправки формы?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 14 дочерний Client Component вызывает hook `useFormStatus` и читает `pending`. Кнопку можно временно отключить и изменить подпись. Hook получает состояние ближайшей родительской формы, поэтому вызов в том же компоненте, который только создаёт `<form>`, не увидит её отправку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли вызвать Server Action не из <code>&lt;form&gt;</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. Server Action можно вызвать из обработчика события, передать в `formAction` отдельной кнопки или запускать через `startTransition`. Но progressive enhancement без JavaScript относится прежде всего к форме. Для произвольного клиентского вызова нужно отдельно продумать состояние выполнения и обработку ошибок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать двойного изменения данных при повторном клике или сетевом повторе?</strong></summary>

<dl>
<dd>
<h2></h2>

Отключение кнопки уменьшает вероятность повторной отправки, но не является серверной гарантией. Для критической операции используют idempotency key, то есть уникальный идентификатор операции, ограничение уникальности в базе данных или транзакцию. Повторный запрос с тем же idempotency key возвращает прежний результат, а не создаёт второй ресурс.

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
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Route Handlers Middleware Edge и Node runtime →](<./08 Route Handlers Middleware Edge и Node runtime.md>)
<!-- CARD-NAV-BOTTOM:END -->
