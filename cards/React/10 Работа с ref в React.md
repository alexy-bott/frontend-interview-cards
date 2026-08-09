# Работа с ref в React

<!-- CARD-NAV-TOP:START -->
[← 09 Мемоизация в React](<./09 Мемоизация в React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Context →](<./11 Context.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Для чего нужен `useRef`? Как связаны DOM-ссылка, `forwardRef`, передача `ref` как prop и `useImperativeHandle`?**

<h2></h2>

<br>
<dl>
<dd>

`useRef` возвращает изменяемый объект с полем:

```ts
{
  current: value;
}
```

При следующих рендерах React возвращает тот же ref-объект.

Начальное значение используется только при инициализации:

```tsx
const valueRef =
  useRef(initialValue);
```

Изменение:

```tsx
valueRef.current = nextValue;
```

не запускает render, потому что React не отслеживает запись в `current` как обновление интерфейса.

Поэтому `ref` подходит для значения, которое:

- должно сохраняться между рендерами;
- относится к конкретному экземпляру компонента;
- требуется обработчикам или внешнему API;
- не определяет отображаемый JSX.

Если пользователь должен увидеть новое значение, используют `state`, а не `ref`.

Неправильно хранить отображаемый счётчик только в `ref`:

```tsx
function Counter() {
  const countRef = useRef(0);

  function increment() {
    countRef.current += 1;
  }

  return (
    <button onClick={increment}>
      {countRef.current}
    </button>
  );
}
```

Значение изменится, но React не выполнит новый render, поэтому текст кнопки не обновится.

Для отображаемого значения нужен `state`:

```tsx
const [
  count,
  setCount,
] = useState(0);
```

Основные сценарии `useRef`:

1. Получить DOM-узел, чтобы сфокусировать поле, прокрутить контейнер или измерить его положение.
2. Сохранить идентификатор таймера, экземпляр сторонней библиотеки или другое значение экземпляра компонента.
3. Предоставить родителю небольшой императивный API дочернего компонента.

Пример DOM-ref:

```tsx
function Search() {
  const inputRef =
    useRef<HTMLInputElement>(
      null,
    );

  function handleFocus() {
    inputRef.current?.focus();
  }

  return (
    <>
      <input ref={inputRef} />

      <button
        type="button"
        onClick={handleFocus}
      >
        Focus
      </button>
    </>
  );
}
```

Для DOM-ref обычно передают начальное значение:

```ts
null
```

Во время первого render DOM-узел ещё не создан, поэтому:

```ts
inputRef.current
```

равен `null`.

Во время commit React присоединяет DOM-узел и устанавливает:

```ts
inputRef.current =
  HTMLInputElement
```

При отсоединении узла React очищает ссылку:

```ts
inputRef.current = null
```

Работа с DOM обычно выполняется:

- в обработчике события;
- в `useEffect`;
- в `useLayoutEffect`, если результат нужен до следующего paint.

Например, focus после клика:

```tsx
function handleClick() {
  inputRef.current?.focus();
}
```

Измерение перед отображением кадра:

```tsx
useLayoutEffect(() => {
  const rect =
    elementRef.current
      ?.getBoundingClientRect();

  // Использование размеров.
}, []);
```

Читать или записывать `ref.current` во время render обычно нельзя.

Render должен зависеть от:

- `props`;
- `state`;
- Context.

`Ref` может измениться без уведомления React, поэтому использование его текущего значения для JSX делает результат непредсказуемым.

Допускается предсказуемая одноразовая инициализация:

```tsx
const playerRef =
  useRef<Player | null>(
    null,
  );

if (playerRef.current === null) {
  playerRef.current =
    new Player();
}
```

Такой код допустим, если:

- условие выполняется только при инициализации;
- результат всегда детерминирован;
- запись не создаёт наблюдаемый побочный эффект;
- значение не определяет текущий JSX.

Нежелательный вариант:

```tsx
const playerRef =
  useRef(
    new Player(),
  );
```

React сохранит только первоначальное значение, но выражение:

```ts
new Player()
```

будет вычисляться при каждом вызове компонента.

Для дорогого объекта лучше использовать проверку:

```tsx
if (
  playerRef.current === null
) {
  playerRef.current =
    new Player();
}
```

В development Strict Mode React может вызвать компонент дважды для проверки чистоты.

При этом ref-объект также может быть создан дважды, но одна версия будет отброшена. Чистая и детерминированная инициализация не должна от этого ломаться.

`ref.current` не является реактивным значением.

Изменение `current`:

- не запускает render;
- не уведомляет Effect;
- не должно использоваться как скрытый канал состояния интерфейса.

Например, зависимость:

```tsx
useEffect(() => {
  // ...
}, [valueRef.current]);
```

не делает ref реактивным. React сможет проверить новую зависимость только после render, а изменение `current` само по себе render не запускает.

В React 18 функциональный компонент не получает `ref` как обычный prop.

Для передачи ref через собственный компонент используют:

```tsx
forwardRef
```

Например:

```tsx
import {
  forwardRef,
} from "react";

type MyInputProps =
  React.ComponentPropsWithoutRef<
    "input"
  >;

const MyInput =
  forwardRef<
    HTMLInputElement,
    MyInputProps
  >(function MyInput(
    props,
    ref,
  ) {
    return (
      <input
        ref={ref}
        {...props}
      />
    );
  });
```

Родитель может получить внутренний `<input>`:

```tsx
function Form() {
  const inputRef =
    useRef<HTMLInputElement>(
      null,
    );

  return (
    <MyInput
      ref={inputRef}
      placeholder="Имя"
    />
  );
}
```

Начиная с React 19 функциональный компонент может принимать `ref` как prop без `forwardRef`.

Например:

```tsx
type MyInputProps =
  React.ComponentPropsWithRef<
    "input"
  >;

function MyInput({
  ref,
  ...props
}: MyInputProps) {
  return (
    <input
      ref={ref}
      {...props}
    />
  );
}
```

Передача `ref` через собственный компонент не происходит автоматически.

Компонент должен явно:

- передать `ref` DOM-элементу;
- передать его другому компоненту;
- использовать его в `useImperativeHandle`.

Например, этот компонент принимает `ref`, но никуда его не передаёт:

```tsx
function MyInput({
  ref,
  ...props
}: MyInputProps) {
  return <input {...props} />;
}
```

Родитель не получит ссылку на внутренний `<input>`.

В React 19 `forwardRef` больше не требуется для новых функциональных компонентов.

При этом он:

- продолжает работать;
- остаётся в существующем коде;
- требуется при поддержке React 18;
- может быть необходим библиотеке с широким диапазоном React peer dependencies.

Документация React относит `forwardRef` к устаревающему API для нового React 19-кода. Его планируют удалить в одной из будущих версий, но из React 19 он не удалён.

Пробрасывать наружу весь DOM-узел не всегда правильно.

Например, внешний код, получивший `<input>`, сможет:

- менять стили;
- заменять значение;
- обращаться к любому DOM API;
- зависеть от внутренней разметки компонента.

`useImperativeHandle` позволяет заменить раскрываемый DOM-узел небольшим объектом с разрешёнными методами.

Например:

```tsx
import {
  useImperativeHandle,
  useRef,
} from "react";

type MyInputHandle = {
  focus(): void;
  select(): void;
};

type MyInputProps =
  React.ComponentPropsWithoutRef<
    "input"
  > & {
    ref?: React.Ref<
      MyInputHandle
    >;
  };

function MyInput({
  ref,
  ...props
}: MyInputProps) {
  const inputRef =
    useRef<HTMLInputElement>(
      null,
    );

  useImperativeHandle(
    ref,
    () => ({
      focus() {
        inputRef.current
          ?.focus();
      },

      select() {
        inputRef.current
          ?.select();
      },
    }),
    [],
  );

  return (
    <input
      ref={inputRef}
      {...props}
    />
  );
}
```

Родитель получает только ограниченный контракт:

```tsx
function Form() {
  const inputRef =
    useRef<MyInputHandle>(
      null,
    );

  function handleEdit() {
    inputRef.current?.focus();
    inputRef.current?.select();
  }

  return (
    <>
      <MyInput
        ref={inputRef}
      />

      <button
        type="button"
        onClick={handleEdit}
      >
        Редактировать
      </button>
    </>
  );
}
```

Родитель не получает весь DOM-узел и не зависит от того, каким элементом реализован `MyInput`.

Сигнатура Hook:

```tsx
useImperativeHandle(
  ref,
  createHandle,
  dependencies,
);
```

`createHandle` возвращает значение, которое получит родитель:

```tsx
() => ({
  focus() {
    // ...
  },
})
```

В массив зависимостей включают все реактивные значения, прочитанные внутри `createHandle`.

React сравнивает их через:

```ts
Object.is
```

Если зависимость изменилась, React создаст новый handle и назначит его переданному `ref`.

Если массив зависимостей пропущен, handle создаётся заново после каждого render.

Императивный API используют только для поведения, которое трудно выразить декларативно:

- focus;
- прокрутка;
- выделение текста;
- измерение;
- запуск императивной анимации;
- управление сторонним виджетом.

Если поведение можно выразить через `props`, обычно выбирают декларативный контракт.

Например, вместо:

```tsx
modalRef.current?.open();
modalRef.current?.close();
```

предпочтительнее:

```tsx
<Modal isOpen={isOpen} />
```

Callback ref — это `ref` в виде функции:

```tsx
<div
  ref={(node) => {
    if (node) {
      node.focus();
    }
  }}
/>
```

React вызывает callback при присоединении узла и передаёт ему DOM-элемент.

Начиная с React 19 callback ref может вернуть cleanup-функцию:

```tsx
<div
  ref={(node) => {
    if (node === null) {
      return;
    }

    observer.observe(node);

    return () => {
      observer.unobserve(
        node,
      );
    };
  }}
/>
```

React вызовет cleanup, когда:

- узел отсоединится;
- компонент размонтируется;
- callback ref заменится другой функцией.

Если callback не возвращает cleanup, React при отсоединении вызывает его с:

```ts
null
```

Если cleanup возвращён, React использует его и не обязан дополнительно вызывать callback с `null`.

Новая inline callback-функция создаётся при каждом render:

```tsx
<div
  ref={(node) => {
    // ...
  }}
/>
```

Если её identity изменилась, React очищает прежний ref и устанавливает новый.

Это обычно не проблема, но для дорогой подписки callback можно сделать стабильным:

```tsx
const handleRef =
  useCallback(
    (
      node:
        HTMLDivElement | null,
    ) => {
      if (node === null) {
        return;
      }

      observer.observe(node);

      return () => {
        observer.unobserve(
          node,
        );
      };
    },
    [observer],
  );
```

В development Strict Mode callback refs получают дополнительный цикл установки и очистки, чтобы обнаружить отсутствующий cleanup.

Callback ref не должен случайно возвращать результат присваивания.

Нежелательно:

```tsx
<div
  ref={(node) =>
    (element = node)
  }
/>
```

Выражение присваивания возвращает присвоенное значение.

В React 19 TypeScript ожидает от callback ref:

- `void`;
- либо cleanup-функцию.

Нужно использовать тело функции без неявного возврата:

```tsx
<div
  ref={(node) => {
    element = node;
  }}
/>
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему изменение <code>ref.current</code> не вызывает рендер?</strong></summary>

<dl>
<dd>
<h2></h2>

`Ref` является обычным изменяемым JavaScript-объектом:

```ts
{
  current: value;
}
```

React возвращает один и тот же объект между рендерами, но не отслеживает каждую запись в:

```ts
ref.current
```

Поэтому изменение:

```tsx
timerRef.current =
  window.setTimeout(
    callback,
    1000,
  );
```

не запускает render.

Это полезно для хранения:

- таймеров;
- DOM-узлов;
- экземпляров библиотек;
- последних служебных значений.

Если изменение должно повлиять на JSX, нужен `state`.

`Ref` не следует использовать как скрытое состояние только ради предотвращения рендера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>useRef</code> отличается от переменной на уровне модуля?</strong></summary>

<dl>
<dd>
<h2></h2>

Каждый смонтированный экземпляр компонента получает собственный ref.

Например:

```tsx
<VideoPlayer />
<VideoPlayer />
```

два компонента получают два независимых:

```ts
playerRef
```

Переменная на уровне модуля общая для всех экземпляров в одной среде выполнения JavaScript:

```ts
let player:
  Player | null = null;
```

Два компонента начнут читать и изменять одно значение.

Это может привести к смешению:

- таймеров;
- DOM-узлов;
- подписок;
- экземпляров сторонних библиотек.

`useRef` связывает значение с жизненным циклом конкретного компонента.

На уровне модуля хранят только намеренно общие:

- константы;
- кеши;
- инфраструктурные singleton-объекты;
- данные с отдельным механизмом управления жизненным циклом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли читать <code>ref.current</code> во время рендера?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет.

Render должен вычислять JSX из реактивных входов:

- `props`;
- `state`;
- Context.

`Ref` может измениться без нового render, поэтому JSX, зависящий от `ref.current`, может не соответствовать фактическому значению.

Нежелательно:

```tsx
function Player() {
  const isPlayingRef =
    useRef(false);

  return (
    <p>
      {isPlayingRef.current
        ? "Играет"
        : "Остановлено"}
    </p>
  );
}
```

Для отображаемого состояния нужен `useState`.

Допустимая граница — детерминированная одноразовая инициализация:

```tsx
const playerRef =
  useRef<Player | null>(
    null,
  );

if (
  playerRef.current === null
) {
  playerRef.current =
    new Player();
}
```

Результат должен быть одинаковым и не создавать наблюдаемого побочного эффекта во время render.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong><code>forwardRef</code> больше не нужен в React 19?</strong></summary>

<dl>
<dd>
<h2></h2>

Для новых функциональных компонентов React 19 можно принимать `ref` как prop:

```tsx
type InputProps =
  React.ComponentPropsWithRef<
    "input"
  >;

function Input({
  ref,
  ...props
}: InputProps) {
  return (
    <input
      ref={ref}
      {...props}
    />
  );
}
```

Поэтому `forwardRef` для такого кода больше не требуется.

Но он остаётся:

- рабочим в React 19;
- необходимым для React 18;
- распространённым в существующем коде;
- необходимым библиотеке, поддерживающей React 18.

Удалять `forwardRef` из библиотеки можно только после изменения минимальной поддерживаемой версии React и проверки публичных TypeScript-типов.

Передача `ref` как prop относится к функциональным компонентам.

У классового компонента `ref` по-прежнему ссылается на экземпляр класса и не передаётся ему как обычный prop.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>useImperativeHandle</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`useImperativeHandle` заменяет значение, которое родитель получает через `ref`.

Вместо всего DOM-узла можно предоставить небольшой публичный API:

```ts
type InputHandle = {
  focus(): void;
  select(): void;
};
```

Внутри компонент сохраняет настоящий DOM-ref:

```tsx
const inputRef =
  useRef<HTMLInputElement>(
    null,
  );
```

и раскрывает только разрешённые операции:

```tsx
useImperativeHandle(
  ref,
  () => ({
    focus() {
      inputRef.current
        ?.focus();
    },

    select() {
      inputRef.current
        ?.select();
    },
  }),
  [],
);
```

Это уменьшает связанность родителя с внутренней разметкой дочернего компонента.

Массив зависимостей должен содержать все реактивные значения, использованные внутри `createHandle`.

При их изменении React назначит ref новый handle.

`useImperativeHandle` не следует использовать для обычного потока данных. Значения интерфейса лучше передавать через `props`, а события — через callbacks.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что изменилось у callback refs в React 19?</strong></summary>

<dl>
<dd>
<h2></h2>

В React 19 callback ref может вернуть функцию очистки:

```tsx
<div
  ref={(node) => {
    if (node === null) {
      return;
    }

    observer.observe(node);

    return () => {
      observer.unobserve(
        node,
      );
    };
  }}
/>
```

React вызовет cleanup, когда:

- узел будет отсоединён;
- компонент размонтируется;
- callback ref заменится другой функцией.

Если cleanup возвращён, React использует его вместо прежней модели обязательного вызова callback с `null`.

Если cleanup не возвращён, callback при отсоединении по-прежнему может быть вызван с `null`.

Из-за нового контракта TypeScript отклоняет callback, который неявно возвращает DOM-узел или результат присваивания:

```tsx
ref={(node) =>
  (element = node)
}
```

Нужно явно ничего не возвращать:

```tsx
ref={(node) => {
  element = node;
}}
```

Либо вернуть настоящую cleanup-функцию.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Решение |
| --- | --- |
| Фокус после открытия диалога | DOM-ref и вызов `focus()` в подходящий момент |
| Измерение элемента | Ref и точечный `useLayoutEffect` |
| Идентификатор таймера | `useRef`, если значение не влияет на JSX |
| Экземпляр карты или редактора | Ref плюс setup и cleanup интеграции |
| Дорогая инициализация объекта | Предсказуемая запись при `ref.current === null` |
| Поле ввода дизайн-системы | `ref` как prop в React 19 или `forwardRef` для React 18 |
| Ограниченный императивный API | `useImperativeHandle` |
| Подписка на конкретный DOM-узел | Callback ref с cleanup |

## Связанные темы

- [07 Эффекты React и cleanup](<./07 Эффекты React и cleanup.md>)
- [13 Portal](<./13 Portal.md>)
- [19 Версии React 18 19 и 19.2](<./19 Версии React 18 19 и 19.2.md>)
- [25 Продвинутая типизация React-компонентов](<../TypeScript/25 Продвинутая типизация React-компонентов.md>)

## Источники

- [React: `useRef`](https://react.dev/reference/react/useRef)
- [React: Manipulating the DOM with Refs](https://react.dev/learn/manipulating-the-dom-with-refs)
- [React: `useImperativeHandle`](https://react.dev/reference/react/useImperativeHandle)
- [React: `forwardRef`](https://react.dev/reference/react/forwardRef)
- [React: Common components and callback refs](https://react.dev/reference/react-dom/components/common)
- [React: StrictMode](https://react.dev/reference/react/StrictMode)
- [React 19: ref as a prop and callback ref cleanup](https://react.dev/blog/2024/12/05/react-19)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Мемоизация в React](<./09 Мемоизация в React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Context →](<./11 Context.md>)
<!-- CARD-NAV-BOTTOM:END -->
