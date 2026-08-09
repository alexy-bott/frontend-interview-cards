# Инверсия зависимостей во frontend

<!-- CARD-NAV-TOP:START -->
[← 04 Принципы Liskov и Interface Segregation](<./04 Принципы Liskov и Interface Segregation.md>) · [↑ Principles](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 DRY KISS YAGNI во frontend →](<./06 DRY KISS YAGNI во frontend.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Dependency Inversion Principle? Как он применяется во frontend без классов и DI-контейнера?**

<h2></h2>

<br>
<dl>
<dd>

Dependency Inversion Principle, или DIP, говорит: высокоуровневая логика не должна напрямую зависеть от конкретных инфраструктурных деталей.

Высокоуровневый и низкоуровневый модули зависят от abstraction, то есть от контракта, сформулированного на языке задачи приложения.

Под высокоуровневой логикой понимают:

- бизнес-правило;
- пользовательский сценарий;
- функциональный модуль;
- координацию нескольких операций.

Под низкоуровневой деталью понимают:

- `fetch`;
- HTTP-клиент;
- RTK Query;
- SDK аналитики;
- `localStorage`;
- IndexedDB;
- конкретный backend API.

DIP регулирует направление зависимостей исходного кода.

Высокоуровневый сценарий не должен импортировать конкретную инфраструктуру:

```text
сценарий обновления профиля
        ↓ не должен зависеть
fetch, URL, HTTP headers, DTO, SDK аналитики
```

Вместо этого сценарий определяет необходимые ему операции:

```ts
type UpdateProfile = (
  input: ProfileInput,
) => Promise<
  | {
      ok: true;
    }
  | {
      ok: false;
      fieldErrors: FieldErrors;
    }
>;

type Track = (
  event: {
    type: "profile_updated";
  },
) => void;
```

Сценарий зависит только от этих контрактов:

```ts
type SubmitProfileDependencies = {
  updateProfile: UpdateProfile;
  track: Track;
};

function createSubmitProfile({
  updateProfile,
  track,
}: SubmitProfileDependencies) {
  return async (
    input: ProfileInput,
  ) => {
    const result =
      await updateProfile(input);

    if (result.ok) {
      track({
        type: "profile_updated",
      });
    }

    return result;
  };
}
```

Сценарий определяет высокоуровневое правило:

```text
1. сохранить профиль;
2. после успеха отправить событие аналитики;
3. вернуть результат операции.
```

При этом он не знает:

- URL;
- HTTP-метод;
- заголовки;
- формат backend DTO;
- конкретный analytics SDK;
- способ хранения токена.

HTTP Adapter реализует контракт `UpdateProfile`:

```ts
const updateProfileViaApi:
  UpdateProfile =
  async (input) => {
    const response = await fetch(
      "/api/profile",
      {
        method: "PUT",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          first_name:
            input.firstName,
          last_name:
            input.lastName,
        }),
      },
    );

    if (response.status === 422) {
      const errorDto =
        await response.json();

      return {
        ok: false,
        fieldErrors:
          mapFieldErrors(errorDto),
      };
    }

    if (!response.ok) {
      throw new Error(
        "Profile update failed",
      );
    }

    return {
      ok: true,
    };
  };
```

Adapter скрывает:

- транспорт;
- формат request DTO;
- формат response DTO;
- HTTP status codes;
- преобразование транспортных ошибок в контракт приложения.

Отдельный Adapter связывает предметное событие с SDK аналитики:

```ts
const trackViaAnalyticsSdk:
  Track =
  (event) => {
    analyticsSdk.send(
      event.type,
    );
  };
```

Конкретные реализации связываются со сценарием в composition root, то есть в точке сборки приложения:

```ts
export const submitProfile =
  createSubmitProfile({
    updateProfile:
      updateProfileViaApi,
    track:
      trackViaAnalyticsSdk,
  });
```

Composition root может находиться:

- при инициализации приложения;
- в route-level модуле;
- в Provider;
- в фабрике функционального модуля;
- на серверной границе.

Именно эта точка может импортировать одновременно:

- высокоуровневый сценарий;
- инфраструктурные реализации.

Инверсия состоит в направлении владения контрактом.

Не функциональный модуль подстраивается под методы внешнего SDK:

```ts
analyticsSdk.sendEvent(
  "profile",
  "update",
  {
    source: "settings",
  },
);
```

а Adapter SDK реализует предметную операцию:

```ts
track({
  type: "profile_updated",
});
```

Контракт принадлежит потребности высокоуровневого потребителя.

Он не должен быть просто копией API конкретной библиотеки:

```ts
type HttpClient = {
  request<T>(
    url: string,
    options: RequestInit,
  ): Promise<T>;
};
```

Такой общий HTTP-контракт всё ещё заставляет бизнес-сценарий знать:

- URL;
- HTTP-метод;
- headers;
- транспортный формат.

Более подходящий контракт выражает предметную операцию:

```ts
type LoadProfile = (
  userId: string,
) => Promise<Profile>;
```

DIP не требует классов.

Контрактом может быть:

- тип функции;
- объектный тип;
- TypeScript `interface`;
- набор callbacks;
- публичный API функционального модуля.

DIP также не требует DI-контейнера.

Dependency injection, или передача зависимости снаружи, может выполняться через:

- аргумент функции;
- аргумент фабрики;
- props;
- React Context;
- Provider;
- composition root.

Дополнительный интерфейс полезен, когда он изолирует:

- нестабильную внешнюю систему;
- несколько реализаций;
- преобразование DTO;
- важную архитектурную границу;
- недетерминированную зависимость вроде времени или сети.

Обёртка:

```ts
function get(
  url: string,
) {
  return fetch(url);
}
```

которая только переименовывает `fetch` и не меняет контракт, сама по себе DIP не обеспечивает.

Абстракция должна уменьшать объём инфраструктурных знаний потребителя, а не только добавлять ещё один вызов.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Dependency inversion и dependency injection - одно и то же?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Dependency Inversion Principle определяет направление зависимости:

```text
высокоуровневое правило
→ зависит от своего контракта

инфраструктура
→ адаптируется к этому контракту
```

Dependency injection, или DI, является техникой передачи конкретной реализации снаружи.

Например:

```ts
function createUseCase(
  repository: Repository,
) {
  // ...
}
```

Передача `repository` является dependency injection.

Но DIP соблюдается только тогда, когда контракт `Repository` отражает потребность сценария, а не просто повторяет API конкретной базы данных или библиотеки.

Можно использовать DI, но нарушать DIP:

```ts
function createUseCase(
  axios: AxiosInstance,
) {
  // Сценарий напрямую знает axios.
}
```

Можно соблюдать DIP без DI-контейнера, передавая обычную функцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выглядит dependency injection во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Самый простой вариант — аргумент функции:

```ts
function createLoadProfile(
  loadProfile: LoadProfile,
) {
  return async (
    userId: string,
  ) => {
    return loadProfile(userId);
  };
}
```

Для React-компонента зависимость можно передать через prop:

```tsx
type ProfilePageProps = {
  loadProfile: LoadProfile;
};

export function ProfilePage({
  loadProfile,
}: ProfilePageProps) {
  // ...
}
```

Для зависимости, используемой глубоко в дереве, можно применить Context:

```tsx
const ServicesContext =
  createContext<Services | null>(
    null,
  );
```

Context полезен для:

- конфигурации окружения;
- клиента аналитики;
- feature flags;
- набора сервисов приложения.

Но его не следует превращать в скрытый глобальный service locator, из которого каждый компонент получает произвольные зависимости.

Явные аргументы и props проще прослеживать. Context оправдан, когда пробрасывание зависимости через множество промежуточных компонентов действительно мешает.

Классический DI-контейнер является только одним возможным инструментом и во frontend часто не нужен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Кто должен определять abstraction, то есть абстракцию?</strong></summary>

<dl>
<dd>
<h2></h2>

Контракт должен отражать потребность высокоуровневого потребителя.

Функциональному модулю профиля нужна операция:

```ts
type LoadProfile = (
  userId: string,
) => Promise<Profile>;
```

Ему не нужен общий транспортный контракт:

```ts
request<T>(
  url: string,
  options: RequestInit,
): Promise<T>
```

Низкоуровневый Adapter переводит конкретный способ обмена данными в контракт сценария:

```text
HTTP response DTO
       ↓
Profile Adapter
       ↓
Profile
```

Физически тип может находиться:

- рядом со сценарием;
- в публичном API функционального модуля;
- в отдельном contracts-модуле.

Главное — направление знаний: контракт не должен определяться ограничениями конкретного SDK, если эти ограничения не являются частью предметной задачи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли custom hook абстракцией?</strong></summary>

<dl>
<dd>
<h2></h2>

Может быть.

Например, hook:

```ts
useProfile()
```

может предоставлять UI понятный контракт:

```ts
{
  profile,
  isLoading,
  saveProfile,
  fieldErrors,
}
```

и скрывать:

- RTK Query;
- HTTP DTO;
- transport errors;
- правила invalidation;
- аналитические side effects.

Но имя hook само по себе зависимость не инвертирует.

Если он возвращает необработанный результат библиотеки:

```ts
return useGetProfileQuery(id);
```

то потребитель по-прежнему зависит от:

- API RTK Query;
- структуры `error`;
- `refetch`;
- `unwrap`;
- generated hook conventions.

Это может быть допустимо внутри одного функционального модуля.

Дополнительный hook нужен не ради имени, а когда он действительно предоставляет более устойчивый предметный контракт.

Бизнес-правило, которое требуется использовать вне React, лучше не прятать только в custom hook. Его можно оформить обычной функцией, а hook использовать как React Adapter к этому сценарию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Adapter связан с DIP?</strong></summary>

<dl>
<dd>
<h2></h2>

Adapter реализует контракт приложения поверх несовместимого внешнего API.

Например, приложение ожидает:

```ts
type LoadUser = (
  id: string,
) => Promise<User | null>;
```

Backend возвращает:

```ts
type UserDto = {
  user_id: string;
  full_name: string;
};
```

и использует `404` для отсутствующего пользователя.

Adapter:

- формирует URL;
- выполняет запрос;
- преобразует `UserDto` в `User`;
- преобразует `404` в `null`;
- нормализует остальные ошибки.

```ts
const loadUserViaApi:
  LoadUser =
  async (id) => {
    const response = await fetch(
      `/api/users/${id}`,
    );

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error(
        "User request failed",
      );
    }

    const dto: UserDto =
      await response.json();

    return {
      id: dto.user_id,
      name: dto.full_name,
    };
  };
```

DIP объясняет, почему внутренний код зависит от `LoadUser`, а не от конкретного backend API.

Adapter является практическим способом реализовать это направление зависимости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужен ли TypeScript <code>interface</code> для каждой зависимости?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Для одной операции достаточно типа функции:

```ts
type Now = () => number;
```

Для нескольких связанных операций можно использовать объектный тип:

```ts
type PreferencesStorage = {
  load(): Promise<Preferences>;
  save(
    value: Preferences,
  ): Promise<void>;
};
```

`interface` может быть удобен, но не является обязательным условием DIP.

Если зависимость:

- используется один раз;
- стабильна;
- не раскрывает лишних деталей;
- не требует преобразования;

отдельное именованное объявление может не дать пользы.

Важно не количество интерфейсов, а направление знаний между модулями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как DIP помогает тестам?</strong></summary>

<dl>
<dd>
<h2></h2>

Тест передаёт контролируемую реализацию внешней границы:

```ts
const updateProfile:
  UpdateProfile =
  async () => ({
    ok: true,
  });

const events:
  Array<{
    type: "profile_updated";
  }> = [];

const submitProfile =
  createSubmitProfile({
    updateProfile,
    track: (event) => {
      events.push(event);
    },
  });
```

Так можно проверить высокоуровневое правило без:

- реальной сети;
- настоящего analytics SDK;
- environment variables;
- сложной инфраструктуры.

Fake или stub должны соблюдать поведенческий контракт production-реализации.

Например, если production Adapter возвращает `null` для отсутствующих данных, тестовая реализация не должна выбрасывать ошибку в той же ситуации.

Отдельные интеграционные тесты проверяют настоящий Adapter:

- с MSW;
- с тестовым сервером;
- с тестовой базой;
- с sandbox внешнего сервиса.

DIP позволяет разделить проверку бизнес-правила и инфраструктурной интеграции.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли большое количество mocks, то есть тестовых подмен, быть признаком плохого DIP?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, это может быть сигналом чрезмерной связанности.

Если тест подменяет десятки внутренних функций:

```text
mock parser
mock mapper
mock helper
mock selector
mock formatter
mock internal hook
```

он связан со структурой реализации, а не с публичным поведением.

Обычно достаточно контролировать несколько внешних или недетерминированных границ:

- сеть;
- время;
- storage;
- analytics;
- внешнее SDK.

Внутренние чистые функции лучше проверять напрямую либо не подменять вообще.

При этом количество mocks само по себе не является доказательством нарушения. Координирующий сценарий действительно может иметь несколько независимых внешних зависимостей.

Важно, являются ли подмены устойчивыми публичными контрактами или внутренними деталями, которые меняются при каждом рефакторинге.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как применить DIP с RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Endpoint и generated hook могут быть публичной границей функционального модуля.

Например:

```ts
useGetProfileQuery()
```

может быть достаточным API, если:

- RTK Query уже является стандартом проекта;
- DTO не протекает в UI;
- ошибки имеют понятную форму;
- замена библиотеки не является реальным требованием.

`transformResponse` помогает преобразовать DTO:

```ts
transformResponse:
  (
    response: ProfileDto,
  ): Profile =>
    mapProfile(response),
```

`transformErrorResponse` может нормализовать транспортную ошибку.

Дополнительный hook оправдан, если UI не должен знать:

- структуру RTK Query error;
- необходимость вызывать `unwrap`;
- tags и invalidation;
- различие query и mutation;
- backend DTO;
- несколько объединённых endpoints.

Например:

```ts
function useProfileEditor() {
  const [
    updateProfile,
    updateState,
  ] =
    useUpdateProfileMutation();

  return {
    saveProfile:
      async (
        values: ProfileInput,
      ) => {
        return updateProfile(
          values,
        ).unwrap();
      },
    isSaving:
      updateState.isLoading,
  };
}
```

Но оборачивать каждый generated hook только ради другого имени не нужно.

DIP требует осознанной границы зависимости, а не обязательного сокрытия любой библиотеки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда абстракция над API лишняя?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда endpoint:

- прост;
- используется в одном месте;
- имеет стабильный контракт;
- возвращает уже подходящую модель;
- не требует нормализации ошибок;
- не имеет альтернативной реализации.

В таком случае дополнительная цепочка:

```text
component
→ hook
→ service
→ repository
→ api client
→ fetch
```

может только усложнить чтение.

Начать можно напрямую через публичный query hook или небольшую функцию запроса.

Граница становится полезной, когда появляются:

- преобразование DTO;
- предметная обработка ошибок;
- несколько источников данных;
- повторяемая логика;
- необходимость тестовой реализации;
- реальная вероятность замены инфраструктуры.

Абстракция должна скрывать решение, а не только переименовывать вызов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как DIP связан с правилом импортов FSD?</strong></summary>

<dl>
<dd>
<h2></h2>

Правила импортов FSD и DIP решают связанные, но не одинаковые задачи.

FSD ограничивает направление зависимостей между слоями и требует использовать публичные API slices.

Это помогает:

- не импортировать внутренние файлы;
- сохранять границы модулей;
- скрывать детали реализации;
- предотвращать хаотические зависимости.

DIP дополнительно спрашивает:

```text
Зависит ли бизнес-правило от инфраструктурной детали?
```

Например, импорт generated hook RTK Query через публичный API может быть корректен по FSD, но функциональный модуль всё равно напрямую зависит от RTK Query.

Это не всегда проблема. Она возникает, если такую зависимость действительно нужно изолировать.

Также нельзя буквально сопоставлять:

```text
высокоуровневый модуль DIP
=
верхний слой FSD
```

В DIP «высокоуровневый» означает бизнес-политику, а не положение каталога.

Adapter размещают там, где он не нарушает правила импортов проекта:

- внутри инфраструктурной части функционального модуля;
- в entity;
- в shared API;
- в app composition layer.

Composition root связывает контракт и реализацию, не создавая обратный импорт бизнес-логики в случайный нижний слой.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Высокоуровневая потребность | Низкоуровневая реализация |
|---|---|
| `updateProfile(input)` | Mutation RTK Query или Adapter над Fetch API |
| `track(event)` | SDK аналитики конкретного поставщика |
| `loadPreferences()` | `localStorage`, IndexedDB или API сервера |
| `now()` | `Date.now` в production и фиксированное время в тесте |
| `isEnabled(flag)` | Поставщик значений feature flags |

## Связанные темы

- [02 Adapter и Facade во frontend](<../Patterns/02 Adapter и Facade во frontend.md>)
- [04 API-слой и преобразование DTO](<../Architecture/04 API-слой и преобразование DTO.md>)
- [03 Моки и таймеры в Jest](<../Testing/03 Моки и таймеры в Jest.md>)
- [06 Основы RTK Query](<../State Management/06 Основы RTK Query.md>)
- [04 Fetch API и управление запросом](<../Web API/04 Fetch API и управление запросом.md>)

## Источники

- [Robert C. Martin: Design Principles and Design Patterns](https://labs.cs.upt.ro/labs/ip2/html/lectures/2/res/Martin-PrinciplesAndPatterns.PDF)
- [React: Passing Data Deeply with Context](https://react.dev/learn/passing-data-deeply-with-context)
- [TypeScript: Type Compatibility](https://www.typescriptlang.org/docs/handbook/type-compatibility.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Принципы Liskov и Interface Segregation](<./04 Принципы Liskov и Interface Segregation.md>) · [↑ Principles](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 DRY KISS YAGNI во frontend →](<./06 DRY KISS YAGNI во frontend.md>)
<!-- CARD-NAV-BOTTOM:END -->
