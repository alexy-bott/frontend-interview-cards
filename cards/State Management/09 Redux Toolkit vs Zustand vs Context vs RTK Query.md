# 09 Redux Toolkit vs Zustand vs Context vs RTK Query

<!-- CARD-NAV-TOP:START -->
[← 08 Zustand store selectors middleware persist](<./08 Zustand store selectors middleware persist.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 TanStack Query React Query vs RTK Query →](<./10 TanStack Query React Query vs RTK Query.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как выбрать между Redux Toolkit, Zustand, Context и RTK Query?

<details>
<summary><strong>Показать ответ</strong></summary>

Сначала определяют тип состояния и его владельца, а затем выбирают инструмент. Эти технологии решают разные задачи и могут использоваться в одном приложении.

Локальный React state подходит, если значение требуется одному компоненту или небольшому поддереву. URL используют для состояния, которое должно восстанавливаться по ссылке. Специализированная form library управляет значениями, валидацией и жизненным циклом сложной формы.

Context является механизмом передачи значения через React-дерево. Он хорошо подходит для относительно стабильных зависимостей: темы, локали, конфигурации, экземпляра сервиса или store. Context сам по себе не предоставляет selectors, middleware, кэш или журнал событий. Одно большое и часто меняющееся значение Provider может обновлять много компонентов-потребителей.

Zustand является внешним store для клиентского состояния с простыми actions и выборочными подписками. Он подходит для общего UI, настроек и процессов средней сложности, когда нужна меньшая церемония, чем в Redux. Поскольку Zustand мало ограничивает архитектуру, команда должна сама определить границы stores, правила actions и persist.

Redux Toolkit подходит для сложного клиентского состояния и процессов, где важны явные события, reducers, middleware, Redux DevTools, воспроизводимая история и единый подход большой команды. Дополнительные понятия окупаются, когда несколько модулей реагируют на общие события или обновления имеют много правил.

RTK Query решает задачу серверного состояния: запросы, кэш, invalidation, повторную загрузку и mutations. Он использует Redux store как инфраструктуру, но не заменяет slices для клиентских процессов. Если Redux не нужен, аналогичную роль может выполнять TanStack Query.

В реальном приложении нормальна комбинация: локальный state для модалки, URL для фильтров, React Hook Form для формы, RTK Query для заказов с backend и Redux Toolkit или Zustand для клиентского процесса оформления. Важно, чтобы одни и те же данные не копировались между несколькими источниками истины.

Критерии выбора:

1. Кто владеет данными: компонент, URL, frontend или backend.
2. Сколько частей приложения читают и изменяют значение.
3. Насколько сложен процесс обновления и нужны ли реакции на события.
4. Нужны ли кэш, повторные запросы, middleware и подробная отладка.
5. Как инструмент будет работать при SSR, тестировании и в команде.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Нужно ли выбрать один state manager на весь проект?</summary>

Нет. Один инструмент для всех видов состояния обычно создаёт лишнюю сложность. Разные слои могут отвечать за свои данные, но у каждого значения должен оставаться один источник истины. Например, фильтр хранится в URL, а query key строится из него, без отдельной копии фильтра в Redux.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему Context не всегда считают полноценным state manager?</summary>

Context доставляет значение потребителям, но не задаёт модель его обновления. В нём нет встроенных actions, selectors, middleware, кэша или DevTools. Вместе с `useReducer` Context может управлять состоянием небольшого поддерева, но для часто меняющегося общего state выборочные подписки внешнего store обычно удобнее.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда выбрать Zustand вместо Redux Toolkit?</summary>

Когда клиентское состояние сравнительно прямое, число согласованных процессов невелико, а selectors и небольшой API дают достаточную наблюдаемость. Redux Toolkit лучше, если многие модули реагируют на общие actions, нужна цепочка middleware и журнал изменений является важной частью отладки.

</details>

<details>
<summary><strong>Вопрос:</strong> Если в проекте есть Redux Toolkit, нужно ли хранить API-данные в slices?</summary>

Обычно нет. Серверные данные с кэшем и повторной загрузкой лучше хранить в RTK Query. Slice оставляют для клиентского состояния и процессов, которые не являются копией backend. Ручной slice оправдан только при особой модели данных, которую кэш запросов действительно не покрывает.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли использовать Zustand вместе с RTK Query?</summary>

Да. Zustand может хранить состояние интерфейса, например выбранную панель, а RTK Query хранит сущности с backend. Копировать результат query в Zustand не нужно: после mutation или повторной загрузки пришлось бы синхронизировать две версии одних данных.

</details>

<details>
<summary><strong>Вопрос:</strong> Как отличить серверное состояние от клиентского?</summary>

Нужно спросить, где находится авторитетная версия. Если данные принадлежат backend, могут измениться независимо от текущей вкладки и требуют синхронизации по сети, это серверное состояние. Если значение описывает только интерфейс или незавершённый локальный процесс, это клиентское состояние.

</details>

<details>
<summary><strong>Вопрос:</strong> Всегда ли часто меняющийся Context вызывает повторную отрисовку всего приложения?</summary>

Нет. Обновляются потребители конкретного Context, а не все компоненты автоматически. Но каждый потребитель получает новое значение Provider целиком, поэтому широкий объект с частыми изменениями создаёт большую область обновления. Context можно разделить, стабилизировать передаваемое значение или заменить внешним store с selectors.

</details>

<details>
<summary><strong>Вопрос:</strong> Какая ошибка выбора встречается чаще всего?</summary>

Поместить server cache, значения форм, URL-фильтры, UI-флаги и чувствительные данные в один глобальный store. После этого непонятно, кто владеет значением, когда оно устаревает и что можно сохранять. Классификация состояния до выбора библиотеки предотвращает эту проблему.

</details>

## Где это встречается во frontend

| Задача | Подходящий инструмент |
| --- | --- |
| Открыта ли локальная модалка | `useState` |
| Тема или экземпляр сервиса | Context |
| Общий UI и настройки | Zustand |
| Сложный клиентский процесс | Redux Toolkit |
| Кэш данных API в Redux-проекте | RTK Query |
| Фильтры, которыми делятся по ссылке | URL |
| Большая форма | React Hook Form |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>)
- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [08 Zustand store selectors middleware persist](<./08 Zustand store selectors middleware persist.md>)
- [10 TanStack Query React Query vs RTK Query](<./10 TanStack Query React Query vs RTK Query.md>)

## Источники

- [Redux docs: When should I use Redux?](https://redux.js.org/faq/general#when-should-i-use-redux)
- [Redux Toolkit docs](https://redux-toolkit.js.org/)
- [RTK Query docs: Overview](https://redux-toolkit.js.org/rtk-query/overview)
- [Zustand docs](https://zustand.docs.pmnd.rs/)
- [React docs: Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Zustand store selectors middleware persist](<./08 Zustand store selectors middleware persist.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 TanStack Query React Query vs RTK Query →](<./10 TanStack Query React Query vs RTK Query.md>)
<!-- CARD-NAV-BOTTOM:END -->
