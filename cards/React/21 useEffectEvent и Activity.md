# useEffectEvent и Activity

<!-- CARD-NAV-TOP:START -->
[← 20 React Compiler](<./20 React Compiler.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [22 Performance profiling и оптимизация React →](<./22 Performance profiling и оптимизация React.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое `useEffectEvent` и `<Activity>`? В какой версии React они появились?**

<h2></h2>

<br>
<dl>
<dd>

`useEffectEvent` и `<Activity>` появились в стабильном React 19.2, выпущенном 1 октября 2025 года.

`useEffectEvent` отделяет нереактивную логику события от реактивной синхронизации эффекта. `<Activity>` скрывает часть интерфейса с сохранением React- и DOM-состояния, очищает её эффекты и позволяет React обрабатывать скрытую работу с меньшим приоритетом.

Эффект должен повторно синхронизироваться при изменении каждого реактивного значения, от которого зависит его подключение к внешней системе.

Но callback внешней системы иногда должен прочитать актуальные `props` или state, не превращая их в причину переподключения.

Например, соединение зависит от `roomId`, а текст уведомления — от текущей `theme`:

```tsx
function ChatRoom({ roomId, theme }) {
  const onConnected = useEffectEvent(() => {
    showNotification("Connected", theme);
  });

  useEffect(() => {
    const connection = createConnection(roomId);

    connection.on("connected", onConnected);
    connection.connect();

    return () => connection.disconnect();
  }, [roomId]);
}
```

`roomId` используется самой логикой подключения, поэтому остаётся реактивной зависимостью эффекта.

`theme` используется только при отдельном событии `connected`, поэтому находится внутри Effect Event и не заставляет React пересоздавать соединение.

Effect Event при вызове читает последние зафиксированные React значения:

- `props`;
- state;
- значения, вычисленные во время последнего завершённого рендера.

Он не читает значения из ещё не завершённого concurrent render.

Effect Event можно вызывать только:

- внутри `useEffect`;
- внутри `useLayoutEffect`;
- внутри `useInsertionEffect`;
- внутри другого Effect Event того же компонента или custom hook.

Его нельзя вызывать:

- во время рендера;
- из обычного `onClick`;
- из произвольной функции вне эффекта;
- после передачи другому компоненту;
- после передачи в другой custom hook.

Например, так использовать Effect Event нельзя:

```tsx
function Component() {
  const onEvent = useEffectEvent(() => {
    console.log("Event");
  });

  return (
    <button onClick={onEvent}>
      Нажать
    </button>
  );
}
```

Для обработчика пользовательского события используют обычную функцию или `useCallback`.

Сам `useEffectEvent` при этом можно использовать внутри custom hook, если Effect Event остаётся рядом с эффектом, который его вызывает:

```tsx
function useInterval(
  callback: () => void,
  delay: number,
) {
  const onTick = useEffectEvent(callback);

  useEffect(() => {
    const intervalId = setInterval(
      onTick,
      delay,
    );

    return () => {
      clearInterval(intervalId);
    };
  }, [delay]);
}
```

В этом примере внешний `callback` может меняться при каждом рендере, но таймер не перезапускается только из-за новой ссылки. При каждом тике Effect Event вызывает последнюю версию callback.

Функция, возвращённая `useEffectEvent`, намеренно не имеет стабильной идентичности. Её ссылка может изменяться при каждом рендере.

Поэтому Effect Event нельзя добавлять в массив зависимостей:

```tsx
useEffect(() => {
  onConnected();
}, [onConnected]);
```

Актуальный `eslint-plugin-react-hooks` потребует удалить Effect Event из зависимостей:

```tsx
useEffect(() => {
  onConnected();
}, []);
```

Effect Event исключается из зависимостей не потому, что React автоматически мемоизировал функцию, а потому, что он является нереактивной частью логики эффекта.

`useEffectEvent` не является способом скрыть любую зависимость от `exhaustive-deps`.

Например, так делать неправильно:

```tsx
const connect = useEffectEvent(() => {
  const connection = createConnection(roomId);
  connection.connect();
});

useEffect(() => {
  connect();
}, []);
```

Здесь изменение `roomId` должно пересоздать соединение. Следовательно, `roomId` относится к реактивной части эффекта и должен оставаться зависимостью:

```tsx
const onConnected = useEffectEvent(() => {
  showNotification("Connected", theme);
});

useEffect(() => {
  const connection = createConnection(roomId);

  connection.on("connected", onConnected);
  connection.connect();

  return () => {
    connection.disconnect();
  };
}, [roomId]);
```

`<Activity>` в React 19.2 имеет два режима:

| Режим | Поведение |
| --- | --- |
| `visible` | Показывает `children`, создаёт эффекты и обрабатывает обновления с обычным приоритетом |
| `hidden` | Скрывает `children`, очищает эффекты, сохраняет состояние и откладывает скрытые обновления до освобождения React |

Если `mode` не передан, используется:

```text
visible
```

Пример:

```tsx
<Activity
  mode={
    activeTab === "draft"
      ? "visible"
      : "hidden"
  }
>
  <DraftEditor />
</Activity>
```

При обычном условном рендере:

```tsx
{isVisible && <DraftEditor />}
```

компонент удаляется из React-дерева.

React:

- выполняет cleanup эффектов;
- уничтожает локальное state компонента;
- удаляет DOM;
- при следующем показе монтирует компонент заново.

При использовании Activity:

```tsx
<Activity
  mode={isVisible ? "visible" : "hidden"}
>
  <DraftEditor />
</Activity>
```

React концептуально размонтирует скрытую часть с точки зрения эффектов, но сохраняет:

- локальное state;
- React-дерево;
- существующие DOM-узлы;
- внутреннее DOM-состояние элементов.

Например, могут сохраниться:

- введённый текст неконтролируемого `<textarea>`;
- выбранное значение нативного элемента;
- позиция воспроизведения media-элемента;
- состояние вложенных React-компонентов.

При переходе в `hidden` React очищает:

- layout effects;
- пассивные effects;
- активные подписки, для которых реализован cleanup.

При возврате в `visible` React:

- показывает сохранённый DOM;
- восстанавливает прежнее state;
- заново запускает эффекты.

Поэтому эффекты внутри Activity должны иметь симметричные setup и cleanup:

```tsx
useEffect(() => {
  const connection = createConnection();
  connection.connect();

  return () => {
    connection.disconnect();
  };
}, []);
```

Скрытые компоненты не полностью замораживаются.

Они продолжают получать новые props и могут повторно рендериться, но React обрабатывает такие обновления с меньшим приоритетом, чем работу видимого интерфейса.

Скрытый Activity также можно использовать для подготовки вероятного следующего экрана:

```tsx
<Suspense fallback={null}>
  <Activity mode="hidden">
    <ReportsPage />
  </Activity>
</Suspense>
```

React может с меньшим приоритетом:

- отрендерить скрытое дерево;
- загрузить необходимый JavaScript;
- прочитать данные через Suspense;
- подготовить изображения и другие ресурсы.

Это может уменьшить задержку при последующем переходе в режим `visible`.

Но Activity не гарантирует мгновенное открытие. Результат зависит от:

- Suspense;
- доступного времени главного потока;
- скорости сети;
- кеширования;
- интеграции фреймворка;
- способа загрузки данных.

Activity заранее загружает только данные, чтение которых участвует в Suspense, например Promise, прочитанный через `use`.

Запрос внутри эффекта не запускается во время скрытого предварительного рендера, потому что эффекты скрытого Activity не монтируются:

```tsx
useEffect(() => {
  fetch("/api/reports");
}, []);
```

Для такого запроса предварительная подготовка через Activity сама по себе не сработает.

Activity обычно скрывает дочерние DOM-элементы через:

```css
display: none;
```

DOM при этом не уничтожается.

Из-за этого нативное поведение некоторых DOM-элементов может продолжаться даже после очистки React effects.

Например:

- `<video>` может продолжить воспроизведение;
- `<audio>` может продолжить проигрывать звук;
- `<iframe>` может продолжить выполнять загруженную страницу.

Такой ресурс нужно останавливать явно:

```tsx
function VideoPlayer() {
  const videoRef =
    useRef<HTMLVideoElement>(null);

  useLayoutEffect(() => {
    const video = videoRef.current;

    return () => {
      video?.pause();
    };
  }, []);

  return (
    <video
      ref={videoRef}
      controls
      src="/video.mp4"
    />
  );
}
```

`useLayoutEffect` подходит здесь, потому что остановка непосредственно связана с моментом визуального скрытия элемента. Cleanup обычного `useEffect` в некоторых сценариях может выполниться позднее.

Activity сохраняет больше DOM, React-дерева и состояния в памяти, чем обычное размонтирование.

Поэтому его не нужно использовать для каждой условной ветки.

Activity подходит, когда:

- пользователь скоро вернётся к экрану;
- нужно сохранить введённые данные;
- повторное создание интерфейса дорого;
- следующий экран полезно подготовить заранее.

Обычное размонтирование предпочтительнее, когда:

- содержимое больше не понадобится;
- повторное монтирование дёшево;
- дерево занимает много памяти;
- state не нужно сохранять;
- ресурсы лучше полностью освободить.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>useEffectEvent</code> отличается от <code>useCallback</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useCallback` кеширует функцию относительно массива зависимостей:

```tsx
const handleClick = useCallback(() => {
  submit(productId);
}, [productId]);
```

Такую функцию можно:

- передавать как prop;
- использовать как обработчик события;
- передавать внешнему API;
- включать в зависимости эффекта.

Effect Event имеет другое назначение.

Он:

- вызывается только из Effects или других Effect Events;
- всегда читает последние зафиксированные `props` и state;
- не должен передаваться другому компоненту;
- не должен включаться в зависимости;
- намеренно не имеет стабильной идентичности.

`useCallback` управляет ссылкой на обычную функцию.

`useEffectEvent` выражает нереактивное событие внутри жизненного цикла эффекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какое устаревшее замыкание исправляет <code>useEffectEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Подписка создаётся для `roomId`, но её callback должен использовать актуальную `theme`.

Если пропустить `theme` из зависимостей:

```tsx
useEffect(() => {
  connection.on("connected", () => {
    showNotification(theme);
  });
}, [roomId]);
```

callback может сохранить старую тему.

Если добавить `theme`:

```tsx
}, [roomId, theme]);
```

соединение будет пересоздаваться при каждом переключении оформления.

Effect Event разделяет две части:

```text
roomId
→ управляет жизненным циклом соединения

theme
→ читается в момент события connected
```

```tsx
const onConnected = useEffectEvent(() => {
  showNotification(theme);
});

useEffect(() => {
  const connection = createConnection(roomId);

  connection.on("connected", onConnected);
  connection.connect();

  return () => connection.disconnect();
}, [roomId]);
```

Соединение не пересоздаётся из-за темы, но уведомление использует её последнее зафиксированное значение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли использовать <code>useEffectEvent</code>, чтобы подавить <code>exhaustive-deps</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Если значение определяет жизненный цикл синхронизации, оно должно оставаться зависимостью.

Например:

```tsx
const connect = useEffectEvent(() => {
  createConnection(roomId).connect();
});

useEffect(() => {
  connect();
}, []);
```

является неправильным использованием.

Изменение `roomId` должно пересоздать соединение, поэтому значение должно находиться внутри эффекта и его зависимостей.

В Effect Event выносят только логику, которая:

- вызывается событием внутри эффекта;
- должна читать актуальные значения;
- не должна самостоятельно запускать повторную синхронизацию.

Перенос всей функции эффекта в `useEffectEvent` скрывает настоящие зависимости и создаёт ошибку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем скрытый Activity отличается от условного рендера?</strong></summary>

<dl>
<dd>
<h2></h2>

Условный рендер:

```tsx
{isVisible && <Editor />}
```

полностью удаляет компонент.

При скрытии React:

- очищает эффекты;
- уничтожает локальное state;
- удаляет DOM.

Activity:

```tsx
<Activity
  mode={isVisible ? "visible" : "hidden"}
>
  <Editor />
</Activity>
```

визуально скрывает интерфейс и очищает его эффекты, но сохраняет React- и DOM-состояние.

При повторном показе пользователь продолжает работу с прежним состоянием.

Скрытые компоненты также могут обновляться с меньшим приоритетом и заранее подготавливаться к следующему показу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Работают ли эффекты внутри скрытого Activity?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

При переходе в `hidden` React выполняет cleanup эффектов дочернего дерева.

При возврате в `visible` эффекты запускаются заново.

Поэтому эффект должен корректно поддерживать повторяющийся цикл:

```text
setup
→ cleanup
→ setup
```

Например:

```tsx
useEffect(() => {
  window.addEventListener(
    "resize",
    handleResize,
  );

  return () => {
    window.removeEventListener(
      "resize",
      handleResize,
    );
  };
}, []);
```

Если эффект не имеет правильного cleanup, скрытый Activity может оставить нежелательную подписку или внешний ресурс.

Для раннего обнаружения таких ошибок полезен `StrictMode`, который в development повторно запускает setup и cleanup эффектов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Сохраняется ли DOM скрытого Activity?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, для дочерних DOM-элементов React обычно применяет:

```css
display: none;
```

и не уничтожает их.

Поэтому сохраняется внутреннее DOM-состояние, например:

- значение неконтролируемого `<textarea>`;
- позиция воспроизведения `<video>`;
- загруженный DOM сложного виджета.

React effects при этом очищаются.

Но собственные действия DOM не обязаны остановиться автоматически. Например, уже запущенное видео может продолжить воспроизведение, потому что элемент остаётся в документе.

Для такого поведения нужна явная очистка, например вызов:

```ts
video.pause();
```

из cleanup эффекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда Activity использовать не стоит?</strong></summary>

<dl>
<dd>
<h2></h2>

Activity не стоит использовать, когда скрытая часть:

- больше не понадобится;
- содержит большой объём DOM или состояния;
- удерживает дорогостоящие ресурсы;
- легко и быстро создаётся заново;
- не должна сохранять пользовательский прогресс.

Activity сохраняет ресурсы ради быстрого возврата.

Для простого раскрывающегося текста обычное условие:

```tsx
{isOpen && <Content />}
```

может быть понятнее и экономнее.

Обычный CSS подходит, когда требуется только визуально скрыть элемент, а эффекты и приоритет React менять не нужно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Инструмент |
| --- | --- |
| Подписка зависит от `roomId`, callback читает тему | `useEffectEvent` |
| Таймер должен читать актуальное состояние без перезапуска | Effect Event внутри эффекта или custom hook |
| Вкладка формы должна сохранить черновик | `<Activity>` |
| Подготовка вероятного следующего экрана | Скрытый Activity и Suspense |
| Скрытый экран не должен держать подписку | Cleanup эффектов Activity |
| Media-элемент продолжает работу после скрытия | Явный cleanup, при необходимости через `useLayoutEffect` |
| Одноразово открываемый тяжёлый экран | Обычное размонтирование может быть экономнее |

## Связанные темы

- [07 useEffect useLayoutEffect и cleanup](<./07 useEffect useLayoutEffect и cleanup.md>)
- [15 Suspense lazy и code splitting](<./15 Suspense lazy и code splitting.md>)
- [19 React 18 19 и 19.2](<./19 React 18 19 и 19.2.md>)
- [08 Замыкание](<../JavaScript/08 Замыкание.md>)

## Источники

- [React 19.2](https://react.dev/blog/2025/10/01/react-19-2)
- [React: `useEffectEvent`](https://react.dev/reference/react/useEffectEvent)
- [React: `<Activity>`](https://react.dev/reference/react/Activity)
- [React: Separating Events from Effects](https://react.dev/learn/separating-events-from-effects)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 20 React Compiler](<./20 React Compiler.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [22 Performance profiling и оптимизация React →](<./22 Performance profiling и оптимизация React.md>)
<!-- CARD-NAV-BOTTOM:END -->
