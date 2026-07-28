# 26 useInsertionEffect useDebugValue flushSync startTransition

<!-- CARD-NAV-TOP:START -->
[← 25 Advanced hooks useId useSyncExternalStore useOptimistic use](<./25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 React DOM form hooks useFormStatus useActionState →](<./27 React DOM form hooks useFormStatus useActionState.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Для чего нужны `useInsertionEffect`, `useDebugValue`, `flushSync` и отдельная функция `startTransition`?

<details>
<summary><strong>Показать ответ</strong></summary>

Это четыре независимых специальных API. `useInsertionEffect` нужен авторам CSS-in-JS библиотек, которые создают стили во время выполнения, `useDebugValue` улучшает отображение пользовательского хука в DevTools, `flushSync` принудительно завершает DOM-обновление, а `startTransition` помечает обновления React как несрочные без предоставления `isPending`.

**`useInsertionEffect`.** Библиотека динамических стилей может вставить CSS до запуска layout-эффектов компонентов. Тогда `useLayoutEffect`, который измеряет элемент, увидит уже применённые стили. Обычный прикладной компонент не должен использовать этот хук для данных или DOM-логики.

Ограничения `useInsertionEffect`:

- выполняется только на клиенте;
- `ref` в этот момент ещё могут быть не установлены;
- обновление состояния внутри запрещено;
- точный момент относительно изменений DOM не является API для прикладного кода;
- функция эффекта может вернуть очистку для удаляемого CSS-правила.

Статический CSS, CSS Modules и заранее извлечённые стили не требуют этого хука. Он существует для библиотеки, которая генерирует правила во время рендера.

**`useDebugValue`.** Добавляет понятную подпись пользовательского хука в React DevTools:

```tsx
function useOnlineStatus() {
  const isOnline = useSyncExternalStore(subscribe, getSnapshot);
  useDebugValue(isOnline ? "Online" : "Offline");
  return isOnline;
}
```

Второй аргумент является функцией форматирования. React DevTools вызывает её при просмотре хука, поэтому дорогое форматирование можно отложить: `useDebugValue(date, formatDate)`. API не пишет сообщения в консоль, не меняет состояние и обычно не нужен каждому простому пользовательскому хуку.

**`flushSync`.** Импортируется из `react-dom` и заставляет React синхронно применить обновления внутри переданной функции, чтобы следующая строка могла читать обновлённый DOM:

```tsx
flushSync(() => {
  setMessages((messages) => [...messages, nextMessage]);
});

listRef.current?.lastElementChild?.scrollIntoView();
```

Ради этого React может выполнить ожидающие обновления и эффекты не только из переданной функции. `flushSync` нарушает обычную пакетную обработку и планирование, ухудшает отзывчивость интерфейса и способен преждевременно показать `fallback` Suspense. Его используют для интеграции с браузерным API или сторонней системой, которой нужен обновлённый DOM к окончанию синхронного вызова, например `onbeforeprint`. Вызывать его во время рендера, метода жизненного цикла или эффекта React нельзя.

**`startTransition`.** Отдельная функция из `react` помечает синхронные setter-функции внутри своего Action как несрочные обновления:

```tsx
startTransition(() => {
  setRoute(nextRoute);
});
```

В отличие от `useTransition`, отдельная функция не сообщает `isPending`. Она нужна вне компонента или там, где состояние ожидания отслеживается другим слоем. Обновление управляемого текстового поля нельзя делать несрочным. Setter-функция внутри `setTimeout` или после `await` не наследует отметку автоматически; её нужно обернуть в новый `startTransition`.

Transition не переносит код в другой поток. Он позволяет React прервать и повторить рендер с меньшим приоритетом. Длинная синхронная функция внутри Action всё равно блокирует главный поток.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Почему <code>useInsertionEffect</code> редко нужен приложению?</summary>

Его задача заключается во вставке CSS, создаваемого во время выполнения, до измерения расположения элементов. Прикладной компонент обычно использует готовые стили, `useEffect` для внешней синхронизации или `useLayoutEffect` для измерения. `useInsertionEffect` работает в слишком ранней фазе для обычной DOM-логики и имеет жёсткие ограничения.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>useInsertionEffect</code> отличается от <code>useLayoutEffect</code>?</summary>

`useInsertionEffect` предназначен для внедрения CSS, чтобы последующие layout-эффекты увидели правильное расположение элементов. `useLayoutEffect` уже может читать DOM и синхронно исправлять визуальное положение до отрисовки браузером. Перенос обычного измерения в `useInsertionEffect` неверен, потому что `ref` ещё могут отсутствовать.

</details>

<details>
<summary><strong>Вопрос:</strong> Для чего нужна функция форматирования в <code>useDebugValue</code>?</summary>

Она преобразует внутреннее значение в удобную подпись только при просмотре хука в DevTools. Это позволяет не выполнять дорогое форматирование на каждом рендере, когда DevTools не запрашивает значение. Для простого логического значения достаточно передать готовую строку.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>flushSync</code> опасен?</summary>

Он блокирует обычное объединение и приоритизацию обновлений, может выполнить дополнительную ожидающую работу и показать `fallback` Suspense. Частое применение ухудшает отзывчивость интерфейса. Сначала проверяют, можно ли выполнить действие после commit через `ref` или эффект либо использовать API библиотеки без синхронного чтения DOM.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем отдельная функция <code>startTransition</code> отличается от <code>useTransition</code>?</summary>

Оба помечают обновление как transition. Хук дополнительно возвращает `isPending` и привязан к компоненту. Отдельную функцию можно вызвать во внешнем хранилище или интеграции маршрутизатора, но состояние ожидания она не предоставляет.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему обновление внутри <code>setTimeout</code> не становится transition автоматически?</summary>

`startTransition` отмечает setter-функции, вызванные синхронно во время выполнения Action. Функция таймера выполняется позже, когда этот контекст уже завершён. Внутри таймера нужен отдельный `startTransition`, если обновление действительно несрочное.

</details>

<details>
<summary><strong>Вопрос:</strong> Переносит ли transition вычисление в Worker?</summary>

Нет. React только меняет приоритет и может освобождать поток между частями рендера. Произвольный тяжёлый цикл остаётся на главном потоке. Для настоящего параллельного расчёта используется Web Worker и передача сериализуемых данных.

</details>

## Мини-задача

```tsx
function handleChange(value: string) {
  startTransition(() => {
    setInput(value);
    setQuery(value);
  });
}
```

<details>
<summary><strong>Вопрос:</strong> Какое обновление нельзя помещать в transition?</summary>

`setInput(value)` управляет управляемым полем и должно выполниться срочно. Его выносят перед `startTransition`. Несрочным оставляют `setQuery(value)`, если он запускает тяжёлый рендер результатов.

</details>

## Где это встречается во frontend

| Ситуация | API |
| --- | --- |
| CSS-in-JS библиотека со стилями времени выполнения | `useInsertionEffect` |
| Диагностика сложного пользовательского хука | `useDebugValue` |
| Браузерный API сразу читает DOM | Редкий `flushSync` |
| Маршрутизатор или хранилище помечает несрочное обновление | `startTransition` |
| Компонент показывает состояние ожидания | `useTransition` вместо отдельной функции |
| Тяжёлая обработка на CPU | Web Worker, а не transition |

## Связанные темы

- [07 useEffect useLayoutEffect и cleanup](<./07 useEffect useLayoutEffect и cleanup.md>)
- [16 useTransition и useDeferredValue](<./16 useTransition и useDeferredValue.md>)
- [22 Performance profiling и оптимизация React](<./22 Performance profiling и оптимизация React.md>)
- [38 Web Workers postMessage structured clone](<../JavaScript/38 Web Workers postMessage structured clone.md>)
- [14 Debugging CSS DevTools common issues](<../CSS/14 Debugging CSS DevTools common issues.md>)

## Источники

- [React: `useInsertionEffect`](https://react.dev/reference/react/useInsertionEffect)
- [React: `useDebugValue`](https://react.dev/reference/react/useDebugValue)
- [React: `startTransition`](https://react.dev/reference/react/startTransition)
- [React DOM: `flushSync`](https://react.dev/reference/react-dom/flushSync)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 25 Advanced hooks useId useSyncExternalStore useOptimistic use](<./25 Advanced hooks useId useSyncExternalStore useOptimistic use.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [27 React DOM form hooks useFormStatus useActionState →](<./27 React DOM form hooks useFormStatus useActionState.md>)
<!-- CARD-NAV-BOTTOM:END -->
