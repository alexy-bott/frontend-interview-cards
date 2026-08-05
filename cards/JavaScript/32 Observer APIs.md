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

Observer APIs сообщают об изменениях, за которыми иначе пришлось бы следить вручную. Браузер накапливает наблюдения и вызывает callback асинхронно, часто передавая сразу несколько записей.

Конкретный момент доставки различается: `MutationObserver` связан с microtask checkpoint, а `IntersectionObserver` и `ResizeObserver` работают через механизмы наблюдения и обновления страницы самого браузера.

Callback любого observer всё равно выполняется на main thread. Observer уменьшает количество ручных проверок, но не делает обработку бесплатной.

| API | Что наблюдает | Типичный сценарий |
| --- | --- | --- |
| `MutationObserver` | Структуру DOM, атрибуты и текстовые узлы | Интеграция с widget или DOM вне контроля приложения |
| `IntersectionObserver` | Пересечение target с viewport или scroll container | Lazy loading, infinite scroll, видимость блока |
| `ResizeObserver` | Размер content box или border box элемента | График, canvas, компонент по размеру контейнера |

`MutationObserver` получает массив объектов `MutationRecord`. При `observe(target, options)` явно выбирают, какие изменения отслеживать: `childList`, `attributes`, `characterData` и при необходимости `subtree`.

Уведомления доставляются во время microtask checkpoint после текущих DOM-изменений. Поэтому несколько изменений могут попасть в один callback.

`IntersectionObserver` не сообщает о каждом событии `scroll`. Callback вызывается после начала наблюдения и когда степень пересечения проходит через один из заданных порогов `threshold`.

`root` задаёт область наблюдения, а при его отсутствии используется viewport. `rootMargin` расширяет или сужает область root, а `intersectionRatio` показывает долю пересечения target. Например, положительный нижний `rootMargin` позволяет начать загрузку до появления target в viewport.

`ResizeObserver` сообщает об изменении размеров конкретного элемента независимо от причины: изменения окна, контента, grid, flex-контейнера или соседней панели. В entry доступны размеры разных box-моделей. Это точнее `window.resize`, когда компонент зависит от собственного контейнера, а не от viewport.

Наблюдение останавливают с учётом конкретного API:

- `IntersectionObserver` и `ResizeObserver` поддерживают `unobserve(target)` для одного элемента и `disconnect()` для всех;
- `MutationObserver` не имеет `unobserve`, поэтому для остановки используется `disconnect()`;
- `takeRecords()` есть у `MutationObserver` и `IntersectionObserver`, но отсутствует у `ResizeObserver`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему <code>MutationObserver</code> связан с microtasks?</strong></summary>

<dl>
<dd>
<h2></h2>

DOM-операция не вызывает callback observer синхронно. Браузер накапливает соответствующие `MutationRecord` и доставляет их во время microtask checkpoint.

Callback выполняется после завершения текущего синхронного кода, но до перехода к следующей task и возможной отрисовке.

Если callback сам изменяет наблюдаемый DOM, он создаёт новые records. Без условия остановки это может привести к повторяющимся вызовам observer.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли <code>MutationObserver</code> следить за React state или JavaScript-объектом?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. `MutationObserver` наблюдает только за изменениями DOM.

React state отслеживается механизмами React, а изменения обычных JavaScript-объектов — через явные функции обновления, state manager или собственную Proxy-механику.

`MutationObserver` применяют, когда DOM изменяет сторонний script, browser extension, `contenteditable`-редактор или другая система вне обычного потока данных приложения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие options нужны <code>MutationObserver</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Хотя бы один из параметров `childList`, `attributes` или `characterData` должен включать соответствующий тип наблюдения.

`subtree: true` распространяет выбранные наблюдения на всех потомков target.

`attributeFilter` ограничивает список отслеживаемых атрибутов и уменьшает количество лишних records. `attributeOldValue` и `characterDataOldValue` добавляют предыдущее значение, если оно действительно требуется обработчику.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>IntersectionObserver</code> обычно лучше scroll listener для lazy loading?</strong></summary>

<dl>
<dd>
<h2></h2>

Коду не нужно на каждое событие `scroll` самостоятельно вызывать `getBoundingClientRect`, сравнивать координаты и реализовывать throttle.

Браузер сам отслеживает геометрическое пересечение и вызывает callback при начале наблюдения и пересечении заданных порогов `threshold`.

Для обычных изображений сначала стоит проверить нативный атрибут `loading="lazy"`. `IntersectionObserver` нужен для кастомной загрузки и более сложной логики появления элементов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличаются <code>rootMargin</code> и <code>threshold</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`rootMargin` изменяет прямоугольник root, относительно которого рассчитывается пересечение. Положительное значение расширяет область, а отрицательное сужает её.

`threshold` задаёт долю target от `0` до `1`, при прохождении которой в любом направлении вызывается callback.

Для предварительной загрузки используют увеличенный root через `rootMargin`, а для условия «видно не менее 50% элемента» используют `threshold: 0.5`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Означает ли <code>isIntersecting</code>, что пользователь действительно видит элемент?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. В базовом режиме `isIntersecting` подтверждает геометрическое пересечение target с root с учётом обрезающих контейнеров.

Это не гарантирует, что пользователь обратил внимание на элемент или что он не перекрыт другим непрозрачным элементом.

Опция `trackVisibility` пытается учитывать фактическую видимость точнее, но требует больше вычислений и имеет ограничения поддержки. Для аналитики также учитывают длительность видимости, состояние вкладки и продуктовые критерии.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать повторной загрузки в infinite scroll?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно проверять `entry.isIntersecting`, состояние `isLoading`, наличие следующей страницы и принадлежность результата текущему запросу.

Флаг `isLoading` не позволяет запустить несколько одинаковых запросов одновременно. На время загрузки sentinel также можно снять с наблюдения, а после добавления данных снова начать наблюдать актуальный элемент.

После получения последней страницы observer нужно отключить. Сам запрос также должен иметь защиту от дублей и устаревших результатов при смене списка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>ResizeObserver</code> отличается от <code>window.resize</code> и container queries?</strong></summary>

<dl>
<dd>
<h2></h2>

`window.resize` сообщает об изменении размеров viewport. Он не сообщает напрямую, какой конкретный элемент изменил размер.

`ResizeObserver` реагирует на размер наблюдаемого элемента и позволяет запустить JavaScript независимо от причины изменения.

CSS container query предпочтительнее, если задача состоит только в изменении стилей по размеру контейнера. Она не требует callback и дополнительного состояния JavaScript.

`ResizeObserver` нужен для вычислений, например изменения внутреннего размера canvas, масштаба графика или параметров виртуализированного списка.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Откуда берётся <code>ResizeObserver loop completed with undelivered notifications</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Ошибка возникает, когда callback изменяет размер наблюдаемого элемента, это создаёт новое уведомление, а следующая обработка снова изменяет размер.

Чтобы не выполнять такой цикл бесконечно в рамках одного обновления страницы, браузер ограничивает доставку и откладывает часть уведомлений.

Это защищает страницу от зависания, но не исправляет логическую причину цикла. Нужно прекратить повторяющееся изменение, сравнивать новый размер с уже применённым или переносить запись в `requestAnimationFrame`, если она должна относиться к следующему кадру.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли всегда вызывать <code>disconnect</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда observer больше не нужен, наблюдение следует остановить. Это прекращает будущие callbacks и удаляет регистрацию наблюдаемых targets.

У `IntersectionObserver` и `ResizeObserver` метод `unobserve(target)` снимает один target, не затрагивая остальные. `disconnect()` прекращает все наблюдения конкретного observer.

У `MutationObserver` метода `unobserve` нет, поэтому для прекращения наблюдений используется `disconnect()`.

В React очистку выполняют в cleanup того effect, в котором observer был создан.

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

Нижняя граница root расширена на 300 пикселей. Поэтому пересечение определяется раньше, и загрузка может начаться до появления sentinel в видимой части viewport.

Флаг `loading` не позволяет повторным callbacks одновременно запустить несколько вызовов `loadNextPage`.

Он не определяет наличие следующей страницы, поэтому после загрузки последней страницы observer нужно отключить через `unobserve` или `disconnect`.

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
