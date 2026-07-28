# Factory Singleton lifecycle

<!-- CARD-NAV-TOP:START -->
[← 05 Compound Components и Headless UI](<./05 Compound Components и Headless UI.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Decorator Proxy Mixin Mediator Flyweight →](<./07 Decorator Proxy Mixin Mediator Flyweight.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Factory и Singleton? Где они встречаются во frontend и почему для Singleton важен lifecycle?**

<h2></h2>

<br>
<dl>
<dd>

Factory, или фабрика, инкапсулирует создание значения. Клиент сообщает необходимые параметры, а Factory решает, какой объект создать, как его настроить и какие зависимости передать. Во frontend Factory часто является обычной функцией: `createApiClient(config)`, `createStore(preloadedState)` или `createTestUser(overrides)`.

Factory полезна, когда создание сложнее прямого литерала или `new`: есть несколько реализаций, значения по умолчанию, конфигурация окружения, зависимости для теста или отдельный экземпляр на каждый запрос. Она не обязана выбирать разные классы; сокрытие сложной сборки одного типа тоже является её задачей.

Singleton, или одиночка, гарантирует один общий instance, то есть экземпляр, в определённом scope. Scope здесь означает границу, внутри которой экземпляр считается единственным. В браузерном приложении это может быть одна загруженная копия модуля во вкладке; на SSR-сервере один экземпляр уровня модуля может обслуживать множество запросов. Поэтому фраза «Singleton один на всё приложение» недостаточно точна.

К Singleton-подобным объектам относятся клиент аналитики, store, Query Client и registry, то есть реестр общих объектов. Общий экземпляр удобен, но создаёт глобальное изменяемое состояние и скрытые зависимости. Если он хранит пользовательские данные на сервере, состояние одного запроса может попасть в другой. Если объект не очищается между тестами или после logout, следующий сценарий получает старые данные.

Lifecycle, или жизненный цикл, описывает, когда экземпляр создаётся, кто им владеет, сколько он живёт и когда очищается. Для браузерной аналитики это может быть жизнь вкладки, для SSR store - один запрос, для теста - один тест. Именно scope и жизненный цикл определяют безопасность решения, а не само слово Singleton.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Factory - это обязательно класс с методом <code>create</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. В JavaScript и TypeScript чаще используют функцию, потому что она уже скрывает создание и может замкнуть конфигурацию. Класс полезен, если сама фабрика хранит зависимости или сложную политику выбора, но добавлять его только ради названия паттерна не нужно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Factory отличается от конструктора?</strong></summary>

<dl>
<dd>
<h2></h2>

Конструктор всегда создаёт экземпляр конкретного класса и вызывается через `new`. Factory может вернуть объект, функцию, ранее созданный экземпляр или одну из нескольких реализаций и не раскрывать конкретный тип клиенту. При простом создании класса конструктор понятнее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Factory отличается от dependency injection?</strong></summary>

<dl>
<dd>
<h2></h2>

Factory создаёт и собирает объект. Dependency injection, или передача зависимостей снаружи, определяет, откуда объект получает необходимые для работы зависимости. Factory часто находится в composition root, то есть точке, где реализации выбираются и связываются друг с другом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли импорт из ES module Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

Модуль вычисляется один раз для каждой его копии в графе модулей, а последующие imports получают те же exports. Это даёт Singleton-подобное поведение, но не глобальную гарантию. Другая вкладка, Web Worker, серверный процесс, дублированная версия npm package или отдельный bundle могут иметь собственную копию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Singleton опасен при SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

Объект уровня модуля на сервере может переживать отдельный запрос. Если в нём лежат данные авторизации, Redux state или кэш запросов пользователя, следующий запрос способен увидеть эти данные. Пользовательское состояние создают заново для каждого запроса, а общими оставляют только сервисы без пользовательского состояния или осознанно общие кэши.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где создавать Redux store или Query Client?</strong></summary>

<dl>
<dd>
<h2></h2>

В client-side приложении обычно создают один экземпляр на запуск приложения и передают через Provider. При SSR создают отдельный экземпляр для каждого запроса, наполняют его данными этого запроса и корректно передают состояние на client. Точная схема зависит от framework и библиотеки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя создавать singleton с побочным эффектом во время React render?</strong></summary>

<dl>
<dd>
<h2></h2>

React render должен оставаться чистым и может выполняться повторно или быть отброшен. Создание подключения, регистрация глобального обработчика или отправка аналитики во время render приведёт к дублированию и утечкам. Долгоживущую инфраструктуру создают вне render либо инициализируют в подходящем жизненном цикле с явной очисткой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как тестировать код, зависящий от Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

Лучше передавать небольшой интерфейс зависимости через аргумент, Provider или Factory. Тогда каждый тест создаёт собственную реализацию. Если используется общий экземпляр уровня модуля, нужны явные `reset`/`dispose`, восстановление mocks и изоляция параллельных тестов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что нужно очищать при logout?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользовательский state, кэш запросов, токены в допустимом storage, активные подписки, WebSocket и идентификаторы аналитики. Сам client можно сохранить, если он не хранит данные пользователя, но его состояние должно перейти в анонимный режим. Конкретная очистка определяется тем, что экземпляр хранит и чем владеет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Hot Module Replacement (HMR) влияет на Singleton?</strong></summary>

<dl>
<dd>
<h2></h2>

HMR обновляет изменённые модули в режиме разработки без полной перезагрузки страницы. В зависимости от сборщика часть старого состояния может сохраниться, а модуль - выполниться повторно. Повторная регистрация обработчика или создание второго client даёт эффекты, которых нет после полной загрузки. Инициализация должна выдерживать повторный вызов, а очистка ресурсов режима разработки должна быть явной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда Singleton оправдан?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда объект действительно представляет общий ресурс с ясным scope: клиент аналитики в браузере, store приложения, registry или logger без изменяемого состояния. Даже тогда зависимости лучше получать через понятную границу, а изменяемое пользовательское состояние не должно незаметно жить дольше пользователя или запроса.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Объект | Разумная область жизни |
|---|---|
| Redux store в SPA | Один экземпляр на запуск приложения |
| Store или Query Client при SSR | Один экземпляр на запрос |
| Клиент аналитики | Один на вкладку с очисткой идентификатора пользователя при logout |
| API client | На приложение или запрос в зависимости от контекста авторизации |
| Factory тестовых данных | Новый результат на каждый вызов |

## Связанные темы

- [03 Redux Toolkit configureStore createSlice Immer](<../State Management/03 Redux Toolkit configureStore createSlice Immer.md>)
- [04 API слой contracts DTO mapping](<../Architecture/04 API слой contracts DTO mapping.md>)
- [03 Server Components Client Components и use client](<../Next.js/03 Server Components Client Components и use client.md>)
- [07 Flaky tests isolation cleanup](<../Testing/07 Flaky tests isolation cleanup.md>)

## Источники

- [Redux Toolkit: configureStore](https://redux-toolkit.js.org/api/configureStore)
- [TanStack Query: SSR and Next.js](https://tanstack.com/query/latest/docs/framework/react/guides/ssr)
- [React: Components and Hooks must be pure](https://react.dev/reference/rules/components-and-hooks-must-be-pure)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Compound Components и Headless UI](<./05 Compound Components и Headless UI.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Decorator Proxy Mixin Mediator Flyweight →](<./07 Decorator Proxy Mixin Mediator Flyweight.md>)
<!-- CARD-NAV-BOTTOM:END -->
