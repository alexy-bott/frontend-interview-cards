# Observer APIs

<!-- CARD-NAV-TOP:START -->
[← 31 DOM events](<./31 DOM events.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [33 requestAnimationFrame и requestIdleCallback →](<./33 requestAnimationFrame и requestIdleCallback.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются `MutationObserver`, `IntersectionObserver` и `ResizeObserver`? Когда использовать каждый из них?**

<h2></h2>

<br>
<dl>
<dd>

Observer APIs сообщают об изменениях, за которыми иначе пришлось бы следить вручную. Браузер собирает наблюдения и вызывает callback асинхронно пачкой. Callback всё равно выполняется на main thread, поэтому observer уменьшает лишние проверки, но не делает обработку бесплатной.

| API | Что наблюдает | Типичный сценарий |
| --- | --- | --- |
| `MutationObserver` | Структуру DOM, attributes, text nodes | Интеграция с widget или DOM вне контроля приложения |
| `IntersectionObserver` | Пересечение target с viewport или scroll container | Lazy loading, infinite scroll, видимость блока |
| `ResizeObserver` | Размер content/border box элемента | График, canvas, компонент по размеру контейнера |

`MutationObserver` получает массив `MutationRecord`. При `observe(target, options)` явно выбирают `childList`, `attributes`, `characterData` и `subtree`. Уведомления доставляются во время microtask checkpoint после текущих DOM-изменений, поэтому несколько мутаций могут попасть в один callback.

`IntersectionObserver` сообщает не каждый scroll, а начальное состояние и пересечение настроенных `threshold`. `root` задаёт область наблюдения, `rootMargin` расширяет или сужает её, а `intersectionRatio` показывает долю пересечения. Например, положительный нижний `rootMargin` позволяет начать подгрузку до появления target в viewport.

`ResizeObserver` сообщает размер конкретного элемента независимо от причины: изменение окна, контента, grid или соседней панели. В entry доступны разные box sizes. Это точнее `window.resize`, когда компонент зависит от собственного контейнера.

Для остановки одного target используют `unobserve(target)`, для всех используют `disconnect()`. `takeRecords()` возвращает накопленные, но ещё не доставленные records там, где API его поддерживает.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>MutationObserver</code> связан с microtasks?</strong></summary>

<dl>
<dd>
<h2></h2>

DOM-операция не вызывает observer синхронно. Браузер ставит доставку накопленных records на microtask checkpoint. Callback видит пачку мутаций после завершения текущего кода, но до следующей task и потенциального paint. Если callback сам меняет наблюдаемый DOM, он может создать новые records и цикл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли <code>MutationObserver</code> следить за React state или JavaScript-объектом?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет, он наблюдает только DOM. React state нужно отслеживать средствами React, а объект через явный state manager, setters или Proxy-механику. MutationObserver применяют, когда DOM меняет сторонний script, browser extension, contenteditable editor или другая система вне обычного data flow.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие options нужны <code>MutationObserver</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Хотя бы один из `childList`, `attributes` или `characterData` должен быть включён. `subtree: true` распространяет наблюдение на потомков. `attributeFilter` ограничивает имена attributes и уменьшает лишние records. `attributeOldValue` и `characterDataOldValue` добавляют прошлое значение, если оно действительно нужно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>IntersectionObserver</code> обычно лучше scroll listener для lazy loading?</strong></summary>

<dl>
<dd>
<h2></h2>

Код не читает `getBoundingClientRect` на каждое scroll event и не реализует собственный throttle. Браузер сам отслеживает пересечения и вызывает callback только при начальном наблюдении и пересечении threshold. Для обычных изображений сначала стоит проверить нативный `loading="lazy"`; observer нужен для кастомной загрузки и сложной логики.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличаются <code>rootMargin</code> и <code>threshold</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`rootMargin` изменяет прямоугольник root, относительно которого считается пересечение. `threshold` задаёт долю target от `0` до `1`, при пересечении которой нужен callback. Для предзагрузки используют увеличенный root через margin, а для аналитики «видно не менее 50%» используют threshold `0.5`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Означает ли <code>isIntersecting</code>, что пользователь действительно видит элемент?</strong></summary>

<dl>
<dd>
<h2></h2>

Базовый режим подтверждает геометрическое пересечение с root и clipping ancestors, но не является полной гарантией внимания или отсутствия перекрытия другим элементом. Опция `trackVisibility` пытается учитывать compromised visibility, но дороже и имеет ограничения поддержки. Для аналитики дополнительно учитывают время видимости, состояние вкладки и продуктовые критерии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать повторной загрузки в infinite scroll?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверять `entry.isIntersecting`, состояние `isLoading`, наличие следующей страницы и identity текущего запроса. На время запроса sentinel можно `unobserve`, а после добавления данных снова наблюдать актуальный элемент. Запрос также должен иметь защиту от дублей и отмену при смене списка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>ResizeObserver</code> отличается от <code>window.resize</code> и container queries?</strong></summary>

<dl>
<dd>
<h2></h2>

`window.resize` говорит только об изменении viewport. `ResizeObserver` реагирует на размер конкретного элемента и позволяет запустить JavaScript. CSS container query предпочтительнее, если задача только изменить стили по размеру контейнера: она не требует callback и ручного state. Observer нужен для вычислений, например изменения canvas buffer или масштаба графика.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Откуда берётся <code>ResizeObserver loop completed with undelivered notifications</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Callback меняет размер наблюдаемого элемента, это создаёт новое уведомление, которое снова меняет размер. Браузер ограничивает доставку в текущем кадре и переносит часть records, чтобы не зависнуть, но логическую петлю не исправляет. Нужно прекратить циклическое изменение, сравнивать новый размер с применённым или вынести запись в rAF, если она действительно относится к следующему кадру.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли всегда вызывать <code>disconnect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда observer больше не нужен, да. Это прекращает callbacks и освобождает связи с targets. Если один observer обслуживает много элементов, `unobserve` снимает конкретный target, не затрагивая остальные. В React очистка выполняется в cleanup того effect, где создан observer.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const sentinel = document.querySelector("#sentinel");
let loading = false;

const observer = new IntersectionObserver(async ([entry]) => {
  if (!entry.isIntersecting || loading) return;

  loading = true;
  try {
    await loadNextPage();
  } finally {
    loading = false;
  }
}, { rootMargin: "0px 0px 300px 0px" });

observer.observe(sentinel);
```

<details>
<summary><strong>Зачем здесь <code>rootMargin</code> и флаг <code>loading</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нижняя граница root расширена на 300 пикселей, поэтому загрузка может начаться до появления sentinel в viewport. `loading` не позволяет повторным callbacks запустить одновременно несколько одинаковых запросов. Для завершённого списка observer также нужно отключить.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | API | Главный нюанс |
| --- | --- | --- |
| DOM стороннего widget | `MutationObserver` | Фильтровать типы мутаций и не создавать цикл |
| Infinite scroll | `IntersectionObserver` | Защита от повторного запроса |
| Lazy block | `IntersectionObserver` | `rootMargin` загружает заранее |
| Responsive chart | `ResizeObserver` | Не менять размер циклически в callback |
| Только адаптивные стили | CSS container query | JavaScript observer может быть не нужен |
| React lifecycle | Любой observer | `unobserve` или `disconnect` в cleanup |

## Связанные темы

- [24 Event Loop](<./24 Event Loop.md>)
- [33 requestAnimationFrame и requestIdleCallback](<./33 requestAnimationFrame и requestIdleCallback.md>)
- [45 DOM API innerHTML layout thrashing](<./45 DOM API innerHTML layout thrashing.md>)
- [02 Rendering pipeline reflow repaint composite](<../Browser Internals/02 Rendering pipeline reflow repaint composite.md>)
- [05 Images fonts resource priority preload lazy loading](<../Performance/05 Images fonts resource priority preload lazy loading.md>)

## Источники

- [MDN: `MutationObserver`](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver)
- [MDN: Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [MDN: `ResizeObserver`](https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver)
- [Resize Observer specification](https://drafts.csswg.org/resize-observer/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 31 DOM events](<./31 DOM events.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [33 requestAnimationFrame и requestIdleCallback →](<./33 requestAnimationFrame и requestIdleCallback.md>)
<!-- CARD-NAV-BOTTOM:END -->
