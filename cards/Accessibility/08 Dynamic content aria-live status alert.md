# Dynamic content aria-live status alert

<!-- CARD-NAV-TOP:START -->
[← 07 Images media alt captions](<./07 Images media alt captions.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Accessibility testing manual automated screen reader →](<./09 Accessibility testing manual automated screen reader.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как сделать динамические обновления интерфейса доступными? Чем отличаются `aria-live`, `status` и `alert`?**

<h2></h2>

<br>
<dl>
<dd>

Изменение DOM само по себе не гарантирует, что скринридер объявит новый текст. Для фоновых обновлений используют live region - область, изменения которой браузер передаёт вспомогательной технологии без перемещения фокуса. Она подходит для результата сохранения, количества найденных элементов, завершения загрузки или общей ошибки.

`aria-live="polite"` ждёт паузы в текущей речи и подходит обычным статусам. `aria-live="assertive"` может прервать объявление и используется только для срочного сообщения, которое требует немедленного внимания. Частые assertive-обновления делают интерфейс практически нечитаемым.

`role="status"` имеет неявное вежливое объявление и подходит сообщению «Изменения сохранены». `role="alert"` имеет неявное срочное объявление и подходит важной ошибке, уже возникшей на странице. Ни одна из этих ролей не перемещает фокус и не превращает сообщение в dialog.

Live region обычно должен существовать в DOM до изменения текста. Если React одновременно создаст уже заполненный контейнер и сразу удалит его, часть комбинаций браузера и скринридера может не объявить сообщение. Надёжнее держать стабильную область, обновлять её текст и не дублировать одно событие сразу через `status`, `alert` и перенос фокуса.

Для нового контекста, в котором пользователь должен действовать, одного объявления недостаточно. При открытии dialog фокус переводят внутрь, после ошибки большой формы - на сводку или поле. Live region сообщает о результате фоновой операции, а управление фокусом (`focus management`) определяет новое место взаимодействия.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>polite</code> отличается от <code>assertive</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`polite` ставит сообщение в очередь и ждёт, пока скринридер закончит текущую речь. `assertive` просит объявить изменение немедленно и может прервать текущий текст. Поэтому `assertive` оставляют для редких критичных ошибок, а сохранение, загрузку и счётчики объявляют через `polite` или `status`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>role="status"</code> отличается от <code>role="alert"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`status` сообщает несрочный результат операции и ведёт себя примерно как `aria-live="polite"`. `alert` предназначен для важного сообщения и обычно объявляется assertive. В отличие от обычной live region, новый элемент с уже заполненным `role="alert"` обычно объявляется при добавлении в DOM. Фокусировать его не требуется, но видимый текст должен оставаться доступен для повторного чтения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда переносить фокус, а когда использовать live region?</strong></summary>

<dl>
<dd>
<h2></h2>

Live region используют, когда пользователь остаётся на текущем элементе: товар добавлен в корзину, данные сохранены, список обновился. Фокус переносят, когда появился новый контекст или требуется действие: открылся dialog, показалась сводка ошибок, началась новая страница SPA. Одновременное объявление и перенос фокуса могут дать дубли.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему скринридер не объявил сообщение в React?</strong></summary>

<dl>
<dd>
<h2></h2>

Частая причина - live region создаётся сразу с готовым текстом, быстро размонтируется или целиком заменяется другим узлом. Область лучше держать стабильной и обновлять её содержимое. Также проверяют, что она не скрыта через `display: none`, `hidden` или `aria-hidden` и что обновления не схлопнулись в одно состояние.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как сделать toast доступным?</strong></summary>

<dl>
<dd>
<h2></h2>

Toast, или временное всплывающее уведомление, должен иметь видимый текст, жить достаточно долго и объявляться с подходящим приоритетом, обычно через `status`. Если внутри есть действие «Отменить», оно должно быть доступно с клавиатуры; при этом нельзя неожиданно перехватывать фокус у пользователя. Критичная ошибка, требующая решения, чаще заслуживает постоянного сообщения или dialog, а не исчезающего toast.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>aria-atomic="true"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он просит объявлять live region целиком при изменении любой её части. Это полезно, когда отдельный изменившийся фрагмент непонятен без контекста, например в сообщении «Загружено 3 из 10». Без `aria-atomic` скринридер может объявить только новое число.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен <code>aria-busy</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`aria-busy="true"` сообщает, что область обновляется и её содержимое пока не готово. После завершения ставят `false`, чтобы вспомогательная технология получила итоговое состояние. Атрибут не показывает индикатор загрузки и не блокирует управление сам по себе; визуальное состояние и логика загрузки реализуются отдельно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подход |
| --- | --- |
| Автосохранение завершено | `role="status"` |
| Поиск вернул новое число результатов | `aria-live="polite"` |
| Критичная ошибка текущей операции | `role="alert"` точечно |
| Открылся dialog | Перенести фокус, а не ограничиваться live region |
| Toast с действием | Объявление без неожиданного перехвата фокуса |
| Обновляется большая область | `aria-busy` и понятный визуальный статус |

## Связанные темы

- [03 Keyboard navigation focus management](<./03 Keyboard navigation focus management.md>)
- [05 Forms labels errors validation accessibility](<./05 Forms labels errors validation accessibility.md>)
- [06 Dialog dropdown overlay accessibility](<./06 Dialog dropdown overlay accessibility.md>)
- [10 Accessibility в React и Radix UI](<./10 Accessibility в React и Radix UI.md>)
- [15 Suspense lazy и code splitting](<../React/15 Suspense lazy и code splitting.md>)

## Источники

- [W3C WAI: Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)
- [WAI-ARIA APG: Alert Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/alert/)
- [MDN: ARIA live regions](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Guides/Live_regions)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Images media alt captions](<./07 Images media alt captions.md>) · [↑ Accessibility](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Accessibility testing manual automated screen reader →](<./09 Accessibility testing manual automated screen reader.md>)
<!-- CARD-NAV-BOTTOM:END -->
