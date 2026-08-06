# E2E Playwright Cypress isolation locators

<!-- CARD-NAV-TOP:START -->
[← 08 Coverage CI и качество тестов](<./08 Coverage CI и качество тестов.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что проверяют E2E-тесты? Как организовать устойчивые браузерные тесты с Playwright или Cypress?**

<h2></h2>

<br>
<dl>
<dd>

E2E, или end-to-end testing, проверяет пользовательский сценарий от начала до конца через запущенное приложение в настоящем браузере. Тест взаимодействует со страницей через DOM, навигацию и браузерные API, а приложение проходит реальные границы между UI, маршрутизацией, состоянием, HTTP-клиентом и окружением.

В зависимости от цели тест может запускаться:

- против dev server;
- против production build;
- против уже развёрнутого приложения;
- с настоящим тестовым backend;
- с контролируемой сетевой заменой.

Само использование настоящего браузера ещё не означает проверку production-сборки или настоящего backend. Чтобы проверить deployment, cookies, CSP, сборку и инфраструктуру, тест должен запускаться против соответствующего развёрнутого артефакта.

Если все HTTP-запросы заменены, такой сценарий точнее называть browser integration test. Это допустимая граница, если совместимость с реальным backend проверяется отдельно.

E2E не должен повторять все комбинации модульных и компонентных тестов. Он особенно полезен для небольшого числа критических путей:

- вход и восстановление авторизации;
- оформление заказа или другая ключевая операция;
- создание, изменение и удаление основной сущности;
- переходы между страницами и прямые ссылки на внутренние страницы (deep links);
- загрузка и скачивание файлов;
- работа с browser APIs;
- проверка production build;
- базовая smoke-проверка после deployment.

Playwright и Cypress предоставляют test runner, управление браузером, способы поиска элементов, ожидания, сетевой контроль и диагностические артефакты.

Конкретный инструмент выбирают по требованиям проекта:

- поддерживаемым браузерам;
- модели параллелизма;
- сетевым возможностям;
- component testing;
- диагностике падений;
- интеграции с CI;
- существующему набору тестов;
- опыту команды.

Устойчивость теста в большей степени зависит от его границ, данных и ожиданий, чем от названия framework.

Хороший E2E-тест соблюдает четыре правила:

1. **Независимость.** Он не требует, чтобы другой тест сначала создал пользователя или изменил настройки.
2. **Управляемые данные.** Начальное состояние создаётся через API, fixture, test-support endpoint или подготовленный seed.
3. **Устойчивые locators.** Элементы ищутся по пользовательской семантике или явному test id, а не по случайной структуре DOM.
4. **Ожидание состояния.** Тест ждёт конкретный URL, response или пользовательский результат, а не фиксированное время.

```ts
import {
  expect,
  test,
} from "@playwright/test";

test(
  "пользователь создаёт проект",
  async ({
    page,
    request,
  }) => {
    const user =
      await createUser(request);

    await page.goto("/login");

    await page
      .getByLabel("Email")
      .fill(user.email);

    await page
      .getByLabel("Пароль")
      .fill(user.password);

    await page
      .getByRole(
        "button",
        {
          name: "Войти",
        },
      )
      .click();

    await page
      .getByRole(
        "link",
        {
          name: "Новый проект",
        },
      )
      .click();

    await page
      .getByLabel("Название")
      .fill("Interview notes");

    await page
      .getByRole(
        "button",
        {
          name: "Создать",
        },
      )
      .click();

    await expect(
      page,
    ).toHaveURL(
      /\/projects\/[^/]+$/,
    );

    await expect(
      page.getByRole(
        "heading",
        {
          name: "Interview notes",
        },
      ),
    ).toBeVisible();
  },
);
```

Подготовку исходных данных обычно выполняют не через UI, а через API или специальную тестовую границу:

```text
Arrange через API
→ пользовательский сценарий через UI
→ assertion через UI
```

Через UI создают данные только тогда, когда сам процесс создания является целью теста.

В Playwright каждый тест по умолчанию получает отдельный `BrowserContext` — изолированный профиль браузера со своими:

- cookies;
- `localStorage`;
- `sessionStorage`;
- страницами;
- permissions;
- сетевым состоянием контекста.

Cypress при включённой test isolation, которая используется по умолчанию для E2E, перед каждым тестом:

- очищает страницу;
- очищает cookies;
- очищает `localStorage`;
- очищает `sessionStorage`;
- сбрасывает intercepts, spies, stubs и aliases.

Эта клиентская изоляция не очищает серверное состояние.

Если два параллельных теста используют:

- одного пользователя;
- одну корзину;
- один черновик;
- одну организацию;
- одно имя проекта;

они всё равно могут конфликтовать.

Для параллельного запуска используют уникальные:

- accounts;
- tenants;
- namespaces;
- emails;
- имена сущностей;
- server-side fixtures.

В Playwright идентификатор можно строить на основе worker:

```ts
const uniqueName =
  `project-${testInfo.workerIndex}`;
```

Однако одного worker id недостаточно, если worker создаёт несколько сущностей. Обычно также добавляют имя теста или отдельный уникальный идентификатор запуска.

Авторизацию необязательно проходить через UI в каждом тесте.

Саму login form проверяют отдельным E2E-сценарием:

```text
ввод credentials
→ отправка формы
→ успешная авторизация
```

Остальные тесты могут получить подготовленную сессию через:

- Playwright `storageState`;
- Cypress `cy.session`;
- API login;
- cookie;
- отдельный setup project.

Это ускоряет набор и убирает ненужную зависимость каждого сценария от страницы входа.

Если тесты изменяют серверное состояние, один общий account для всех workers может создавать конфликты. Тогда каждому worker или тесту выдают отдельного пользователя.

Файл `storageState` способен содержать:

- cookies;
- access tokens;
- данные storage;
- действующую сессию.

Его не коммитят в репозиторий и не публикуют в открытых CI artifacts.

Locators должны отражать устойчивый публичный контракт интерфейса.

В Playwright в первую очередь используют:

```ts
page.getByRole(
  "button",
  {
    name: "Сохранить",
  },
);

page.getByLabel("Email");

page.getByText(
  "Профиль сохранён",
);

page.getByTestId(
  "virtual-list",
);
```

Role, label и видимый текст подходят, когда семантика и формулировка являются частью пользовательского контракта.

Test id подходит, когда:

- элемент не имеет подходящей пользовательской семантики;
- текст зависит от локализации;
- содержимое часто меняется;
- нужен стабильный технический контракт.

Cypress официально рекомендует устойчивые `data-*`-атрибуты:

```html
<button data-cy="save-profile">
  Сохранить
</button>
```

```ts
cy.get(
  '[data-cy="save-profile"]',
).click();
```

Через Cypress Testing Library также можно использовать queries по роли и label:

```ts
cy.findByRole(
  "button",
  {
    name: "Сохранить",
  },
).click();
```

Неустойчивые selectors:

```text
.card > div:nth-child(2) button
.button-primary.active
//*[@id="root"]/div[2]/form/button
```

Они зависят от:

- CSS-классов;
- вложенности;
- порядка контейнеров;
- случайных деталей реализации.

Безопасная перестановка разметки способна сломать такой тест без изменения пользовательского поведения.

Playwright Locator повторно находит актуальный элемент перед действием:

```ts
const button =
  page.getByRole(
    "button",
    {
      name: "Сохранить",
    },
  );

await button.click();
```

Если React заменил DOM-узел новым между созданием locator и click, Playwright найдёт актуальный элемент.

Поэтому Locator предпочтительнее сохранённого `ElementHandle`, который может стать отсоединённым от DOM.

Playwright и Cypress имеют разные модели автоматического ожидания.

Перед `locator.click()` Playwright ждёт, что locator:

- найдёт ровно один элемент;
- элемент станет видимым;
- перестанет двигаться;
- сможет получать pointer events;
- станет enabled.

Playwright также повторяет web-first assertions:

```ts
await expect(
  page.getByRole(
    "heading",
  ),
).toHaveText(
  "Dashboard",
);
```

Не каждая обычная проверка повторяется автоматически:

```ts
const text =
  await page.textContent("h1");

expect(text).toBe(
  "Dashboard",
);
```

Здесь значение было прочитано один раз. Предпочтительнее assertion над Locator.

Cypress повторяет связанные queries и assertions:

```ts
cy.get(
  '[data-cy="status"]',
).should(
  "have.text",
  "Saved",
);
```

Query и assertion будут повторяться до успеха или timeout.

Non-query commands выполняются один раз. Cypress не воспроизводит произвольное действие заново только потому, что последующая проверка не прошла.

Фиксированное ожидание:

```ts
await page.waitForTimeout(
  3000,
);
```

или:

```ts
cy.wait(3000);
```

не связано с состоянием приложения.

На быстрой машине оно тратит время, а на медленной может закончиться до результата.

Ожидают наблюдаемое условие:

```ts
await expect(
  page,
).toHaveURL(
  /\/dashboard$/,
);

await expect(
  page.getByRole(
    "heading",
    {
      name: "Dashboard",
    },
  ),
).toBeVisible();
```

Если сам сетевой response является важной частью сценария, в Playwright ожидание создают до действия:

```ts
const responsePromise =
  page.waitForResponse(
    (response) =>
      response.url()
        .endsWith(
          "/api/projects",
        )
      && response
        .request()
        .method() === "POST",
  );

await page
  .getByRole(
    "button",
    {
      name: "Создать",
    },
  )
  .click();

const response =
  await responsePromise;

expect(
  response.ok(),
).toBe(true);
```

Если сначала выполнить click, а затем зарегистрировать `waitForResponse`, быстрый запрос может завершиться раньше начала ожидания.

Но сетевой response не нужно проверять в каждом UI-сценарии. Когда контрактом является пользовательский результат, предпочтительнее дождаться:

```text
нового URL
видимого сообщения
созданной сущности
изменения состояния кнопки
```

При падении browser test должен оставлять достаточно данных для расследования:

- stack trace;
- screenshot;
- trace или Test Replay;
- сообщения консоли;
- сетевые запросы;
- video при необходимости;
- информацию о retry.

Для Playwright можно использовать:

```ts
use: {
  screenshot:
    "only-on-failure",

  trace:
    "retain-on-failure",

  video:
    "retain-on-failure",
}
```

`trace: "retain-on-failure"` сохраняет trace упавшей попытки.

Другой распространённый режим:

```ts
trace:
  "on-first-retry"
```

записывает trace первой повторной попытки, а не первоначального падения.

Это экономит ресурсы, но повторная попытка может пройти и не воспроизвести исходное состояние. Режим выбирают осознанно в зависимости от стоимости traces и требований диагностики.

При retry Playwright классифицирует тесты:

```text
passed
→ прошёл с первой попытки

flaky
→ упал, но прошёл после retry

failed
→ не прошёл после всех retries
```

Retry помогает собрать дополнительную диагностику, но не исправляет нестабильный тест.

Случайно прошедшая повторная попытка не означает, что исходная проблема исчезла.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем E2E-тест отличается от интеграционного компонентного теста?</strong></summary>

<dl>
<dd>
<h2></h2>

React-компонентный тест часто выполняется через React Testing Library в `jsdom`, рендерит часть React tree и контролирует сетевую границу через MSW.

Он быстрый и удобный для множества состояний, но `jsdom` не проверяет:

- настоящий layout;
- браузерный движок;
- production build;
- полную навигацию;
- реальные cookies и browser policies.

Однако компонентный тест не обязательно работает в `jsdom`.

Playwright и Cypress component testing могут монтировать отдельный компонент в настоящем браузере. Такой тест проверяет браузерную среду, но всё ещё ограничен частью приложения и обычно не проходит полный пользовательский путь через deployment.

E2E открывает всё запущенное приложение и проверяет более широкую границу.

Если тест запускается против production build и настоящего тестового backend, он может обнаружить ошибки:

- маршрутизации;
- CSP;
- cookies;
- загрузки bundle;
- browser API;
- конфигурации deployment;
- интеграции frontend и backend.

Эти уровни дополняют друг друга:

```text
Component test
→ много состояний на узкой границе

E2E
→ несколько критичных путей через широкую границу
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбирать между Playwright и Cypress?</strong></summary>

<dl>
<dd>
<h2></h2>

Сравнивают:

- поддержку нужных браузеров;
- модель параллелизма;
- сетевые возможности;
- component testing;
- traces и диагностику;
- интеграцию с CI;
- существующие тесты;
- опыт команды;
- стоимость миграции.

Playwright предоставляет BrowserContext и единый API для Chromium, Firefox и WebKit.

Cypress использует собственную очередь команд, встроенное повторение queries и assertions, интерактивный runner и отдельную модель browser- и Node-контекстов.

У инструментов также различаются:

- стиль написания тестов;
- управление вкладками и окнами;
- работа с несколькими origins;
- подход к selectors;
- экосистема облачной диагностики.

Небольшой proof of concept на двух реальных сценариях показывает больше, чем абстрактная таблица функций.

Оба инструмента способны создать устойчивый набор. Миграция оправдана конкретным ограничением, а не только популярностью framework.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие locators считаются устойчивыми?</strong></summary>

<dl>
<dd>
<h2></h2>

В Playwright сначала используют locators, отражающие восприятие пользователя:

- роль и доступное имя;
- label поля;
- видимый текст;
- осмысленный test id.

```ts
page.getByRole(
  "button",
  {
    name: "Удалить",
  },
);
```

Cypress также поддерживает пользовательские queries через Cypress Testing Library, но его официальная стратегия часто использует устойчивые `data-*`-атрибуты:

```ts
cy.get(
  '[data-cy="delete-project"]',
);
```

Test id особенно полезен, если:

- текст меняется из-за i18n;
- элемент технический;
- семантика не позволяет однозначно выбрать элемент;
- копирайтинг не является контрактом теста.

Цепочки CSS-классов, `nth-child` и XPath по структуре DOM хрупки.

Playwright Locators повторно находят актуальный элемент перед действием, поэтому не следует хранить старый DOM handle без необходимости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое auto-waiting и почему оно лучше фиксированного sleep?</strong></summary>

<dl>
<dd>
<h2></h2>

В Playwright auto-waiting проверяет готовность элемента перед действием.

Для click Playwright ждёт:

- одно совпадение locator;
- видимость;
- стабильное положение;
- возможность получить событие;
- enabled-состояние.

Web-first assertions также повторяются:

```ts
await expect(
  locator,
).toBeVisible();
```

В Cypress queries и assertions повторяются как связанная цепочка:

```ts
cy.get(
  '[data-cy="status"]',
).should(
  "contain.text",
  "Saved",
);
```

`sleep(3000)` не связан с состоянием приложения:

- на быстрой машине тратит время;
- на медленной может закончиться слишком рано;
- скрывает настоящее условие готовности.

Ожидать нужно наблюдаемое состояние:

- URL изменился;
- кнопка стала enabled;
- появился heading;
- исчез loader;
- завершился конкретный запрос.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как подготавливать данные для E2E?</strong></summary>

<dl>
<dd>
<h2></h2>

Начальное состояние создают через:

- публичный API;
- специальный test-support endpoint;
- fixture базы;
- управляемый seed;
- отдельную fixture test runner.

Через UI создают данные только тогда, когда сам этот процесс является проверяемым сценарием.

Данные должны быть:

- независимыми;
- воспроизводимыми;
- уникальными при параллельном запуске;
- доступными для последующей очистки.

Для уникальности используют:

- worker index;
- run id;
- test id;
- отдельного пользователя;
- tenant или namespace.

Cleanup после теста полезен, но на него нельзя полагаться полностью: процесс может аварийно завершиться до teardown.

Поэтому окружение также должно периодически удалять устаревшие тестовые данные либо полностью пересоздаваться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли использовать настоящий backend во всех E2E?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Граница зависит от цели.

Небольшой набор тестов с настоящим тестовым backend проверяет:

- совместимость deployment;
- auth;
- cookies;
- API;
- серверные side effects;
- кеширование;
- реальный контракт систем.

Для редкой server error, сторонней оплаты или опасного побочного эффекта response можно перехватить.

Это делает сценарий:

- быстрее;
- безопаснее;
- детерминированнее.

Но если каждый HTTP-запрос заменён, тест уже не подтверждает интеграцию с настоящим backend и ближе к browser integration test.

Это допустимо, если граница названа явно, а реальный контракт проверяется:

- отдельными E2E;
- contract tests;
- API integration tests;
- тестами backend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как ускорить авторизацию в E2E-тестах?</strong></summary>

<dl>
<dd>
<h2></h2>

Сессию создают через API или отдельный setup и сохраняют состояние авторизации.

В Playwright используют:

```text
storageState
```

В Cypress:

```text
cy.session()
```

Следующие тесты начинают работу уже с подготовленной сессией.

Сам UI login проверяют отдельным сценарием.

Если тесты только читают данные, иногда можно переиспользовать один account.

Если они изменяют серверное состояние, каждому worker или тесту лучше дать отдельного пользователя.

Файл `storageState` способен содержать действующие credentials, cookies и tokens, поэтому его:

- добавляют в `.gitignore`;
- создают заново в безопасном окружении;
- не публикуют как общедоступный artifact;
- удаляют после завершения CI job.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужен ли Page Object, то есть объект страницы?</strong></summary>

<dl>
<dd>
<h2></h2>

Page Object полезен, когда объединяет:

- устойчивые locators;
- повторяемые действия;
- понятные операции предметной области.

Например:

```ts
await checkoutPage
  .submitOrder(order);
```

Он уменьшает дублирование и даёт одно место для изменения контракта страницы.

Большой Page Object, который скрывает:

- assertions;
- test data;
- все переходы;
- важные детали сценария;

ухудшает читаемость.

Часто лучше использовать:

- небольшие Page Objects;
- fixtures;
- helpers по пользовательским задачам;
- отдельные API helpers для Arrange.

Из текста теста должно быть видно:

- что сделал пользователь;
- какие важные данные использованы;
- какой результат проверяется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как запускать E2E параллельно без конфликтов?</strong></summary>

<dl>
<dd>
<h2></h2>

Каждый тест получает изолированное клиентское состояние, а серверные данные разделяют по:

- уникальному пользователю;
- tenant;
- namespace;
- имени сущности;
- отдельной базе или schema.

Нельзя использовать одну изменяемую:

- корзину;
- заявку;
- организацию;
- настройку;
- учётную запись;

для нескольких workers.

Большой набор распределяют по shards между CI jobs.

Setup не должен создавать один незащищённый глобальный ресурс для всех tests.

Если сценарий действительно меняет общий ресурс, его:

- сериализуют точечно;
- переносят в отдельный project;
- запускают в отдельном окружении;
- либо проектируют ресурс так, чтобы его можно было изолировать.

Глобальный последовательный запуск всего набора обычно скрывает проблему данных и увеличивает время CI.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что сохранять при падении browser test?</strong></summary>

<dl>
<dd>
<h2></h2>

Минимальный набор:

- stack trace;
- screenshot;
- ошибки консоли;
- сетевой лог;
- сведения о retry.

Для Playwright особенно полезен trace:

- действия;
- DOM snapshots;
- locators;
- console;
- network;
- состояние страницы по шагам.

Нужно различать режимы:

```text
retain-on-failure
→ сохранить trace упавшей попытки

on-first-retry
→ записать trace первой повторной попытки
```

Video добавляют, если движение, drag-and-drop или последовательность окон важны и trace недостаточен.

Cypress при падениях может сохранять screenshots, video и данные повторных попыток; при использовании Cypress Cloud доступна дополнительная диагностика запуска.

Артефакты желательно сохранять для каждой значимой упавшей попытки, а не только для окончательного результата после retry.

Из headers, URL, cookies и storage удаляют tokens и персональные данные перед публикацией или длительным хранением.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен visual regression test?</strong></summary>

<dl>
<dd>
<h2></h2>

Visual regression сравнивает screenshot с утверждённым эталоном и обнаруживает изменения, которые DOM-assertions могут не увидеть:

- layout;
- цвета;
- шрифты;
- отступы;
- перекрытия;
- адаптивное состояние.

Он полезен для:

- design system;
- ключевых экранов;
- разных viewport;
- светлой и тёмной темы;
- состояний ошибки и загрузки.

Для стабильного сравнения фиксируют:

- браузер;
- операционную систему;
- viewport;
- шрифты;
- тестовые данные;
- текущую дату;
- animations;
- динамический контент.

Динамические области маскируют только осмысленно.

Изменившийся screenshot требует просмотра человеком. Автоматическое обновление эталона без анализа уничтожает ценность проверки.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Подходящая E2E-проверка |
| --- | --- |
| Login | Один UI-сценарий входа, остальные тесты используют подготовленную сессию |
| Checkout | Один основной путь и несколько критических отказов |
| Права доступа | Отдельные browser contexts пользователей с разными ролями |
| Deep link | Прямой переход по URL и восстановление состояния страницы |
| File download | Событие скачивания, имя и содержимое файла |
| Production deployment | Smoke-сценарий на развёрнутом production artifact |
| Изолированная ошибка API | Browser integration test с сетевым перехватом |
| Design system | Visual regression в фиксированной среде |
| Параллельный запуск | Уникальный account или namespace для каждого worker |

## Связанные темы

- [01 Стратегия тестирования frontend](<./01 Стратегия тестирования frontend.md>)
- [06 MSW и моки API](<./06 MSW и моки API.md>)
- [07 Flaky tests isolation cleanup](<./07 Flaky tests isolation cleanup.md>)
- [08 Coverage CI и качество тестов](<./08 Coverage CI и качество тестов.md>)
- [09 Accessibility testing manual automated screen reader](<../Accessibility/09 Accessibility testing manual automated screen reader.md>)

## Источники

- [Playwright: Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright: Locators](https://playwright.dev/docs/locators)
- [Playwright: Auto-waiting](https://playwright.dev/docs/actionability)
- [Playwright: Assertions](https://playwright.dev/docs/test-assertions)
- [Playwright: Isolation](https://playwright.dev/docs/browser-contexts)
- [Playwright: Parallelism](https://playwright.dev/docs/test-parallel)
- [Playwright: Authentication](https://playwright.dev/docs/auth)
- [Playwright: API testing](https://playwright.dev/docs/api-testing)
- [Playwright: Retries](https://playwright.dev/docs/test-retries)
- [Playwright: Trace Viewer](https://playwright.dev/docs/trace-viewer)
- [Playwright: Visual comparisons](https://playwright.dev/docs/test-snapshots)
- [Cypress: Best Practices](https://docs.cypress.io/app/core-concepts/best-practices)
- [Cypress: Test Isolation](https://docs.cypress.io/app/core-concepts/test-isolation)
- [Cypress: Retry-ability](https://docs.cypress.io/app/core-concepts/retry-ability)
- [Cypress: Test Retries](https://docs.cypress.io/app/guides/test-retries)
- [Cypress: Screenshots and Videos](https://docs.cypress.io/app/guides/screenshots-and-videos)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Coverage CI и качество тестов](<./08 Coverage CI и качество тестов.md>) · [↑ Testing](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
