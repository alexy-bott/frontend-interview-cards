# useTransition и useDeferredValue

<!-- CARD-NAV-TOP:START -->
[← 15 Suspense lazy и разделение кода](<./15 Suspense lazy и разделение кода.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 SSR SSG и hydration в React →](<./17 SSR SSG и hydration в React.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Для чего нужны `useTransition` и `useDeferredValue`? Чем они отличаются от debounce?**

<h2></h2>

<br>
<dl>
<dd>

`useTransition` и `useDeferredValue` позволяют React обрабатывать часть обновлений как несрочные.

Срочное обновление, например ввод символа, должно немедленно отразиться в поле. Перестроение тяжёлого списка можно выполнять в фоне с меньшим приоритетом, прервать при следующем вводе и начать заново с актуальными данными.

Это не означает, что React откладывает вызов функции или запускает JavaScript в другом потоке. React меняет приоритет собственного render и может уступать более срочным обновлениям.

`useTransition` возвращает `isPending` и `startTransition`:

```tsx
const [isPending, startTransition] =
  useTransition();

const [tab, setTab] =
  useState("overview");

function selectTab(nextTab: string) {
  startTransition(() => {
    setTab(nextTab);
  });
}
```

Функция, переданная в `startTransition`, выполняется сразу.

React помечает как Transition обновления состояния, которые были синхронно запланированы во время её выполнения:

```text
startTransition callback
→ выполняется сразу

setState внутри callback
→ получает несрочный приоритет
```

Сам setter не выполняется позже по таймеру. Отложенным и прерываемым становится render, вызванный этим обновлением.

Render Transition может быть прерван более срочным обновлением и начат заново с актуальными данными.

Например:

```text
начался render тяжёлой вкладки
→ пользователь ввёл символ
→ React прерывает несрочный render
→ применяет обновление поля
→ повторяет render вкладки
```

`isPending` становится `true` после запуска Transition и остаётся таким, пока связанные Actions не завершатся и итоговое состояние не будет показано пользователю.

```tsx
<button
  disabled={isPending}
  onClick={() => {
    startTransition(() => {
      setTab("reports");
    });
  }}
>
  {isPending
    ? "Открытие..."
    : "Отчёты"}
</button>
```

Состояние, непосредственно управляющее текстовым полем, нельзя обновлять внутри Transition:

```tsx
function handleChange(
  event:
    React.ChangeEvent<HTMLInputElement>,
) {
  startTransition(() => {
    setQuery(event.target.value);
  });
}
```

Если `query` передаётся в:

```tsx
<input value={query} />
```

поле должно синхронно отражать пользовательский ввод.

Обычно разделяют срочное значение поля и несрочное состояние результатов:

```tsx
const [query, setQuery] =
  useState("");

const [searchQuery, setSearchQuery] =
  useState("");

function handleChange(
  event:
    React.ChangeEvent<HTMLInputElement>,
) {
  const nextQuery =
    event.target.value;

  setQuery(nextQuery);

  startTransition(() => {
    setSearchQuery(nextQuery);
  });
}
```

```tsx
<input
  value={query}
  onChange={handleChange}
/>

<Results query={searchQuery} />
```

`query` обновляет поле срочно, а `searchQuery` может временно отставать.

`useDeferredValue(value)` решает похожую задачу с другой точки управления.

Он возвращает отложенную версию уже полученного значения:

```tsx
const [query, setQuery] =
  useState("");

const deferredQuery =
  useDeferredValue(query);
```

```tsx
return (
  <>
    <input
      value={query}
      onChange={(event) => {
        setQuery(
          event.target.value,
        );
      }}
    />

    <Results
      query={deferredQuery}
    />
  </>
);
```

При обновлении происходят два render:

```text
срочный render
→ query уже новый
→ deferredQuery ещё предыдущий

фоновый render
→ query новый
→ deferredQuery новый
```

Если во время фонового render приходит ещё одно изменение, React прерывает незавершённую работу и начинает её заново с последним значением.

На первоначальном render без второго аргумента:

```tsx
useDeferredValue(value)
```

отложенное значение равно исходному `value`, потому что предыдущего значения ещё нет.

В React 19 можно передать начальное отложенное значение:

```tsx
const deferredQuery =
  useDeferredValue(
    query,
    "",
  );
```

На первом render будет возвращён `initialValue`, после чего React запланирует фоновый render с фактическим `value`.

На последующих обновлениях `initialValue` больше не используется.

Если исходное обновление уже выполняется внутри Transition, `useDeferredValue` возвращает новое значение и не создаёт дополнительный отложенный render, потому что само обновление уже несрочное.

Разница между API заключается в точке управления:

| API | Что откладывается |
| --- | --- |
| `useTransition` | Конкретное обновление состояния, setter которого доступен текущему коду |
| `useDeferredValue` | Использование уже полученного значения в части дерева |

`useTransition` выбирают, когда код контролирует setter:

```tsx
startTransition(() => {
  setSelectedTab(nextTab);
});
```

`useDeferredValue` выбирают, когда значение:

- уже существует;
- приходит как prop;
- возвращается другим hook;
- должно срочно использоваться в одной части дерева и несрочно — в другой.

Например:

```tsx
function SearchResults({
  query,
}: {
  query: string;
}) {
  const deferredQuery =
    useDeferredValue(query);

  return (
    <SlowResults
      query={deferredQuery}
    />
  );
}
```

Чтобы отложенный prop действительно помог тяжёлому дочернему компоненту, тот должен уметь пропустить срочный render, пока значение не изменилось.

Например:

```tsx
const SlowResults =
  memo(function SlowResults({
    query,
  }: {
    query: string;
  }) {
    return (
      <ExpensiveList
        query={query}
      />
    );
  });
```

Без `memo` родитель рендерится с новым `query`, и `SlowResults` также будет вызван, хотя `deferredQuery` пока остался прежним.

Аналогичную оптимизацию может выполнить React Compiler.

В `useDeferredValue` лучше передавать:

- примитив;
- стабильный объект;
- объект, созданный вне render;
- объект, мемоизированный по обоснованной причине.

Нежелательно:

```tsx
const deferredFilters =
  useDeferredValue({
    query,
    category,
  });
```

Новый объект создаётся при каждом render и считается изменившимся по `Object.is`, что может запускать лишние фоновые обновления.

Лучше передать отдельные примитивы или стабильное значение:

```tsx
const deferredQuery =
  useDeferredValue(query);

const deferredCategory =
  useDeferredValue(category);
```

Признак временно устаревшего интерфейса можно вычислить сравнением исходного и отложенного значения:

```tsx
const isStale =
  query !== deferredQuery;
```

Например:

```tsx
<div
  style={{
    opacity:
      isStale ? 0.6 : 1,
  }}
>
  <Results
    query={deferredQuery}
  />
</div>
```

Так пользователь продолжает видеть прежние результаты и одновременно понимает, что они обновляются.

`useDeferredValue` не добавляет фиксированную задержку.

React начинает фоновый render как можно скорее после срочного render.

На быстром устройстве отставание может быть почти незаметным. На медленном устройстве оно будет больше.

Фоновый render:

- имеет меньший приоритет;
- может быть прерван;
- начинается заново после нового значения;
- не запускает Effects, пока не будет успешно применён через commit.

Если фоновый render приостановился из-за Suspense, пользователь продолжает видеть прежнее deferred-содержимое до готовности нового.

Transition также интегрирован с Suspense.

Если уже показанное содержимое снова приостанавливается из-за Transition, React старается сохранить его вместо немедленной замены ближайшим `fallback`.

```text
старый экран уже показан
→ transition к новому экрану
→ новый экран ожидает ресурс
→ старый экран пока остаётся видимым
```

`isPending` позволяет показать индикатор внутри существующего интерфейса.

Однако Transition не ждёт готовности вообще всех вложенных данных.

Новая Suspense-граница, которая ещё не показывала содержимое, может отобразить собственный `fallback`.

Первая загрузка, для которой прежнего интерфейса ещё нет, также показывает fallback.

`useTransition` и `useDeferredValue` не являются debounce или throttle.

Debounce ждёт паузу заданной длительности:

```text
ввод
→ ожидание 300 мс
→ запуск работы
```

Throttle ограничивает максимальную частоту запуска:

```text
не чаще одного раза
за указанный интервал
```

Transition может начать render сразу:

```text
ввод
→ срочное обновление поля
→ немедленная попытка фонового render
```

Если пользователь продолжает ввод, React прерывает устаревший render.

`useDeferredValue` также не гарантирует уменьшение числа сетевых запросов.

Он управляет приоритетом render, но:

- не устанавливает задержку;
- не отменяет запрос;
- не устраняет одинаковые запросы;
- не защищает от устаревшего ответа;
- не реализует кеш.

Для уменьшения числа запросов используют:

- debounce;
- кеш;
- дедупликацию;
- `AbortController`;
- проверку актуальности ответа.

Эти подходы можно сочетать:

```text
debounce
→ уменьшает число запросов

useDeferredValue
→ сохраняет отзывчивость render
```

`useTransition` и `useDeferredValue` не уменьшают автоматически общий объём вычислений.

Они меняют приоритет и позволяют отбросить незавершённый render, но не делают тяжёлую функцию быстрее.

React может уступать главный поток между частями собственной работы.

Однако произвольная долгая синхронная функция внутри одного компонента не может быть прервана посередине:

```tsx
function SlowComponent() {
  const result =
    runVeryLongCalculation();

  return <View data={result} />;
}
```

Пока `runVeryLongCalculation()` выполняется, главный поток заблокирован.

В таком случае рассматривают:

- оптимизацию алгоритма;
- мемоизацию;
- виртуализацию;
- уменьшение объёма данных;
- дробление вычисления;
- Web Worker.

В React 19 функция, переданная в `startTransition`, может быть асинхронной:

```tsx
startTransition(
  async () => {
    await saveChanges();
  },
);
```

Ожидание асинхронной Action учитывается в `isPending`.

Но обновление состояния после `await` пока нужно повторно обернуть в `startTransition`:

```tsx
startTransition(
  async () => {
    const result =
      await saveChanges();

    startTransition(() => {
      setResult(result);
    });
  },
);
```

Это текущее ограничение React.

Также Transition сам по себе не гарантирует порядок завершения нескольких асинхронных запросов.

Например:

```text
запрос A начался первым
запрос B начался вторым
запрос B завершился первым
запрос A завершился последним
```

Поздний ответ A может перезаписать более актуальный результат B.

Для сохранения порядка используют:

- `useActionState`;
- form Actions;
- очередь операций;
- отмену предыдущего запроса;
- идентификатор актуального запроса;
- проверку актуальности ответа.

Несколько одновременно выполняющихся Transitions React сейчас может объединять.

Поэтому один `isPending` не всегда соответствует ровно одной предметной операции.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong><code>useTransition</code> является debounce?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Debounce запускает работу только после паузы:

```text
ввод
→ ожидание
→ запуск
```

Transition выполняет Action сразу, но помечает запланированные обновления как несрочные:

```text
ввод
→ срочное обновление
→ фоновый render
```

React может начать render немедленно, прервать его и повторить после следующего ввода.

Debounce может сократить число запросов к API.

Transition предназначен прежде всего для управления приоритетом React-render.

В поиске их можно сочетать:

```text
debounce
→ ограничивает запросы

transition
→ сохраняет отзывчивость интерфейса
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда выбирать <code>useTransition</code>, а когда <code>useDeferredValue</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useTransition` выбирают, когда код контролирует setter несрочного состояния:

```tsx
startTransition(() => {
  setTab(nextTab);
});
```

`useDeferredValue` выбирают, когда значение уже существует или приходит как prop:

```tsx
const deferredQuery =
  useDeferredValue(query);
```

Упрощённо:

```text
есть доступ к setter
→ useTransition

есть только готовое значение
→ useDeferredValue
```

Оба решения наиболее полезны, когда тяжёлое поддерево способно пропустить срочный render при прежних входных данных, например благодаря `memo` или React Compiler.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему состояние текстового поля нельзя обновлять в transition?</strong></summary>

<dl>
<dd>
<h2></h2>

Управляемое поле должно сразу получить новое значение после `onChange`.

Если обновлять его состояние как Transition:

```tsx
startTransition(() => {
  setQuery(
    event.target.value,
  );
});
```

React может отложить render, а поле временно останется со старым `value`.

Это приводит к запаздыванию или возврату введённого значения.

Правильно обновить состояние поля срочно:

```tsx
setQuery(
  event.target.value,
);
```

а тяжёлую часть отделить:

```tsx
const deferredQuery =
  useDeferredValue(query);
```

либо обновить отдельное состояние внутри Transition.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Отправляет ли <code>useDeferredValue</code> меньше запросов?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет такой гарантии.

`useDeferredValue`:

- не устанавливает временную задержку;
- не отменяет запросы;
- не реализует кеш;
- не устраняет одинаковые запросы.

Он откладывает React-render части интерфейса.

Для сокращения запросов используют:

- debounce;
- кеш;
- дедупликацию;
- `AbortController`;
- защиту от устаревших ответов.

Даже если запрос связан с deferred-значением, нельзя строить сетевую стратегию на предположении, что React обязательно пропустит все промежуточные значения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему transition не спасает от тяжёлой синхронной функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Пока функция непрерывно выполняется, главный поток не может обработать ввод или нарисовать следующий кадр:

```tsx
const result =
  calculateLargeDataset(data);
```

React умеет уступать поток между частями собственной render-работы, но не может прервать произвольный JavaScript-вызов посередине.

Такое вычисление:

- оптимизируют;
- мемоизируют;
- делят на части;
- уменьшают по объёму;
- выносят в Web Worker.

Transition меняет приоритет render, но не ускоряет сам алгоритм.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как transitions взаимодействуют с Suspense?</strong></summary>

<dl>
<dd>
<h2></h2>

Если уже показанный интерфейс обновляется внутри Transition и новое дерево приостанавливается, React старается сохранить прежнее содержимое вместо немедленного показа ближайшего `fallback`.

```text
показан старый экран
→ начался Transition
→ новый экран ожидает данные
→ старый экран пока остаётся видимым
```

Через `isPending` можно показать индикатор в существующем интерфейсе.

Но Transition не ждёт готовности всех новых вложенных границ.

Новая Suspense-граница, содержимое которой ещё не было показано, может отобразить собственный fallback.

При первой загрузке без прежнего содержимого fallback также показывается.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен второй аргумент <code>initialValue</code> у <code>useDeferredValue</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Сигнатура выглядит так:

```tsx
useDeferredValue(
  value,
  initialValue,
);
```

На первоначальном render React возвращает `initialValue`, а затем запускает фоновый render с фактическим `value`.

Например:

```tsx
const deferredQuery =
  useDeferredValue(
    query,
    "",
  );
```

Если второй аргумент не передан, первый render сразу возвращает исходное `value`, потому что предыдущего значения ещё нет.

На последующих обновлениях `initialValue` не используется.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Поиск по большой таблице | Срочное обновление поля и `useDeferredValue` для списка |
| Переключение тяжёлой вкладки | `startTransition` и локальный `isPending` |
| Навигация с Suspense | Transition сохраняет уже показанный экран |
| Асинхронная Action | Повторный `startTransition` для setter после `await` |
| Несколько конкурирующих запросов | `useActionState`, отмена или проверка актуальности |
| Частые запросы поиска | Debounce и отмена, а не только отложенное значение |
| Тысячи строк | Виртуализация вместе с приоритетами |
| Тяжёлый расчёт на CPU | Web Worker или оптимизация алгоритма |

## Связанные темы

- [02 Обновление интерфейса в React](<./02 Обновление интерфейса в React.md>)
- [15 Suspense lazy и разделение кода](<./15 Suspense lazy и разделение кода.md>)
- [22 Диагностика производительности React](<./22 Диагностика производительности React.md>)
- [38 Web Workers и передача данных](<../JavaScript/38 Web Workers и передача данных.md>)
- [04 Fetch API и управление запросом](<../Web API/04 Fetch API и управление запросом.md>)

## Источники

- [React: `useTransition`](https://react.dev/reference/react/useTransition)
- [React: `useDeferredValue`](https://react.dev/reference/react/useDeferredValue)
- [React: `startTransition`](https://react.dev/reference/react/startTransition)
- [React: `<Suspense>`](https://react.dev/reference/react/Suspense)
- [React: `useActionState`](https://react.dev/reference/react/useActionState)
- [React 18: Transitions](https://react.dev/blog/2022/03/29/react-v18)
- [React 19: Actions](https://react.dev/blog/2024/12/05/react-19)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 15 Suspense lazy и разделение кода](<./15 Suspense lazy и разделение кода.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 SSR SSG и hydration в React →](<./17 SSR SSG и hydration в React.md>)
<!-- CARD-NAV-BOTTOM:END -->
