# Error Boundaries

<!-- CARD-NAV-TOP:START -->
[← 11 Context](<./11 Context.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Portal →](<./13 Portal.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Error Boundary в React? Какие ошибки он перехватывает и какие не перехватывает?**

<h2></h2>

<br>
<dl>
<dd>

Error Boundary, или граница обработки ошибок, — специальный компонент, который перехватывает ошибку в дочернем React-дереве и вместо сломанной области показывает запасной интерфейс, или fallback UI.

Граница не предотвращает саму ошибку. Она:

- ограничивает область отказа;
- сохраняет остальную часть приложения доступной;
- предоставляет пользователю понятный следующий шаг;
- даёт место для логирования ошибки.

Без подходящей Error Boundary ошибка во время рендера может привести к удалению соответствующего React-интерфейса с экрана.

В стабильном публичном React API собственная граница реализуется классовым компонентом:

```tsx
type ErrorBoundaryProps =
  React.PropsWithChildren;

type ErrorBoundaryState = {
  hasError: boolean;
};

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = {
    hasError: false,
  };

  static getDerivedStateFromError(
    _error: Error,
  ): ErrorBoundaryState {
    return {
      hasError: true,
    };
  }

  componentDidCatch(
    error: Error,
    info: React.ErrorInfo,
  ) {
    reportErrorToService({
      error,
      componentStack:
        info.componentStack,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <p role="alert">
          Не удалось показать этот блок.
        </p>
      );
    }

    return this.props.children;
  }
}
```

Использование:

```tsx
<ErrorBoundary>
  <Profile />
</ErrorBoundary>
```

Если `Profile` или его потомок выбросит поддерживаемую React ошибку, граница покажет fallback вместо своего дочернего поддерева.

Методы границы выполняют разные задачи.

`static getDerivedStateFromError` обновляет состояние в ответ на ошибку:

```text
ошибка
→ hasError = true
→ следующий render показывает fallback
```

Он должен быть чистым и не выполнять побочные эффекты.

`componentDidCatch` является необязательным и обычно используется для логирования:

```tsx
componentDidCatch(
  error: Error,
  info: React.ErrorInfo,
) {
  reportErrorToService({
    error,
    componentStack:
      info.componentStack,
  });
}
```

`error` содержит саму ошибку и её обычный JavaScript stack.

`info.componentStack` содержит component stack — путь по React-дереву до компонента, в котором произошёл сбой.

Для диагностики также полезны:

- URL;
- версия приложения;
- версия микрофронтенда;
- название пользовательского сценария;
- идентификатор события;
- технические данные запроса;
- feature flags.

Не следует отправлять в систему мониторинга:

- пароль;
- токен;
- данные банковской карты;
- другие чувствительные пользовательские данные.

Error Boundary перехватывает ошибки, которые React получает при обработке дочернего дерева, прежде всего во время render.

Для классовых компонентов сюда также относятся ошибки в:

- `render`;
- конструкторе;
- методах жизненного цикла дочерних компонентов.

Граница не перехватывает:

- ошибку внутри самой границы;
- ошибку внутри её fallback UI;
- обычную ошибку обработчика события;
- произвольную асинхронную ошибку из `setTimeout`, `requestAnimationFrame` или Promise callback;
- ошибку серверного рендера этим клиентским экземпляром границы;
- ошибку, которую код уже поймал и не бросил дальше.

Если ошибка произошла внутри самой Error Boundary:

```text
ErrorBoundary
→ его render упал
```

её может обработать только другая граница выше:

```tsx
<RootErrorBoundary>
  <WidgetErrorBoundary>
    <Widget />
  </WidgetErrorBoundary>
</RootErrorBoundary>
```

То же относится к ошибке в fallback UI внутренней границы.

Обычный обработчик события выполняется после commit:

```tsx
function handleClick() {
  throw new Error(
    "Не удалось сохранить",
  );
}
```

Такую ошибку Error Boundary автоматически не перехватит.

Её обрабатывают рядом с действием:

```tsx
async function handleSave() {
  try {
    await saveProfile();
  } catch (error) {
    setSaveError(
      normalizeError(error),
    );
  }
}
```

После этого компонент показывает локальное состояние ошибки:

```tsx
{saveError && (
  <p role="alert">
    Не удалось сохранить профиль.
  </p>
)}
```

Если после ошибки требуется заменить всё поддерево через Error Boundary, компонент может сохранить ошибку и бросить её при следующем render:

```tsx
function ProfileEditor() {
  const [
    fatalError,
    setFatalError,
  ] = useState<Error | null>(
    null,
  );

  if (fatalError) {
    throw fatalError;
  }

  async function handleSave() {
    try {
      await saveProfile();
    } catch (error) {
      setFatalError(
        normalizeError(error),
      );
    }
  }

  // ...
}
```

При этом Error Boundary не перехватывает произвольное отклонение Promise автоматически:

```tsx
fetchData().then(() => {
  throw new Error(
    "Request failed",
  );
});
```

Ошибка возникла внутри обычного асинхронного callback вне render React.

Однако фраза «Error Boundary не ловит асинхронные ошибки» является слишком грубой.

Некоторые React API передают асинхронную ошибку обратно в React-модель.

Например, если Promise, прочитанный через `use`, отклонён, React направит ошибку в ближайший Error Boundary:

```tsx
function Albums({
  albumsPromise,
}: {
  albumsPromise:
    Promise<Album[]>;
}) {
  const albums =
    use(albumsPromise);

  return (
    <AlbumsList
      albums={albums}
    />
  );
}
```

Отказ загрузки компонента через `lazy` также передаётся ближайшей границе:

```tsx
const Editor =
  lazy(() =>
    import("./Editor"),
  );
```

Если Promise динамического импорта отклонится, React бросит причину отказа для ближайшего Error Boundary.

Ошибки из функции, переданной в `startTransition`, также могут обрабатываться границей:

```tsx
startTransition(() => {
  performAction();
});
```

В React 19 неизвестная ошибка внутри Action, например `useActionState`, также может быть повторно брошена React и показана через ближайший Error Boundary.

Упрощённо:

```text
обычный Promise callback
→ Error Boundary автоматически не ловит

ошибка, которую React повторно бросил во время render
→ Error Boundary ловит

ошибка из поддерживаемой React Action
→ React может направить её в Error Boundary
```

Ожидаемые бизнес-ошибки обычно не следует превращать в исключения Error Boundary.

Например:

```text
неверный пароль
товар закончился
недостаточно прав
поле не прошло валидацию
```

Такие состояния являются частью обычного пользовательского сценария и должны отображаться локально.

Error Boundary больше подходит для неожиданных технических ошибок:

```text
undefined is not a function
неожиданная структура данных
ошибка стороннего виджета
сбой загрузки lazy-компонента
```

Клиентская Error Boundary не выполняется во время серверного рендера.

Ошибки SSR обрабатываются:

- серверным renderer;
- React-фреймворком;
- серверным маршрутом;
- серверным механизмом логирования.

В некоторых сценариях React может показать серверный fallback `Suspense` и повторить проблемный render на клиенте.

Если ошибка повторится уже на клиенте, ближайший клиентский Error Boundary сможет показать свой fallback.

Границы размещают вокруг областей, которые могут отказать независимо:

- маршрута;
- крупного виджета;
- редактора;
- микрофронтенда;
- стороннего компонента;
- lazy-загружаемой части приложения.

Например:

```tsx
<AppShell>
  <ErrorBoundary>
    <DashboardRoute />
  </ErrorBoundary>
</AppShell>
```

Ошибка страницы не удалит общий каркас приложения.

Для независимых виджетов можно использовать отдельные границы:

```tsx
<Dashboard>
  <ErrorBoundary>
    <SalesWidget />
  </ErrorBoundary>

  <ErrorBoundary>
    <TrafficWidget />
  </ErrorBoundary>
</Dashboard>
```

Ошибка одного виджета не должна удалять соседний.

Одна граница у корня полезна как последняя защита от полностью пустого экрана:

```tsx
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

Но если внутри упадёт небольшой блок, корневая граница заменит fallback-интерфейсом всё приложение.

Слишком мелкая граница вокруг каждой кнопки также создаёт:

- лишнюю разметку;
- сложную отчётность;
- fallback без контекста;
- затруднённое восстановление.

Границу выбирают по области, для которой можно создать осмысленный независимый fallback.

После срабатывания обычная классовая граница остаётся в состоянии:

```ts
hasError === true
```

Простой повторный render детей сам по себе её не сбросит.

Для повтора нужно:

1. Устранить или изменить причину ошибки.
2. Сбросить состояние Error Boundary.
3. Повторно отрендерить поддерево.

Библиотека `react-error-boundary` предоставляет для этого готовые API сброса.

В собственной границе можно реализовать метод:

```tsx
reset = () => {
  this.setState({
    hasError: false,
  });
};
```

и передать его fallback-интерфейсу.

Другой вариант — перемонтировать саму границу с новым `key`:

```tsx
<ErrorBoundary
  key={retryVersion}
>
  <Profile />
</ErrorBoundary>
```

Важно, что новый `key` должен пересоздать Error Boundary.

Смена `key` только у скрытого ребёнка не сбросит состояние:

```tsx
<ErrorBoundary>
  <Profile
    key={retryVersion}
  />
</ErrorBoundary>
```

потому что граница продолжает показывать fallback и не рендерит `Profile`.

Бесконечно повторять тот же render без изменения причины нельзя:

```text
reset
→ тот же ошибочный render
→ та же ошибка
→ fallback
```

В React 19 `createRoot` и `hydrateRoot` поддерживают callbacks для централизованной отчётности:

```tsx
const root =
  createRoot(container, {
    onCaughtError(
      error,
      errorInfo,
    ) {
      reportCaughtError({
        error,
        componentStack:
          errorInfo.componentStack,
      });
    },

    onUncaughtError(
      error,
      errorInfo,
    ) {
      reportUncaughtError({
        error,
        componentStack:
          errorInfo.componentStack,
      });
    },

    onRecoverableError(
      error,
      errorInfo,
    ) {
      reportRecoverableError({
        error,
        componentStack:
          errorInfo.componentStack,
      });
    },
  });
```

Их назначение:

| Callback | Когда вызывается |
| --- | --- |
| `onCaughtError` | Ошибка была поймана Error Boundary |
| `onUncaughtError` | Ошибка не была поймана ни одной границей |
| `onRecoverableError` | React обнаружил ошибку, но автоматически восстановился |

Эти callbacks:

- помогают централизовать логирование;
- получают `componentStack`;
- работают на уровне React root;
- не создают локальный fallback UI;
- не заменяют Error Boundary.

Error Boundary отвечает за пользовательский интерфейс и изоляцию отказа.

Root callbacks отвечают за общую отчётность и наблюдаемость приложения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое fallback UI у Error Boundary?</strong></summary>

<dl>
<dd>
<h2></h2>

Fallback UI — запасной интерфейс, который Error Boundary показывает вместо упавшего дочернего поддерева.

Он может содержать:

- понятное сообщение;
- безопасное действие «Повторить»;
- ссылку назад;
- переход на главную страницу;
- сохранённую доступную часть данных;
- идентификатор ошибки для поддержки.

Например:

```tsx
<div role="alert">
  <p>
    Не удалось загрузить редактор.
  </p>

  <button
    type="button"
    onClick={onRetry}
  >
    Повторить
  </button>
</div>
```

Fallback должен соответствовать размеру области.

Для небольшого виджета достаточно компактного сообщения.

Для ошибки маршрута может потребоваться полноценная страница с навигацией.

Fallback не должен:

- раскрывать технический stack пользователю;
- показывать чувствительные данные;
- ломать раскладку всей страницы;
- бесконечно повторять неустранённую ошибку.

Для динамически появившегося сообщения подходит:

```html
role="alert"
```

Но автоматически перемещать фокус следует только тогда, когда это действительно улучшает доступность сценария.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему boundary не ловит ошибку в <code>onClick</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обработчик события выполняется после commit, когда интерфейс уже показан.

Ошибка внутри обычного `onClick` не является ошибкой незавершённого render:

```tsx
function handleClick() {
  throw new Error(
    "Save failed",
  );
}
```

Поэтому Error Boundary автоматически её не перехватывает.

Ожидаемую ошибку операции обрабатывают рядом с действием:

```tsx
async function handleClick() {
  try {
    await save();
  } catch (error) {
    setError(
      normalizeError(error),
    );
  }
}
```

После этого показывают локальное состояние ошибки.

Если ошибка является фатальной для поддерева, обработчик может записать её в состояние, а компонент бросит её при следующем render.

Отдельное исключение — работа, которую React выполняет как Transition:

```tsx
startTransition(() => {
  performAction();
});
```

Ошибка из поддерживаемой Transition-функции может быть направлена в ближайший Error Boundary.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Перехватит ли Error Boundary отклонённый Promise?</strong></summary>

<dl>
<dd>
<h2></h2>

Само необработанное отклонение произвольного Promise Error Boundary автоматически не перехватит:

```tsx
fetchData().then(() => {
  throw new Error(
    "Request failed",
  );
});
```

Но Promise может быть интегрирован с React.

Если Promise читается через:

```tsx
use(promise)
```

и отклоняется, React передаст ошибку ближайшей границе.

Библиотека загрузки данных также может:

1. Сохранить ошибку запроса.
2. Запланировать render.
3. Бросить сохранённую ошибку во время render.

В этот момент Error Boundary сработает.

Отклонение Promise динамического импорта `lazy` также превращается React в ошибку для ближайшей границы:

```tsx
const Page =
  lazy(() =>
    import("./Page"),
  );
```

Поэтому важен не только асинхронный источник ошибки, но и то, каким способом она попала обратно в React.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли реализовать Error Boundary обычным функциональным компонентом?</strong></summary>

<dl>
<dd>
<h2></h2>

В стабильном публичном React API собственный Error Boundary по-прежнему реализуется классовым компонентом.

Для этого используются:

```tsx
static getDerivedStateFromError
```

и необязательный:

```tsx
componentDidCatch
```

Функциональный компонент не имеет прямого Hook, полностью заменяющего этот механизм.

Чтобы не писать классовую границу самостоятельно, можно использовать библиотеку:

```text
react-error-boundary
```

Она предоставляет удобный интерфейс:

- fallback-компонент;
- функцию сброса;
- `resetKeys`;
- callbacks логирования.

Внутри механизм перехвата всё равно опирается на поддерживаемую React границу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Error Boundary отличается от <code>Suspense</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Suspense` обрабатывает временное ожидание поддерживаемого ресурса:

```text
ресурс ещё не готов
→ показать loading fallback
```

Error Boundary обрабатывает ошибку:

```text
операция завершилась ошибкой
→ показать error fallback
```

Для `lazy` обычно нужны обе границы:

```tsx
<ErrorBoundary>
  <Suspense
    fallback={
      <PageSkeleton />
    }
  >
    <LazyPage />
  </Suspense>
</ErrorBoundary>
```

Пока JavaScript-бандл загружается, работает fallback `Suspense`.

Если динамический импорт завершится ошибкой, React передаст причину отказа Error Boundary.

`Suspense` не является универсальным обработчиком ошибок, а Error Boundary не является индикатором загрузки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбрать уровень Error Boundary?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно определить область, которая:

- может отказать независимо;
- имеет осмысленный fallback;
- может быть восстановлена отдельно;
- не должна удалять соседние части интерфейса.

Типичные уровни:

```text
корень приложения
→ последняя защита

маршрут
→ изоляция отдельной страницы

крупный виджет
→ сохранение остальных блоков панели

сторонняя интеграция
→ изоляция нестабильного API

микрофронтенд
→ независимый отказ одного модуля
```

Граница не должна молча скрывать проблему.

При срабатывании:

- ошибка логируется;
- пользователь получает понятное сообщение;
- предоставляется безопасный следующий шаг;
- сохраняется работоспособная часть приложения.

Не нужно автоматически оборачивать каждый маленький компонент в отдельную границу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как реализовать повтор после ошибки?</strong></summary>

<dl>
<dd>
<h2></h2>

Повтор требует сбросить состояние самой Error Boundary.

Одновременно нужно изменить причину ошибки:

- повторить запрос;
- обновить кеш;
- изменить входные данные;
- заново загрузить часть бандла;
- восстановить сторонний виджет.

Собственная граница может предоставить метод:

```tsx
resetErrorBoundary = () => {
  this.setState({
    hasError: false,
  });
};
```

Библиотека `react-error-boundary` предоставляет готовую функцию сброса и `resetKeys`.

Можно также перемонтировать границу:

```tsx
<ErrorBoundary
  key={retryVersion}
>
  <Editor />
</ErrorBoundary>
```

Новый `key` создаст новый экземпляр Error Boundary с начальным состоянием.

Если причина не изменилась, следующий render немедленно завершится той же ошибкой.

Поэтому кнопка повтора не должна запускать бесконечный цикл одинакового падения.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Область | Польза Error Boundary |
| --- | --- |
| Маршрут | Ошибка страницы не удаляет общий каркас приложения |
| Виджет панели данных | Остальные виджеты продолжают работать |
| Часть бандла из `lazy` | Ошибка загрузки получает отдельный интерфейс и повтор |
| Данные, прочитанные через `use` | Отклонённый Promise получает error fallback |
| React Action или Transition | Неизвестная ошибка может быть направлена в ближайшую границу |
| Сторонний редактор или график | Нестабильная интеграция изолирована |
| Микрофронтенд | Отказ одного блока не размонтирует соседние |
| Корень приложения | Последняя защита от полностью пустого экрана |

## Связанные темы

- [15 Suspense lazy и разделение кода](<./15 Suspense lazy и разделение кода.md>)
- [17 SSR SSG и hydration в React](<./17 SSR SSG и hydration в React.md>)
- [19 Версии React 18 19 и 19.2](<./19 Версии React 18 19 и 19.2.md>)
- [07 Обработка ошибок и наблюдаемость](<../Architecture/07 Обработка ошибок и наблюдаемость.md>)

## Источники

- [React: Catching rendering errors with an error boundary](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [React: `use`](https://react.dev/reference/react/use)
- [React: `useTransition`](https://react.dev/reference/react/useTransition)
- [React: `useActionState`](https://react.dev/reference/react/useActionState)
- [React: `lazy`](https://react.dev/reference/react/lazy)
- [React: `Suspense`](https://react.dev/reference/react/Suspense)
- [React DOM: `createRoot`](https://react.dev/reference/react-dom/client/createRoot)
- [React DOM: `hydrateRoot`](https://react.dev/reference/react-dom/client/hydrateRoot)
- [React 19: New root error callbacks](https://react.dev/blog/2024/12/05/react-19#error-handling)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 11 Context](<./11 Context.md>) · [↑ React](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Portal →](<./13 Portal.md>)
<!-- CARD-NAV-BOTTOM:END -->
