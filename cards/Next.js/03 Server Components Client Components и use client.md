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

Server Components выполняются только на сервере во время сборки или обработки запроса. В App Router это тип компонентов по умолчанию. Они могут напрямую читать базу данных, файловую систему и секретные environment variables, то есть переменные окружения, а их реализация не попадает в клиентский бандл. В них нельзя использовать `useState`, `useEffect`, обработчики DOM-событий и API браузера.

Client Components нужны для состояния, эффектов, событий, API браузера и клиентских подписок. Название не означает, что при первом открытии они вообще не рендерятся на сервере. Next.js формирует для них начальный HTML, затем браузер загружает JavaScript и гидратирует этот HTML. При последующих переходах Client Components обновляются на клиенте с использованием нового RSC Payload.

Директива `"use client"` задаёт границу модулей. Её ставят во входном файле, который импортируется из Server Component. Сам файл и все модули, импортированные из него, становятся частью клиентского графа зависимостей. Директива не нужна в каждом дочернем файле.

Границу располагают как можно ниже. Если вся page помечена `"use client"` ради одной кнопки, в клиентский бандл может попасть лишний код. Обычно Server Component получает данные и рендерит небольшой интерактивный Client Component.

Server Component может импортировать Client Component и передавать ему сериализуемые props, то есть свойства. Функцию, экземпляр класса, соединение с базой или secret передать через эту границу нельзя. Server Action является специальной серверной ссылкой и поддерживается React отдельно.

Client Component не импортирует Server Component как обычную зависимость. Но Server Component может заранее сформировать серверное содержимое и передать его в Client Component через `children` или другое React-свойство. Так серверный код остаётся на сервере, хотя визуально находится внутри клиентской оболочки.

`"use server"` не помечает Server Component. Она объявляет Server Action или модуль с серверными actions. Для защиты от случайного импорта серверного модуля в клиентский код используют пакет `server-only`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Выполняется ли Client Component на сервере?</strong></summary>

<dl>
<dd>
<h2></h2>

При первом полном открытии Next.js использует его инструкции для формирования начального HTML на сервере. Но состояние, эффекты и события начинают работать только после загрузки JavaScript и гидратации в браузере. При последующей клиентской навигации его интерфейс обновляется на клиенте без нового полного HTML-документа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в Server Component нельзя использовать <code>useState</code> и <code>onClick</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Server Component не сохраняет интерактивный экземпляр в браузере и его код не загружается туда. `useState` требует клиентского жизненного цикла, а `onClick` требует DOM listener, то есть обработчик DOM-события. Интерактивный участок нужно вынести за границу `"use client"`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>"use client"</code> влияет на bundle?</strong></summary>

<dl>
<dd>
<h2></h2>

Все статические imports из клиентского входного файла становятся кандидатами на включение в клиентские chunks, то есть части бандла. Чем выше граница и чем больше зависимостей под ней, тем больше JavaScript нужно скачать, разобрать и выполнить. Server Components, переданные через композицию, не включаются в этот граф.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему props из Server Component должны сериализоваться?</strong></summary>

<dl>
<dd>
<h2></h2>

React передаёт их через сетевую границу в RSC Payload. Обычные данные можно закодировать, а замыкание, DOM-узел или подключение к базе не имеет переносимого представления для браузера. Поддерживаемые типы определяет протокол React, а Server Actions передаются как специальные ссылки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли передать Server Component внутрь Client Component?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если Server Component создаёт дерево выше и передаёт готовый React-узел через `children` или prop. Client Component получает ссылку на место в RSC Payload, а не импортирует серверную реализацию. Это позволяет сочетать интерактивную оболочку с серверным содержимым.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где размещать Context Provider?</strong></summary>

<dl>
<dd>
<h2></h2>

React Context не поддерживается внутри Server Components как источник клиентского состояния, поэтому Provider делают Client Component. Его оборачивают вокруг минимальной нужной части дерева. Сам Server Component может рендерить этот Provider и передавать ему server-rendered children.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как не допустить попадания серверного кода в клиентский бандл?</strong></summary>

<dl>
<dd>
<h2></h2>

Секреты и доступ к данным держат в отдельных server modules, добавляют `import "server-only"` и не импортируют их из client entry. Переменные без `NEXT_PUBLIC_` Next.js не раскрывает клиенту, но архитектурная граница всё равно должна быть явной.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Тип компонента |
| --- | --- |
| Получить данные напрямую из базы данных или CMS | Server Component |
| Использовать `onClick` или `useState` | Client Component |
| Показать серверные данные внутри интерактивной модалки | Server Component внутри Client Component |
| Подключить Theme Provider | Client Component |
| Скрыть секрет и server SDK | Server module с `server-only` |

## Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [18 Server Components и Server Actions](<../React/18 Server Components и Server Actions.md>)

## Источники

- [Next.js 14 docs: Server Components](https://nextjs.org/docs/14/app/building-your-application/rendering/server-components)
- [Next.js 14 docs: Client Components](https://nextjs.org/docs/14/app/building-your-application/rendering/client-components)
- [Next.js 14 docs: Composition Patterns](https://nextjs.org/docs/14/app/building-your-application/rendering/composition-patterns)
- [React docs: Server Components](https://react.dev/reference/rsc/server-components)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 SSR SSG ISR Streaming и hydration →](<./04 SSR SSG ISR Streaming и hydration.md>)
<!-- CARD-NAV-BOTTOM:END -->
