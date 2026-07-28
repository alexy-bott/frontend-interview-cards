# Advanced hooks useId useSyncExternalStore useOptimistic use

<!-- CARD-NAV-TOP:START -->
[← 24 HOC render props PureComponent Component lifecycle](<./24 HOC render props PureComponent Component lifecycle.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 useInsertionEffect useDebugValue flushSync startTransition →](<./26 useInsertionEffect useDebugValue flushSync startTransition.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Для чего нужны `useId`, `useSyncExternalStore`, `useOptimistic` и API `use`? К каким версиям React они относятся?**

<h2></h2>

<br>
<dl>
<dd>

`useId` и `useSyncExternalStore` появились в React 18. `useOptimistic` и `use` появились в стабильном React 19. Эти API решают независимые задачи: идентификаторы для связей доступности, согласованную подписку на внешнее хранилище, оптимистичный интерфейс и чтение Promise или Context во время рендера.

**`useId`.** Создаёт уникальный идентификатор для связей доступности одного экземпляра компонента. Он согласуется между серверным рендером и гидратацией при одинаковом дереве:

```tsx
function PasswordField() {
  const id = useId();

  return (
    <>
      <label htmlFor={id}>Password</label>
      <input id={id} aria-describedby={`${id}-hint`} />
      <p id={`${id}-hint`}>At least 12 characters</p>
    </>
  );
}
```

`useId` не является идентификатором данных и не подходит для `key`. Ключ списка должен происходить из `user.id` или другого устойчивого поля сущности. Для нескольких корневых узлов React можно задать согласованный `identifierPrefix` в серверном и клиентском API, чтобы исключить конфликт идентификаторов.

**`useSyncExternalStore`.** Подписывает компонент на изменяемое состояние вне React и сохраняет согласованное чтение при конкурентном рендеринге:

```tsx
const isOnline = useSyncExternalStore(
  subscribeToOnlineStatus,
  getOnlineSnapshot,
  getServerOnlineSnapshot
);
```

`subscribe` регистрирует функцию обратного вызова и возвращает функцию отписки. `getSnapshot` возвращает текущий неизменяемый снимок состояния. Пока хранилище не изменилось, повторный `getSnapshot` должен возвращать тот же результат по `Object.is`; для изменяемого внутреннего хранилища нужен кешированный иммутабельный снимок. `getServerSnapshot` задаёт значение для SSR и гидратации и должно совпасть с первоначальным клиентским снимком.

Хук предотвращает tearing, или разрыв согласованности, когда компоненты одной commit-фазы видят разные версии внешнего хранилища. Он предназначен прежде всего для авторов хранилищ и подписок на браузерные API. Прикладной код Redux или Zustand обычно использует готовый хук библиотеки, уже построенный на подходящей подписке.

**`useOptimistic`.** Позволяет показать ожидаемый результат сразу, пока Action выполняется:

```tsx
const [optimisticMessages, addOptimisticMessage] = useOptimistic(
  messages,
  (currentMessages, text: string) => [
    ...currentMessages,
    { id: `temp-${currentMessages.length}`, text, sending: true },
  ]
);
```

Второй аргумент, функция оптимистичного обновления, должен быть чистым. После успешной операции основное состояние должно получить подтверждённые данные сервера, например настоящий `id`. Если Action завершилась ошибкой и базовое состояние не изменилось, оптимистичное состояние возвращается к нему. Приложение отдельно показывает ошибку, обрабатывает повтор, порядок параллельных действий и защиту от дублей.

**`use`.** Читает поддерживаемый ресурс во время рендера. В React 19 это Promise или Context. Ожидающий Promise активирует ближайший `fallback` Suspense, выполненный возвращает значение, а отклонённый передаёт ошибку ближайшему Error Boundary. `use(Context)` читает Context подобно `useContext`.

В отличие от обычных хуков, `use` можно вызвать в условии или цикле, но только внутри компонента или пользовательского хука. Его нельзя помещать в `try/catch`: ошибку обрабатывает Error Boundary, а ожидание Suspense. Promise должен быть стабильным и происходить из кеша фреймворка либо быть создан в Server Component и передан Client Component. Новый Promise при каждом клиентском рендере заставляет React снова ожидать и не является полноценным слоем работы с данными.

В Server Component для обычного получения данных чаще используют `await`, потому что асинхронный компонент продолжает выполнение с того же места. `use` полезен, когда Promise передаётся глубже, особенно через Client Component и границу Suspense.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>useId</code> нельзя использовать как ключ списка?</strong></summary>

<dl>
<dd>
<h2></h2>

`useId` идентифицирует экземпляр компонента и DOM-связь, а `key` должен идентифицировать конкретную сущность данных среди соседей. При сортировке пользователя нужно узнавать по `user.id`, а не по позиции хука в дереве. Кроме того, хук нельзя вызывать внутри `map` в одном компоненте.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда прикладному коду нужен <code>useSyncExternalStore</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При собственной интеграции с браузерным API или внешним хранилищем, которые живут вне состояния React: статус сети, общее хранилище истории или подписка на CSS-медиазапрос. Для готовой библиотеки состояния лучше использовать её официальный хук-селектор, потому что он уже обеспечивает согласованные снимки и подписку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>getSnapshot</code> должен быть кеширован?</strong></summary>

<dl>
<dd>
<h2></h2>

React вызывает его многократно и сравнивает результат через `Object.is`. Если функция каждый раз создаёт новый объект без изменения хранилища, React увидит бесконечную последовательность изменений. Иммутабельное хранилище может вернуть текущий объект, а изменяемое хранилище сохраняет последний снимок и создаёт новый только после реального изменения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>getServerSnapshot</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он возвращает значение во время SSR и первоначальной гидратации. Клиент должен получить тот же снимок, иначе разметка не совпадёт. Например, серверный снимок статуса сети можно зафиксировать как `true` и использовать его до первой фактической браузерной подписки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что может пойти не так с оптимистичным интерфейсом?</strong></summary>

<dl>
<dd>
<h2></h2>

Сервер может отклонить действие, вернуть другой объект или принять параллельные операции в ином порядке. Оптимистично добавленный элемент получает временный идентификатор, затем заменяется подтверждённым ответом сервера. Ошибка откатывает базовое представление и остаётся видимой пользователю, а изменение не отправляется повторно без защиты от дублей.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>use</code> отличается от обычного хука?</strong></summary>

<dl>
<dd>
<h2></h2>

Он умеет читать Promise или Context и допускается в условиях и циклах. Но его всё равно вызывают только внутри React-компонента или хука и не оборачивают в `try/catch`. `use` не хранит локальное состояние и не заменяет `useEffect` для произвольного клиентского запроса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт с отклонённым Promise в <code>use</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

React бросит причину во время рендера. Ближайший Error Boundary покажет интерфейс ошибки. Suspense обрабатывает только ожидание, а не отказ. Если отклонение Promise нужно преобразовать в обычное значение, это делают заранее через цепочку Promise, а не `try/catch` вокруг `use`.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
function Users({ users }) {
  const id = useId();

  return users.map((user) => (
    <UserRow key={`${id}-${user.name}`} user={user} />
  ));
}
```

<details>
<summary><strong>Почему такой <code>key</code> хуже <code>user.id</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

React id относится к экземпляру списка, а `name` может измениться или повториться. Key должен сохранять идентичность пользователя при редактировании и перестановке, поэтому нужен устойчивый уникальный `user.id`. `useId` здесь вообще не требуется.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | API |
| --- | --- |
| Переиспользуемое поле с подписью и подсказкой | `useId` |
| Собственное внешнее хранилище | `useSyncExternalStore` |
| SSR внешней подписки | `getServerSnapshot` |
| Комментарий появляется до ответа | `useOptimistic` |
| Promise из Server Component | `use` и Suspense в Client Component |
| Условное чтение Context | `use(Context)` |

## Связанные темы

- [03 Reconciliation key и списки](<./03 Reconciliation key и списки.md>)
- [15 Suspense lazy и code splitting](<./15 Suspense lazy и code splitting.md>)
- [18 Server Components и Server Actions](<./18 Server Components и Server Actions.md>)
- [19 React 18 19 и 19.2](<./19 React 18 19 и 19.2.md>)
- [01 Виды состояния во frontend](<../State Management/01 Виды состояния во frontend.md>)
- [05 Forms labels errors validation accessibility](<../Accessibility/05 Forms labels errors validation accessibility.md>)

## Источники

- [React: `useId`](https://react.dev/reference/react/useId)
- [React: `useSyncExternalStore`](https://react.dev/reference/react/useSyncExternalStore)
- [React: `useOptimistic`](https://react.dev/reference/react/useOptimistic)
- [React: `use`](https://react.dev/reference/react/use)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 24 HOC render props PureComponent Component lifecycle](<./24 HOC render props PureComponent Component lifecycle.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [26 useInsertionEffect useDebugValue flushSync startTransition →](<./26 useInsertionEffect useDebugValue flushSync startTransition.md>)
<!-- CARD-NAV-BOTTOM:END -->
