# 05 Selectors normalization и createEntityAdapter

<!-- CARD-NAV-TOP:START -->
[← 04 Async logic createAsyncThunk listener middleware](<./04 Async logic createAsyncThunk listener middleware.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 RTK Query createApi query mutation tags →](<./06 RTK Query createApi query mutation tags.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое selectors в Redux? Зачем нужны нормализация данных и `createEntityAdapter`?

<details>
<summary><strong>Показать ответ</strong></summary>

Selector является чистой функцией, которая получает Redux state и возвращает нужное значение. Простой selector читает поле, а производный selector вычисляет результат: фильтрует список, объединяет сущности, считает сумму или определяет доступные действия. Компонент зависит от публичных selectors, а не от всей внутренней структуры store.

`useSelector` подписывает React-компонент на Redux store. После каждого action React Redux снова запускает selector и по умолчанию сравнивает прежний и новый результат строгим сравнением `===`. Если selector каждый раз создаёт новый объект или массив, ссылка меняется и компонент лишний раз отрисовывается даже при одинаковом содержимом.

Для простых значений достаточно обычного selector. Для дорогого вычисления или результата с новой ссылкой используют `createSelector` из Reselect, который входит в Redux Toolkit. Он принимает входные selectors и функцию вычисления. Пока входные значения не изменились по ссылке, selector возвращает сохранённый результат и не запускает вычисление повторно.

Мемоизация не означает, что любой selector нужно оборачивать в `createSelector`. Чтение `state.auth.userId` не требует кэша. Мемоизация полезна, когда есть реальное вычисление или нужна стабильная ссылка для React. Selector должен оставаться чистым, потому что он может выполняться несколько раз и в произвольный момент.

Нормализация данных означает хранение коллекции как таблицы сущностей:

```ts
{
  ids: ["u1", "u2"],
  entities: {
    u1: { id: "u1", name: "Ann" },
    u2: { id: "u2", name: "Max" }
  }
}
```

`entities` даёт прямой доступ по id, а `ids` хранит порядок. Другие сущности и списки ссылаются на пользователя по id, а не содержат независимые копии объекта. Поэтому изменение пользователя выполняется в одном месте и не создаёт рассинхронизацию.

`createEntityAdapter` создаёт начальную форму `{ ids, entities }`, reducers для типовых операций создания, чтения, обновления и удаления (CRUD), а также готовые selectors: `selectIds`, `selectEntities`, `selectAll`, `selectTotal`, `selectById`. `selectId` задаёт поле уникального идентификатора, а `sortComparer` может поддерживать `ids` в отсортированном порядке.

Нормализация полезна для больших коллекций, частых обновлений по id и связей между сущностями. Маленький локальный список без переиспользования проще хранить массивом. Также важно не путать нормализованный Redux slice с кэшем RTK Query: RTK Query хранит отдельные результаты запросов и по умолчанию не объединяет одинаковую сущность из разных записей кэша в одну глобальную запись.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему производные данные не хранят в store?</summary>

Если значение полностью вычисляется из существующего state, его копия создаёт второй источник истины. Например, сохранённый `filteredUsers` может устареть после изменения `users` или `filter`. Лучше хранить исходные данные и параметры, а результат получать через selector. Исключение возможно, если результат приходит как самостоятельная серверная сущность или его вычисление является отдельным бизнес-процессом.

</details>

<details>
<summary><strong>Вопрос:</strong> Как <code>useSelector</code> решает, нужна ли повторная отрисовка?</summary>

После action он запускает selector и сравнивает новый результат с предыдущим. По умолчанию используется строгое сравнение ссылок `===`. Примитивы сравниваются по значению, но новый объект или массив считается изменившимся. Можно выбрать отдельные поля несколькими hooks, вернуть мемоизированный результат или явно применить поверхностное сравнение `shallowEqual`.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает <code>createSelector</code>?</summary>

Он запускает входные selectors, сравнивает их результаты с предыдущими и вызывает функцию вычисления только при изменении входов. Если входы прежние, возвращается тот же сохранённый результат. Поэтому мемоизированный selector одновременно экономит вычисление и сохраняет ссылку на массив или объект.

</details>

<details>
<summary><strong>Вопрос:</strong> Может ли мемоизированный selector принимать props или id?</summary>

Да. Id передают как дополнительный аргумент во входной selector, например `(state, id) => id`. Нужно учитывать область кэша: если один экземпляр selector попеременно вызывается с большим количеством разных параметров, его кэш может быть неэффективен. Для независимых экземпляров компонентов иногда создают фабрику selectors или используют мемоизацию с подходящим размером кэша.

</details>

<details>
<summary><strong>Вопрос:</strong> Как выглядит нормализованная коллекция и зачем нужны обе части?</summary>

`entities` является словарём `id -> entity` и обеспечивает прямое чтение и обновление сущности. `ids` задаёт состав и порядок коллекции. Вместе они позволяют быстро получить запись по id и одновременно построить упорядоченный массив для интерфейса.

</details>

<details>
<summary><strong>Вопрос:</strong> Что генерирует <code>createEntityAdapter</code>?</summary>

Созданный adapter предоставляет `getInitialState`, операции `addOne`, `setAll`, `upsertMany`, `updateOne`, `removeOne` и другие reducers, а также набор мемоизированных selectors через `getSelectors`. Эти функции работают с единой формой `ids/entities` и сокращают повторяющийся CRUD-код.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему не стоит подписывать компонент на весь slice?</summary>

Результатом будет ссылка на весь объект slice, поэтому изменение любого его поля инициирует повторную отрисовку компонента. Лучше выбирать минимально нужное значение. Например, строка таблицы может получать пользователя через `selectById(state, id)`, а не весь список. Это уменьшает область подписки и делает зависимость компонента явной.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нормализация лишняя?</summary>

Когда список маленький, локальный, редко изменяется и одна сущность не повторяется в разных местах. Нормализация добавляет косвенные ссылки и selectors, поэтому должна решать реальную проблему обновлений и связей, а не применяться автоматически к каждому массиву.

</details>

## Где это встречается во frontend

| Сценарий | Решение |
| --- | --- |
| Строка большой таблицы | `selectById(state, id)` |
| Фильтрация коллекции | `createSelector` |
| Обновление одной сущности | Нормализованный `entities[id]` |
| CRUD над большой коллекцией | `createEntityAdapter` |
| Подсчёт производного значения | Selector вместо копии в store |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [03 Redux Toolkit configureStore createSlice Immer](<./03 Redux Toolkit configureStore createSlice Immer.md>)
- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [09 useMemo useCallback и React memo](<../React/09 useMemo useCallback и React memo.md>)

## Источники

- [Redux docs: Deriving Data with Selectors](https://redux.js.org/usage/deriving-data-selectors)
- [React Redux docs: Hooks](https://react-redux.js.org/api/hooks)
- [Redux Toolkit docs: createSelector](https://redux-toolkit.js.org/api/createSelector)
- [Redux Toolkit docs: createEntityAdapter](https://redux-toolkit.js.org/api/createEntityAdapter)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Async logic createAsyncThunk listener middleware](<./04 Async logic createAsyncThunk listener middleware.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 RTK Query createApi query mutation tags →](<./06 RTK Query createApi query mutation tags.md>)
<!-- CARD-NAV-BOTTOM:END -->
