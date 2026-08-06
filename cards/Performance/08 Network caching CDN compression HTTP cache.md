# Network caching CDN compression HTTP cache

<!-- CARD-NAV-TOP:START -->
[← 07 Main thread long tasks Web Workers](<./07 Main thread long tasks Web Workers.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Performance budgets CI monitoring RUM →](<./09 Performance budgets CI monitoring RUM.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как сеть, HTTP cache, CDN и сжатие влияют на производительность frontend-приложения?**

<h2></h2>

<br>
<dl>
<dd>

Скорость загрузки зависит не только от размера файлов.

До получения ресурса браузеру могут потребоваться:

```text
поставить запрос в очередь
→ определить IP через DNS
→ установить транспортное соединение
→ выполнить TLS
→ отправить HTTP request
→ дождаться первого байта
→ получить response body
```

При повторном запросе часть работы может быть пропущена:

- DNS уже известен;
- соединение открыто;
- TLS session переиспользуется;
- ресурс находится в HTTP cache;
- ответ находится на ближайшем CDN edge;
- Service Worker возвращает локальный ответ.

Поэтому один URL в разных условиях может загружаться совершенно по-разному.

### Из чего складывается сетевое время

Упрощённая модель:

```text
request duration
=
queueing
+
connection setup
+
request transfer
+
server processing и network latency
+
response download
```

В Chrome DevTools отдельные фазы можно увидеть в:

```text
Network
→ выбрать request
→ Timing
```

Возможные фазы:

| Фаза | Что происходит |
| --- | --- |
| Queueing | Запрос ожидает приоритета, соединения или других ресурсов |
| DNS Lookup | Домен преобразуется в IP-адрес |
| Initial connection | Устанавливается TCP или QUIC-соединение |
| SSL/TLS | Согласовывается защищённое соединение |
| Request sent | Отправляются method, headers и body запроса |
| Waiting (TTFB) | Ожидается первый байт ответа |
| Content Download | Загружается тело ответа |

Не каждый запрос проходит все фазы.

Например, при переиспользовании соединения могут отсутствовать:

```text
DNS
TCP/QUIC setup
TLS
```

При использовании свежего local cache сетевой запрос может вообще не выполняться.

### Latency и bandwidth

**Latency**, или задержка, показывает, сколько времени проходит до начала получения результата.

На неё влияют:

- физическое расстояние;
- число сетевых переходов;
- round trips;
- создание соединения;
- TLS;
- очередь сервера;
- последовательные зависимости.

**Bandwidth**, или пропускная способность, показывает, сколько данных можно передать за единицу времени.

Упрощённо:

```text
маленькие последовательные запросы
→ часто ограничены latency

большой файл
→ сильнее зависит от bandwidth
```

Например, десять запросов по `5 КБ`, выполняемых строго последовательно, могут оказаться медленнее одного запроса `100 КБ`.

Причина:

```text
каждый новый запрос
→ ждёт отдельный round trip
```

Высокая пропускная способность не устраняет задержку последовательного обнаружения.

### Cold и warm connection

**Cold connection:**

```text
DNS
→ transport connection
→ TLS
→ request
```

**Warm connection:**

```text
готовое соединение
→ request
```

Warm request обычно быстрее, но соединение не хранится бесконечно.

Оно может быть закрыто:

- сервером;
- браузером;
- proxy;
- NAT;
- из-за простоя;
- при смене сети;
- при ограничении ресурсов устройства.

Поэтому локальный повторный тест с открытым соединением не полностью воспроизводит первое посещение пользователя.

### TTFB

TTFB, Time to First Byte, — время до получения первого байта ответа.

Для документа в него могут входить:

```text
DNS
+
connection
+
TLS
+
путь по сети
+
CDN
+
очередь backend
+
server rendering
+
database
```

Большой TTFB HTML особенно важен, потому что браузер позже обнаруживает:

- CSS;
- JavaScript;
- изображения;
- preload;
- шрифты;
- другие ресурсы страницы.

Упрощённо:

```text
поздний HTML
→ позднее обнаружение ресурсов
→ поздний LCP
```

Для отдельного API-запроса высокий TTFB может задержать конкретное взаимодействие или client navigation.

TTFB является диагностической метрикой, а не полным показателем пользовательского опыта.

Быстрый TTFB не гарантирует:

- хороший LCP;
- маленький JavaScript;
- быструю hydration;
- хороший INP.

### Размеры ресурса

Для сетевых ресурсов различают несколько размеров.

| Показатель | Что показывает |
| --- | --- |
| Transfer size | Response headers и тело в переданном виде |
| Encoded body size | Размер body после gzip, Brotli или другого content encoding |
| Decoded body size | Размер body после декодирования |
| Runtime representation | Структуры, созданные браузером после parsing и выполнения |

Например:

```text
JavaScript source
→ 1 МБ

Brotli body
→ 250 КБ

transfer с headers
→ немного больше 250 КБ
```

По сети пользователь получает около `250 КБ`, но браузер затем должен:

```text
распаковать
→ разобрать около 1 МБ JavaScript
→ скомпилировать
→ выполнить
```

Поэтому:

```text
маленький transfer size
≠
маленькая CPU-стоимость
```

В Chrome Network при включённых больших строках Size может показывать:

```text
переданный размер
/
размер после распаковки
```

Для ресурса из memory cache или disk cache вместо сетевого размера DevTools может показать источник cache.

В Performance Resource Timing нулевой `transferSize` может означать local cache.

Для cross-origin ресурса без разрешающего:

```http
Timing-Allow-Origin
```

детальные размеры также могут быть скрыты, поэтому один ноль нельзя интерпретировать без дополнительного контекста.

### Что такое HTTP cache

HTTP cache хранит ответы и повторно использует их по HTTP-правилам.

Возможные cache:

- memory cache браузера;
- disk cache браузера;
- proxy cache;
- CDN edge cache;
- другой shared cache.

Упрощённая последовательность:

```text
request
→ найти подходящую cache entry
→ проверить freshness
→ использовать ответ
  или выполнить validation
  или получить новый ответ
```

HTTP cache управляется преимущественно через:

- `Cache-Control`;
- `Expires`;
- `ETag`;
- `Last-Modified`;
- `Vary`;
- status code;
- method;
- cache key.

Cache не обязательно означает браузер.

Различают:

```text
private cache
→ cache конкретного пользователя,
  обычно browser cache

shared cache
→ cache между несколькими клиентами,
  например CDN
```

### Fresh и stale response

Cache entry имеет возраст и срок свежести.

Пока ответ fresh:

```text
cache hit
→ ответ используется
→ origin не вызывается
```

После окончания срока ответ становится stale.

Дальнейшее поведение зависит от директив:

```text
stale
→ revalidate

или:

stale
→ временно использовать,
  если это явно разрешено

или:

stale
→ получить полный новый ответ
```

Fresh cache hit обычно быстрее revalidation:

```text
fresh cache hit
→ нет network round trip

revalidation
→ network request
→ ожидание origin/CDN
→ 304 или новый body
```

### Типичная стратегия по ресурсам

| Ресурс | Частая стратегия | Причина |
| --- | --- | --- |
| JS и CSS с content hash | `public, max-age=31536000, immutable` | Новый контент получает новый URL |
| Изображение с versioned URL | Долгий `max-age`, при необходимости `immutable` | Изменение публикуется по новому URL |
| HTML SPA | `no-cache` или небольшой `max-age` | Документ должен быстро получить ссылки на текущие chunks |
| Cacheable SSR HTML | `s-maxage`, иногда `stale-while-revalidate` | CDN может отдавать общий HTML с edge |
| Персональный API | `private` или `no-store` | Shared cache не должен смешивать пользователей |
| Чувствительные данные | Обычно `no-store` | Ответ не должен сохраняться HTTP cache |
| Публичный API | `max-age`, `s-maxage`, validators | Браузер и CDN уменьшают обращения к origin |
| Редко меняющийся JSON | Долгий TTL или validation | Зависит от допустимой устарелости |

Это не универсальные заголовки.

Стратегию выбирают по вопросам:

```text
Может ли ответ храниться?

Кто может его хранить?

Как долго он остаётся корректным?

Можно ли показать stale response?

Как cache узнает об изменении?

Различается ли ответ между пользователями?
```

### Content hash

Content hash включается в URL ресурса:

```text
app.a81f3c.js
```

При изменении содержимого:

```text
app.a81f3c.js
→ app.94d8e2.js
```

Старый URL продолжает означать старое содержимое, а новый URL — новую версию.

Поэтому ресурс можно хранить долго:

```http
Cache-Control: public, max-age=31536000, immutable
```

Основной механизм корректности здесь — новый URL.

`immutable` дополнительно сообщает, что во время freshness lifetime ресурс не планируется изменять.

Нельзя публиковать другое содержимое по прежнему hashed URL:

```text
один URL
→ разные bytes
```

Это нарушит cache contract и может оставить у пользователей несовместимые версии приложения.

### Почему HTML кешируют иначе

HTML является точкой входа.

Он содержит ссылки на assets:

```html
<script
  src="/assets/app.a81f3c.js"
></script>
```

После нового deployment HTML должен ссылаться на новую сборку:

```html
<script
  src="/assets/app.94d8e2.js"
></script>
```

Если старый HTML хранить как immutable asset, пользователь продолжит получать ссылки старого релиза.

Это может привести к:

- работе на старой версии;
- запросу удалённых chunks;
- несовместимости с новым API;
- `ChunkLoadError`.

Поэтому HTML часто:

```text
хранят с no-cache
```

или:

```text
дают небольшой max-age
+
revalidation
```

Публичный SSR HTML можно хранить на CDN дольше, если приложение допускает заданную устарелость и имеет продуманную invalidation-стратегию.

Главное различие:

```text
hashed asset
→ URL меняется вместе с содержимым

HTML
→ URL обычно остаётся прежним
```

### `max-age`

Пример:

```http
Cache-Control: max-age=3600
```

Ответ считается fresh, пока его возраст не превысил один час.

Пока он fresh, cache может использовать его без обращения к origin.

`max-age` относится к cache в общем случае:

- private browser cache;
- shared cache, если другие директивы это разрешают.

Возраст ответа можно увидеть через:

```http
Age: 600
```

Это означает, что shared cache оценивает возраст ответа примерно в `600` секунд.

### `s-maxage`

```http
Cache-Control: public, max-age=60, s-maxage=3600
```

Для browser cache:

```text
fresh 60 секунд
```

Для shared cache:

```text
fresh 3600 секунд
```

`s-maxage` переопределяет для shared cache:

- `max-age`;
- `Expires`.

Он также требует от shared cache успешно revalidate stale response перед повторным использованием, если другая директива явно не разрешает stale.

Это позволяет:

```text
браузер
→ чаще обновляет данные

CDN
→ дольше переиспользует общий ответ
```

### `no-cache`

```http
Cache-Control: no-cache
```

Название часто интерпретируют неправильно.

`no-cache` не означает:

```text
не сохранять ответ
```

Он означает:

```text
ответ можно сохранить,
но нельзя повторно использовать
без успешной validation
```

Повторный запрос может получить:

```text
304 без body
```

и затем использовать сохранённое содержимое.

Это полезно для HTML:

```text
локальная копия хранится
→ сервер подтверждает актуальность
→ body не скачивается повторно
```

Но network round trip всё равно остаётся.

### `no-store`

```http
Cache-Control: no-store
```

`no-store` сообщает private и shared cache не сохранять request/response для последующего использования.

Он применяется, когда хранение недопустимо, например для некоторых:

- персональных данных;
- финансовых ответов;
- одноразовых документов;
- чувствительной информации.

`no-store` не следует ставить на все ресурсы автоматически.

Для публичного versioned JavaScript он уничтожит преимущества cache и заставит пользователя снова загружать неизменившийся файл.

### `max-age=0`

```http
Cache-Control: max-age=0
```

Ответ становится stale сразу.

Он может сохраниться, но при обычном повторном использовании потребуется проверка актуальности, если другая директива не разрешает использовать stale response.

Это близко к распространённому поведению `no-cache`, но выражает его через нулевой freshness lifetime.

Директивы не следует считать полностью взаимозаменяемыми во всех сочетаниях.

### `must-revalidate`

```http
Cache-Control: max-age=60, must-revalidate
```

Пока ответ fresh, его можно использовать.

После перехода в stale:

```text
cache обязан успешно проверить origin
перед повторным использованием
```

Даже при недоступности origin cache не должен молча использовать stale response только потому, что он сохранился локально.

`must-revalidate` нужен, когда использование неподтверждённой stale-версии может нарушить корректность.

Различие:

```text
no-cache
→ validation перед каждым reuse

must-revalidate
→ validation после перехода в stale
```

### `private`

```http
Cache-Control: private, max-age=60
```

Ответ может храниться private cache, например браузером конкретного пользователя.

Shared cache не должен хранить такой ответ для повторной выдачи другим пользователям.

`private` не означает:

```text
ответ зашифрован

ответ не хранится

данные автоматически изолированы
при смене аккаунта
```

Для чувствительного персонального ответа часто проще использовать:

```http
Cache-Control: private, no-store
```

Если browser caching персонального ответа всё же нужен, необходимо отдельно проверить:

- cache key;
- logout;
- смену аккаунта;
- URL;
- cookies;
- `Authorization`;
- invalidation.

### `public`

```http
Cache-Control: public, max-age=3600
```

`public` явно разрешает shared caching, если остальные условия хранения выполнены.

Он особенно важен, когда ответ иначе мог бы не храниться shared cache, например request содержит:

```http
Authorization
```

Нельзя добавлять `public` к персональному ответу только ради CDN.

Сначала нужно доказать, что один и тот же response безопасно выдавать всем подходящим клиентам.

### Validators

Validator позволяет спросить:

```text
Изменился ли сохранённый ответ?
```

Основные механизмы:

- `ETag`;
- `Last-Modified`.

Они не задают срок свежести самостоятельно.

Они помогают проверить stale response без повторной передачи полного body.

### `ETag`

Сервер возвращает:

```http
ETag: "a81f3c"
```

При validation клиент отправляет:

```http
If-None-Match: "a81f3c"
```

Если представление не изменилось:

```http
HTTP/1.1 304 Not Modified
```

Browser использует сохранённый body.

Если изменилось:

```http
HTTP/1.1 200 OK
```

и получает новый response body.

`ETag` должен соответствовать выбранному представлению.

Если сервер отдаёт разные encoded variants:

```text
gzip
Brotli
identity
```

нужно корректно учитывать их в caching и validation.

### `Last-Modified`

Сервер может вернуть:

```http
Last-Modified:
  Wed, 05 Aug 2026 10:00:00 GMT
```

Клиент отправляет:

```http
If-Modified-Since:
  Wed, 05 Aug 2026 10:00:00 GMT
```

Если ресурс не изменён, сервер может ответить `304`.

`Last-Modified` проще, но обычно менее точно описывает версию, чем специально сформированный `ETag`.

Если доступны оба validator, `If-None-Match` имеет приоритет над `If-Modified-Since`.

### Что экономит `304`

`304 Not Modified` не передаёт полный response body.

Это уменьшает:

- transfer size;
- время передачи крупного ресурса;
- нагрузку на bandwidth.

Но не устраняет:

- network round trip;
- connection setup, если соединения нет;
- latency;
- работу CDN или origin;
- server validation;
- request и response headers.

Упрощённо:

```text
fresh cache hit
→ быстрее

304 validation
→ экономит body,
  но ждёт сеть

200 response
→ ждёт сеть
  и передаёт body
```

### `stale-while-revalidate`

Пример:

```http
Cache-Control:
  max-age=60,
  stale-while-revalidate=300
```

Первые `60` секунд ответ fresh.

Следующие `300` секунд cache может:

```text
быстро отдать stale response
+
проверить новую версию
в фоне
```

Это скрывает от пользователя latency validation.

Но приложение должно допускать, что пользователь временно увидит устаревшие данные.

Подход хорошо подходит, например, для:

- публичной статьи;
- каталога с допустимой задержкой;
- общих справочных данных;
- страницы, где краткая stale-версия лучше ожидания.

Он может быть неприемлем для:

- баланса счёта;
- окончательной цены заказа;
- прав доступа;
- одноразового token;
- данных, где устаревший ответ создаёт ошибочное действие.

`stale-while-revalidate` не запускает фоновую работу бесконечно сам по себе.

Обычно revalidation инициируется запросом, который пришёл внутри разрешённого stale-window.

### `stale-if-error`

```http
Cache-Control:
  max-age=60,
  stale-if-error=3600
```

После окончания freshness cache может временно использовать stale response, если при обращении к origin произошла подходящая ошибка:

- network failure;
- `500`;
- `502`;
- `503`;
- `504`.

Цель:

```text
устаревший доступный ответ
лучше полной ошибки
```

Это повышает availability, но также требует заранее определить максимально допустимую устарелость.

`stale-if-error` и `stale-while-revalidate` решают разные задачи:

```text
stale-while-revalidate
→ скрыть latency обновления

stale-if-error
→ пережить ошибку origin
```

### CDN

CDN, Content Delivery Network, располагает точки присутствия ближе к пользователям.

Упрощённая схема:

```text
пользователь
→ ближайший CDN edge
→ origin
```

Без CDN:

```text
пользователь
→ каждый раз обращается
  к удалённому origin
```

С CDN:

```text
cache hit
→ edge отдаёт ответ

cache miss
→ edge запрашивает origin
→ может сохранить ответ
→ отдаёт пользователю
```

CDN может уменьшить:

- сетевое расстояние;
- TTFB;
- нагрузку на origin;
- число повторных вычислений;
- передачу между пользователем и origin.

CDN не гарантирует ускорение любого ответа.

Результат зависит от:

- географии точек присутствия;
- cache hit ratio;
- cache key;
- TTL;
- маршрутизации;
- скорости origin;
- CDN configuration;
- размера ответа;
- частоты запросов.

### CDN cache hit и miss

**Hit:**

```text
ответ уже находится
на подходящем edge
```

Пользователь не ждёт полный путь до origin.

**Miss:**

```text
edge не нашёл ответ
→ запросил origin
→ получил и, возможно, сохранил
```

Первый пользователь получает стоимость miss.

Следующие пользователи выиграют только если:

- response разрешено хранить;
- cache key совпадает;
- TTL не истёк;
- entry не была удалена;
- запрос пришёл на edge или cache tier, где entry доступна.

Возможны и промежуточные состояния:

- revalidated;
- stale hit;
- bypass;
- expired;
- dynamic;
- hit на regional tier, но miss на edge.

Названия зависят от CDN-провайдера.

### Cache hit ratio

Cache hit ratio показывает долю запросов, обслуженных из CDN cache.

Упрощённо:

```text
hits / все cache-eligible requests
```

Низкий hit ratio может означать:

- слишком короткий TTL;
- слишком детальный cache key;
- уникальные query parameters;
- cookies;
- частые purge;
- много редко запрашиваемых URL;
- ответ запрещено хранить;
- распределение трафика по большому числу edge;
- неправильную конфигурацию.

Высокий hit ratio сам по себе не гарантирует корректность.

Если key недостаточно точный, cache может быстро отдавать неправильный вариант ответа.

### Cache key

Cache key определяет, какой сохранённый ответ соответствует request.

В базовой модели важны:

- method;
- target URI;
- выбранные request headers через `Vary`.

Конкретный CDN может дополнительно учитывать или нормализовать:

- query parameters;
- cookies;
- host;
- protocol;
- device category;
- собственные правила;
- authentication state.

Например:

```text
/products?page=1
/products?page=2
```

обычно являются разными cache entries.

Но параметры аналитики:

```text
/products?utm_source=mail
/products?utm_source=search
```

могут описывать один и тот же контент.

Если CDN без необходимости включает их в key, hit ratio снижается.

Удалять параметры из key можно только тогда, когда они действительно не меняют response.

### `Vary`

Ответ:

```http
Vary: Accept-Encoding
```

сообщает, что представление зависит от request header `Accept-Encoding`.

Cache хранит отдельные варианты, например:

```text
gzip
Brotli
identity
```

Другой пример:

```http
Vary: Accept-Language
```

означает, что язык влияет на response.

Без значимого `Vary` cache может переиспользовать неправильный вариант.

Слишком широкий `Vary` создаёт большое число entries.

Опасный пример:

```http
Vary: User-Agent
```

У `User-Agent` огромное число вариантов, поэтому hit ratio может резко снизиться.

`Vary: *` означает, что сохранённый response нельзя использовать для другого request без обращения к origin.

CDN-провайдеры могут иметь собственные ограничения и настройки поддержки `Vary`, поэтому итоговое поведение проверяют на конкретной инфраструктуре.

### Cookies и CDN

Cookie часто содержит уникальные пользовательские данные.

Если весь `Cookie` участвует в cache key:

```text
почти каждый пользователь
→ отдельная cache entry
```

Hit ratio уменьшается.

Если cookie влияет на response, но не учитывается:

```text
cache может отдать
неправильный вариант
```

Распространённая стратегия:

```text
публичные маршруты
→ общий cache без персональных cookies

персональные маршруты
→ bypass shared cache
  или отдельная безопасная стратегия
```

Не следует автоматически добавлять:

```http
Vary: Cookie
```

ко всему сайту.

Сначала определяют конкретный признак, действительно меняющий ответ.

Иногда вместо большого cookie используют небольшой нормализованный header, например категорию языка или устройства, если инфраструктура контролирует его формирование.

### CDN purge и invalidation

Иногда URL не меняется, но ответ нужно удалить из CDN cache до окончания TTL.

Для этого CDN предоставляет:

- purge по URL;
- purge по tag;
- surrogate key;
- path invalidation;
- version switch.

Purge полезен для:

- исправления ошибочной цены;
- удаления публикации;
- срочного обновления HTML;
- отзыва небезопасного файла.

Но frequent purge уменьшает преимущества cache и может создать волну cache miss.

Для static assets надёжнее:

```text
versioned URL
+
долгий TTL
```

чем постоянная очистка одного неизменного URL.

### Cache warming

После deployment новый hashed asset ещё отсутствует на edge.

Первый запрос в каждом регионе может получить miss.

Cache warming заранее запрашивает важные URL или наполняет верхний cache tier.

Это может быть полезно для:

- крупных релизов;
- глобальной аудитории;
- ограниченного набора критичных assets;
- ожидаемого traffic spike.

Но warming всех возможных URL может:

- создать лишнюю нагрузку;
- заполнить cache неиспользуемыми данными;
- вытеснить популярные entries.

Сначала определяют действительно горячие ресурсы.

### Сжатие HTTP-ответов

Клиент сообщает поддерживаемые content codings:

```http
Accept-Encoding: br, gzip
```

Сервер выбирает вариант и отвечает:

```http
Content-Encoding: br
```

После получения browser декодирует body.

Для корректного caching вариантов обычно используется:

```http
Vary: Accept-Encoding
```

Без него shared cache должен иным способом гарантировать, что клиент получит поддерживаемый вариант.

### Brotli и gzip

Для текстовых ресурсов обычно используют:

- Brotli;
- gzip как совместимый fallback.

Brotli часто лучше сжимает:

- JavaScript;
- CSS;
- HTML;
- JSON;
- SVG;
- текстовые файлы.

Gzip обычно:

- быстрее сжимается;
- широко поддерживается;
- используется как fallback;
- может быть выгоден для динамического ответа при ограниченном CPU.

Выбор зависит от:

- размера ответа;
- частоты генерации;
- серверного CPU;
- cache;
- возможности precompression;
- требуемой задержки.

### Static precompression

Static assets можно сжать во время build:

```text
app.js
app.js.br
app.js.gz
```

CDN или web-server выбирает готовый вариант по `Accept-Encoding`.

Преимущества:

- высокий уровень сжатия;
- отсутствие compression CPU на каждый request;
- предсказуемый результат;
- возможность хранить encoded variant на CDN.

Это особенно подходит для immutable assets:

- JS;
- CSS;
- SVG;
- JSON;
- WebAssembly, если сжатие даёт выигрыш.

Нужно гарантировать правильные:

- `Content-Encoding`;
- `Content-Type`;
- `Vary`;
- cache headers.

### Dynamic compression

SSR HTML или динамический JSON может сжиматься во время request.

Слишком высокий уровень Brotli способен увеличить TTFB из-за CPU-сжатия.

Упрощённый trade-off:

```text
сильнее compression
→ меньше bytes
→ больше server CPU
→ возможный больший TTFB
```

Поэтому для динамических ответов выбирают разумный уровень либо cache сжатого результата.

Маленький response иногда не стоит сжимать: headers и CPU могут быть заметнее выигрыша.

### Что обычно не сжимают повторно

Уже сжатые форматы:

- JPEG;
- PNG;
- WebP;
- AVIF;
- MP4;
- WebM;
- WOFF2;
- ZIP;
- PDF с уже сжатыми потоками.

Повторный gzip/Brotli обычно даёт минимальный выигрыш и тратит CPU.

Для них важнее:

- правильный codec;
- качество;
- физические размеры;
- adaptive variants;
- streaming;
- range requests;
- CDN.

SVG является текстовым форматом, поэтому обычно хорошо сжимается через Brotli или gzip.

### HTTP/1.1

HTTP/1.1 не имеет встроенного multiplexing нескольких exchanges в одном соединении.

Браузеры открывают несколько соединений к origin, чтобы выполнять запросы параллельно.

Это создаёт стоимость:

- дополнительных connections;
- TLS;
- congestion control;
- ограничения числа одновременных запросов.

Исторические техники вроде domain sharding пытались открыть больше соединений, но при HTTP/2 и HTTP/3 часто становятся вредными.

### HTTP/2

HTTP/2 добавляет multiplexing:

```text
одно соединение
→ несколько одновременных streams
```

Также используются:

- бинарное framing;
- сжатие HTTP fields;
- stream prioritization;
- более эффективное использование соединения.

Это уменьшает необходимость объединять все assets в один огромный файл только ради количества HTTP-запросов.

Но HTTP/2 работает поверх TCP.

Если TCP packet потерян, восстановление порядка может временно остановить данные всех HTTP/2 streams этого соединения.

Это транспортный head-of-line blocking.

HTTP/2 также не устраняет application waterfall:

```text
HTML
→ JS
→ dynamic import
→ API
```

Следующий request всё равно не начнётся до обнаружения зависимости.

### HTTP/3

HTTP/3 использует QUIC.

QUIC предоставляет:

- stream multiplexing;
- per-stream reliability;
- интегрированный TLS;
- более быструю установку соединения в некоторых сценариях;
- отсутствие TCP-level blocking между независимыми streams.

Если packet одного stream потерян:

```text
этот stream может ждать восстановления

другие независимые streams
→ могут продолжить работу
```

Но HTTP/3 не исправляет архитектурные зависимости:

```text
script должен выполниться
→ только затем известен URL
→ request всё равно начинается поздно
```

Протокол уменьшает часть сетевой стоимости, но не заменяет правильный dependency graph и раннее обнаружение ресурсов.

### Request chains

Request chain возникает, когда следующий ресурс становится известен только после предыдущего.

Пример:

```text
HTML
→ CSS
→ CSS background image
```

Другой пример:

```text
HTML
→ initial JavaScript
→ dynamic import
→ library chunk
→ API request
```

Даже при хорошем cache и HTTP/3 каждый следующий шаг ждёт обнаружения.

Для критического пути проверяют:

- можно ли обнаружить ресурс раньше;
- можно ли запустить requests параллельно;
- действительно ли dependency обязательна;
- нужен ли preload;
- не создаёт ли lazy loading ранний waterfall;
- можно ли получить данные на сервере;
- не блокирует ли redirect.

### Redirects

Redirect добавляет дополнительный request-response cycle:

```text
старый URL
→ 301/302
→ новый URL
```

Для навигации это может включить:

- дополнительную latency;
- повторную проверку cache;
- новый origin;
- новое соединение;
- новый TLS.

Постоянные перенаправления cacheable, но лучше сразу использовать финальный URL в:

- HTML;
- API-клиенте;
- asset manifest;
- canonical links;
- preload;
- внутренней навигации.

Особенно вредны redirect chains:

```text
A
→ B
→ C
→ D
```

### `preconnect`

```html
<link
  rel="preconnect"
  href="https://cdn.example.com"
  crossorigin
>
```

`preconnect` заранее подготавливает соединение с origin.

Он может включить:

- DNS;
- TCP или QUIC connection;
- TLS.

Это полезно, когда критический request точно пойдёт на другой origin, но сам URL ресурса пока не обнаружен.

Например:

```text
HTML
→ позже CSS обнаружит font
на отдельном origin
```

`preconnect` не загружает сам ресурс.

Слишком много таких подсказок расходует:

- sockets;
- CPU;
- память;
- сетевые ресурсы.

Используют небольшое число критичных origins.

### `dns-prefetch`

```html
<link
  rel="dns-prefetch"
  href="//cdn.example.com"
>
```

`dns-prefetch` выполняет только DNS lookup.

Он дешевле `preconnect`, но не создаёт transport/TLS connection.

Упрощённо:

```text
origin точно нужен скоро
→ preconnect

origin только вероятно понадобится
→ dns-prefetch
```

Оба механизма являются подсказками, а не гарантией конкретного времени выполнения.

### HTTP cache и Cache API

HTTP cache:

- работает автоматически;
- следует HTTP headers;
- участвует в обычном fetch;
- управляется браузером.

Cache API:

```js
const cache =
  await caches.open(
    "app-v1",
  );

await cache.put(
  request,
  response,
);
```

- управляется JavaScript;
- хранит пары `Request`/`Response`;
- часто используется Service Worker;
- требует собственной стратегии версий и удаления.

Запись в Cache API не означает появление ответа в HTTP cache.

Запись в HTTP cache не означает появление в Cache API.

Это независимые уровни.

### Service Worker и HTTP cache

Service Worker может перехватить `fetch`:

```text
page request
→ Service Worker fetch handler
```

Далее он может:

- вернуть ответ из Cache API;
- обратиться к network;
- использовать normal fetch;
- создать собственную fallback-стратегию;
- обновить Cache API.

Network fetch внутри Service Worker в зависимости от request и cache mode может также взаимодействовать с HTTP cache.

Поэтому возможна многоуровневая схема:

```text
Cache API
→ HTTP cache
→ CDN
→ origin
```

Это усложняет диагностику.

В DevTools проверяют:

- `from ServiceWorker`;
- Cache Storage;
- Disable cache;
- bypass Service Worker;
- request initiator;
- response headers.

Service Worker не должен бессрочно хранить старые assets без versioning и cleanup.

### ChunkLoadError после deployment

Сценарий:

```text
1. Пользователь открыл старый HTML.
2. Выполнен новый deployment.
3. Старые assets удалены.
4. Пользователь открыл lazy route.
5. Runtime запросил старый hashed chunk.
6. Сервер вернул 404.
```

Защита:

- content hash;
- атомарная публикация;
- сначала загрузить assets, затем переключить HTML;
- некоторое время хранить предыдущие assets;
- корректно кешировать HTML;
- учитывать открытые SPA-вкладки;
- управляемо предлагать refresh;
- не создавать бесконечный reload loop.

Долгое cache старого hashed chunk не является проблемой, если файл остаётся доступен по своему неизменному URL.

Проблема появляется, когда URL удалён раньше, чем его перестали запрашивать активные клиенты.

### Cache busting

Плохая стратегия:

```text
app.js
→ изменить содержимое
→ оставить тот же URL
→ пытаться очистить cache у всех
```

Лучше:

```text
app.a1.js
→ app.b2.js
```

Иногда используют query version:

```text
app.js?v=2
```

Query parameter обычно создаёт другой cache key, но поведение промежуточной инфраструктуры может зависеть от конфигурации.

Hashed filename делает versioning более явным и лучше интегрируется с asset manifest.

Для HTML URL обычно остаётся прежним, поэтому он требует короткого TTL, validation или управляемой CDN invalidation.

### Как диагностировать сеть и cache

Порядок:

```text
1. Выбрать конкретный маршрут и сценарий.
2. Разделить cold и warm load.
3. Записать Network waterfall.
4. Проверить protocol и connection reuse.
5. Найти последовательные request chains.
6. Проверить TTFB и Content Download.
7. Сравнить transfer и decoded size.
8. Проверить Content-Encoding.
9. Проверить Cache-Control, Age, ETag и Vary.
10. Определить memory cache, disk cache, Service Worker или CDN.
11. Проверить CDN hit ratio и cache key.
12. Повторить тест без Disable cache.
13. Проверить поведение после deployment.
14. Сравнить полевые TTFB и LCP.
```

### Проверка cache в DevTools

Для cold load:

```text
открыть DevTools
→ Network
→ Disable cache
→ reload
```

Опция работает, пока DevTools открыт.

Для warm load:

```text
выключить Disable cache
→ повторить навигацию
```

В Network проверяют:

- Status;
- Size;
- Time;
- Initiator;
- Priority;
- Protocol;
- response headers;
- request headers;
- Timing;
- source вроде memory cache или disk cache.

Чтобы проверить `304`:

```text
не отключать cache
→ выполнить reload
→ найти conditional request
→ проверить If-None-Match
  или If-Modified-Since
```

Чтобы проверить CDN:

- посмотреть `Age`;
- посмотреть vendor-specific cache status;
- сравнить TTFB из разных регионов;
- проверить cache analytics;
- сравнить hit и miss;
- убедиться, что response действительно cacheable.

### Что измерять после оптимизации

Изменение cache или CDN проверяют не только по одному локальному reload.

Полезные показатели:

- TTFB p75;
- cache hit ratio;
- origin request count;
- origin bandwidth;
- CDN egress;
- transfer size;
- `304` rate;
- cache bypass rate;
- error rate;
- LCP;
- число `ChunkLoadError`;
- доля stale responses;
- время purge propagation.

Также проверяют корректность:

```text
не получают ли пользователи
чужие персональные данные

не остаётся ли старая цена

не загружаются ли
несовместимые chunks

не кешируется ли error response
дольше допустимого
```

### Главный принцип

```text
network performance
=
latency
+
bytes
+
server work
+
порядок обнаружения
+
cache reuse
```

Cache помогает только тогда, когда:

```text
ответ безопасно переиспользовать

cache key корректен

TTL соответствует данным

invalidation работает

клиент получает нужную версию
```

Практическая стратегия:

```text
versioned static assets
→ долгий immutable cache

HTML
→ короткий cache
  или validation

публичные общие данные
→ browser/CDN cache
  с допустимой freshness

персональные данные
→ private или no-store
  по требованиям безопасности

текстовые ресурсы
→ Brotli/gzip

критические requests
→ раннее обнаружение
  и отсутствие waterfall
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Из каких этапов складывается время сетевого запроса?</strong></summary>

<dl>
<dd>
<h2></h2>

Возможные этапы:

```text
queueing
→ DNS
→ TCP или QUIC
→ TLS
→ request
→ ожидание первого байта
→ download
```

При повторном запросе часть этапов может исчезнуть благодаря:

- DNS cache;
- открытому соединению;
- TLS session;
- HTTP cache;
- CDN cache;
- Service Worker.

В Chrome DevTools точные фазы конкретного запроса находятся во вкладке `Timing`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем задержка сети (latency) отличается от пропускной способности (bandwidth)?</strong></summary>

<dl>
<dd>
<h2></h2>

Latency — время ожидания до начала результата или отдельного сетевого round trip.

Bandwidth — объём данных, передаваемый за единицу времени.

```text
много маленьких последовательных requests
→ ограничение latency

один большой файл
→ ограничение bandwidth
```

Высокий bandwidth не устраняет application waterfall, если следующий request становится известен только после предыдущего.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое TTFB и почему он может быть большим?</strong></summary>

<dl>
<dd>
<h2></h2>

TTFB — время до первого байта response.

В него могут входить:

- DNS;
- connection;
- TLS;
- network latency;
- CDN miss;
- очередь origin;
- server rendering;
- database;
- внешние API.

Для HTML большой TTFB задерживает обнаружение всех следующих ресурсов и способен ухудшить LCP.

Для диагностики разделяют connection setup, waiting и работу origin.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем transfer size отличается от resource size?</strong></summary>

<dl>
<dd>
<h2></h2>

Transfer size включает переданные response headers и encoded body.

Decoded resource size показывает размер body после gzip, Brotli или другого decoding.

Например:

```text
transfer
→ 300 КБ

decoded JavaScript
→ 1 МБ
```

Browser всё равно должен разобрать и выполнить восстановленный код.

В Resource Timing нулевой `transferSize` может означать local cache или скрытые cross-origin timings, поэтому проверяют также URL, `decodedBodySize` и `Timing-Allow-Origin`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему файлы с content hash можно кешировать надолго?</strong></summary>

<dl>
<dd>
<h2></h2>

Hash зависит от содержимого:

```text
app.a81f.js
```

При изменении создаётся новый URL:

```text
app.b42c.js
```

Старый URL продолжает обозначать старый файл, поэтому его можно хранить с долгим `max-age`.

Нельзя изменять содержимое уже опубликованного hashed URL.

HTML новой версии должен ссылаться на новые assets.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему HTML обычно не кешируют так же, как файлы с hash в имени?</strong></summary>

<dl>
<dd>
<h2></h2>

URL HTML обычно остаётся прежним, но его содержимое меняется и начинает ссылаться на новые chunks.

Старый HTML может:

- оставить пользователя на прежнем релизе;
- запросить удалённый chunk;
- конфликтовать с новым API.

Поэтому HTML обычно использует `no-cache`, короткий `max-age` или CDN-стратегию с управляемой freshness и invalidation.

Предыдущие hashed assets сохраняют достаточно долго для открытых вкладок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>no-cache</code>, <code>no-store</code> и <code>max-age=0</code> отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

`no-cache`:

```text
хранить можно
→ перед reuse нужна validation
```

`no-store`:

```text
не сохранять response
для последующего reuse
```

`max-age=0`:

```text
response сразу stale
→ обычно нужна validation
```

Для конфиденциальных данных политику выбирают по требованиям хранения и безопасности, а не только ради скорости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работают <code>ETag</code> и ответ <code>304 Not Modified</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Сервер возвращает:

```http
ETag: "version-42"
```

Browser при следующей validation отправляет:

```http
If-None-Match: "version-42"
```

Если response не изменился:

```http
304 Not Modified
```

Browser использует сохранённый body.

`304` экономит передачу body, но не устраняет network latency и server validation.

Fresh cache hit обычно быстрее.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое <code>stale-while-revalidate</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Директива разрешает временно вернуть stale response, пока cache обновляет его без блокировки пользователя.

```http
Cache-Control:
  max-age=60,
  stale-while-revalidate=300
```

```text
0–60 секунд
→ fresh

следующие 300 секунд
→ stale можно показать,
  параллельно выполняя validation
```

Стратегия подходит только тогда, когда кратковременная устарелость допустима.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при CDN cache hit и cache miss?</strong></summary>

<dl>
<dd>
<h2></h2>

При hit нужный вариант response уже находится в CDN cache.

```text
edge
→ пользователь
```

При miss:

```text
edge
→ origin
→ edge
→ пользователь
```

CDN может сохранить response для следующих requests.

Польза зависит от совпадения cache key, freshness и правил конкретного CDN.

Первый request после purge или deployment часто получает miss.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое cache key и как <code>Vary</code> на него влияет?</strong></summary>

<dl>
<dd>
<h2></h2>

Cache key определяет, может ли сохранённый response удовлетворить новый request.

В базовом HTTP caching учитываются URI и request headers, перечисленные в `Vary`.

```http
Vary: Accept-Encoding
```

создаёт отдельные варианты для разных content codings.

Слишком широкий `Vary`, уникальные query parameters и cookies уменьшают cache hit ratio.

Недостаточно точный key способен привести к выдаче неправильного response.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>max-age</code> отличается от <code>s-maxage</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`max-age` задаёт freshness для cache в общем случае.

`s-maxage` переопределяет этот срок для shared cache, например CDN.

```http
Cache-Control:
  public,
  max-age=60,
  s-maxage=3600
```

Browser может считать response fresh `60` секунд, а CDN — `3600`.

`s-maxage` также требует validation stale response shared cache перед обычным повторным использованием.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать Brotli, а когда gzip?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно сервер поддерживает оба encoding и выбирает по `Accept-Encoding`.

Brotli часто сильнее сжимает текстовые static assets.

Gzip:

- быстрее сжимается;
- широко поддерживается;
- используется как fallback;
- может быть выгоднее для динамического response при ограниченном CPU.

Static assets лучше precompress во время build, а dynamic compression настраивают с учётом TTFB и server load.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему сжатие JavaScript не решает проблему большого bundle полностью?</strong></summary>

<dl>
<dd>
<h2></h2>

Compression уменьшает network bytes.

После загрузки browser выполняет:

```text
decode
→ parse
→ compile
→ module evaluation
→ execution
```

На слабом CPU эти этапы могут быть дороже передачи.

Поэтому одновременно уменьшают:

- initial JavaScript;
- число modules;
- module side effects;
- runtime work;
- объём hydration.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем HTTP cache отличается от Cache API и Service Worker cache?</strong></summary>

<dl>
<dd>
<h2></h2>

HTTP cache управляется браузером по HTTP headers.

Cache API управляется JavaScript и хранит пары `Request`/`Response`.

Service Worker часто использует Cache API, чтобы:

- работать offline;
- возвращать fallback;
- реализовать cache-first или network-first;
- обновлять resources в фоне.

Хранилища независимы и требуют отдельной стратегии versioning и cleanup.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему после нового деплоя может возникнуть <code>ChunkLoadError</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Открытая вкладка продолжает использовать runtime старого релиза.

После deployment она может запросить старый lazy chunk, который уже удалён.

Защита:

- content hash;
- атомарная публикация;
- хранение предыдущих assets;
- короткий cache HTML;
- управляемое предложение обновить страницу;
- защита от бесконечного reload.

Старые hashed assets должны оставаться доступными дольше возможной жизни активных клиентов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>private</code>, <code>public</code> и <code>must-revalidate</code> отличаются друг от друга?</strong></summary>

<dl>
<dd>
<h2></h2>

`private` запрещает shared cache хранить response, но разрешает private cache.

`public` явно разрешает shared caching при выполнении остальных условий.

`must-revalidate` относится не к месту хранения, а к повторному использованию stale response:

```text
после окончания freshness
→ обязательна успешная validation
```

Директивы могут использоваться совместно, потому что отвечают на разные вопросы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что показывает заголовок <code>Age</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Age` показывает рассчитанный shared cache возраст response в секундах.

```http
Age: 120
```

Он помогает понять, что ответ, вероятно, был получен через промежуточный cache.

Но отсутствие `Age` не доказывает CDN miss: конкретная инфраструктура может формировать другие headers или скрывать детали.

Для полной диагностики используют также CDN-specific cache status и analytics.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем HTTP/2 отличается от HTTP/3 с точки зрения производительности?</strong></summary>

<dl>
<dd>
<h2></h2>

HTTP/2 multiplexes несколько streams через одно TCP-соединение.

Потеря TCP packet может временно задержать все streams этого соединения, потому что TCP восстанавливает общий упорядоченный поток байтов.

HTTP/3 использует QUIC с независимыми streams.

Потеря данных одного stream не обязана блокировать остальные.

Оба протокола не устраняют application waterfall, когда следующий URL становится известен только после выполнения предыдущего ресурса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужны <code>preconnect</code> и <code>dns-prefetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`preconnect` заранее подготавливает DNS, transport connection и TLS для критичного внешнего origin.

`dns-prefetch` выполняет только DNS lookup.

```text
origin точно нужен скоро
→ preconnect

origin может понадобиться
→ dns-prefetch
```

Слишком много подсказок расходует connections и CPU.

Их применяют только для небольшого числа значимых origins и проверяют через Network Timing.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что лучше для cache busting: query parameter или hashed filename?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба варианта могут создать новый URL:

```text
app.js?v=2

app.a81f3c.js
```

Hashed filename яснее связывает URL с содержимым и обычно лучше интегрируется со сборщиком, CDN и asset manifest.

Query parameters могут обрабатываться CDN по собственным правилам: учитываться, сортироваться, игнорироваться или нормализоваться.

Для production assets обычно предпочитают content hash в имени.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли кешировать персональный API-ответ?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно только при явно продуманной изоляции и invalidation.

`private` запрещает shared caching, но browser cache всё равно может сохранить response.

Нужно проверить:

- смену аккаунта;
- logout;
- одинаковый URL для разных пользователей;
- cookies;
- `Authorization`;
- cache key;
- допустимый срок хранения.

Для чувствительных персональных данных безопасным исходным вариантом обычно является `private, no-store`, пока необходимость cache не доказана отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как Service Worker взаимодействует с HTTP cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Service Worker может перехватить request раньше обычного network response.

Он может:

```text
вернуть Cache API response

или:

выполнить fetch
→ HTTP cache
→ CDN
→ origin
```

Поэтому один request способен пройти через несколько уровней cache.

Для диагностики проверяют:

- `from ServiceWorker`;
- Cache Storage;
- HTTP headers;
- Disable cache;
- bypass Service Worker;
- request cache mode.

Service Worker требует собственной стратегии versioning и удаления старых entries.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как понять, откуда фактически пришёл response?</strong></summary>

<dl>
<dd>
<h2></h2>

В Chrome Network проверяют:

- Size;
- Status;
- Timing;
- Protocol;
- Initiator;
- response headers;
- пометки memory cache, disk cache или ServiceWorker.

Для CDN дополнительно смотрят:

- `Age`;
- vendor-specific cache status;
- `Via`;
- `Server-Timing`;
- CDN analytics.

Заголовки конкретного CDN не стандартизированы, поэтому их интерпретируют по документации провайдера.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что проверяют |
| --- | --- |
| Повторная загрузка приложения снова скачивает JS | `Cache-Control`, content hash, Disable cache и источник response |
| CDN почти не уменьшает TTFB | Cache hit ratio, cache key, TTL, cookies, query parameters и origin |
| JS мало весит по сети, но долго блокирует страницу | Decoded size, parsing, module evaluation и execution |
| HTML продолжает загружать старый релиз | Freshness HTML, CDN purge и Service Worker |
| После deployment часть пользователей получает ошибку chunk | Срок хранения старых assets, атомарность deployment и reload recovery |
| LCP-изображение начинает загружаться поздно | Request chain, initiator, priority, preload и cache |
| Browser получает gzip вместо Brotli | `Accept-Encoding`, `Content-Encoding`, CDN variants и `Vary` |
| CDN хранит слишком много почти одинаковых entries | Query parameters, cookies, `Vary` и нормализация cache key |
| Один пользователь получает персональный response другого состояния | `private`/`no-store`, cache key, logout и смена аккаунта |
| `304` всё равно занимает заметное время | Network latency, connection setup и server validation |
| Service Worker отдаёт старые файлы | Cache API versioning, activate cleanup и fetch strategy |
| HTTP/3 включён, но route всё равно медленный | Application waterfall, TTFB, resource size и main-thread work |

## Связанные темы

- [06 HTTP cache cookies storage basics](<../Web Basics/06 HTTP cache cookies storage basics.md>)
- [08 DNS TCP UDP HTTP2 basics](<../Web Basics/08 DNS TCP UDP HTTP2 basics.md>)
- [05 Nginx static serving SPA fallback cache headers](<../DevOps/05 Nginx static serving SPA fallback cache headers.md>)
- [09 Production build assets hashing base publicPath](<../Tooling/09 Production build assets hashing base publicPath.md>)
- [04 Bundle size code splitting tree shaking loading strategy](<./04 Bundle size code splitting tree shaking loading strategy.md>)

## Источники

- [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [RFC 9113: HTTP/2](https://www.rfc-editor.org/rfc/rfc9113)
- [RFC 9114: HTTP/3](https://www.rfc-editor.org/rfc/rfc9114)
- [RFC 5861: stale-while-revalidate and stale-if-error](https://www.rfc-editor.org/rfc/rfc5861)
- [RFC 8246: Cache-Control immutable](https://www.rfc-editor.org/rfc/rfc8246)
- [W3C: Resource Timing](https://www.w3.org/TR/resource-timing/)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
- [MDN: Cache-Control](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control)
- [MDN: ETag](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/ETag)
- [MDN: Vary](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Vary)
- [MDN: Content-Encoding](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Encoding)
- [MDN: PerformanceResourceTiming](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming)
- [web.dev: HTTP Cache](https://web.dev/articles/http-cache)
- [web.dev: Content delivery networks](https://web.dev/articles/content-delivery-networks)
- [Chrome DevTools: Network features reference](https://developer.chrome.com/docs/devtools/network/reference/)
- [Chrome DevTools: Network panel](https://developer.chrome.com/docs/devtools/network)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Main thread long tasks Web Workers](<./07 Main thread long tasks Web Workers.md>) · [↑ Performance](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Performance budgets CI monitoring RUM →](<./09 Performance budgets CI monitoring RUM.md>)
<!-- CARD-NAV-BOTTOM:END -->
