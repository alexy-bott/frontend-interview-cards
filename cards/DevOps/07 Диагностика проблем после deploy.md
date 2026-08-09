# Диагностика проблем после deploy

<!-- CARD-NAV-TOP:START -->
[← 06 Переменные окружения и secrets в CI CD](<./06 Переменные окружения и secrets в CI CD.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Стратегии развёртывания и rollback →](<./08 Стратегии развёртывания и rollback.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как действовать, если после deploy frontend в production что-то сломалось?**

<h2></h2>

<br>
<dl>
<dd>

При production-инциденте главная цель — не сразу найти идеальное объяснение, а безопасно восстановить пользовательский сценарий и не увеличить влияние ошибки.

Практический порядок:

```text
обнаружить симптом
→ оценить влияние
→ остановить распространение
→ временно восстановить работу
→ локализовать слой ошибки
→ устранить причину
→ проверить восстановление
→ предотвратить повторение
```

Сначала фиксируют факты:

- точное время начала;
- production environment;
- текущий release ID;
- commit SHA;
- artifact или image digest;
- версию runtime config;
- затронутые маршруты;
- долю пользователей;
- браузеры и регионы;
- feature flags;
- критичность сценария;
- возможность потери или повреждения данных.

Формулировка:

```text
frontend сломан
```

слишком общая.

Реальный симптом может быть таким:

```text
главная страница не открывается
index.html возвращает 503
JavaScript chunk возвращает 404
вместо JavaScript приходит HTML
приложение падает при bootstrap
API возвращает 401
CORS блокирует запрос
часть пользователей получает старую версию
сломался только новый feature flag
```

Разные симптомы требуют разных первых действий.

Если используется canary, rolling deployment или постепенное включение через feature flag, сначала останавливают дальнейшее распространение неисправной версии:

```text
остановить rollout
→ не увеличивать процент трафика
→ зафиксировать текущую долю пользователей
```

Продолжать rollout во время диагностики опасно: число затронутых пользователей будет расти, а события разных версий смешаются в мониторинге.

Дальше выбирают **mitigation**, то есть временное действие, которое уменьшает влияние инцидента:

- выключить функцию через feature flag;
- вернуть предыдущую публичную конфигурацию;
- временно отключить проблемный маршрут;
- восстановить удалённые chunks;
- переключить трафик на предыдущий artifact;
- выполнить rollback deployment.

Mitigation не обязательно устраняет root cause.

Например:

```text
выключили новый checkout
→ пользователи снова могут оформить заказ
→ причина ошибки в новой реализации ещё не исправлена
```

После восстановления сервиса продолжают расследование и выпускают постоянное исправление.

Ручное изменение файлов внутри production container или на сервере не является нормальным hotfix:

```text
открыть container
→ отредактировать app.js
```

Такой процесс создаёт неизвестное состояние:

- изменение не связано с commit;
- следующий deploy его перезапишет;
- artifact больше не соответствует production;
- rollback становится непредсказуемым;
- невозможно повторить проверку.

Hotfix должен пройти через репозиторий, pipeline, build и контролируемый deploy, даже если путь выпуска ускорен по процедуре инцидента.

Одновременно строят временную линию:

```text
последний успешный release
→ начало нового deploy
→ изменение config
→ переключение трафика
→ рост ошибок
→ первый пользовательский сигнал
→ mitigation
→ восстановление метрик
```

Проверяют не только frontend commit.

Инцидент мог совпасть с изменением:

- backend API;
- authentication;
- CDN;
- Nginx;
- DNS;
- TLS certificate;
- runtime config;
- feature flags;
- Service Worker;
- стороннего script;
- browser policy.

Release metadata должны позволять определить, какой код реально выполняется у пользователя.

Полезно предоставлять безопасные сведения:

```text
releaseId
commitSha
buildTime
configVersion
environment
```

Их можно:

- добавлять в error tracking;
- показывать на диагностической странице;
- отдавать через безопасный endpoint;
- помещать в HTML meta;
- записывать в стартовое событие приложения.

Например:

```html
<meta
  name="app-release"
  content="frontend-2026.08.05.3"
/>
```

Эти данные не должны содержать secrets.

Диагностику ведут по слоям.

```text
1. DNS, TLS, CDN, load balancer.
2. HTML и статические assets.
3. Выполнение JavaScript.
4. Runtime config.
5. API, authentication и CORS.
6. Service Worker и browser cache.
7. Пользовательский сценарий.
```

Сначала проверяют, доступен ли сам документ:

```bash
curl -I https://example.com/
```

Смотрят:

- HTTP status;
- `Content-Type`;
- `Cache-Control`;
- `Age`;
- `ETag`;
- CDN headers;
- release headers;
- время ответа.

Если `index.html` не получен, JavaScript-приложение ещё не запускалось. Проблема находится на уровне:

- DNS;
- TLS;
- CDN;
- ingress;
- Nginx;
- static hosting;
- deploy файлов.

Дальше проверяют assets, указанные в HTML:

```text
/assets/app.a84f31.js
/assets/styles.82c17a.css
```

Для каждого ресурса важны:

- status;
- Content-Type;
- размер;
- Content-Encoding;
- cache headers;
- соответствие текущему release;
- наличие файла на origin.

JavaScript должен возвращаться как JavaScript, а не как HTML.

Если отсутствующий chunk получает:

```http
200 OK
Content-Type: text/html
```

значит SPA fallback скрывает реальный `404`.

Типичные признаки:

```text
Unexpected token '<'
Failed to load module script
MIME type text/html is not executable
```

После загрузки assets проверяют Console.

Белый экран можно разделить на несколько случаев.

**Ошибка до bootstrap:**

```text
основной script не загрузился
неподдерживаемый синтаксис
ошибка CSP
неверный Content-Type
```

**Ошибка во время bootstrap:**

```text
не загрузился config.json
не прошла валидация config
ошибка создания API client
ошибка hydration
```

**Ошибка после первого render:**

```text
runtime exception компонента
ошибка route
необработанный Promise
ошибка данных API
```

В Console ищут первую содержательную ошибку, а не десятки последующих сообщений, вызванных первоначальным падением.

Минифицированный stack trace:

```text
at a (app.a84f31.js:1:18241)
```

восстанавливают через source map именно той сборки, которая выпущена пользователю.

Для сопоставления обычно нужны:

```text
release
dist или build identifier
имя файла
source map той же сборки
```

Source map от другого commit или повторно собранного artifact может восстановить неверную строку.

Поэтому source maps загружают в error tracking в build job и связывают с тем же release ID, что и deployable artifact.

Публичная раздача source maps для этого не обязательна.

После JavaScript проверяют runtime config:

```text
/config.json
/config.js
```

Проблемы могут быть такими:

- файл не существует;
- файл закэширован от прошлого окружения;
- URL API пустой;
- environment указан неверно;
- config не соответствует текущему release;
- вместо JSON пришёл HTML;
- CDN отдаёт старую версию.

Проверяют:

```text
HTTP status
Content-Type
Cache-Control
config version
API origin
release compatibility
```

До успешной загрузки и валидации config приложение не должно начинать запросы к случайному или `undefined` URL.

Следующий слой — API.

В Network определяют:

- URL;
- HTTP method;
- status;
- request headers;
- response headers;
- credentials;
- CORS;
- timeout;
- correlation ID.

Типичные случаи:

```text
401
→ сессия отсутствует или истекла

403
→ пользователь аутентифицирован, но операция запрещена

404
→ неверный API URL или route

5xx
→ ошибка backend или инфраструктуры

CORS error
→ browser не разрешил frontend прочитать cross-origin response
```

CORS-сообщение в браузере не всегда означает, что backend вообще не ответил. Например, сервер мог вернуть `500`, но без допустимого CORS-header, и frontend увидел только блокировку доступа к response.

Для диагностики используют:

- browser Network;
- API gateway logs;
- backend logs;
- request ID;
- trace ID.

Нужно отличать frontend-причину от backend-причины.

Пример frontend-причины:

```text
неверный API_BASE_URL
не переданы credentials
неверный HTTP method
не обработан допустимый ответ
```

Пример backend-причины:

```text
API возвращает 500
изменилась схема ответа
не работает база
истекла server session
```

Иногда ошибка находится на границе:

```text
backend изменил контракт
+
frontend ещё использует старый формат
```

Поэтому при rollout нескольких сервисов важна временная обратная совместимость.

Отдельно проверяют Service Worker.

Он может вернуть ответ из Cache API до обращения к CDN и Nginx:

```text
страница
→ Service Worker
→ Cache API
→ HTTP cache
→ CDN
→ origin
```

Проверяют:

- `navigator.serviceWorker.controller`;
- active worker;
- waiting worker;
- cache names;
- содержимое Cache Storage;
- update strategy;
- release, которому принадлежат ответы.

Опция DevTools:

```text
Disable cache
```

в основном влияет на обычный HTTP cache, пока DevTools открыт.

Она не обязана отключать Service Worker и не доказывает, какой именно cache был источником проблемы.

Для эксперимента Service Worker отключают отдельно или используют режим bypass, после чего сравнивают ответы.

`ChunkLoadError` часто возникает при динамическом import.

Сценарий:

```text
пользователь открыл старую версию
→ новый deploy удалил старые chunks
→ пользователь позже открыл lazy route
→ старая вкладка запросила old-hash.js
→ 404
```

Другие причины:

- неверный `base` или `publicPath`;
- частичная публикация;
- CDN-узлы с разными версиями;
- повреждённый response;
- Service Worker смешал releases;
- Nginx вернул HTML вместо JavaScript.

Перезагрузка может помочь отдельному пользователю, потому что он получит новый HTML.

Но это не устраняет причину:

- другие старые вкладки продолжат ломаться;
- CDN может всё ещё отдавать старый HTML;
- Service Worker может сохранить несовместимый cache;
- старые chunks остаются удалёнными.

Во время инцидента можно временно восстановить отсутствующие assets предыдущего release.

Долгосрочно нужны:

- content hash в именах;
- атомарная публикация;
- старые assets с достаточным сроком хранения;
- короткая revalidation HTML;
- согласованный Service Worker lifecycle;
- обработчик ошибки динамического import.

Обработчик может предложить обновить страницу, но не должен бесконечно перезагружать её.

Перед reload полезно проверить, что доступна другая версия, и сохранить несохранённое пользовательское состояние.

Rollback выбирают, когда:

- затронут критичный сценарий;
- влияние массовое;
- причина пока неясна;
- стабильный предыдущий artifact готов;
- hotfix нельзя быстро проверить;
- дальнейшее ожидание дороже возврата версии.

Rollback должен переключать immutable artifact:

```text
release 43
→ release 42
```

Например:

```text
Docker image digest
static release directory
object storage version
```

Плавающий tag:

```text
latest
```

не доказывает, какое содержимое было возвращено.

После rollback проверяют фактический:

- release ID;
- commit SHA;
- digest;
- config version;
- CDN response;
- active Service Worker.

Hotfix выбирают, если:

- причина точно локализована;
- изменение мало;
- rollback несовместим с backend или данными;
- исправление можно быстро проверить;
- риск hotfix ниже риска rollback.

Hotfix не должен обходить обязательные проверки без осознанной процедуры.

Минимальный путь:

```text
исправление
→ review
→ CI
→ build нового artifact
→ staging или canary
→ smoke test
→ production
```

После rollback или hotfix нельзя считать инцидент завершённым только по успешному статусу deploy job.

Нужно доказать восстановление:

- правильный release обслуживает трафик;
- error rate снизился;
- критичный маршрут работает;
- synthetic test проходит;
- пользовательские метрики восстановились;
- CDN перестал отдавать неисправный HTML;
- Service Worker не возвращает старый ответ;
- новые ошибки не появились.

Проверку проводят из внешней точки, а не только внутри production container.

Rollback может не помочь, если проблема находится вне frontend artifact:

- остался новый runtime config;
- CDN продолжает отдавать новый HTML;
- Service Worker хранит старый cache;
- backend уже изменил несовместимый контракт;
- feature flag остался включён;
- миграция данных необратима;
- tag переключён, но digest остался прежним.

Поэтому release нужно рассматривать как набор совместимых частей:

```text
frontend artifact
runtime config
backend API
feature flags
CDN state
Service Worker state
```

Health check и smoke test отвечают на разные вопросы.

**Liveness check** проверяет, не завис ли процесс и требуется ли его перезапустить.

**Readiness check** проверяет, готов ли экземпляр принимать трафик.

Для Nginx container это может быть HTTP-ответ внутреннего endpoint.

Для SSR server readiness может учитывать завершение обязательной инициализации.

Но успешный health check:

```text
port открыт
GET /health → 200
```

не доказывает, что пользовательская SPA работает.

Например:

- `index.html` старый;
- chunk отсутствует;
- config невалиден;
- API недоступен;
- JavaScript падает при bootstrap.

**Smoke test** после deploy проверяет продукт снаружи.

Минимальный smoke test frontend:

```text
GET /
→ HTML получен

основной JavaScript
→ 200 и корректный Content-Type

client route
→ возвращает SPA HTML

runtime config
→ доступен и валиден

критичный API
→ отвечает ожидаемым статусом

основной сценарий
→ завершается
```

Для авторизованного сценария используют отдельную тестовую учётную запись с минимальными правами и контролируемыми данными.

Smoke test должен быть:

- коротким;
- стабильным;
- быстрым;
- безопасным для повторного запуска;
- способным остановить rollout.

Он не заменяет полную регрессию.

Synthetic monitoring может периодически повторять часть smoke-проверок уже после deploy и обнаруживать проблему до обращения пользователей.

Observability должна связывать событие с контекстом.

Полезные поля:

```text
environment
release
route pattern
error type
browser
region
feature flag
request ID
duration
```

Не следует безусловно отправлять:

- access token;
- refresh token;
- cookie;
- password;
- содержимое формы;
- полный URL с секретными query;
- персональные данные;
- полный API response.

Route лучше нормализовать:

```text
/orders/:orderId
```

вместо сохранения реального идентификатора заказа.

При большом количестве одинаковых ошибок применяют grouping и sampling, но критичные события не должны полностью исчезать из-за слишком агрессивного ограничения.

Для связи frontend с backend edge или backend возвращает безопасный идентификатор:

```http
X-Request-ID: 9d2...
```

Frontend добавляет его в error tracking или показывает пользователю как код обращения в поддержку.

Тогда расследование выглядит так:

```text
browser error
→ request ID
→ API gateway
→ backend service
→ database trace
```

Request ID не должен содержать token или персональные данные.

После восстановления выполняют root cause analysis.

Нужно ответить:

```text
Что технически произошло?
Почему существующие проверки это не остановили?
Почему влияние оказалось таким большим?
Что помогло восстановиться?
Что замедлило восстановление?
```

Postmortem не должен превращаться в поиск виноватого.

Результат должен содержать конкретные действия:

| Действие | Владелец | Срок | Проверка результата |
| --- | --- | --- | --- |
| Хранить старые chunks 14 дней | Platform | Дата | Старый lazy route загружается после deploy |
| Добавить smoke test config | Frontend | Дата | Pipeline падает при невалидном config |
| Останавливать canary по error rate | SRE | Дата | Автоматический rollback в тесте |
| Добавить release ID в UI | Frontend | Дата | Версия видна в диагностике |

Общие формулировки:

```text
быть внимательнее
лучше тестировать
```

не являются проверяемыми предотвращающими действиями.

До инцидента полезно подготовить runbook:

- где посмотреть текущий release;
- как остановить rollout;
- как выключить feature flag;
- как выполнить rollback;
- как очистить конкретный CDN-объект;
- как проверить Service Worker;
- какие smoke tests выполнить;
- кто имеет production-доступ;
- кто принимает решение о восстановлении;
- куда записывать временную линию.

Практический алгоритм:

```text
1. Подтвердить production-инцидент.
2. Зафиксировать release, время и влияние.
3. Остановить дальнейший rollout.
4. Выбрать безопасный mitigation.
5. Проверить HTML, assets и config.
6. Проверить Console, API и Service Worker.
7. Выполнить rollback или проверенный hotfix.
8. Подтвердить фактическую версию и восстановление метрик.
9. Найти root cause.
10. Добавить проверяемое предотвращающее действие.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что проверить в первые минуты после сообщения об инциденте?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала подтверждают, что ошибка относится к production, а не к локальному или тестовому окружению.

Фиксируют:

- точный URL;
- время;
- release ID;
- browser;
- регион;
- шаги воспроизведения;
- затронутый сценарий;
- долю пользователей;
- текущий rollout;
- последние изменения config и feature flags.

Затем проверяют:

```text
главная страница
критичный маршрут
error tracking
метрики
последний pipeline
текущий artifact digest
```

Если идёт canary или rolling deploy, его сначала останавливают.

Скриншот без URL, времени и release даёт мало информации. Полезно получить request ID и точный маршрут, не собирая лишние персональные данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем mitigation отличается от исправления root cause?</strong></summary>

<dl>
<dd>
<h2></h2>

Mitigation уменьшает влияние инцидента:

```text
выключить feature flag
выполнить rollback
вернуть старый config
восстановить удалённый chunk
```

Пользовательский сценарий снова работает, но техническая причина может оставаться.

Root cause fix устраняет условие, из-за которого инцидент возник:

```text
исправить cache policy
сделать deploy атомарным
добавить совместимость API
исправить код
```

Во время критичного инцидента сначала выбирают быстрое и безопасное восстановление, а не продолжают долгую диагностику при сломанном production.

После стабилизации выполняют постоянное исправление и проверяют предотвращение повторения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как расследовать белый экран после релиза?</strong></summary>

<dl>
<dd>
<h2></h2>

В Network последовательно проверяют:

1. `index.html`.
2. Основной JavaScript.
3. CSS.
4. Динамические chunks.
5. Runtime config.
6. Первые API-запросы.

Для каждого ресурса смотрят:

- status;
- Content-Type;
- размер;
- URL;
- cache source;
- release.

Если основной script не загрузился, приложение ещё не запустилось.

Если файлы загрузились, в Console находят первую runtime-ошибку и восстанавливают исходную строку через source map того же release.

Также проверяют:

- CSP;
- `base`/`publicPath`;
- поддержку браузера;
- config validation;
- active Service Worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как понять, находится ли проблема во frontend или backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала проверяют, был ли запрос сформирован frontend и какой ответ реально пришёл.

Frontend-причина вероятна, если:

- запрос отправлен на неправильный URL;
- отсутствуют credentials;
- неверен method или body;
- ответ корректный, но UI его неправильно обработал;
- ошибка произошла до отправки запроса.

Backend-причина вероятна, если:

- endpoint стабильно возвращает `5xx`;
- нарушен контракт ответа;
- сервер не принимает корректный запрос;
- ошибка видна в backend logs.

Проблема может находиться на границе:

```text
frontend старой версии
+
backend нового несовместимого контракта
```

Для точного ответа связывают browser event с backend log через request или trace ID.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему после release возникает <code>404</code> на JavaScript chunk?</strong></summary>

<dl>
<dd>
<h2></h2>

Частый сценарий:

```text
старая вкладка
→ старый runtime
→ lazy import
→ запрос old-hash.js
→ файл уже удалён
```

Другие причины:

- неверный `base` или `publicPath`;
- неатомарный deploy;
- asset не был опубликован;
- разные версии CDN;
- Service Worker вернул старый HTML;
- fallback заменил `404` HTML-ответом.

Проверяют:

- точный URL;
- manifest release;
- наличие файла на origin;
- CDN;
- Content-Type;
- cache headers;
- текущий release пользователя.

Предотвращение:

- content hashes;
- атомарный deploy;
- хранение старых assets;
- короткая revalidation HTML;
- согласованный Service Worker lifecycle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему ошибка проявляется только у части пользователей?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользователи могут отличаться по:

- canary release;
- feature flag;
- browser;
- региону CDN;
- tenant;
- роли;
- account type;
- Service Worker;
- старой открытой вкладке;
- runtime config;
- расширениям браузера.

События сегментируют по:

```text
release
browser
region
route pattern
flag variant
```

Но в tags не передают tokens, полные URL с чувствительными параметрами и лишние персональные данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>После deploy ошибка появилась только у части пользователей. Что делать, если они могли остаться на старой версии из кэша браузера?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала подтверждают источник старой версии.

Возможные уровни:

```text
browser HTTP cache
CDN
Service Worker Cache Storage
старая открытая вкладка
```

Сравнивают release пользователя с production.

В Network проверяют:

- URL HTML и chunks;
- источник response;
- `Cache-Control`;
- `Age`;
- `ETag`;
- `404`;
- Content-Type.

Во вкладке Application проверяют:

- controller;
- active/waiting Service Worker;
- Cache Storage.

Опция Disable cache не отключает автоматически Service Worker, поэтому исчезновение ошибки после её включения ещё не доказывает источник.

Во время инцидента можно:

- вернуть удалённые assets;
- выполнить rollback;
- выключить feature;
- точечно очистить старый HTML в CDN;
- предложить контролируемое обновление страницы.

Просьба очистить все данные сайта является временной пользовательской мерой, а не исправлением production-процесса.

Предотвращение:

- HTML и config регулярно revalidate;
- hashed assets хранятся долго;
- старые chunks не удаляются сразу;
- deploy выполняется атомарно;
- Service Worker не смешивает releases;
- backend временно совместим со старым frontend.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должно быть подготовлено для быстрого rollback?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужны:

- immutable artifacts предыдущих versions;
- image digest или release directory;
- запись текущего deployment;
- готовая команда переключения;
- права на rollback;
- ответственный;
- smoke test;
- совместимое API;
- стратегия возврата config и feature flags.

Rollback не должен требовать повторной сборки старого commit.

Предыдущий проверенный artifact должен уже существовать в registry или release storage.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить, что rollback действительно завершился успешно?</strong></summary>

<dl>
<dd>
<h2></h2>

Недостаточно увидеть зелёную deploy job.

Проверяют:

1. Фактический release ID.
2. Artifact или image digest.
3. Runtime config.
4. HTML и chunks через CDN.
5. Critical route.
6. Error rate.
7. Synthetic test.
8. Service Worker state.

После переключения наблюдают метрики некоторое время.

Если error rate не снизился, проблема могла находиться в config, backend, CDN или browser cache, а не в возвращённом frontend artifact.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему после rollback проблема может остаться?</strong></summary>

<dl>
<dd>
<h2></h2>

Возможные причины:

- CDN отдаёт неисправный HTML;
- Service Worker хранит старый cache;
- runtime config не откатился;
- feature flag остался включён;
- backend уже изменил контракт;
- migration необратима;
- переключён tag, но не digest;
- часть instances осталась на новой версии.

Нужно проверить весь release-набор:

```text
artifact
config
backend
flags
CDN
Service Worker
```

и подтвердить фактическую версию response.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбрать между hotfix и rollback?</strong></summary>

<dl>
<dd>
<h2></h2>

Rollback предпочтителен, если:

- влияние массовое;
- сломан критичный сценарий;
- причина неясна;
- предыдущая версия совместима;
- rollback подготовлен.

Hotfix подходит, если:

- причина точно локализована;
- изменение мало;
- rollback опасен;
- исправление быстро проверяется;
- риск нового изменения контролируем.

Главный критерий — минимальное время безопасного восстановления пользователей, а не желание сохранить новый release.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему error tracking показывает только минифицированный stack trace?</strong></summary>

<dl>
<dd>
<h2></h2>

Возможные причины:

- source maps не созданы;
- карты не загружены;
- указан другой release;
- map относится к другой сборке;
- URL файла не совпадает;
- mapping удалён слишком рано.

Build job должна загрузить source maps с тем же release и build identifier, которые использует production artifact.

Повторная сборка того же commit не всегда гарантирует идентичные имена и позиции, поэтому карты берут от фактически выпущенного artifact.

Публично раздавать их для symbolication необязательно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должен проверять frontend smoke test после deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

Smoke test должен выполняться снаружи production runtime и проверять:

- актуальный HTML;
- основной JavaScript;
- отсутствие `404` chunks;
- корректный Content-Type;
- runtime config;
- критичный API;
- основной пользовательский сценарий;
- release ID.

Для защищённого приложения используют тестовую учётную запись с минимальными правами.

Smoke test должен быть коротким, стабильным и безопасным для повторного запуска.

Полная регрессия выполняется раньше и не заменяется smoke test.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие данные frontend можно отправлять в logs и error tracking?</strong></summary>

<dl>
<dd>
<h2></h2>

Допустимы безопасные технические поля:

- release;
- environment;
- route pattern;
- browser;
- error type;
- duration;
- feature variant;
- request ID.

Нельзя безусловно отправлять:

- tokens;
- cookies;
- passwords;
- authorization headers;
- содержимое форм;
- полный API response;
- чувствительные query parameters.

User ID при необходимости псевдонимизируют и обрабатывают по политике продукта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как связать ошибку браузера с backend logs?</strong></summary>

<dl>
<dd>
<h2></h2>

Backend или edge создаёт безопасный request ID:

```http
X-Request-ID: 9d2...
```

Frontend добавляет его в error tracking или показывает как код обращения в поддержку.

Серверная команда находит тот же ID в gateway и service logs.

Для распределённой цепочки используют trace ID.

Идентификатор не должен содержать body, token или персональные данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что должно быть в runbook production-инцидента?</strong></summary>

<dl>
<dd>
<h2></h2>

Runbook должен содержать заранее проверенные действия:

- где посмотреть release ID;
- как остановить rollout;
- как выключить feature flag;
- как выполнить rollback;
- как проверить digest;
- как очистить конкретный CDN cache;
- как проверить Service Worker;
- какие smoke tests запустить;
- кто принимает решение;
- кому сообщить об инциденте.

Команды и ссылки периодически проверяют.

Runbook, который впервые читают только во время инцидента и который содержит устаревшие команды, почти не ускоряет восстановление.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Симптом | Первый слой проверки |
| --- | --- |
| Страница не открывается | DNS, TLS, CDN, Nginx и HTML status |
| Белый экран | Chunks, MIME type, Console, config и source maps |
| `ChunkLoadError` | HTML/assets version, CDN, Service Worker и atomic deploy |
| API `401` или CORS | Cookies, origin, credentials и runtime config |
| Только часть пользователей | Release, browser, region, flag и Service Worker |
| Ошибка растёт во время canary | Остановить rollout и сравнить версии |
| Rollback не помог | Digest, config, cache, flags и backend compatibility |
| Deploy зелёный, но сайт сломан | Внешний smoke test и production metrics |
| Ошибка только в error tracking | Проверить release mapping и source maps |
| Повторяющийся инцидент | Runbook, postmortem и проверяемое предотвращение |

## Связанные темы

- [05 Настройка Nginx для SPA](<./05 Настройка Nginx для SPA.md>)
- [08 Source maps в production](<../Tooling/08 Source maps в production.md>)
- [07 Обработка ошибок и наблюдаемость](<../Architecture/07 Обработка ошибок и наблюдаемость.md>)
- [05 CORS и preflight-запросы](<../Web API/05 CORS и preflight-запросы.md>)
- [07 Service Worker и стратегии кеширования](<../Browser Internals/07 Service Worker и стратегии кеширования.md>)

## Источники

- [GitLab: Environments and deployments](https://docs.gitlab.com/ci/environments/)
- [GitLab: Deployment safety](https://docs.gitlab.com/ci/environments/deployment_safety/)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
- [Sentry: JavaScript source maps](https://docs.sentry.io/platforms/javascript/sourcemaps/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 06 Переменные окружения и secrets в CI CD](<./06 Переменные окружения и secrets в CI CD.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [08 Стратегии развёртывания и rollback →](<./08 Стратегии развёртывания и rollback.md>)
<!-- CARD-NAV-BOTTOM:END -->
