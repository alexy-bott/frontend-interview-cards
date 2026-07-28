# 07 Decorator Proxy Mixin Mediator Flyweight

<!-- CARD-NAV-TOP:START -->
[← 06 Factory Singleton lifecycle](<./06 Factory Singleton lifecycle.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 God Object Class Extraction REP CCP →](<./08 God Object Class Extraction REP CCP.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Чем отличаются Decorator и Proxy? Какие задачи решают Mixin, Mediator и Flyweight во frontend?

<details>
<summary><strong>Показать ответ</strong></summary>

Decorator, или декоратор, оборачивает объект или функцию с совместимым интерфейсом и добавляет поведение до или после передачи вызова оригиналу. Например, исходная функция выполняет HTTP-запрос, а обёртки добавляют логирование, метрики или retry, то есть повторные попытки. Клиент по-прежнему вызывает тот же смысловой контракт.

Proxy, или заместитель, встаёт вместо другого объекта и контролирует доступ к нему. Он может отложить создание ресурса, проверить права, ограничить операции, выполнить lazy loading, или отложенную загрузку, либо перенаправить вызов удалённому объекту. Встроенный JavaScript `Proxy` является языковым механизмом перехвата операций через traps, например `get` и `set`; паттерн Proxy можно реализовать и без него.

Структура Decorator и Proxy может выглядеть одинаково: оба делегируют вызов другому объекту. Различается намерение. Decorator наращивает обязанности, а Proxy управляет доступом или представляет другой объект. На практике один wrapper может совмещать обе роли, поэтому важно объяснять задачу.

Остальные паттерны решают другие проблемы:

| Паттерн | Механизм | Frontend-пример |
|---|---|---|
| Mixin | Добавляет набор методов нескольким объектам или классам | Legacy class components; в современном React чаще заменяется hooks и композицией |
| Mediator | Отдельный объект координирует взаимодействие участников | Dialog manager управляет общим слоем модальных окон, не связывая features друг с другом |
| Flyweight | Выносит одинаковое состояние множества объектов в общий разделяемый объект | Тысячи узлов графа хранят `styleId`, а стили лежат в одном registry, или реестре |

Flyweight разделяет внутреннее общее состояние и внешний контекст конкретного элемента. Например, общий объект стиля содержит цвет и шрифт, а node хранит только координаты и ссылку на стиль. Это экономит память при действительно большом числе повторений, но усложняет модель данных и не нужно обычному списку из десятков элементов.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Decorator и обычный wrapper - одно и то же?</summary>

Wrapper - общее название любой обёртки. Decorator сохраняет совместимый контракт и позволяет наслаивать дополнительное поведение вокруг исходного объекта. Если обёртка полностью меняет интерфейс, она ближе к Adapter; если только упрощает подсистему - к Facade.

</details>

<details>
<summary><strong>Вопрос:</strong> Может ли React HOC быть Decorator?</summary>

Higher-order component (HOC) принимает компонент и возвращает новый компонент с дополнительным поведением или props, поэтому может быть Decorator-подобной реализацией. Однако HOC иногда меняет публичный контракт props и создаёт несколько вложенных обёрток. Для повторного использования логики современный React часто использует собственные hooks и обычную композицию.

</details>

<details>
<summary><strong>Вопрос:</strong> TypeScript decorator и паттерн Decorator - одно и то же?</summary>

Нет. TypeScript decorators - синтаксический механизм, вызывающий специальные функции для классов и их элементов. С его помощью можно реализовать Decorator-подобное поведение, а также добавлять метаданные или регистрацию. Современные decorators и старый режим `experimentalDecorators` имеют разную модель, поэтому конфигурацию проекта нужно учитывать отдельно.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему порядок decorators важен?</summary>

Обёртки вложены друг в друга. `withRetry(withMetrics(request))` измеряет каждую попытку внутри retry иначе, чем `withMetrics(withRetry(request))`, где снаружи измеряется вся операция. Порядок должен отражать требуемое поведение ошибок, кэша, повторных попыток и логирования.

</details>

<details>
<summary><strong>Вопрос:</strong> Где встроенный <code>Proxy</code> используется на практике?</summary>

Библиотеки могут отслеживать чтение и запись свойств или строить реактивное состояние. Например, Immer через Proxy создаёт draft, то есть временную изменяемую версию state, отслеживает операции над ней и строит новый immutable результат без изменения исходного объекта. Это языковой механизм внутри библиотеки; прикладному коду не обязательно самостоятельно строить паттерн Proxy.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие риски у JavaScript <code>Proxy</code>?</summary>

Перехваченные операции становятся менее очевидными, отладка усложняется, а некорректные traps, то есть обработчики операций `get`, `set` и других, могут нарушить обязательные правила объекта и вызвать `TypeError`. Proxy является отдельным объектом: `proxy !== target`, даже если обращения делегируются target. Для простой проверки данных явная функция обычно понятнее.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему Mixins редко используют в современном React?</summary>

Mixin неявно добавляет методы и state, может создавать конфликты имён и затрудняет понимание источника поведения. Hooks возвращают значения и функции явно, а композиция компонентов показывает структуру в JSX. Mixins всё ещё встречаются в legacy-коде с классами и некоторых API фреймворков.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем Mediator отличается от event bus?</summary>

Mediator знает участников и содержит явную логику их координации. Event bus в Pub/Sub обычно только доставляет события подписчикам и не обязан понимать сценарий. Например, dialog manager решает, какой Dialog открыть и как закрыть предыдущий; общий bus лишь передал бы событие неизвестному набору listeners.

</details>

<details>
<summary><strong>Вопрос:</strong> Как Mediator превращается в God Object?</summary>

Если через него проходят все формы, уведомления, навигация, API и бизнес-правила, он получает слишком много причин для изменения. Mediator должен координировать одну связную группу участников, например стек модальных окон. Несвязанные сценарии получают отдельные координаторы или прямые зависимости.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем Flyweight отличается от list virtualization?</summary>

Flyweight уменьшает объём данных на объект за счёт разделения повторяющегося состояния. Виртуализация списка уменьшает число одновременно созданных DOM-элементов, отображая только видимую часть. Для огромной диаграммы могут применяться оба подхода, но они решают разные проблемы.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда эти паттерны не стоит использовать?</summary>

Decorator не нужен для одной простой проверки, Proxy - если явный API достаточен, Mediator - когда два модуля могут взаимодействовать напрямую через понятный контракт, а Flyweight - без измеренной проблемы памяти. Название паттерна не оправдывает дополнительный слой.

</details>

## Где это встречается во frontend

> [!NOTE]
> | Сценарий | Подход |
> |---|---|
> | Добавить повторные попытки и метрики к API-функции | Последовательность Decorator-обёрток с осознанным порядком |
> | Контролировать чтение и запись draft state | JavaScript `Proxy` внутри библиотеки управления состоянием |
> | Управлять общим стеком Dialog | Ограниченный Mediator `dialogManager` |
> | Поддерживать поведение legacy-классов | Существующий Mixin, постепенно заменяемый композицией |
> | Отрисовать большой граф | Flyweight для общих стилей и отдельная оптимизация рендеринга |

## Связанные темы

- [15 Proxy Reflect](<../JavaScript/15 Proxy Reflect.md>)
- [28 abstract classes implements decorators](<../TypeScript/28 abstract classes implements decorators.md>)
- [04 Observer PubSub EventTarget events](<./04 Observer PubSub EventTarget events.md>)
- [05 Dependency Inversion API adapters hooks](<../Principles/05 Dependency Inversion API adapters hooks.md>)
- [06 React performance rerenders memo profiler virtualization](<../Performance/06 React performance rerenders memo profiler virtualization.md>)

## Источники

- [MDN: Proxy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy)
- [TypeScript: Decorators](https://www.typescriptlang.org/docs/handbook/decorators.html)
- [TypeScript 5.0: Decorators](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html#decorators)
- [React: Reusing logic with custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [Immer: Introduction and how Immer works](https://immerjs.github.io/immer/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Factory Singleton lifecycle](<./06 Factory Singleton lifecycle.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 God Object Class Extraction REP CCP →](<./08 God Object Class Extraction REP CCP.md>)
<!-- CARD-NAV-BOTTOM:END -->
