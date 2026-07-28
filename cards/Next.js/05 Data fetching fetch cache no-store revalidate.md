# Data fetching fetch cache no-store revalidate

<!-- CARD-NAV-TOP:START -->
[← 04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Кэширование Data Cache Full Route Cache Router Cache →](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как в Next.js 14 загружают данные через `fetch`? Что делают `force-cache`, `no-store`, `revalidate` и как обновлять кэш по меткам и путям?**

<h2></h2>

<br>
<dl>
<dd>

В App Router Server Component может быть `async` и получать данные непосредственно перед рендерингом. Next.js 14 расширяет серверный `fetch`: кроме обычного HTTP-запроса он управляет Data Cache, то есть серверным кэшем данных, и позволяет задать срок и способ обновления результата.

В Next.js 14 `fetch` без явной настройки обычно использует `force-cache` и сохраняет ответ в Data Cache. Исключение возникает в динамическом контексте, например после использования `cookies()`, где значение по умолчанию становится `no-store`. Чтобы код не зависел от неочевидной эвристики, важные запросы лучше настраивать явно.

`cache: "force-cache"` разрешает переиспользовать ответ между серверными запросами. `cache: "no-store"` каждый раз обращается к источнику данных и не помещает ответ в Data Cache. Некэшированный `fetch` также делает маршрут динамическим и исключает его из Full Route Cache, но другие явно кэшируемые запросы того же маршрута могут остаться в Data Cache.

`next: { revalidate: 60 }` кэширует данные и разрешает обновлять их не чаще одного раза в 60 секунд. В Next.js 14 первый запрос после истечения интервала получает прежнее значение и запускает обновление в фоне. При нескольких `fetch` одного статического маршрута наименьший интервал определяет период revalidation всего маршрута.

Для событийного обновления запросу назначают tags, то есть метки:

```ts
await fetch("https://api.example.com/posts", {
  next: { tags: ["posts"] },
});
```

После изменения данных `revalidateTag("posts")` обновляет связанные записи, а `revalidatePath("/posts")` обновляет данные и результат рендеринга для указанного пути. Tag описывает группу данных и удобен, когда один ресурс используется в разных маршрутах. Path удобен, когда известен конкретный участок интерфейса.

React отдельно выполняет Request Memoization, или мемоизацию запроса: одинаковые GET-вызовы `fetch` с одинаковыми URL и настройками внутри одного прохода рендеринга выполняются один раз. Это не постоянный кэш и не переживает запрос. Мемоизация действует в React-дереве, включая pages, layouts, `generateMetadata` и `generateStaticParams`, но не относится к Route Handlers.

Если данные читаются через ORM или клиент базы данных без `fetch`, React `cache` может устранить повтор функции в одном серверном рендеринге. Для постоянного кэша между запросами в Next.js 14 использовали `unstable_cache`. Эти механизмы решают разные задачи: мемоизация сокращает повторы внутри одного рендеринга, а Data Cache переиспользует данные между запросами.

Server Component не нужно заставлять обращаться к собственному Route Handler по HTTP. Он уже находится на сервере и может напрямую вызвать функцию доступа к данным. Внутренний HTTP добавляет сетевой переход, усложняет передачу авторизации и во время сборки может обращаться к ещё не запущенному серверу.

Начиная с Next.js 15 серверный `fetch` больше не кэшируется по умолчанию. Поэтому ответ о значениях по умолчанию должен начинаться с версии: для Next.js 14 базовая модель кэширует, для 15/16 кэш включают явно или используют новую модель соответствующей версии.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>force-cache</code> отличается от <code>no-store</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`force-cache` сначала ищет ответ в серверном Data Cache и сохраняет результат при отсутствии записи. `no-store` всегда обращается к источнику и не записывает ответ в этот кэш. Это не те же настройки, что HTTP-кэш браузера: в серверном `fetch` Next.js они управляют Data Cache.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>revalidate: 60</code> отличается от <code>no-store</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`revalidate: 60` переиспользует кэш и допускает устаревание до заданного интервала, после чего обновляет его в фоне. `no-store` выполняет запрос при каждом рендеринге. Первый вариант уменьшает нагрузку и задержку, второй нужен для строго персональных или постоянно меняющихся данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>revalidateTag</code> отличается от <code>revalidatePath</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Tag связывается с данными и может обновить их во всех маршрутах, которые использовали эту метку. Path адресует конкретную страницу или layout. После изменения поста tag `posts` удобен для списка, главной страницы и боковой панели, а path подходит для обновления одного известного маршрута.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Являются ли Data Cache и мемоизация запросов (Request Memoization) одним механизмом?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Data Cache находится на серверной стороне Next.js и может переживать много запросов и развёртываний, если это поддерживает платформа. Request Memoization принадлежит React, действует только во время рендеринга одного дерева и затем очищается. Один вызов `fetch` может одновременно получить значение из Data Cache и быть мемоизирован внутри текущего рендеринга.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему два одинаковых запроса иногда всё равно выполняются дважды?</strong></summary>

<dl>
<dd>
<h2></h2>

Мемоизация учитывает URL и настройки, относится только к GET и работает внутри React-дерева компонентов. Разные headers, body или настройки дают другой запрос. Route Handler не входит в React-дерево, а переданный `AbortSignal` отключает автоматическую мемоизацию такого `fetch`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли <code>cookies()</code> все данные некэшируемыми?</strong></summary>

<dl>
<dd>
<h2></h2>

Он делает маршрут динамическим, потому что рендеринг зависит от конкретного запроса. Но это не запрещает явно кэшировать общие данные в Data Cache. Например, персональный header может зависеть от cookie, а общий каталог использовать отдельный `fetch` с `force-cache`. Нельзя помещать пользовательский ответ под общий ключ кэша.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли проверять <code>response.ok</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. `fetch` отклоняет Promise при сетевой ошибке, но ответ 404 или 500 сам по себе является успешным завершением HTTP-запроса. Код должен проверить status или `ok`, преобразовать ожидаемую ошибку либо выбросить исключение, которое обработает ближайший `error.tsx`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что изменилось в Next.js 15?</strong></summary>

<dl>
<dd>
<h2></h2>

`fetch` перестал кэшироваться по умолчанию. Для отдельного запроса указывают `cache: "force-cache"`, а значение по умолчанию для сегмента можно изменить через `fetchCache = "default-cache"`. Поэтому перенос кода с 14 на 15 может увеличить число запросов, если прежний кэш подразумевался неявно.

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

- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [01 Виды состояния во frontend](<../State Management/01 Виды состояния во frontend.md>)

## Источники

- [Next.js 14 docs: Fetching, Caching, and Revalidating](https://nextjs.org/docs/14/app/building-your-application/data-fetching/fetching-caching-and-revalidating)
- [Next.js 14 docs: fetch](https://nextjs.org/docs/14/app/api-reference/functions/fetch)
- [Next.js 14 docs: Caching](https://nextjs.org/docs/14/app/building-your-application/caching)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Кэширование Data Cache Full Route Cache Router Cache →](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>)
<!-- CARD-NAV-BOTTOM:END -->
