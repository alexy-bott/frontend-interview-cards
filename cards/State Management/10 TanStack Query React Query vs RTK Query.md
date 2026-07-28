# TanStack Query React Query vs RTK Query

<!-- CARD-NAV-TOP:START -->
[← 09 Redux Toolkit vs Zustand vs Context vs RTK Query](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое TanStack Query, ранее React Query, и чем он отличается от RTK Query?**

<h2></h2>

<br>
<dl>
<dd>

TanStack Query является библиотекой для серверного состояния. Она загружает данные, хранит кэш, объединяет одинаковые запросы, повторяет неудачные запросы, обновляет данные при фокусе и помогает синхронизировать кэш после изменений на сервере. Общее состояние интерфейса (UI state) она не заменяет.

Основой кэша является `queryKey`, или ключ запроса. Это сериализуемый массив, например `["users", { page, search }]`. Все переменные, от которых зависит `queryFn`, должны входить в ключ. Иначе разные запросы могут использовать одну запись кэша или изменение параметра не запустит новую загрузку.

`useQuery` связывает `queryKey` с `queryFn`, которая получает данные. Компоненты с одинаковым ключом используют общий результат. Для условного запуска применяют `enabled` или `skipToken`, а данные конкретной записи можно обновить или пометить устаревшими через `QueryClient`.

У TanStack Query есть отдельные понятия свежести и хранения:

- `staleTime` определяет, сколько данные считаются свежими;
- `gcTime` определяет, сколько неактивная query хранится до удаления из памяти.

По умолчанию `staleTime` равен 0, поэтому полученные данные сразу считаются устаревшими, но не исчезают и могут отображаться. Устаревшие queries повторно загружаются в фоне при новом подключении компонента, возвращении фокуса и восстановлении сети. Неактивная query по умолчанию удаляется через 5 минут. Неудачный query по умолчанию повторяется 3 раза. Эти настройки полезно знать, потому что неожиданные запросы часто являются результатом стандартного поведения, а не ошибкой.

Structural sharing, или сохранение общих ссылок, по умолчанию оставляет прежние ссылки у неизменившихся частей JSON-совместимого результата. Это помогает React-мемоизации. Однако библиотека не превращает все ответы в глобальную нормализованную таблицу сущностей.

Mutation, то есть операция изменения данных на сервере, после успеха обычно помечает связанные queries устаревшими через `queryClient.invalidateQueries` или обновляет их ответом сервера через `setQueryData`. Для оптимистичного обновления (optimistic update) в `onMutate` отменяют конфликтующую повторную загрузку, сохраняют прежний кэш и применяют ожидаемое изменение. `onError` выполняет откат, а `onSettled` синхронизирует данные.

RTK Query решает ту же основную задачу, но является частью Redux Toolkit. Его API строится вокруг `createApi`, endpoints, сгенерированных hooks и tags. TanStack Query строится вокруг query keys, query functions и `QueryClient` и не требует Redux store.

Если Redux Toolkit уже является основной инфраструктурой, важны общий журнал actions, middleware и централизованное описание endpoints, RTK Query обычно органичнее. Если Redux проекту не нужен или слой данных должен оставаться независимым, TanStack Query часто проще. Выбирать следует по архитектуре проекта и опыту команды, а не по списку почти одинаковых возможностей.

При SSR создают отдельный `QueryClient` для каждого серверного запроса, заранее загружают данные, сериализуют кэш через `dehydrate` и восстанавливают его при гидратации (hydration) на клиенте. Общий серверный экземпляр (singleton) может смешать кэш разных пользователей. Нулевой `staleTime` также приводит к фоновой повторной загрузке сразу после гидратации, поэтому для SSR часто задают разумный период свежести.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое <code>queryKey</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Это адрес записи кэша и описание её зависимостей. Верхний уровень ключа должен быть массивом, а вложенные значения должны сериализоваться. Например, `["user", userId]` отделяет пользователей, а `["users", { page, search }]` отделяет варианты списка. Порядок элементов массива значим.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему все параметры <code>queryFn</code> должны входить в <code>queryKey</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

TanStack Query повторно использует кэш и запускает query при изменении ключа. Если `queryFn` читает `userId`, но ключ всегда равен `["user"]`, разные пользователи будут делить одну запись. Включение зависимости в ключ одновременно исправляет кэш и делает повторную загрузку декларативной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>staleTime</code> отличается от <code>gcTime</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`staleTime` относится к актуальности данных: пока query считается свежей, обычные триггеры не требуют повторной загрузки. `gcTime` относится к памяти: после исчезновения всех подписчиков query становится неактивной и позже удаляется. Данные могут считаться устаревшими, но всё ещё храниться и показываться во время фоновой повторной загрузки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие важные настройки по умолчанию есть у TanStack Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Данные query по умолчанию сразу считаются устаревшими. Такие queries могут повторно загружаться при подключении компонента, возвращении фокуса и восстановлении сети. Неактивный кэш удаляется через 5 минут, а неудачный query повторяется 3 раза. Для JSON-совместимых результатов действует сохранение общих ссылок (structural sharing). Эти настройки меняют по требованиям конкретных данных, а не отключают глобально без причины.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как обновить кэш после mutation?</strong></summary>

<dl>
<dd>
<h2></h2>

Если точный результат неизвестен или затронуто много данных, связанные queries помечают устаревшими через `invalidateQueries`. Если сервер вернул окончательный объект, его можно записать через `setQueryData` без лишнего запроса. При сложных зависимостях invalidation обычно безопаснее ручного обновления нескольких записей кэша.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как устроено оптимистичное обновление?</strong></summary>

<dl>
<dd>
<h2></h2>

Перед mutation код отменяет активную повторную загрузку затрагиваемой query, сохраняет прежнее значение и сразу применяет ожидаемый результат через `setQueryData`. При ошибке сохранённое значение возвращают, а после завершения query помечают устаревшей для проверки серверной версии. При параллельных mutations нужно учитывать порядок и конфликты.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличается invalidation, то есть пометка query как устаревшей, в TanStack Query и RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

TanStack Query обычно находит данные по полному или частичному `queryKey` через `invalidateQueries`. RTK Query связывает query и mutation через `providesTags` и `invalidatesTags`. В обоих случаях данные помечаются устаревшими и при нужных условиях загружаются повторно, но модель адресации различается.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли использовать TanStack Query вместе с Redux Toolkit?</strong></summary>

<dl>
<dd>
<h2></h2>

Да. TanStack Query хранит серверный кэш, а Redux Toolkit управляет клиентскими процессами. Но использовать одновременно TanStack Query и RTK Query для одних и тех же ресурсов обычно не стоит: появятся два кэша и неоднозначные правила их обновления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что важно при SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

`QueryClient` создают отдельно для каждого серверного запроса, чтобы данные пользователей не смешивались. На сервере кэш преобразуют в сериализуемое состояние через `dehydrate`, а на клиенте восстанавливают во время гидратации. Также настраивают `staleTime`, иначе query может сразу после загрузки страницы запустить фоновый повторный запрос.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нормализует ли TanStack Query сущности между разными queries?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Каждая запись кэша хранит собственный результат по `queryKey`. Сохранение общих ссылок работает внутри обновлённого результата, но не превращает одинакового пользователя из двух разных queries в одну глобальную сущность. При необходимости нормализацию проектируют отдельно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | TanStack Query | RTK Query |
| --- | --- | --- |
| Ключ кэша | `queryKey` | Endpoint и аргументы |
| Повторная загрузка после mutation | `invalidateQueries` | `invalidatesTags` |
| Ручное изменение кэша | `setQueryData` | `updateQueryData` |
| Интеграция с Redux | Не обязательна | Является частью решения |
| Описание API | `queryFn` и options рядом с hooks | Endpoints внутри `createApi` |
| SSR | `QueryClient`, `dehydrate` и `hydrate` | Инициализация Redux state и RTK Query |

## Связанные темы

- [01 Виды состояния во frontend](<./01 Виды состояния во frontend.md>)
- [06 RTK Query createApi query mutation tags](<./06 RTK Query createApi query mutation tags.md>)
- [07 RTK Query cache lifecycle optimistic updates polling](<./07 RTK Query cache lifecycle optimistic updates polling.md>)
- [09 Redux Toolkit vs Zustand vs Context vs RTK Query](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>)

## Источники

- [TanStack Query docs: Overview](https://tanstack.com/query/latest/docs/framework/react/overview)
- [TanStack Query docs: Query Keys](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys)
- [TanStack Query docs: Important Defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults)
- [TanStack Query docs: Invalidations from Mutations](https://tanstack.com/query/latest/docs/framework/react/guides/invalidations-from-mutations)
- [TanStack Query docs: Optimistic Updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)
- [TanStack Query docs: Server Rendering and Hydration](https://tanstack.com/query/latest/docs/framework/react/guides/ssr)
- [RTK Query docs: Overview](https://redux-toolkit.js.org/rtk-query/overview)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Redux Toolkit vs Zustand vs Context vs RTK Query](<./09 Redux Toolkit vs Zustand vs Context vs RTK Query.md>) · [↑ State Management](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
