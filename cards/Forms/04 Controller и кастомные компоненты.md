# Controller и кастомные компоненты

<!-- CARD-NAV-TOP:START -->
[← 03 React Hook Form register handleSubmit formState](<./03 React Hook Form register handleSubmit formState.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Валидация форм schema resolver async validation →](<./05 Валидация форм schema resolver async validation.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Зачем в React Hook Form нужен `Controller`? Почему не всегда хватает `register`?**

<h2></h2>

<br>
<dl>
<dd>

`register` подходит полю, которому можно передать стандартный контракт нативного элемента: `ref`, `name`, `onChange` и `onBlur`.

Составной `Select` (выпадающий список), `DatePicker` (выбор даты), поле с маской или `Combobox` (поле ввода со списком вариантов) может не предоставлять доступ к обычному `<input>` либо сообщать об изменении через собственный prop, например `onValueChange`.

`Controller` связывает такой управляемый компонент с React Hook Form.

Он получает `control`, `name` и `render prop` — функцию, внутри которой рендерится поле. В неё приходят:

- `field` со значением и обработчиками;
- `fieldState` с ошибкой, `isTouched`, `isDirty` и `invalid`.

Хук `useController` предоставляет тот же контракт и удобен внутри переиспользуемого компонента поля.

Из `field` обычно используют:

- `value`;
- `onChange`;
- `onBlur`;
- `name`;
- `ref`;
- `disabled`.

Эти свойства сопоставляют с API конкретного компонента.

Если компонент вызывает `onValueChange(value)`, полученное значение передают в `field.onChange`:

```tsx
<Select
  value={field.value}
  onValueChange={field.onChange}
/>
```

`field.onChange` уже обновляет значение и состояние поля в RHF. Дополнительно вызывать `setValue` для того же изменения обычно не нужно.

Если пропустить `onBlur`, режим проверки `onBlur` и `touchedFields` могут работать неверно.

`field.ref` нужно передать фокусируемому элементу управления. Если ref попадёт только на внешнюю обёртку, автоматический фокус на поле с ошибкой может не сработать.

Управляемому полю задают начальное значение через `useForm({ defaultValues })` или через `defaultValue` конкретного `Controller`.

Предпочтительно задавать единую базу значений на уровне `useForm`:

```tsx
const form = useForm<FormValues>({
  defaultValues: {
    country: "",
  },
});
```

`defaultValue` у отдельного `Controller` используют, если значение не задано на уровне формы. Дублировать два разных начальных значения для одного поля не следует.

Значение не должно быть `undefined`. Для очищенного поля используют `""`, `null`, `false`, пустой массив или другое значение, которое поддерживают компонент, модель формы и схема валидации.

Вызов `field.onChange(undefined)` также некорректен.

Поле внутри `Controller` уже зарегистрировано, поэтому добавлять к тому же элементу `{...register(name)}` нельзя. Это создаст двойную регистрацию и конкурирующие обработчики.

Для обычного `<input>` `Controller` без отдельной причины не нужен: `register` проще и сохраняет неуправляемую модель поля.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему пользовательский Select часто требует <code>Controller</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользовательский Select может не предоставлять обычный DOM-элемент `<select>` или `<input>` со стандартным контрактом.

Например, он принимает:

```text
value
onValueChange
```

вместо:

```text
value
onChange(event)
```

`Controller` передаёт ему текущее `field.value`, а новое значение возвращает в `field.onChange`.

Если пользовательский компонент предоставляет реальный `<input>` и позволяет передать ему `ref`, `name`, `onChange` и `onBlur`, его можно подключить через обычный `register`.

Важно смотреть не на название «кастомный компонент», а на его публичный API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что находится в <code>field</code> внутри <code>Controller</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В `field` находятся данные и обработчики для подключения компонента:

- `value` — текущее значение;
- `onChange` — передача нового значения в RHF;
- `onBlur` — отметка взаимодействия и запуск проверки в соответствующем режиме;
- `name` — путь поля в данных формы;
- `ref` — ссылка для регистрации и управления фокусом;
- `disabled` — состояние отключённого поля, если оно настроено через RHF.

Их передают напрямую или адаптируют к API компонента.

Например:

```tsx
<DatePicker
  value={field.value}
  onChange={date => field.onChange(date)}
  onBlur={field.onBlur}
  disabled={field.disabled}
  inputRef={field.ref}
/>
```

Если не передать `onBlur`, состояние `touched` может работать неверно.

Если не передать `ref` фокусируемому элементу, автоматический фокус на ошибке может не сработать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему управляемый компонент без начального значения может вызвать предупреждение?</strong></summary>

<dl>
<dd>
<h2></h2>

Если сначала `value` равен `undefined`, React может считать поле неуправляемым, а после появления строки, объекта или другого значения — управляемым.

Начальное значение задают сразу:

- в `defaultValues` у `useForm`;
- либо через `defaultValue` отдельного `Controller`, если значение не задано на уровне формы.

Для очищения передают допустимое значение вроде `""`, `null`, `false` или пустого массива, но не `undefined`.

Тип пустого значения должен быть согласован между компонентом, TypeScript-моделью формы и схемой валидации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как это связано с Radix UI?</strong></summary>

<dl>
<dd>
<h2></h2>

Многие Radix Primitives поддерживают управляемые пары props:

```text
value / onValueChange
checked / onCheckedChange
open / onOpenChange
```

Для значения формы создают адаптер через `Controller` или `useController`.

Например, для Radix Select:

```tsx
<Controller
  control={control}
  name="country"
  render={({ field }) => (
    <Select.Root
      value={field.value}
      onValueChange={field.onChange}
      disabled={field.disabled}
    >
      {/* части Select */}
    </Select.Root>
  )}
/>
```

Актуальный `Select.Root` также поддерживает `name`, `required` и `disabled` для интеграции с нативной формой.

Но нативное участие компонента в отправке и управление его значением через RHF — разные задачи. Для состояния RHF всё равно нужно передать `field.value` и вернуть изменение через `field.onChange`.

Также нужно проверить:

- куда передать `ref` для фокуса;
- как компонент представляет пустое значение;
- создаёт ли он скрытый нативный control;
- как значение попадёт в `FormData`;
- правильно ли связаны label и сообщение об ошибке.

Сам факт использования Radix не гарантирует правильную интеграцию с RHF и сериализацию значения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя использовать <code>Controller</code> и <code>register</code> для одного поля одновременно?</strong></summary>

<dl>
<dd>
<h2></h2>

`Controller` уже регистрирует поле через `control`.

Дополнительный `register` добавит второй набор:

- `ref`;
- `onChange`;
- `onBlur`;
- `name`.

Обработчики могут начать конкурировать, а значение и состояние поля — обновляться несколько раз или непредсказуемо.

Нужно выбрать один способ подключения:

- `register` для стандартного нативного контракта;
- `Controller` или `useController` для управляемого или нестандартного API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где преобразовать значение DatePicker или Select?</strong></summary>

<dl>
<dd>
<h2></h2>

На границе адаптера значение компонента преобразуют в тип, выбранный для модели формы, и передают в `field.onChange`.

Например, компонент может вернуть объект варианта:

```ts
type Option = {
  label: string;
  value: string;
};
```

Но форма хранит только идентификатор:

```tsx
onChange={option => {
  field.onChange(option?.value ?? "");
}}
```

Для DatePicker модель формы может хранить `Date | null` либо строку даты. Выбор должен быть единым для всей формы.

Преобразование обычно разделяют на три границы:

```text
UI-компонент → модель формы → DTO запроса
```

Адаптер переводит значение UI-компонента в модель формы.

Перед отправкой модель формы преобразуют в DTO, например `Date` — в ISO-строку.

Отображаемый формат, внутренний тип формы и транспортный формат backend не следует смешивать в одном неявном обработчике.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Компонент | Почему нужен адаптер |
| --- | --- |
| Пользовательский `Select` | Нестандартный `onValueChange` |
| `DatePicker` | Значение `Date | null`, а не DOM-событие |
| Поле с маской | Управляемое значение и форматирование |
| `Combobox` | Значение может быть сложным объектом |
| Radix `Select` | API `value`/`onValueChange` отличается от нативного события |

## Связанные темы

- [03 React Hook Form register handleSubmit formState](<./03 React Hook Form register handleSubmit formState.md>)
- [07 Performance watch useWatch field arrays](<./07 Performance watch useWatch field arrays.md>)
- [10 useRef ref prop forwardRef и imperative handle](<../React/10 useRef ref prop forwardRef и imperative handle.md>)
- [09 Shared UI design system Radix UI](<../Architecture/09 Shared UI design system Radix UI.md>)

## Источники

- [React Hook Form docs: Controller](https://react-hook-form.com/docs/usecontroller/controller)
- [React Hook Form README](https://github.com/react-hook-form/react-hook-form)
- [React Hook Form docs: useController](https://react-hook-form.com/docs/usecontroller)
- [Radix UI: Select](https://www.radix-ui.com/primitives/docs/components/select)
- [Radix UI docs](https://www.radix-ui.com/primitives)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 React Hook Form register handleSubmit formState](<./03 React Hook Form register handleSubmit formState.md>) · [↑ Forms](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Валидация форм schema resolver async validation →](<./05 Валидация форм schema resolver async validation.md>)
<!-- CARD-NAV-BOTTOM:END -->
