# JSX SyntheticEvent и декларативность

<!-- CARD-NAV-TOP:START -->
[← 22 Performance profiling и оптимизация React](<./22 Performance profiling и оптимизация React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 HOC render props PureComponent Component lifecycle →](<./24 HOC render props PureComponent Component lifecycle.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое JSX и SyntheticEvent? Как React обрабатывает события декларативного интерфейса?**

<h2></h2>

<br>
<dl>
<dd>

JSX является расширением синтаксиса JavaScript для описания React-элементов. Он похож на HTML, но не является строкой разметки и не обрабатывается браузером напрямую. Инструмент сборки применяет современное преобразование JSX и создаёт вызовы служебных функций React. Результатом становятся объекты с типом, `props` и дочерними элементами.

```tsx
const button = <Button disabled={isSaving}>Save</Button>;
```

JSX следует правилам JavaScript и React:

- компонент пишется с заглавной буквы, а строка `"button"` обозначает DOM-элемент;
- JavaScript-выражение помещается в `{}`, а инструкция вроде `if` выполняется до `return`;
- несколько соседних узлов оборачиваются в общий элемент или Fragment;
- DOM-свойства используют имена вроде `className`, `htmlFor`, `onClick`;
- массив элементов получает стабильные `key`;
- `props` и React-элементы являются снимками данных только для чтения и не мутируются после создания.

React по умолчанию экранирует строки, вставленные в JSX, поэтому текст пользователя не интерпретируется как HTML. Риск XSS появляется при `dangerouslySetInnerHTML` или другом обходе этой модели. HTML из внешнего источника нужно санитизировать проверенной библиотекой и дополнительно ограничивать политикой безопасности контента (Content Security Policy, CSP); TypeScript-тип `string` не делает разметку безопасной.

Декларативность означает, что JSX описывает результат для текущих `props` и состояния. Обработчик события обновляет состояние, React повторно вычисляет JSX и синхронизирует DOM. Код не должен одновременно вручную менять тот же DOM-узел и ожидать, что React будет считать это источником истины.

SyntheticEvent является объектом события, который React передаёт JSX-обработчику. Он предоставляет знакомые поля и методы: `target`, `currentTarget`, `preventDefault()`, `stopPropagation()` и `nativeEvent`. `nativeEvent` содержит исходное браузерное событие. Начиная с React 17 SyntheticEvent больше не использует старый пул объектов событий, поэтому `event.persist()` в современном React ничего не делает.

React устанавливает общие слушатели событий на корневой контейнер и сопоставляет DOM-событие с React-деревом. Обработчики фазы всплытия записываются как `onClick`, а фазы перехвата как `onClickCapture`. Большинство событий React всплывает, но нужно знать исключения конкретного события, например `onScroll` работает только на назначенном элементе.

`event.target` является исходным DOM-узлом, где произошло событие. `event.currentTarget` является узлом, чей обработчик сейчас выполняется. Если пользователь нажал на `<span>` внутри `<button onClick>`, `target` может быть `span`, а `currentTarget` будет `button`. В TypeScript `currentTarget` обычно даёт более полезный тип обработчика.

`preventDefault()` отменяет стандартное действие браузера, например переход по ссылке или обычную отправку формы. Он не останавливает всплытие. `stopPropagation()` останавливает дальнейшее распространение, но не отменяет стандартное действие. `return false` в обработчике React не выполняет ни одну из этих операций.

Portal сохраняет React-родительство, поэтому события React всплывают через владельцев Portal, хотя DOM расположен в другом контейнере. Нативный слушатель вне соответствующего корневого узла React следует фактическому DOM-пути, что важно при смешивании React и стороннего императивного кода.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Обязателен ли JSX для React?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. React-элементы можно создавать через `createElement` или служебные функции JSX напрямую. JSX делает вложенное дерево и `props` читаемее. В production-сборке браузер получает преобразованный JavaScript, а не исходный JSX.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему обычный <code>if</code> нельзя написать внутри <code>{}</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В фигурных скобках JSX ожидается выражение, то есть конструкция со значением. `if` является инструкцией: он управляет выполнением, но не возвращает значение. Условие выполняют до `return`, используют тернарный оператор или выделяют отдельный компонент. Длинная цепочка `&&` и тернарных операторов читается хуже, чем ясная переменная.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем SyntheticEvent отличается от нативного события?</strong></summary>

<dl>
<dd>
<h2></h2>

Нативное событие создаёт браузер, например `PointerEvent` или `SubmitEvent`. SyntheticEvent создаёт React для JSX-обработчика и предоставляет согласованный интерфейс, связанный с React-деревом. Исходный объект доступен через `event.nativeEvent`, но соответствие типов событий не всегда один к одному.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работают фазы перехвата и всплытия в React?</strong></summary>

<dl>
<dd>
<h2></h2>

`onClickCapture` вызывается при движении события сверху вниз по React-дереву до `target`. Затем обработчик целевого элемента и `onClick` родителей вызываются снизу вверх. Фаза перехвата полезна для общей диагностики или инфраструктуры, но прикладные обработчики обычно используют фазу всплытия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>target</code> отличается от <code>currentTarget</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`target` указывает на самый глубокий элемент, где началось событие, и остаётся тем же при всплытии. `currentTarget` меняется и указывает на элемент текущего обработчика. Для значения формы часто читают `currentTarget`, если обработчик назначен непосредственно полю или форме.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>preventDefault()</code> отличается от <code>stopPropagation()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Первый отменяет действие браузера, но событие продолжает всплывать. Второй останавливает переход к следующим обработчикам, но браузерное действие может выполниться. Иногда нужны оба вызова, но каждый должен соответствовать конкретному поведению.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли JSX от XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

React экранирует строковые значения в JSX, поэтому `<script>` из строки отображается как текст. Это не защищает `dangerouslySetInnerHTML`, опасный URL, прямую DOM-инъекцию или уязвимость стороннего виджета. Непроверенный HTML санитизируют, а не считают безопасным из-за JSX.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему событие Portal доходит до React-родителя?</strong></summary>

<dl>
<dd>
<h2></h2>

React хранит Portal в прежнем React-дереве и вызывает обработчики по этой иерархии. DOM-предки при этом другие. Поэтому всплывающий компонент не является изолированным и должен учитывать родительские JSX-обработчики.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```tsx
function Form() {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    console.log(event.target);
    console.log(event.currentTarget);
  }

  return (
    <form onSubmit={handleSubmit}>
      <button type="submit">
        <span>Save</span>
      </button>
    </form>
  );
}
```

<details>
<summary><strong>Что означают <code>target</code> и <code>currentTarget</code>, если нажать на текст внутри <code>span</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Точный нативный `target` может быть `span` или вложенным узлом, на котором началось событие. `currentTarget` в `handleSubmit` всегда является `<form>`, потому что обработчик `submit` назначен форме. `preventDefault()` отменит стандартную отправку, но не остановит всплытие события.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Условная разметка | JavaScript-выражения и ясные ветви до `return` |
| Список элементов | Стабильные `key` из данных |
| Отправка формы | `preventDefault` или `action` формы React 19 |
| Кнопка с иконкой | Различать `target` и `currentTarget` |
| Общий обработчик контейнера | Всплытие, перехват и делегирование |
| HTML из CMS | Санитизация перед `dangerouslySetInnerHTML` |
| Portal | React и DOM-иерархии событий различаются |

## Связанные темы

- [01 Что такое React и зачем он нужен](<./01 Что такое React и зачем он нужен.md>)
- [03 Reconciliation key и списки](<./03 Reconciliation key и списки.md>)
- [13 Portal](<./13 Portal.md>)
- [31 DOM events](<../JavaScript/31 DOM events.md>)
- [03 Event delegation capture bubble](<../Browser Internals/03 Event delegation capture bubble.md>)
- [02 XSS reflected stored DOM React](<../Security/02 XSS reflected stored DOM React.md>)

## Источники

- [React: Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- [React: Responding to Events](https://react.dev/learn/responding-to-events)
- [React: `SyntheticEvent`](https://react.dev/reference/react-dom/components/common#react-event-object)
- [React: `dangerouslySetInnerHTML`](https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 22 Performance profiling и оптимизация React](<./22 Performance profiling и оптимизация React.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [24 HOC render props PureComponent Component lifecycle →](<./24 HOC render props PureComponent Component lifecycle.md>)
<!-- CARD-NAV-BOTTOM:END -->
