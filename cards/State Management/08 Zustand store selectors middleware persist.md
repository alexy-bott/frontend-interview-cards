# 08 Zustand store selectors middleware persist

<!-- CARD-NAV-TOP:START -->
[← 07 RTK Query cache lifecycle optimistic updates polling](<./07 RTK Query cache lifecycle optimistic updates polling.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Redux Toolkit vs Zustand vs Context vs RTK Query →](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое Zustand? Как в нём работают store, selectors, middleware и `persist`?

<details>
<summary><strong>Показать ответ</strong></summary>

Zustand является библиотекой для клиентского состояния с небольшим API. Store находится вне React, а функция `create` возвращает React hook для чтения состояния и вызова actions. Компонент подписывается на выбранную часть store и повторно отрисовывается, только когда результат selector изменился.

```ts
type UiStore = {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
};

export const useUiStore = create<UiStore>((set) => ({
  sidebarOpen: false,
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
```

`set` обновляет store. При передаче объекта Zustand по умолчанию поверхностно объединяет его с текущим состоянием. Функциональная форма `set(state => nextState)` нужна, когда новое значение зависит от предыдущего. Actions обычно размещают рядом с данными, чтобы правила изменения не размазывались по компонентам.

Selector определяет подписку: `useUiStore(state => state.sidebarOpen)`. По умолчанию результат сравнивается через `Object.is`. Если selector каждый раз возвращает новый объект или массив, ссылка меняется и компонент лишний раз отрисовывается. Тогда выбирают поля отдельными selectors, возвращают стабильное значение или применяют `useShallow` для поверхностного сравнения.

Store можно читать и изменять вне React через `getState`, `setState` и `subscribe`. Для изолированных экземпляров, внедрения зависимостей (dependency injection), SSR и тестов создают store вне React через `createStore`, передают его через Context и используют hook `useStore`. Provider не обязателен для единственного клиентского экземпляра (singleton), но нужен, если store должен принадлежать конкретному поддереву.

Middleware расширяют поведение store. `persist` сохраняет выбранную часть состояния в `localStorage` или другом хранилище, `devtools` подключает Redux DevTools, `subscribeWithSelector` даёт выборочные подписки вне React. Порядок и типы middleware нужно настраивать осознанно, а не добавлять их автоматически.

Для `persist` важно определить, что действительно должно переживать перезагрузку. `partialize` выбирает сохраняемые поля, `version` помечает версию структуры, `migrate` преобразует старые данные, а `skipHydration` позволяет вручную управлять восстановлением. Обычно сохраняют тему, раскладку и пользовательские настройки. Серверный кэш, большие ответы API, токены и чувствительные данные не следует бездумно помещать в хранилище браузера.

При SSR сервер одновременно обслуживает разных пользователей, поэтому глобальный store на уровне модуля может передать состояние между запросами. В Next.js store с пользовательскими данными создают отдельно для каждого запроса или дерева и инициализируют одинаковыми данными на сервере и клиенте. Иначе возможны утечка данных и ошибка гидратации (hydration), то есть несовпадение первой клиентской отрисовки с серверным HTML. React Server Components не должны читать или изменять клиентский Zustand store.

Zustand подходит для общего UI и клиентских процессов с простыми правилами. Он не предоставляет серверный кэш, пометку данных как устаревших и повторные запросы, поэтому данные API лучше отдавать RTK Query или TanStack Query. Простота Zustand требует договорённостей о границах store, иначе в нём быстро смешиваются несвязанные формы, ответы API и временные UI-флаги.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Как компонент подписывается на Zustand store?</summary>

Hook принимает selector и сохраняет его результат. После обновления store selector выполняется снова, а результат сравнивается с предыдущим через `Object.is`. Если значение не изменилось, повторная отрисовка из-за store не требуется. Поэтому selector должен возвращать минимально нужную и стабильную часть состояния.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда нужен <code>useShallow</code>?</summary>

Когда selector возвращает объект, массив или кортеж (tuple) из нескольких полей и достаточно сравнить их верхний уровень. Без `useShallow` новый объект является новым результатом при каждом вызове. Для одного примитива или стабильной ссылки он не нужен, а для глубоких структур лучше пересмотреть форму state, а не выполнять дорогое глубокое сравнение.

</details>

<details>
<summary><strong>Вопрос:</strong> Как работает <code>set</code>?</summary>

`set({ count: 1 })` поверхностно объединяет переданные поля с текущим store. Вложенный объект при этом не объединяется глубоко, поэтому его нужно копировать или использовать Immer middleware. Если обновление зависит от прежнего значения, применяют `set(state => ({ count: state.count + 1 }))`. Для полной замены вторым аргументом передают `true`: `set(nextState, true)`. Это нужно использовать осторожно, чтобы вместе с прежним state не удалить actions.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем Zustand отличается от Context?</summary>

Context передаёт одно значение через React-дерево, и изменение значения Provider уведомляет компоненты-потребители. Zustand является внешним store с выборочными подписками через selectors. Context удобен для относительно стабильной зависимости, а Zustand обычно удобнее для часто меняющегося общего состояния, когда разным компонентам нужны разные поля.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда Redux Toolkit лучше Zustand?</summary>

Когда важны единая событийная модель, явные actions, общая цепочка middleware, подробный журнал в DevTools и сложная координация многих модулей. Zustand требует меньше кода и подходит для более прямых обновлений, но почти не навязывает архитектурные ограничения. Поэтому выбор зависит от сложности процессов и размера команды, а не только от размера bundle.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие риски есть у <code>persist</code>?</summary>

В хранилище может остаться несовместимая старая структура, чувствительные данные или слишком большой объём. Сохранённое состояние восстанавливается не одновременно с серверной отрисовкой, что способно вызвать несовпадение при гидратации (hydration mismatch). Нужны `partialize`, `version`, `migrate`, безопасное поведение до восстановления и осознанная модель хранения.

</details>

<details>
<summary><strong>Вопрос:</strong> Зачем нужны <code>version</code> и <code>migrate</code>?</summary>

После релиза поля store могут быть переименованы или изменить формат, а в браузере пользователя останутся старые данные. `version` позволяет обнаружить несовпадение схемы, а `migrate` преобразует сохранённое значение в текущую форму. Если безопасная миграция невозможна, старое состояние лучше сбросить.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему глобальный store с единственным экземпляром опасен при SSR?</summary>

Область видимости серверного модуля (module scope) может жить дольше одного HTTP-запроса. Если store хранит пользователя или данные страницы, следующий запрос способен увидеть предыдущее значение. Store создают отдельно на запрос и передают нужному React-дереву. Начальное состояние клиента должно совпадать с серверным, чтобы гидратация была корректной.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли хранить ответы API в Zustand?</summary>

Технически можно, но тогда кэширование, актуальность, устранение одинаковых запросов, отмену и синхронизацию придётся реализовать самостоятельно. Для обычного серверного состояния надёжнее специализированная библиотека запросов и кэша. В Zustand имеет смысл хранить только клиентскую часть процесса, например выбранный id, а сами сущности получать из кэша запросов.

</details>

## Где это встречается во frontend

| Сценарий | Решение в Zustand |
| --- | --- |
| Общая боковая панель | Небольшой store интерфейса |
| Многошаговый клиентский процесс | State и actions |
| Подписка на несколько полей | Selectors и при необходимости `useShallow` |
| Настройки между перезагрузками | `persist` с `partialize` и `migrate` |
| Изолированный store для виджета | Store вне React и Context |
| Next.js SSR | Store на запрос и одинаковая инициализация |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [09 Redux Toolkit vs Zustand vs Context vs RTK Query](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>)
- [10 TanStack Query React Query vs RTK Query](<./10 TanStack Query React Query vs RTK Query.md>)

## Источники

- [Zustand docs](https://zustand.docs.pmnd.rs/)
- [Zustand docs: Prevent rerenders with useShallow](https://zustand.docs.pmnd.rs/learn/guides/prevent-rerenders-with-use-shallow)
- [Zustand docs: persist middleware](https://zustand.docs.pmnd.rs/reference/middlewares/persist)
- [Zustand docs: Setup with Next.js](https://zustand.docs.pmnd.rs/learn/guides/nextjs)
- [Zustand docs: SSR and Hydration](https://zustand.docs.pmnd.rs/learn/guides/ssr-and-hydration)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 RTK Query cache lifecycle optimistic updates polling](<./07 RTK Query cache lifecycle optimistic updates polling.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Redux Toolkit vs Zustand vs Context vs RTK Query →](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>)
<!-- CARD-NAV-BOTTOM:END -->
