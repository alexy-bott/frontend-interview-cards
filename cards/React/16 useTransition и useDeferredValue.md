# 16 useTransition и useDeferredValue

<!-- CARD-NAV-TOP:START -->
[← 15 Suspense lazy и code splitting](<./15 Suspense lazy и code splitting.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 Hydration SSR и SSG →](<./17 Hydration SSR и SSG.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Для чего нужны `useTransition` и `useDeferredValue`? Чем они отличаются от debounce?

<details>
<summary><strong>Показать ответ</strong></summary>

`useTransition` и `useDeferredValue` позволяют React обрабатывать часть обновлений как несрочные. Срочное обновление, например ввод символа, должно немедленно отразиться в поле. Перестроение тяжёлого списка можно начать с меньшим приоритетом, прервать при следующем вводе и завершить, когда главный поток свободнее.

`useTransition` возвращает `isPending` и `startTransition`. В функцию `startTransition` передают синхронный вызов setter-функций, обновления которых нужно пометить как несрочные:

```tsx
const [isPending, startTransition] = useTransition();
const [tab, setTab] = useState("overview");

function selectTab(nextTab: string) {
  startTransition(() => {
    setTab(nextTab);
  });
}
```

Рендер перехода может быть прерван более срочным обновлением и начат заново с новыми данными. `isPending` остаётся `true`, пока связанная работа не завершена. Обновление, управляющее текстовым полем, нельзя помещать в transition: поле должно синхронно отражать ввод. Обычно состояние поля обновляется срочно, а отдельное состояние результатов или навигации обновляется внутри transition.

`useDeferredValue(value)` возвращает отложенную версию значения, которая может временно отставать от актуальной. Сначала React рендерит срочную часть со старым значением, затем с меньшим приоритетом пытается построить дерево с новым. Если приходит ещё одно изменение, незавершённый рендер отбрасывается. Это удобно, когда setter-функция находится выше или значение уже приходит как prop:

```tsx
const [query, setQuery] = useState("");
const deferredQuery = useDeferredValue(query);

return (
  <>
    <input value={query} onChange={(event) => setQuery(event.target.value)} />
    <Results query={deferredQuery} />
  </>
);
```

Разница заключается в точке управления: `useTransition` помечает конкретное обновление состояния как несрочное, а `useDeferredValue` откладывает распространение уже полученного значения в часть дерева. Признак временно устаревшего интерфейса можно вычислить как `query !== deferredQuery` и визуально обозначить, не заменяя готовые результаты индикатором загрузки.

Transition не является debounce или throttle. Debounce откладывает запуск до паузы, а throttle ограничивает частоту запусков; transition может начать работу сразу. `useDeferredValue` также не уменьшает число сетевых запросов автоматически: если `fetch` привязан к исходному `query`, запрос уйдёт при каждом вводе. Временная задержка управляет частотой запуска, а transition управляет приоритетом рендера React; эти подходы можно сочетать.

Эти API не переносят JavaScript в другой поток и не гарантируют уменьшение общего объёма вычислений. React может освобождать главный поток между частями собственного рендера, но длинная синхронная функция всё равно его блокирует. Для неё нужны более быстрый алгоритм, мемоизация, виртуализация списка, дробление работы или Web Worker.

Если `startTransition` получает асинхронную функцию, React 19 учитывает её ожидание в состоянии `isPending`. Однако обновления состояния после `await` пока нужно снова оборачивать в `startTransition`, чтобы они сохранили несрочный приоритет. Несвязанные transitions могут объединяться React; это ограничение текущей реализации, поэтому `isPending` не всегда описывает одну предметную операцию.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> <code>useTransition</code> является debounce?</summary>

Нет. Debounce запускает работу после временной паузы и может сократить число запросов. Transition запускает обновление с меньшим приоритетом; React может начать его сразу, прервать и повторить. В поиске debounce может ограничивать частоту запросов к API, а отложенное значение сохранять отзывчивость тяжёлого списка.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда выбирать <code>useTransition</code>, а когда <code>useDeferredValue</code>?</summary>

`useTransition` выбирают, когда код контролирует setter-функцию несрочного состояния. `useDeferredValue` выбирают, когда значение уже существует или приходит как prop, а отложить нужно его использование в тяжёлом поддереве. Оба решения наиболее полезны, когда дорогое дерево способно пропустить работу при равных входных данных, например благодаря Compiler или `memo`.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему состояние текстового поля нельзя обновлять в transition?</summary>

Управляемое поле должно синхронно получить новое `value` после `onChange`, иначе ввод будет запаздывать или возвращаться к прежнему значению. Сам `query` обновляют срочно, а результаты поиска получают отложенный `query` или отдельное состояние, обновляемое в transition.

</details>

<details>
<summary><strong>Вопрос:</strong> Отправляет ли <code>useDeferredValue</code> меньше запросов?</summary>

Нет. Он откладывает рендер React с новым значением, но не вводит временную задержку и не отменяет побочные эффекты, привязанные к исходному состоянию. Для сокращения запросов нужны debounce, отмена через AbortController, кеш и защита от устаревших ответов.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему transition не спасает от тяжёлой синхронной функции?</summary>

Пока функция непрерывно выполняется, главный поток не может обработать ввод или отрисовать следующий кадр. React умеет освобождать поток между частями собственной работы рендера, но не может прервать произвольный цикл внутри компонента. Вычисление оптимизируют, делят или выносят в Web Worker.

</details>

<details>
<summary><strong>Вопрос:</strong> Как transitions взаимодействуют с Suspense?</summary>

Если навигация или другое обновление помечено как transition, React старается сохранить уже показанный интерфейс, пока новое дерево ожидает данные, вместо немедленной замены ближайшим `fallback`. `isPending` позволяет показать индикатор в существующем интерфейсе. Первая загрузка без прежнего содержимого всё равно показывает запасной интерфейс.

</details>

<details>
<summary><strong>Вопрос:</strong> Для чего нужен второй аргумент <code>initialValue</code> у <code>useDeferredValue</code>?</summary>

В актуальном React можно передать начальную отложенную версию для первого рендера. React сначала вернёт `initialValue`, затем запланирует рендер с меньшим приоритетом и фактическим `value`. На последующих обновлениях этот аргумент не используется.

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Поиск по большой таблице | Срочное обновление поля и `useDeferredValue` для списка |
| Переключение тяжёлой вкладки | `startTransition` и локальный `isPending` |
| Навигация с Suspense | Transition сохраняет уже показанный экран |
| Частые запросы поиска | Debounce и отмена, а не только отложенное значение |
| Тысячи строк | Virtualization вместе с приоритетами |
| Тяжёлый расчёт на CPU | Web Worker или оптимизация алгоритма |

## Связанные темы

- [02 Render commit и Fiber](<./02 Render commit и Fiber.md>)
- [15 Suspense lazy и code splitting](<./15 Suspense lazy и code splitting.md>)
- [22 Performance profiling и оптимизация React](<./22 Performance profiling и оптимизация React.md>)
- [38 Web Workers postMessage structured clone](<../JavaScript/38 Web Workers postMessage structured clone.md>)
- [04 Fetch API AbortController credentials headers](<../Web API/04 Fetch API AbortController credentials headers.md>)

## Источники

- [React: `useTransition`](https://react.dev/reference/react/useTransition)
- [React: `useDeferredValue`](https://react.dev/reference/react/useDeferredValue)
- [React: `startTransition`](https://react.dev/reference/react/startTransition)
- [React 18: Transitions](https://react.dev/blog/2022/03/29/react-v18)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 15 Suspense lazy и code splitting](<./15 Suspense lazy и code splitting.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 Hydration SSR и SSG →](<./17 Hydration SSR и SSG.md>)
<!-- CARD-NAV-BOTTOM:END -->
