# Дополнительные паттерны во frontend

<!-- CARD-NAV-TOP:START -->
[← 06 Factory Singleton и жизненный цикл](<./06 Factory Singleton и жизненный цикл.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Декомпозиция God Object и границы модулей →](<./08 Декомпозиция God Object и границы модулей.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются Decorator и Proxy? Какие задачи решают Mixin, Mediator и Flyweight во frontend?**

<h2></h2>

<br>
<dl>
<dd>

Эти паттерны решают разные задачи:

| Паттерн | Основная задача |
|---|---|
| Decorator | Добавить объекту поведение, сохранив совместимый контракт |
| Proxy | Контролировать доступ к другому объекту или представлять его |
| Mixin | Добавить одинаковый набор возможностей нескольким объектам |
| Mediator | Централизовать координацию связанных участников |
| Flyweight | Разделить повторяющееся состояние между множеством объектов |

Decorator и Proxy внешне часто выглядят одинаково:

```text
client
→ wrapper
→ original object
```

Оба могут хранить исходный объект и делегировать ему вызовы.

Главное различие — намерение:

```text
Decorator
→ добавляет обязанности

Proxy
→ контролирует доступ
  или представляет другой объект
```

### Decorator

Decorator, или декоратор, оборачивает объект или функцию с совместимым контрактом и добавляет поведение до или после вызова оригинала.

Например, есть функция HTTP-запроса:

```ts
type Request<T> = () => Promise<T>;
```

Исходная операция:

```ts
const loadUser: Request<User> =
  async () => {
    const response =
      await fetch("/api/user");

    if (!response.ok) {
      throw new Error(
        "Failed to load user",
      );
    }

    return response.json();
  };
```

Decorator логирования:

```ts
function withLogging<T>(
  request: Request<T>,
): Request<T> {
  return async () => {
    console.log(
      "Request started",
    );

    try {
      const result =
        await request();

      console.log(
        "Request completed",
      );

      return result;
    } catch (error) {
      console.error(
        "Request failed",
        error,
      );

      throw error;
    }
  };
}
```

Decorator повторных попыток:

```ts
function withRetry<T>(
  request: Request<T>,
  maxAttempts: number,
): Request<T> {
  return async () => {
    let lastError:
      unknown = null;

    for (
      let attempt = 1;
      attempt <= maxAttempts;
      attempt += 1
    ) {
      try {
        return await request();
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError;
  };
}
```

Обёртки можно комбинировать:

```ts
const request =
  withLogging(
    withRetry(
      loadUser,
      3,
    ),
  );

const user =
  await request();
```

Клиент по-прежнему работает с контрактом:

```text
Request<User>
```

и не знает, сколько дополнительных слоёв добавлено.

Decorator часто используют для:

- logging;
- metrics;
- retry;
- cache;
- tracing;
- authorization check;
- нормализации ошибок;
- ограничения времени операции.

Порядок Decorator важен.

```ts
withLogging(
  withRetry(request, 3),
);
```

означает:

```text
один внешний log
→ внутри несколько попыток
```

Другой порядок:

```ts
withRetry(
  withLogging(request),
  3,
);
```

означает:

```text
каждая попытка
→ логируется отдельно
```

То же относится к cache и metrics.

Например:

```text
metrics снаружи retry
→ измеряется вся операция

metrics внутри retry
→ измеряется каждая попытка
```

Порядок должен отражать требования продукта и наблюдаемости.

Decorator сохраняет смысловой контракт исходного объекта.

Если wrapper полностью меняет интерфейс:

```text
ExternalApi
→ другой интерфейс приложения
```

он ближе к Adapter.

Если wrapper предоставляет упрощённый API над подсистемой, он ближе к Facade.

`Wrapper` — более общее слово для любой обёртки.

Не каждый wrapper является Decorator.

### Proxy

Proxy, или заместитель, встаёт вместо другого объекта и контролирует взаимодействие с ним.

Упрощённо:

```text
client
→ Proxy
→ real subject
```

Proxy может:

- лениво создать дорогой ресурс;
- проверить право доступа;
- ограничить частоту операций;
- кэшировать результат;
- представить удалённый объект;
- скрыть сетевой вызов;
- вести журнал доступа;
- отозвать доступ;
- управлять lifecycle ресурса.

Пример ленивого Proxy:

```ts
type ReportService = {
  generate(): Promise<string>;
};

function createReportServiceProxy(
  createService:
    () => ReportService,
): ReportService {
  let service:
    ReportService | null =
    null;

  function getService() {
    service ??=
      createService();

    return service;
  }

  return {
    generate() {
      return getService()
        .generate();
    },
  };
}
```

Реальный сервис не создаётся до первого вызова:

```text
create proxy
→ ресурс ещё не создан

generate()
→ создать real service
→ делегировать вызов
```

Другой пример — protection proxy:

```ts
function createAdminProxy(
  service: AdminService,
  canAccess: () => boolean,
): AdminService {
  return {
    deleteUser(userId) {
      if (!canAccess()) {
        throw new Error(
          "Forbidden",
        );
      }

      return service.deleteUser(
        userId,
      );
    },
  };
}
```

Клиент вызывает тот же контракт, но Proxy решает, разрешено ли передать вызов реальному объекту.

Разрешение frontend не является защитой само по себе.

Backend всё равно должен выполнить собственную авторизацию.

Frontend Proxy здесь может:

- скрыть недоступное действие;
- дать раннюю ошибку;
- централизовать UI-политику;
- не отправлять заведомо запрещённый запрос.

Но он не заменяет серверную проверку прав.

### Decorator и Proxy

Один и тот же wrapper может совмещать обе роли.

Например, кэширующая обёртка:

```text
добавляет cache
→ Decorator

не обращается к реальному объекту
при cache hit
→ Proxy-подобный контроль доступа
```

Поэтому паттерн определяют по основной задаче.

| Вопрос | Decorator | Proxy |
|---|---|---|
| Зачем добавлен слой? | Расширить поведение | Управлять доступом |
| Реальный объект обычно существует? | Да | Может создаваться лениво |
| Может ли вызов не дойти до объекта? | Иногда | Часто |
| Можно ли наслаивать несколько обёрток? | Это типичный сценарий | Возможно, но не основная цель |
| Основной акцент | Дополнительные обязанности | Замещение и контроль |

### JavaScript `Proxy`

Встроенный JavaScript `Proxy` — языковой механизм перехвата операций над объектом.

Он создаётся через:

```ts
const proxy =
  new Proxy(
    target,
    handler,
  );
```

`handler` содержит traps:

```text
get
set
has
deleteProperty
ownKeys
apply
construct
```

Пример проверки записи:

```ts
const user =
  new Proxy(
    {
      name: "Alex",
    },
    {
      set(
        target,
        property,
        value,
        receiver,
      ) {
        if (
          property === "name" &&
          typeof value !==
            "string"
        ) {
          throw new TypeError(
            "name must be a string",
          );
        }

        return Reflect.set(
          target,
          property,
          value,
          receiver,
        );
      },
    },
  );
```

Встроенный `Proxy` и паттерн Proxy связаны идеей замещения, но не являются одним и тем же.

Паттерн можно реализовать обычным объектом:

```ts
const serviceProxy = {
  getUser() {
    return realService
      .getUser();
  },
};
```

А JavaScript `Proxy` может использоваться для других задач метапрограммирования:

- реактивность;
- валидация;
- отслеживание чтения;
- drafts;
- virtual properties;
- debugging.

Traps должны соблюдать invariants объекта.

Например, Proxy не может сообщить произвольные сведения о non-configurable properties, если это нарушает правила target.

Нарушение invariants приводит к:

```text
TypeError
```

Для стандартного делегирования внутри traps обычно используют `Reflect`:

```ts
Reflect.get(
  target,
  property,
  receiver,
);
```

Но нужно избегать рекурсии.

Если trap снова выполняет операцию через тот же Proxy, он может вызвать сам себя бесконечно.

JavaScript Proxy является отдельным объектом:

```ts
proxy !== target;
```

Это может влиять на:

- identity checks;
- `Map` и `Set`;
- сравнение по ссылке;
- доступ к некоторым внутренним slots;
- debugging.

Proxy стоит использовать, когда перехват операций действительно является частью модели.

Для простой проверки или явного API обычная функция часто понятнее.

### Immer и Proxy

Immer использует Proxy для создания draft:

```ts
const nextState =
  produce(
    currentState,
    (draft) => {
      draft.user.name =
        "Alex";
    },
  );
```

`draft` выглядит изменяемым, но Immer отслеживает операции и создаёт новый immutable result.

Концептуально:

```text
current state
→ Proxy draft
→ записать изменения
→ новый state
```

Неизменённые части могут сохранять прежние ссылки через structural sharing.

Это пример использования языкового `Proxy` внутри библиотеки.

Прикладному коду Redux Toolkit обычно не нужно самостоятельно создавать Proxy для reducers.

### TypeScript decorators

TypeScript decorator и паттерн Decorator — разные понятия.

Паттерн Decorator:

```text
wrapper
→ сохраняет совместимый контракт
→ добавляет поведение
```

TypeScript decorator — специальная функция, применяемая синтаксисом:

```ts
@logged
class UserService {
  // ...
}
```

С её помощью можно:

- изменить или заменить класс;
- обернуть метод;
- выполнить регистрацию;
- добавить metadata;
- изменить инициализацию поля.

Она может реализовать Decorator-подобное поведение, но сам синтаксис не определяет паттерн.

В TypeScript существуют две разные модели.

Современные decorators поддерживаются начиная с TypeScript 5.0 без обязательного `experimentalDecorators`.

Legacy decorators включаются через:

```json
{
  "compilerOptions": {
    "experimentalDecorators": true
  }
}
```

Эти модели отличаются:

- сигнатурами функций;
- порядком работы;
- доступным context;
- emit;
- поддержкой параметров;
- совместимостью с `emitDecoratorMetadata`.

Decorator, написанный для legacy-модели, не обязательно работает как современный decorator.

Поэтому при чтении проекта нужно сначала проверить:

- версию TypeScript;
- `tsconfig`;
- используемый framework;
- ожидаемую модель decorators.

### React HOC и Decorator

Higher-order component принимает компонент и возвращает новый компонент:

```ts
const EnhancedComponent =
  withPermission(
    OriginalComponent,
  );
```

HOC может быть Decorator-подобным, если добавляет поведение и сохраняет ожидаемый контракт.

Например:

```tsx
function withLoading<P>(
  Component:
    React.ComponentType<P>,
) {
  return function WithLoading(
    props:
      P & {
        isLoading: boolean;
      },
  ) {
    if (props.isLoading) {
      return <Spinner />;
    }

    return (
      <Component {...props} />
    );
  };
}
```

Но HOC не всегда является строгим Decorator.

Он может:

- добавить обязательные props;
- скрыть часть props;
- изменить lifecycle;
- изменить структуру DOM;
- не передать ref;
- потерять static properties;
- создать глубокое дерево wrappers.

Для повторного использования stateful-логики современный React часто использует custom hooks.

Для визуального расширения часто достаточно обычной композиции:

```tsx
<Card>
  <ProtectedContent />
</Card>
```

HOC остаётся полезен, если проект или библиотека уже использует такой API либо нужно оборачивать компонент как значение.

### Mixin

Mixin добавляет набор методов или свойств нескольким объектам или классам без построения обычной иерархии наследования.

Упрощённо:

```text
Mixin behavior
→ Object A
→ Object B
→ Object C
```

Пример объектного Mixin:

```ts
const selectable = {
  select() {
    console.log("selected");
  },

  unselect() {
    console.log(
      "unselected",
    );
  },
};

const item = {
  id: "42",
};

Object.assign(
  item,
  selectable,
);
```

После этого `item` получает методы Mixin.

Mixin применялся для повторного использования поведения в системах, где:

- множественное наследование недоступно;
- несколько классов должны получить одинаковые методы;
- framework ожидает расширение prototype или объекта.

Проблемы Mixin:

- конфликт имён;
- неясный источник метода;
- скрытые зависимости от `this`;
- изменение prototype;
- сложный порядок применения;
- неявно добавляемое state;
- трудная типизация;
- сложная замена поведения.

Например, два Mixins могут определить:

```text
initialize()
destroy()
```

и последний незаметно перезапишет предыдущий метод.

Mixin также может предполагать, что объект уже содержит:

```text
this.user
this.store
this.options
```

Но это требование не видно из сигнатуры вызова.

Поэтому Mixin часто создаёт более скрытые связи, чем явная композиция.

### Mixin и React hooks

Custom hook не является Mixin в строгом смысле.

Hook:

```ts
const {
  value,
  select,
} = useSelection();
```

явно возвращает данные и функции.

Он не копирует методы в компонент и не изменяет prototype.

Различие:

```text
Mixin
→ внедряет возможности в объект

Hook
→ явно возвращает значения
  для композиции логики
```

Hooks обычно проще отслеживать:

- видно место вызова;
- видно возвращаемые значения;
- зависимости передаются аргументами;
- конфликты имён решаются обычным переименованием;
- поведение не появляется неявно на `this`.

В современном React Mixins в основном встречаются:

- в legacy class components;
- в старых библиотеках;
- в сторонних framework API;
- при постепенной миграции старого проекта.

Не нужно переписывать стабильный legacy Mixin только ради названия.

Но при изменении такого кода полезно постепенно выделять:

- чистые функции;
- сервисы;
- hooks;
- композиционные компоненты.

### Mediator

Mediator, или посредник, централизует взаимодействие нескольких связанных участников.

Без Mediator:

```text
A ↔ B
A ↔ C
B ↔ C
```

Каждый участник знает о других и координирует их напрямую.

С Mediator:

```text
A ─┐
B ─┼→ Mediator
C ─┘
```

Участники сообщают Mediator о событиях или намерениях, а он решает, что должны сделать остальные части.

Frontend-примеры:

- менеджер стека Dialog;
- координатор сложной формы;
- менеджер overlay;
- drag-and-drop coordinator;
- orchestration нескольких независимых widgets;
- редактор с toolbar, canvas и selection panel.

Например, dialog manager может решать:

```text
открыть новый Dialog
→ закрыть несовместимый предыдущий
→ сохранить trigger
→ обновить Overlay
→ восстановить focus после закрытия
```

Отдельные Dialog не обязаны знать друг о друге.

Пример ограниченного контракта:

```ts
type DialogMediator = {
  open(
    dialog: DialogDescriptor,
  ): void;

  close(
    dialogId: string,
  ): void;

  closeTop(): void;
};
```

Mediator знает участников и содержит логику координации.

Он отличается от event bus.

```text
Event bus
→ доставляет события

Mediator
→ понимает сценарий
  и принимает решения
```

Например, event bus может доставить:

```text
dialog:opened
```

неизвестному набору listeners.

Mediator сам решает:

- можно ли открыть Dialog;
- какой Dialog закрыть;
- как обновить stack;
- куда вернуть focus.

Обязательную последовательность обычно безопаснее держать в Mediator или use case, чем распределять между случайными subscribers.

Mediator отличается и от Facade.

```text
Facade
→ предоставляет простой вход
  в сложную подсистему

Mediator
→ координирует взаимодействие
  участников подсистемы
```

Один объект может выполнять обе роли.

Например, `dialogManager.open()` является простым Facade API и одновременно координирует Dialog через Mediator-логику.

### Риск God Object

Mediator может превратиться в God Object, если через него проходят все процессы приложения:

```text
forms
dialogs
notifications
navigation
API
analytics
permissions
business rules
```

Тогда он:

- получает слишком много причин для изменения;
- становится центральной зависимостью;
- скрывает владельцев сценариев;
- усложняет тестирование;
- связывает несвязанные features.

Mediator должен координировать одну связную группу участников.

Например:

```text
dialogStackMediator
editorMediator
dragDropCoordinator
```

лучше, чем:

```text
applicationMediator
```

для всех действий приложения.

Если два модуля могут общаться через простой явный контракт, отдельный Mediator может быть лишним.

### Flyweight

Flyweight, или приспособленец, уменьшает потребление памяти при большом числе похожих объектов.

Он разделяет состояние на две части:

```text
intrinsic state
→ одинаковое и разделяемое

extrinsic state
→ уникальное для конкретного объекта
```

Например, на canvas отображаются сотни тысяч узлов.

Без Flyweight каждый узел хранит полный стиль:

```ts
type Node = {
  x: number;
  y: number;
  color: string;
  fontFamily: string;
  fontSize: number;
  borderWidth: number;
};
```

Если тысячи узлов имеют одинаковые стили, данные повторяются.

С Flyweight общий стиль хранится один раз:

```ts
type NodeStyle = {
  color: string;
  fontFamily: string;
  fontSize: number;
  borderWidth: number;
};

type GraphNode = {
  x: number;
  y: number;
  styleId: string;
};
```

Registry:

```ts
const styles =
  new Map<
    string,
    NodeStyle
  >();
```

Каждый node хранит только:

```text
координаты
+
styleId
```

При рендере внешний контекст и общий стиль объединяются:

```ts
function drawNode(
  node: GraphNode,
  style: NodeStyle,
) {
  // x и y относятся к node,
  // стиль разделяется.
}
```

Другие frontend-примеры:

- разделяемые стили узлов диаграммы;
- повторяющиеся glyph descriptions;
- большой редактор документов;
- tile metadata карты;
- повторяющаяся конфигурация объектов игрового поля;
- registry неизменяемых форматов или шаблонов.

Разделяемое внутреннее состояние желательно делать immutable.

Если один потребитель изменит общий Flyweight:

```text
изменятся все объекты,
которые на него ссылаются
```

Если нужен другой стиль, безопаснее получить другой Flyweight или создать новую версию.

Factory или registry часто отвечает за повторное использование:

```ts
function getNodeStyle(
  key: string,
): NodeStyle {
  const existing =
    styles.get(key);

  if (existing) {
    return existing;
  }

  const style =
    createNodeStyle(key);

  styles.set(
    key,
    style,
  );

  return style;
}
```

Flyweight оправдан, когда:

- объектов действительно много;
- повторяющееся состояние занимает заметную память;
- данные можно безопасно разделить;
- измерения показывают проблему;
- стоимость дополнительной косвенности окупается.

Для списка из нескольких десятков элементов он обычно не нужен.

### Flyweight, cache и interning

Flyweight похож на cache, но намерение отличается.

```text
Cache
→ сохранить результат,
  чтобы не вычислять или не загружать повторно

Flyweight
→ разделить одно состояние
  между множеством объектов
```

Registry Flyweight может технически использовать cache:

```text
одинаковый key
→ один общий объект
```

Создание единственного объекта для одинакового значения также называют interning.

Например:

```text
одинаковая строка конфигурации
→ одна каноническая instance
```

Эти идеи пересекаются, но не каждый cache является Flyweight.

### Flyweight и virtualization

Flyweight и виртуализация решают разные проблемы.

```text
Flyweight
→ уменьшает данные
  на один объект

Virtualization
→ уменьшает число объектов
  или DOM-узлов,
  отображаемых одновременно
```

Для огромной диаграммы могут понадобиться оба подхода:

```text
общие стили
→ Flyweight

только видимые элементы
→ virtualization
```

Flyweight не сокращает число DOM-узлов сам по себе.

Virtualization не устраняет повторяющиеся данные в сохранённой модели.

### Flyweight и `React.memo`

`React.memo` не является Flyweight.

`React.memo` может пропустить повторный render компонента, если props не изменились по правилам сравнения.

Flyweight разделяет одно внутреннее состояние между множеством объектов.

```text
React.memo
→ оптимизация повторного render

Flyweight
→ оптимизация представления данных в памяти
```

Объекты props могут случайно использовать общие ссылки, но это ещё не делает компонент реализацией Flyweight.

### Когда использовать паттерны

Практический выбор начинается с проблемы.

```text
Нужно добавить поведение,
не меняя исходный контракт
→ Decorator

Нужно управлять доступом
или лениво представить объект
→ Proxy

Нужно внедрить одинаковые методы
в несколько legacy-объектов
→ Mixin

Нужно централизовать координацию
связанных участников
→ Mediator

Нужно разделить повторяющееся состояние
огромного числа объектов
→ Flyweight
```

Перед добавлением паттерна проверяют прямое решение.

```text
одна дополнительная проверка
→ обычная функция

один локальный вызов
→ прямой API

два явно связанных модуля
→ прямой контракт

несколько десятков объектов
→ обычные данные
```

Паттерн не нужен только потому, что код можно формально описать его названием.

### Основные ограничения

**Decorator:**

- порядок обёрток влияет на результат;
- stack trace становится глубже;
- ошибка может обрабатываться несколько раз;
- большое число wrappers усложняет поиск фактического поведения.

**Proxy:**

- реальное выполнение скрыто;
- lazy-ошибка возникает позже;
- identity может отличаться;
- JavaScript traps усложняют отладку;
- некорректные traps нарушают invariants.

**Mixin:**

- конфликты имён;
- скрытые зависимости;
- неявно добавляемое поведение;
- сложный lifecycle.

**Mediator:**

- может превратиться в God Object;
- участники начинают зависеть от одного центра;
- слишком общий контракт скрывает разные сценарии.

**Flyweight:**

- появляется дополнительный lookup;
- модель делится на внутреннее и внешнее состояние;
- изменение общего объекта затрагивает множество потребителей;
- оптимизация может не окупиться без большого объёма данных.

Главный принцип:

```text
одинаковая форма wrapper
не означает одинаковый паттерн
```

Нужно объяснять:

```text
какая проблема решается
какая зависимость изменяется
какую цену добавляет решение
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Decorator и обычный wrapper - одно и то же?</strong></summary>

<dl>
<dd>
<h2></h2>

Wrapper — общее название любой обёртки.

Decorator является wrapper, который:

- сохраняет совместимый смысловой контракт;
- делегирует исходному объекту;
- добавляет поведение;
- допускает наслаивание обёрток.

Если wrapper меняет интерфейс, он ближе к Adapter.

Если предоставляет упрощённый вход в подсистему — к Facade.

Если контролирует доступ или ленивое создание — к Proxy.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли React HOC быть Decorator?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, HOC может быть Decorator-подобной реализацией:

```text
Component
→ HOC
→ EnhancedComponent
```

Например, HOC добавляет:

- проверку прав;
- loading state;
- error boundary;
- данные Context.

Но HOC может изменить props, ref, DOM-структуру и lifecycle, поэтому не каждый HOC является строгим Decorator.

В современном React для повторного использования логики часто используют custom hooks, а для визуального расширения — обычную композицию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>TypeScript decorator и паттерн Decorator - одно и то же?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Паттерн Decorator — способ оборачивания совместимого объекта или функции.

TypeScript decorator — синтаксический механизм для классов и их элементов:

```ts
@logged
class Service {}
```

Он может реализовать Decorator-подобное поведение, регистрацию или metadata.

Нужно также различать:

```text
современные decorators
```

и:

```text
legacy experimentalDecorators
```

Их сигнатуры и возможности отличаются, поэтому decorator нельзя автоматически переносить между двумя режимами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему порядок decorators важен?</strong></summary>

<dl>
<dd>
<h2></h2>

Обёртки вложены друг в друга.

```ts
withRetry(
  withMetrics(request),
);
```

измеряет каждую попытку отдельно.

```ts
withMetrics(
  withRetry(request),
);
```

измеряет всю операцию вместе с повторами.

Аналогично порядок влияет на:

- cache;
- authorization;
- timeout;
- error mapping;
- logging;
- tracing.

Порядок является частью контракта и должен покрываться тестами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Где встроенный <code>Proxy</code> используется на практике?</strong></summary>

<dl>
<dd>
<h2></h2>

JavaScript `Proxy` используют для:

- реактивности;
- отслеживания чтения;
- валидации записи;
- virtual properties;
- debugging;
- immutable drafts.

Например, Immer предоставляет draft через Proxy.

Код изменяет draft обычными операциями, а Immer создаёт новый immutable result и сохраняет ссылки на неизменённые части.

Прикладному коду Redux Toolkit обычно не нужно самостоятельно создавать Proxy для reducers.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие риски у JavaScript <code>Proxy</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Основные риски:

- операции становятся неявными;
- debugging усложняется;
- `proxy !== target`;
- traps могут вызвать рекурсию;
- некоторые объекты используют внутренние slots;
- нарушение invariants приводит к `TypeError`.

Для стандартного делегирования применяют `Reflect`, но нужно следить, чтобы операция не попала обратно в тот же trap бесконечно.

Для простой проверки данных явная функция обычно понятнее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему Mixins редко используют в современном React?</strong></summary>

<dl>
<dd>
<h2></h2>

Mixin неявно добавляет объекту:

- методы;
- state;
- lifecycle;
- зависимости от `this`.

Это создаёт конфликты имён и затрудняет понимание источника поведения.

Custom hook явно возвращает значения и функции:

```ts
const {
  value,
  update,
} = useFeature();
```

Композиция компонентов показывает структуру в JSX.

Mixins всё ещё могут встречаться в legacy class components и старых framework API.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Mediator отличается от event bus?</strong></summary>

<dl>
<dd>
<h2></h2>

Event bus обычно доставляет событие:

```text
publisher
→ bus
→ subscribers
```

Он не обязан понимать бизнес-сценарий.

Mediator знает участников и решает, как их координировать:

```text
Dialog открыт
→ закрыть конфликтующий Dialog
→ обновить stack
→ настроить Overlay
→ сохранить focus target
```

Если обязательный порядок распределён между listeners bus, зависимость становится скрытой.

Связную последовательность часто понятнее держать в Mediator или use case.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Mediator превращается в God Object?</strong></summary>

<dl>
<dd>
<h2></h2>

Это происходит, когда один Mediator начинает управлять несвязанными областями:

- Dialog;
- формы;
- API;
- навигация;
- analytics;
- permissions;
- notifications.

Он получает слишком много причин для изменения и становится центральной зависимостью.

Mediator должен координировать одну связную группу участников:

```text
dialogStackMediator
editorMediator
dragDropCoordinator
```

Несвязанные сценарии получают отдельные координаторы или прямые контракты.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Flyweight отличается от list virtualization?</strong></summary>

<dl>
<dd>
<h2></h2>

Flyweight уменьшает количество повторяющихся данных:

```text
много объектов
→ один общий style object
```

Virtualization уменьшает количество одновременно созданных элементов:

```text
большой список
→ в DOM только видимый диапазон
```

Для большой диаграммы могут использоваться оба подхода.

Они оптимизируют разные части системы и требуют отдельных измерений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда эти паттерны не стоит использовать?</strong></summary>

<dl>
<dd>
<h2></h2>

Decorator не нужен для одной короткой проверки.

Proxy не нужен, если прямой API уже ясно выражает доступ.

Mixin не нужен, если поведение можно передать явной функцией или композицией.

Mediator не нужен, когда два модуля могут взаимодействовать через простой контракт.

Flyweight не нужен без большого числа повторений и измеренной проблемы памяти.

Название паттерна не компенсирует стоимость дополнительного слоя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Decorator отличается от middleware?</strong></summary>

<dl>
<dd>
<h2></h2>

Decorator оборачивает один объект или функцию и возвращает совместимую версию:

```text
request
→ decorated request
```

Middleware является элементом цепочки обработки:

```text
input
→ middleware A
→ middleware B
→ handler
```

Middleware обычно получает функцию `next` или аналогичный механизм передачи управления.

Функционально эти идеи могут пересекаться: цепочку middleware можно построить вложенными decorators.

Различие определяется моделью API и намерением, а не только формой функции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли <code>React.memo</code> реализацией Proxy?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет.

`React.memo` сообщает React, что повторный render компонента можно пропустить, если props считаются неизменившимися.

Proxy представляет другой объект и контролирует обращения к нему.

Обе идеи могут избегать лишней работы, но имеют разные контракты и области применения.

Точнее считать `React.memo` механизмом мемоизации рендера, а не реализацией Proxy pattern.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Mixin отличается от custom hook?</strong></summary>

<dl>
<dd>
<h2></h2>

Mixin внедряет методы или свойства в объект:

```text
object
+
mixin methods
```

Custom hook вызывается явно и возвращает значения:

```ts
const feature =
  useFeature();
```

Hook:

- не изменяет prototype;
- не копирует методы в компонент;
- явно получает зависимости;
- явно возвращает API;
- позволяет переименовать результаты.

Поэтому hooks решают похожую задачу повторного использования логики, но используют композицию, а не Mixin-механику.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Mediator отличается от Facade?</strong></summary>

<dl>
<dd>
<h2></h2>

Facade упрощает внешний доступ к подсистеме:

```text
client
→ простой API
→ подсистема
```

Mediator координирует взаимодействие участников внутри:

```text
participant A
participant B
participant C
→ Mediator
```

Один объект может выполнять обе роли.

Например, `dialogManager.open()` является простым Facade API, а внутренняя логика управления stack выполняет роль Mediator.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Flyweight отличается от cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Cache сохраняет результат, чтобы не выполнять работу повторно:

```text
key
→ ранее вычисленное значение
```

Flyweight позволяет множеству объектов использовать одно общее состояние:

```text
object A ─┐
object B ─┼→ shared style
object C ─┘
```

Registry Flyweight может быть реализован через cache, но намерение отличается.

Не каждый cache уменьшает повторение состояния внутри множества объектов.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Подход |
|---|---|
| Добавить retry, metrics и logging к API-функции | Последовательность Decorator-обёрток |
| Лениво создать дорогой клиент | Proxy с отложенной инициализацией |
| Контролировать чтение и запись draft state | JavaScript `Proxy` внутри Immer |
| Поддерживать поведение legacy-классов | Существующий Mixin, постепенно заменяемый композицией |
| Управлять общим стеком Dialog | Ограниченный Mediator `dialogManager` |
| Координировать части сложного редактора | Mediator конкретного editor scope |
| Отрисовать большой граф | Flyweight для общих стилей и отдельная virtualization |
| Несколько десятков обычных элементов | Прямые данные без Flyweight |
| Одна дополнительная проверка перед вызовом | Обычная функция без цепочки Decorator |

## Связанные темы

- [15 Proxy Reflect](<../JavaScript/15 Proxy Reflect.md>)
- [28 Классы и декораторы в TypeScript](<../TypeScript/28 Классы и декораторы в TypeScript.md>)
- [04 Observer PubSub и браузерные события](<./04 Observer PubSub и браузерные события.md>)
- [05 Инверсия зависимостей во frontend](<../Principles/05 Инверсия зависимостей во frontend.md>)
- [06 Производительность React](<../Performance/06 Производительность React.md>)

## Источники

- [MDN: Proxy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy)
- [MDN: Proxy.revocable](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy/revocable)
- [TypeScript: Decorators](https://www.typescriptlang.org/docs/handbook/decorators.html)
- [TypeScript 5.0: Decorators](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html#decorators)
- [React: Reusing logic with custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [Immer: Introduction and how Immer works](https://immerjs.github.io/immer/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Factory Singleton и жизненный цикл](<./06 Factory Singleton и жизненный цикл.md>) · [↑ Patterns](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Декомпозиция God Object и границы модулей →](<./08 Декомпозиция God Object и границы модулей.md>)
<!-- CARD-NAV-BOTTOM:END -->
