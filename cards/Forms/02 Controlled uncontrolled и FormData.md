# Controlled uncontrolled и FormData

<!-- CARD-NAV-TOP:START -->
[← 01 Формы во frontend](<./01 Формы во frontend.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 React Hook Form register handleSubmit formState →](<./03 React Hook Form register handleSubmit formState.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются controlled- и uncontrolled-формы, то есть управляемые и неуправляемые формы? Где здесь используется `FormData`?**

<h2></h2>

<br>
<dl>
<dd>

Controlled и uncontrolled — характеристики отдельных полей, а не обязательно всей формы. Одна форма может сочетать оба подхода.

Controlled, или управляемое, поле получает текущее значение из состояния React-компонента. Текстовый `<input>` использует `value` и `onChange`, а флажки и переключатели (`checkbox` и `radio`) — `checked` и `onChange`.

React является владельцем значения, поэтому компонент может сразу строить по нему другой интерфейс, форматировать ввод или синхронизировать зависимые поля. Обработчик `onChange` должен синхронно обновлять значение, переданное в `value` или `checked`.

Uncontrolled, или неуправляемое, поле хранит текущее значение в DOM. React задаёт только начальное значение через `defaultValue` или `defaultChecked`, а данные читаются через `ref` или при отправке формы.

Такой подход хорошо сочетается с нативным `<form>` и React Hook Form и не требует обновлять состояние родительского компонента на каждый символ.

`FormData` — браузерный API для сбора элементов формы, участвующих в отправке. Ключ берётся из `name`, а значение имеет тип `string` или `File`.

Поле без `name`, поле с `disabled` и неотмеченный checkbox не попадут в результат; `readonly`-поле попадёт. Несколько контролов с одним именем создают повторяющиеся ключи, которые читают через `getAll()`.

`FormData` можно использовать и с controlled-полями: если они имеют `name`, объект прочитает их текущее значение из DOM при отправке.

`new FormData(form)` не включает данные конкретной кнопки отправки, потому что при обычном программном создании объекта submitter не указан.

Если `name` и `value` кнопки важны, передают её вторым аргументом:

```ts
const formData = new FormData(form, submitter);
```

Submitter — элемент, которым была инициирована отправка формы. При обычной нативной отправке браузер учитывает его автоматически.

Поле не должно переключаться между controlled- и uncontrolled-режимами в течение жизни.

Для управляемой строки начальное значение задают как `''`, а не `undefined`. Для управляемого checkbox или radio используют логическое значение, например `false`, а не `undefined`. Иначе после появления данных React предупредит о смене режима.

Изменение `defaultValue` после первого монтирования не заменяет текущее DOM-значение неуправляемого поля. Для явного сброса используют нативный reset, `form.reset()` или перемонтирование поля с другим `key`, если это действительно необходимо.

`<input type="file">` остаётся неуправляемым: файл выбирает пользователь, а код читает `files`, `ref` или `FormData`.

В React 19 функцию можно передать через prop `action` формы. Такая функция называется Action и получает `FormData`.

`useFormStatus()` позволяет дочернему компоненту прочитать состояние отправки родительской формы, включая `pending` и отправляемые данные.

`useActionState()` добавляет к Action состояние результата и признак ожидания. При использовании возвращённой функции как `action` формы исходная Action получает предыдущий state первым аргументом, а `FormData` — вторым:

```ts
async function action(previousState: State, formData: FormData) {
  // ...
}
```

Ожидаемую ошибку обычно возвращают как часть нового состояния. Выброшенная ошибка передаётся ближайшему Error Boundary.

После успешного выполнения Action React автоматически сбрасывает неуправляемые поля. Поэтому для формы редактирования нужно заранее решить, нужен ли такой сброс.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что значит source of truth в форме?</strong></summary>

<dl>
<dd>
<h2></h2>

`Source of truth`, или источник актуального значения, определяет владельца данных.

В управляемом поле это состояние React-компонента, в неуправляемом — DOM. От выбора зависит, кто обновляет значение, где его читать и какие изменения вызывают повторный render React-компонента.

Источник истины выбирается для конкретного поля. Например, поисковая строка может быть controlled, а поле выбора файла в той же форме — uncontrolled.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие поля попадут в <code>FormData</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В `FormData` попадают элементы формы, участвующие в отправке: `<input>`, `<select>`, `<textarea>` и выбранная кнопка отправки, если у них есть `name` и они не `disabled`.

Особенности:

- у `checkbox` и `radio` учитываются только отмеченные варианты;
- у `<select multiple>` может быть несколько значений;
- поле выбора файла передаёт объекты `File`;
- `readonly`-поле участвует в отправке;
- кнопка добавляется, только если она является submitter отправки или явно передана в `new FormData(form, submitter)`.

Поле может быть controlled или uncontrolled — для `FormData` важны его текущее DOM-значение и правила нативной отправки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему после <code>Object.fromEntries(formData)</code> часть данных потерялась?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный объект не хранит несколько значений одного ключа. При преобразовании повторяющихся ключей через `Object.fromEntries()` в объекте останется последнее значение.

Поэтому несколько checkbox с одним `name` или `<select multiple>` нельзя корректно преобразовать таким способом без дополнительной обработки.

Такие поля читают через:

```ts
const values = formData.getAll(name);
```

Затем значения преобразуют по контракту приложения или API.

Также нужно учитывать:

- неотмеченный checkbox отсутствует в `FormData`;
- отмеченный checkbox без явного `value` передаёт строку `"on"`, а не логическое `true`;
- числа приходят строками;
- файлы приходят объектами `File`;
- `FormData.get()` может вернуть `null`, если ключ отсутствует.

Типы нужно проверять и преобразовывать явно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отправить <code>FormData</code> через <code>fetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Объект передают как тело запроса:

```ts
fetch(url, {
  method: "POST",
  body: formData,
});
```

Заголовок `Content-Type` вручную не задают. Браузер сформирует `multipart/form-data` с уникальным `boundary`, то есть разделителем частей.

Если вручную установить заголовок без правильного `boundary`, сервер может не разобрать тело запроса.

Перед отправкой всё равно нужно учитывать контракт backend: некоторые endpoints ожидают JSON, а не `multipart/form-data`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Создаёт ли <code>name="user.email"</code> вложенный объект автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `FormData` — плоский multimap, то есть набор ключей, каждому из которых может соответствовать одно или несколько значений.

Точка и квадратные скобки остаются частью строки имени:

```text
user.email
items[0].name
```

Серверный фреймворк может интерпретировать такое соглашение собственным парсером, но это поведение не определено самим `FormData`.

Для JSON клиент явно строит, проверяет и преобразует вложенный объект.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему React предупреждает о переходе uncontrolled input в controlled?</strong></summary>

<dl>
<dd>
<h2></h2>

При первом render поле получило `value={undefined}`, поэтому React счёл его неуправляемым.

После загрузки данных появилось строковое `value`, и владельцем значения стал React. Поле изменило режим в течение жизни компонента, что React не поддерживает.

Для управляемого текстового поля задают строковое значение сразу:

```tsx
<input
  value={name ?? ""}
  onChange={event => setName(event.target.value)}
/>
```

Для checkbox используют логическое значение:

```tsx
<input
  type="checkbox"
  checked={isEnabled ?? false}
  onChange={event => setIsEnabled(event.target.checked)}
/>
```

Переданный `onChange` должен синхронно обновлять значение, иначе React вернёт полю предыдущее значение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>FormData</code> связан с React 19 Actions?</strong></summary>

<dl>
<dd>
<h2></h2>

Функция в `<form action={fn}>` получает `FormData`:

```tsx
function save(formData: FormData) {
  const name = formData.get("name");
}

<form action={save}>
  <input name="name" />
  <button type="submit">Сохранить</button>
</form>
```

`useFormStatus` внутри дочернего компонента формы предоставляет информацию о последней отправке родительской формы:

- `pending`;
- `data`;
- `method`;
- `action`.

Hook не отслеживает форму, объявленную в том же компоненте, где он вызывается. Компонент с `useFormStatus` должен находиться внутри соответствующего `<form>`.

`useActionState` возвращает:

- текущее состояние;
- функцию Action;
- признак `isPending`.

Если возвращённая функция передана в `action`, обработчик получает предыдущий state первым аргументом и `FormData` вторым:

```ts
async function save(previousState: State, formData: FormData) {
  // ...
}
```

Эти API дополняют нативный сценарий формы, но не запрещают controlled-поля там, где интерфейсу нужно актуальное состояние React-компонента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему поле выбора файла нельзя сделать обычным controlled-полем?</strong></summary>

<dl>
<dd>
<h2></h2>

Файл может выбрать только пользователь. JavaScript не может произвольно установить путь к файлу в `value` из соображений безопасности.

React читает выбранные файлы через:

- `input.files`;
- `ref`;
- `FormData`.

Сбросить выбор можно через нативный reset, присваивание пустой строки в допустимом сценарии или перемонтирование поля.

Само значение пути использовать нельзя: браузер не раскрывает реальное расположение файла на устройстве пользователя.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Подход |
| --- | --- |
| Поиск с реакцией на каждый символ | Управляемое поле |
| Простая форма отправки | Неуправляемые поля + `FormData` |
| Большая форма с RHF | Обычно `register` с нативными полями; controlled-компоненты через адаптер |
| Загрузка файла | Неуправляемое поле + `FileList` или `FormData` |
| Маска или форматирование | Управляемое поле или адаптер компонента |

## Связанные темы

- [14 Controlled и uncontrolled компоненты](<../React/14 Controlled и uncontrolled компоненты.md>)
- [03 React Hook Form register handleSubmit formState](<./03 React Hook Form register handleSubmit formState.md>)
- [19 React 18 19 и 19.2](<../React/19 React 18 19 и 19.2.md>)

## Источники

- [React docs: input](https://react.dev/reference/react-dom/components/input)
- [MDN: FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [MDN: FormData constructor](https://developer.mozilla.org/en-US/docs/Web/API/FormData/FormData)
- [React v19: form Actions](https://react.dev/blog/2024/12/05/react-19)
- [React docs: form](https://react.dev/reference/react-dom/components/form)
- [React docs: useFormStatus](https://react.dev/reference/react-dom/hooks/useFormStatus)
- [React docs: useActionState](https://react.dev/reference/react/useActionState)
- [MDN: Using FormData Objects](https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest_API/Using_FormData_Objects)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Формы во frontend](<./01 Формы во frontend.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 React Hook Form register handleSubmit formState →](<./03 React Hook Form register handleSubmit formState.md>)
<!-- CARD-NAV-BOTTOM:END -->
