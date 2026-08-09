# Portal

<!-- CARD-NAV-TOP:START -->
[← 12 Error Boundaries](<./12 Error Boundaries.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 Управляемые и неуправляемые компоненты →](<./14 Управляемые и неуправляемые компоненты.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Portal в React? Как он влияет на Context, события, CSS и доступность всплывающих компонентов?**

<h2></h2>

<br>
<dl>
<dd>

Portal позволяет отрендерить DOM-узлы дочернего компонента в другой DOM-контейнер, сохранив компонент на прежнем месте React-дерева.

Portal создают функцией `createPortal` из `react-dom`:

```tsx
import {
  createPortal,
} from "react-dom";

function Modal({
  children,
}: {
  children:
    React.ReactNode;
}) {
  const modalRoot =
    document.getElementById(
      "modal-root",
    );

  if (modalRoot === null) {
    return null;
  }

  return createPortal(
    children,
    modalRoot,
  );
}
```

`createPortal` возвращает React node, который можно использовать в JSX как обычного ребёнка:

```tsx
function Page() {
  return (
    <main>
      <Modal>
        <p>Содержимое окна</p>
      </Modal>
    </main>
  );
}
```

Portal меняет физическое размещение DOM, но:

- не создаёт отдельное React-приложение;
- не создаёт отдельный React root;
- не меняет логического родителя компонента;
- не разрывает Context и React-события.

Portal используют для:

- модальных окон;
- tooltip;
- popover;
- выпадающих меню;
- контекстных меню;
- уведомлений;
- других overlay-компонентов.

Такой интерфейс часто должен выйти из DOM-контейнера, который создаёт ограничения:

```css
overflow: hidden;
```

или собственный stacking context, например из-за:

```css
transform: translateZ(0);
```

```css
position: relative;
z-index: 1;
```

```css
opacity: 0.9;
```

Перенос Portal ближе к:

```html
<body>
```

может помочь выйти из локального `overflow` и stacking context родительского компонента.

Но Portal сам по себе не гарантирует, что элемент окажется поверх всего интерфейса.

Нужно учитывать:

- stacking context контейнера Portal;
- `z-index` соседних слоёв;
- порядок DOM-элементов;
- системные browser overlays;
- top layer браузера.

Обычный Portal не попадает в top layer.

В top layer могут находиться, например:

- `<dialog>`, открытый через `showModal()`;
- элементы, открытые через Popover API;
- полноэкранный элемент.

Top layer располагается выше обычных stacking contexts документа.

Поэтому в некоторых сценариях нативный:

```html
<dialog>
```

может решить проблему наложения без Portal.

У Portal одновременно существуют две иерархии:

| Иерархия | Что определяет |
| --- | --- |
| React-дерево | `props`, состояние, Context, Error Boundary и всплытие React-событий |
| DOM-дерево | CSS-селекторы, наследование, расположение, `contains()`, фокус и нативное всплытие событий |

Например:

```tsx
function Page() {
  return (
    <div
      onClick={() => {
        console.log(
          "Page click",
        );
      }}
    >
      <Modal>
        <button>
          Save
        </button>
      </Modal>
    </div>
  );
}
```

Кнопка может физически находиться внутри:

```html
<body>
  <div id="modal-root">
    <button>Save</button>
  </div>
</body>
```

Но логически она остаётся дочерним элементом `Page` в React-дереве.

Context продолжает работать по React-дереву.

Если Portal создан внутри provider:

```tsx
<ThemeContext value="dark">
  <Modal>
    <DialogContent />
  </Modal>
</ThemeContext>
```

то `DialogContent` прочитает:

```tsx
const theme =
  useContext(
    ThemeContext,
  );
```

и получит значение:

```text
dark
```

Физическое расположение DOM под `body` на Context не влияет.

Так же продолжают работать:

- `props`;
- локальное состояние;
- callbacks;
- Error Boundaries;
- Suspense;
- другие React-механизмы.

React-события из Portal всплывают по React-дереву.

Например:

```tsx
function Page() {
  return (
    <div
      onClick={() => {
        console.log(
          "page click",
        );
      }}
    >
      <Modal>
        <button
          onClick={() => {
            console.log(
              "button click",
            );
          }}
        >
          Save
        </button>
      </Modal>
    </div>
  );
}
```

После клика вывод будет таким:

```text
button click
page click
```

Хотя в DOM кнопка не находится внутри `div` компонента `Page`.

Это поведение связано с React-деревом, а не с тем, что `SyntheticEvent` является отдельным видом всплытия.

`SyntheticEvent` предоставляет React-обработчикам единый интерфейс:

- `target`;
- `currentTarget`;
- `preventDefault()`;
- `stopPropagation()`;
- `nativeEvent`.

При этом нужно различать два случая:

```text
React onClick
→ распространяется по React-дереву

addEventListener
→ распространяется по DOM-дереву
```

Например, нативный обработчик:

```ts
document.addEventListener(
  "click",
  handleClick,
);
```

видит реальный DOM-путь события.

React-обработчик родителя:

```tsx
<div onClick={handleClick}>
```

может получить событие через React-дерево, даже если Portal расположен в другом DOM-контейнере.

Если React-родитель не должен обрабатывать события из Portal, можно остановить всплытие внутри содержимого:

```tsx
function DialogContent() {
  return (
    <div
      onClick={(event) => {
        event.stopPropagation();
      }}
    >
      ...
    </div>
  );
}
```

Но `stopPropagation()` следует использовать только при наличии осмысленной границы поведения.

Часто правильнее разместить обработчики ближе к тому интерфейсу, за который они отвечают.

CSS работает по физическому DOM-дереву.

Обычный класс продолжает применяться:

```tsx
<div
  className={
    styles.tooltip
  }
/>
```

CSS Modules также продолжают работать, потому что сгенерированное имя класса остаётся на DOM-элементе.

Но селектор, зависящий от DOM-предка, может перестать совпадать:

```css
.card .tooltip {
  color: white;
}
```

После переноса `.tooltip` в `modal-root` он больше не является DOM-потомком `.card`.

Поэтому этот стиль не применится.

Наследуемые свойства также берутся от реальных DOM-предков:

```css
color
font-family
line-height
```

То же относится к CSS custom properties:

```css
.card {
  --tooltip-background:
    black;
}
```

Если Portal находится вне `.card`, переменная может стать недоступной:

```css
.tooltip {
  background:
    var(
      --tooltip-background
    );
}
```

Дизайн-система обычно размещает общие токены на предке, который доступен и основному приложению, и Portal-контейнеру:

```css
:root {
  --color-background:
    white;
  --color-text:
    black;
}
```

Другие варианты:

- добавить theme-класс на `body`;
- добавить theme-класс на Portal-контейнер;
- передавать значения через Context и применять их как классы;
- создавать Portal внутри DOM-контейнера конкретной темы.

Portal помогает обойти некоторые ограничения `overflow` и stacking context, но не решает автоматически:

- позиционирование;
- размеры;
- collision detection;
- переключение стороны popover;
- адаптацию к viewport;
- scroll tracking;
- систему `z-index`.

Эти задачи реализуются отдельно.

`domNode`, переданный в `createPortal`, должен существовать к моменту рендера Portal:

```tsx
createPortal(
  children,
  domNode,
);
```

Контейнер обычно создают один раз:

```html
<div id="root"></div>
<div id="modal-root"></div>
```

и используют на протяжении всего жизненного цикла приложения.

Если во время следующего render передать другой DOM-контейнер:

```tsx
createPortal(
  children,
  anotherDomNode,
);
```

React пересоздаст Portal-содержимое в новом месте.

Это может привести к потере:

- локального React state;
- состояния неконтролируемых DOM-элементов;
- focus;
- выделения текста;
- незавершённых анимаций;
- состояния стороннего виджета.

Поэтому контейнер Portal делают стабильным.

При необходимости идентичность нескольких Portal можно дополнительно задавать третьим аргументом `key`:

```tsx
createPortal(
  children,
  domNode,
  portalKey,
);
```

На сервере отсутствуют:

```text
window
document
DOM nodes
```

Поэтому нельзя безусловно выполнять во время SSR:

```tsx
document.getElementById(
  "modal-root",
);
```

Компонент может:

- использовать предусмотренный React-фреймворком механизм;
- быть клиентским компонентом;
- получить контейнер после монтирования;
- не создавать Portal, пока DOM недоступен.

Например, для клиентского Portal:

```tsx
function Modal({
  children,
}: {
  children:
    React.ReactNode;
}) {
  const [
    container,
    setContainer,
  ] = useState<
    HTMLElement | null
  >(null);

  useEffect(() => {
    setContainer(
      document.getElementById(
        "modal-root",
      ),
    );
  }, []);

  if (container === null) {
    return null;
  }

  return createPortal(
    children,
    container,
  );
}
```

Такой подход откладывает появление содержимого до выполнения Effect.

Он подходит не для каждого интерфейса.

Если модальное содержимое должно присутствовать в первоначальном HTML, лучше использовать архитектуру и API конкретного SSR-фреймворка.

Важно, чтобы серверный HTML и первый клиентский render не противоречили друг другу.

Иначе может возникнуть hydration mismatch.

Portal решает только размещение DOM.

Полноценное модальное окно дополнительно требует:

- доступного имени;
- корректной семантики;
- управления фокусом;
- ограничения фонового взаимодействия;
- обработки клавиатуры;
- управления прокруткой;
- корректного закрытия.

Доступное имя задают через:

```tsx
aria-labelledby
```

или:

```tsx
aria-label
```

Например:

```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby={
    titleId
  }
>
  <h2 id={titleId}>
    Подтверждение
  </h2>
</div>
```

`role="dialog"` сообщает тип элемента.

`aria-modal="true"` сообщает assistive technologies, что диалог является модальным.

Но эти атрибуты сами по себе:

- не перемещают фокус;
- не удерживают Tab внутри;
- не делают фон неактивным;
- не блокируют прокрутку;
- не обрабатывают `Escape`.

При открытии модального окна обычно нужно:

1. Сохранить элемент, который открыл окно.
2. Перенести начальный фокус внутрь.
3. Ограничить перемещение Tab областью диалога.
4. Сделать фон недоступным для взаимодействия.
5. Обработать закрытие по `Escape`.
6. После закрытия вернуть фокус на открывающий элемент.

Для блокировки фонового взаимодействия может использоваться:

```html
inert
```

Но его нужно применять к правильной области приложения, не включая сам Portal.

Также часто блокируют прокрутку страницы на время открытия модального окна.

Клик по backdrop можно использовать для закрытия, но нужно отличать:

```text
клик непосредственно по backdrop
```

от:

```text
клик по содержимому диалога
```

Например:

```tsx
function Backdrop({
  onClose,
  children,
}: {
  onClose(): void;
  children:
    React.ReactNode;
}) {
  return (
    <div
      onClick={(event) => {
        if (
          event.target ===
          event.currentTarget
        ) {
          onClose();
        }
      }}
    >
      {children}
    </div>
  );
}
```

Нативный `<dialog>` с вызовом:

```ts
dialog.showModal();
```

предоставляет часть необходимого поведения:

- размещение в top layer;
- модальный режим;
- нативную семантику;
- обработку фонового взаимодействия браузером.

Но даже при использовании `<dialog>` нужно проверить:

- доступное имя;
- начальный фокус;
- возврат фокуса;
- сценарий закрытия;
- поддержку требуемых браузеров;
- поведение вложенных overlay.

Требования к доступному modal значительно сложнее самого Portal.

Поэтому в production обычно используют проверенные примитивы:

- Radix UI;
- React Aria;
- Headless UI;
- компоненты дизайн-системы с проверенной доступностью.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как всплывают события из Portal?</strong></summary>

<dl>
<dd>
<h2></h2>

Нативное событие сначала возникает на реальном DOM-узле.

React связывает этот узел с соответствующим компонентом и вызывает React-обработчики вдоль React-родителей Portal.

Например:

```tsx
function Page() {
  return (
    <div
      onClick={() => {
        console.log(
          "Page",
        );
      }}
    >
      <Modal>
        <button
          onClick={() => {
            console.log(
              "Button",
            );
          }}
        >
          Save
        </button>
      </Modal>
    </div>
  );
}
```

Кнопка физически может находиться в `modal-root`, но логически остаётся потомком `Page`.

Результат:

```text
Button
Page
```

Нативные обработчики, добавленные через `addEventListener`, ориентируются на DOM-дерево.

React-обработчики, объявленные через JSX, ориентируются на React-дерево.

Если дальнейшее React-всплытие не требуется:

```tsx
onClick={(event) => {
  event.stopPropagation();
}}
```

Но остановку события применяют только при осознанной границе поведения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Причём здесь <code>SyntheticEvent</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`SyntheticEvent` — объект React, передаваемый JSX-обработчику:

```tsx
function handleClick(
  event:
    React.MouseEvent<
      HTMLButtonElement
    >,
) {
  // ...
}
```

Он предоставляет единый интерфейс:

- `target`;
- `currentTarget`;
- `preventDefault()`;
- `stopPropagation()`;
- `nativeEvent`.

Исходное браузерное событие доступно через:

```tsx
event.nativeEvent
```

Всплытие события из Portal по React-родителям определяется положением компонента в React-дереве.

Сам по себе `SyntheticEvent` является интерфейсом события, а не причиной сохранения React-иерархии Portal.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Работает ли Context внутри Portal?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

Context ищется по React-родителям, а не по DOM-предкам.

Например:

```tsx
<ThemeContext value="dark">
  <Modal>
    <Dialog />
  </Modal>
</ThemeContext>
```

Внутри `Dialog`:

```tsx
const theme =
  useContext(
    ThemeContext,
  );
```

вернёт:

```text
dark
```

даже если DOM диалога находится непосредственно под `body`.

Portal меняет DOM-контейнер, но не логического React-родителя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт при смене контейнера Portal?</strong></summary>

<dl>
<dd>
<h2></h2>

Если передать другой `domNode`:

```tsx
createPortal(
  children,
  nextContainer,
);
```

React пересоздаст Portal-поддерево в новом контейнере.

Это не является обычным физическим перемещением существующих DOM-узлов с гарантированным сохранением всего состояния.

Могут быть потеряны:

- локальный state компонентов;
- значение неконтролируемого поля;
- focus;
- выделение;
- состояние DOM;
- незавершённая анимация;
- экземпляр сторонней библиотеки.

Контейнер вроде:

```text
#modal-root
```

обычно создают один раз и сохраняют стабильным.

Если Portal должен намеренно стать новым поддеревом, его идентичность также можно изменить через `key`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Portal влияет на CSS?</strong></summary>

<dl>
<dd>
<h2></h2>

CSS использует физическое DOM-дерево.

Собственный класс элемента продолжает работать:

```tsx
<div
  className={
    styles.tooltip
  }
/>
```

Но селектор с DOM-предком может перестать совпадать:

```css
.card .tooltip {
  background: black;
}
```

После Portal `.tooltip` больше не находится внутри `.card`.

Наследуемые свойства и CSS-переменные также приходят от нового DOM-пути.

Например, переменная:

```css
.card {
  --tooltip-color: black;
}
```

не будет доступна Portal под `body`, если она не определена на общем предке.

Portal может помочь выйти из:

- `overflow: hidden`;
- локального stacking context;
- ограничений layout-контейнера.

Но отдельно всё равно проектируют:

- позиционирование;
- тему;
- CSS-токены;
- `z-index`;
- collision detection;
- реакцию на scroll и resize.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как определить клик вне выпадающего меню, отрендеренного через Portal?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно проверять физическое DOM-дерево.

Обычно существуют две области:

- элемент, открывающий меню;
- содержимое меню внутри Portal.

```tsx
function handlePointerDown(
  event: PointerEvent,
) {
  const target =
    event.target;

  if (
    !(target instanceof Node)
  ) {
    return;
  }

  const isInsideTrigger =
    triggerRef.current
      ?.contains(target);

  const isInsideContent =
    contentRef.current
      ?.contains(target);

  if (
    !isInsideTrigger &&
    !isInsideContent
  ) {
    close();
  }
}
```

Для Shadow DOM и составных деревьев полезен:

```ts
event.composedPath()
```

Слушатель часто устанавливают на:

```text
pointerdown
```

в capture phase, чтобы обнаружить нажатие до последующих действий.

При этом нужно учитывать:

- вложенные popover;
- scrollbar;
- pointer capture;
- нажатие внутри trigger;
- нажатие внутри Portal-content;
- элементы из другого Shadow Root.

Готовые overlay-библиотеки обычно уже решают эти граничные случаи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>createPortal</code> недостаточно для модального окна?</strong></summary>

<dl>
<dd>
<h2></h2>

Portal только выбирает DOM-контейнер.

Он не реализует автоматически:

- `role="dialog"`;
- доступное имя;
- `aria-modal="true"`;
- начальный focus;
- focus trap;
- возврат focus;
- закрытие по `Escape`;
- блокировку фонового взаимодействия;
- scroll lock;
- обработку backdrop.

Даже такой код:

```tsx
createPortal(
  <div>
    Modal content
  </div>,
  document.body,
);
```

создаёт только DOM-элемент в другом месте.

Для полноценного диалога нужно реализовать всё поведение отдельно либо использовать готовый доступный примитив.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Portal работает с SSR?</strong></summary>

<dl>
<dd>
<h2></h2>

На сервере нет:

```text
document
window
DOM node
```

Поэтому нельзя выполнять во время SSR:

```tsx
createPortal(
  children,
  document.body,
);
```

или:

```tsx
document.getElementById(
  "modal-root",
);
```

Компонент может:

- быть клиентским;
- получить контейнер после монтирования;
- использовать API фреймворка;
- не рендерить Portal до появления DOM.

Первый клиентский render должен соответствовать HTML, созданному сервером.

Например, если сервер вернул `null`, первый клиентский render также должен вернуть `null`, а Portal можно добавить следующим обновлением после Effect.

При этом критически важный первоначальный контент не следует без необходимости делать доступным только после клиентского Effect.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
function Page() {
  return (
    <div onClick={() => console.log("page click")}>
      <Modal />
    </div>
  );
}

function Modal() {
  return createPortal(
    <button onClick={() => console.log("modal button")}>Save</button>,
    document.body
  );
}
```

<details>
<summary><strong>Какие сообщения появятся после клика по кнопке?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала:

```text
modal button
```

затем:

```text
page click
```

если обработчик кнопки не вызвал:

```tsx
event.stopPropagation()
```

Кнопка физически находится под `body` в DOM, но компонент `Modal` остаётся ребёнком `Page` в React-дереве.

Поэтому React-событие продолжает всплывать к обработчику `Page`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| UI | Что даёт Portal |
| --- | --- |
| Модальное окно | Отдельный DOM-слой поверх основной раскладки |
| Всплывающая подсказка | Выход из `overflow: hidden` и независимое позиционирование |
| Выпадающее меню или popover | Размещение содержимого вне локального stacking context |
| Уведомления | Общий контейнер уведомлений |
| Дизайн-система | Единый слой overlay с согласованными `z-index`, темой и правилами focus |
| Клик снаружи | Необходимость проверять реальное DOM-дерево |
| SSR-приложение | Необходимость создавать Portal только при наличии DOM-контейнера |
| Нативный `<dialog>` | Возможность использовать browser top layer вместо обычного Portal-слоя |

## Связанные темы

- [11 Context](<./11 Context.md>)
- [23 JSX события и декларативность](<./23 JSX события и декларативность.md>)
- [31 DOM events](<../JavaScript/31 DOM events.md>)
- [06 Доступность модальных окон и меню](<../Accessibility/06 Доступность модальных окон и меню.md>)

## Источники

- [React: `createPortal`](https://react.dev/reference/react-dom/createPortal)
- [WAI-ARIA APG: Dialog Modal Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 12 Error Boundaries](<./12 Error Boundaries.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 Управляемые и неуправляемые компоненты →](<./14 Управляемые и неуправляемые компоненты.md>)
<!-- CARD-NAV-BOTTOM:END -->
