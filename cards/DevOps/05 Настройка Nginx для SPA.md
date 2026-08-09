# Настройка Nginx для SPA

<!-- CARD-NAV-TOP:START -->
[← 04 Docker-сборка frontend-приложения](<./04 Docker-сборка frontend-приложения.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Переменные окружения и secrets в CI CD →](<./06 Переменные окружения и secrets в CI CD.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как настроить Nginx для раздачи frontend SPA? Что важно в SPA fallback и cache headers?**

<h2></h2>

<br>
<dl>
<dd>

После production-сборки статическая SPA состоит из файлов:

```text
index.html
JavaScript chunks
CSS
images
fonts
manifest
service worker
runtime config
```

Nginx принимает HTTP-запрос, выбирает подходящий `location`, сопоставляет URL с файлом внутри `root`, устанавливает `Content-Type`, применяет сжатие и добавляет cache headers.

Клиентский router начинает работать только после того, как браузер:

1. Получил `index.html`.
2. Загрузил JavaScript.
3. Инициализировал приложение.
4. Передал текущий URL router.

Поэтому первый запрос к адресу:

```text
/orders/42
```

всегда сначала обрабатывает сервер.

Если физического файла `/orders/42` нет, Nginx должен вернуть основной HTML SPA. После этого React Router или другой client router показывает нужный экран.

Это называется **SPA fallback**.

При этом fallback предназначен только для клиентских маршрутов приложения.

Его нельзя безусловно применять ко всем отсутствующим URL:

```text
/orders/42
→ index.html

/assets/app-missing.js
→ 404

/api/orders/42
→ API response или API 404

/config.js
→ реальный файл или 404
```

Если отсутствующий JavaScript chunk получит `index.html` со статусом `200`, браузер попытается обработать HTML как JavaScript.

В результате возможны ошибки:

```text
Unexpected token '<'
```

```text
Failed to load module script
```

```text
MIME type text/html is not executable
```

Кроме того, monitoring увидит успешный HTTP `200` вместо реального `404`, что усложнит диагностику сломанного deploy.

Пример конфигурации для Vite SPA:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    include /etc/nginx/mime.types;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/css
        text/plain
        application/javascript
        application/json
        application/xml
        image/svg+xml;

    location = /index.html {
        add_header Cache-Control "no-cache";
    }

    location = /config.js {
        add_header Cache-Control "no-store";
    }

    location = /service-worker.js {
        add_header Cache-Control "no-cache";
    }

    location ^~ /assets/ {
        try_files $uri =404;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Конфигурацию нужно адаптировать под реальный output сборщика.

Например, Service Worker может называться:

```text
sw.js
```

а assets могут находиться не только в:

```text
/assets/
```

но и в других каталогах.

Директива:

```nginx
root /usr/share/nginx/html;
```

задаёт корневой каталог.

Для URL:

```text
/assets/app.a84f31.js
```

Nginx проверяет файл:

```text
/usr/share/nginx/html/assets/app.a84f31.js
```

`include /etc/nginx/mime.types` подключает таблицу расширений и Content-Type.

Например:

```text
.html → text/html
.css  → text/css
.js   → application/javascript
.svg  → image/svg+xml
```

Во многих стандартных конфигурациях Nginx этот файл уже подключён на уровне `http`. Его не нужно повторно включать, если MIME types уже наследуются из общей конфигурации.

Nginx сначала выбирает `location`.

Exact location:

```nginx
location = /index.html
```

совпадает только с точным URL `/index.html`.

Prefix location:

```nginx
location /assets/
```

обрабатывает URL, начинающиеся с `/assets/`.

Модификатор:

```nginx
location ^~ /assets/
```

сообщает, что после выбора этого prefix location не нужно искать совпадающий regular-expression location.

В простой конфигурации без regex это не обязательно, но помогает защитить каталог assets при дальнейшем расширении файла.

В `location /assets/` используется:

```nginx
try_files $uri =404;
```

Nginx проверяет существование запрошенного файла.

Если файл отсутствует, возвращается настоящий:

```http
404 Not Found
```

Fallback на HTML здесь отсутствует намеренно.

В основном location:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

Nginx проверяет варианты по порядку.

Сначала:

```nginx
$uri
```

проверяет реальный файл.

Например:

```text
/favicon.ico
/robots.txt
/image.png
```

Затем:

```nginx
$uri/
```

проверяет реальный каталог.

Если приложение не раздаёт физических каталогов и это поведение не требуется, конфигурацию иногда упрощают:

```nginx
try_files $uri /index.html;
```

Последний аргумент:

```nginx
/index.html
```

выполняет внутренний переход на основной HTML.

После внутреннего перехода Nginx снова выбирает подходящий `location`, поэтому для ответа применяется exact location:

```nginx
location = /index.html {
    add_header Cache-Control "no-cache";
}
```

В результате client route получает HTML с политикой кэширования HTML, а не с политикой исходного URL.

API нужно отделить от SPA fallback:

```nginx
location ^~ /api/ {
    proxy_pass http://backend;
}
```

Если backend вернул:

```http
404 Not Found
```

Nginx не должен заменять этот ответ на `index.html`.

То же относится к:

- uploads;
- WebSocket endpoint;
- health checks;
- metrics;
- runtime config;
- Service Worker;
- статическим assets.

Политику HTTP cache выбирают по изменяемости ресурса.

`index.html` является указателем на текущую версию приложения.

Например:

```html
<script
  type="module"
  src="/assets/app.a84f31.js"
></script>
```

После нового build имя может измениться:

```html
<script
  type="module"
  src="/assets/app.b91c20.js"
></script>
```

Если браузер долго использует старый `index.html`, он продолжит запрашивать старые chunks.

Поэтому HTML обычно отдают с:

```http
Cache-Control: no-cache
```

`no-cache` не означает, что ответ вообще нельзя хранить.

Он означает:

```text
ответ можно сохранить,
но перед повторным использованием нужно проверить свежесть
```

Nginx для статических файлов обычно может использовать validators:

```text
ETag
Last-Modified
```

Браузер отправляет условный запрос:

```http
If-None-Match: "..."
```

или:

```http
If-Modified-Since: ...
```

Если файл не изменился, сервер может вернуть:

```http
304 Not Modified
```

без повторной передачи body.

`no-store` означает другое:

```text
не сохранять ответ в HTTP cache
```

Для обычного публичного `index.html` это часто излишне.

`no-store` применяют, когда ответ:

- содержит чувствительные данные;
- не должен оставаться в browser cache;
- формируется персонально;
- имеет соответствующую модель угроз.

Для статической SPA `index.html` обычно не должен содержать пользовательские секреты или персональные данные.

JavaScript и CSS с настоящим content hash в имени можно кэшировать надолго:

```text
app.a84f31.js
styles.92d8c1.css
```

Пример:

```http
Cache-Control: public, max-age=31536000, immutable
```

`max-age=31536000` разрешает использовать ответ примерно год без обращения к origin.

`immutable` сообщает, что содержимое URL не изменится в течение freshness lifetime.

Это безопасно только при выполнении двух условий:

1. Имя действительно зависит от содержимого.
2. Файл под старым URL никогда не перезаписывается другим содержимым.

При изменении файла должен появляться новый URL:

```text
app.a84f31.js
→
app.b91c20.js
```

Нельзя отдавать:

```text
/app.js
```

с годовым immutable cache, если при каждом deploy содержимое `/app.js` меняется.

Не все файлы frontend имеют content hash.

Отдельной политики могут требовать:

- `index.html`;
- `config.js`;
- `manifest.webmanifest`;
- `service-worker.js`;
- `robots.txt`;
- `favicon.ico`;
- source maps;
- runtime-generated files.

Runtime config с постоянным URL:

```text
/config.js
```

может меняться без нового frontend image.

Если приложение должно получать актуальное значение при каждой загрузке, можно использовать:

```http
Cache-Control: no-store
```

Если допустимо хранение с обязательной проверкой:

```http
Cache-Control: no-cache
```

Service Worker script с постоянным именем также не должен получать долгий immutable cache.

Обычно используют:

```http
Cache-Control: no-cache
```

Браузер применяет отдельный алгоритм проверки обновлений Service Worker, но длительная freshness-политика для стабильного URL способна усложнить предсказуемое обновление самого worker и его импортов.

При использовании Service Worker нужно помнить, что он может перехватить запрос раньше обычного обращения к сети:

```text
страница
→ Service Worker
→ Cache API
→ HTTP cache
→ origin/CDN
```

Поэтому исправление Nginx-конфигурации не гарантирует, что уже открытая PWA сразу получит новый ответ.

Нужно отдельно проверить:

- активную версию worker;
- waiting worker;
- Cache Storage;
- update strategy;
- момент перезагрузки clients;
- удаление старых cache names.

Политика origin должна быть согласована с CDN.

Browser cache и CDN — разные уровни.

Директива:

```text
max-age
```

задаёт freshness прежде всего для browser cache и других caches.

Для shared cache можно использовать:

```text
s-maxage
```

Например:

```http
Cache-Control: public, max-age=0, s-maxage=60, must-revalidate
```

означает, что браузер должен проверять ответ сразу, а CDN может считать его свежим 60 секунд.

Но такая политика означает, что после deploy CDN способен ещё некоторое время отдавать предыдущий HTML.

Поэтому команда должна согласовать:

- origin headers;
- CDN TTL;
- purge/invalidation;
- stale serving;
- момент переключения релиза.

CDN не должен продолжать долго хранить старый HTML при уже удалённых старых assets.

Одновременно не следует без необходимости очищать immutable hashed assets: их URL уникальны, и старые версии могут быть нужны открытым вкладкам.

Нужно проверять фактические response headers через:

```bash
curl -I https://example.com/
```

```bash
curl -I https://example.com/assets/app.a84f31.js
```

а не только читать Nginx config.

Заголовки могут быть изменены:

- Nginx;
- ingress;
- reverse proxy;
- object storage;
- CDN;
- Service Worker.

Следует избегать нескольких противоречащих друг другу политик:

```text
Expires
Cache-Control
CDN rules
Service Worker cache strategy
```

Конечное поведение определяет совокупность всех уровней.

Правильные cache headers не исправляют неатомарный deploy.

Опасный сценарий:

```text
1. Удалили старые chunks.
2. Начали загружать новые chunks.
3. Опубликовали новый index.html.
```

Между шагами пользователь может получить смешанную версию.

Другой сценарий:

```text
старая вкладка уже открыта
→ пользователь позже открывает lazy route
→ runtime запрашивает старый chunk
→ файл уже удалён
→ ChunkLoadError
```

При атомарном deploy новую версию сначала публикуют полностью:

```text
/releases/42/
```

Затем проверяют:

- наличие HTML;
- наличие chunks;
- корректные MIME types;
- cache headers;
- client route fallback.

Только после этого одним переключением делают версию активной:

```text
current → /releases/42/
```

Или переключают:

- load balancer;
- container image;
- CDN origin;
- object storage release prefix.

Старые hashed assets сохраняют дольше, чем потенциально живут:

- старый HTML;
- browser cache;
- CDN cache;
- открытые вкладки;
- Service Worker cache.

Новый HTML публикуют только после того, как все файлы, на которые он ссылается, уже доступны.

Сжатие уменьшает объём передаваемых текстовых ресурсов.

Для динамического gzip:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
```

`gzip_types` перечисляет дополнительные MIME types.

`text/html` Nginx обычно умеет сжимать при включённом gzip без дополнительного перечисления.

Обычно полезно сжимать:

- HTML;
- CSS;
- JavaScript;
- JSON;
- XML;
- SVG;
- plain text.

Повторное gzip обычно почти не помогает для уже сжатых форматов:

- JPEG;
- PNG;
- WebP;
- AVIF;
- MP4;
- WOFF2;
- архивов.

Если build заранее создаёт:

```text
app.js.gz
```

Nginx с поддерживаемым модулем может отдавать его через:

```nginx
gzip_static on;
```

Brotli может выполняться:

- CDN;
- отдельным Nginx-модулем;
- другим reverse proxy.

Для сжатого ответа должны быть корректными:

```text
Content-Type
Content-Encoding
Vary: Accept-Encoding
```

`gzip_vary on` добавляет:

```http
Vary: Accept-Encoding
```

Это помогает shared cache различать gzip- и identity-варианты ответа.

Путь production-сборки должен совпадать с адресом публикации.

Если SPA публикуется в корне:

```text
https://example.com/
```

Vite обычно использует:

```ts
base: "/"
```

Если приложение публикуется под:

```text
https://example.com/admin/
```

нужно согласовать:

- Vite `base`;
- Webpack `publicPath`;
- router basename;
- Nginx locations;
- fallback URL;
- ссылки на manifest и Service Worker.

Например, для Vite:

```ts
export default defineConfig({
  base: "/admin/",
});
```

Для React Router:

```tsx
<BrowserRouter basename="/admin">
  <App />
</BrowserRouter>
```

Nginx fallback должен вести на HTML того же приложения:

```nginx
location /admin/ {
    try_files $uri $uri/ /admin/index.html;
}
```

Assets также должны запрашиваться внутри правильного пути:

```text
/admin/assets/app.a84f31.js
```

Если приложение собрано для `/`, браузер может запросить:

```text
/assets/app.a84f31.js
```

вместо:

```text
/admin/assets/app.a84f31.js
```

и получить `404` либо файлы другого приложения.

При проксировании API важно учитывать семантику `proxy_pass`.

Например:

```nginx
location /api/ {
    proxy_pass http://backend;
}
```

обычно сохраняет исходный URI:

```text
/api/users
→
http://backend/api/users
```

Вариант с завершающим `/`:

```nginx
location /api/ {
    proxy_pass http://backend/;
}
```

заменяет совпавший prefix:

```text
/api/users
→
http://backend/users
```

Эту разницу нужно выбирать осознанно.

При proxy также обычно передают контекст исходного запроса:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

Для WebSocket дополнительно настраивают upgrade headers.

Reverse proxy того же origin может избавить браузер от cross-origin CORS-сценария, но не отменяет:

- authentication;
- authorization;
- CSRF-защиту;
- проверку входных данных;
- ограничения API.

Конфигурацию проверяют в несколько этапов.

Сначала синтаксис:

```bash
nginx -t
```

Затем запускают реальный image или server и проверяют HTTP-поведение.

Минимальный smoke-набор:

```text
GET /
→ 200 + text/html

GET /orders/42
→ 200 + text/html

GET /assets/existing.js
→ 200 + JavaScript MIME + immutable cache

GET /assets/missing.js
→ 404

GET /config.js
→ ожидаемая cache policy

GET /api/missing
→ API 404, не index.html
```

Дополнительно проверяют:

- gzip или Brotli;
- `Vary`;
- ETag/revalidation;
- Service Worker script;
- subpath;
- response через CDN;
- старую открытую вкладку после нового deploy.

Главный принцип:

```text
client route
→ index.html

реальный asset
→ файл

отсутствующий asset
→ 404

API
→ backend response

HTML
→ быстро проверять свежесть

hashed asset
→ долго кэшировать

deploy
→ публиковать атомарно
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему обновление страницы на <code>/profile</code> возвращает <code>404</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При переходе внутри приложения client router изменяет URL через History API и показывает новый экран без загрузки отдельного HTML-файла:

```text
/ → /profile
```

При reload браузер уже отправляет серверу прямой запрос:

```http
GET /profile
```

Nginx пытается найти физический путь `/profile`.

Если его нет и SPA fallback не настроен, сервер возвращает `404`.

Конфигурация:

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

возвращает основной HTML, после чего client router читает `/profile` и показывает нужный экран.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя возвращать <code>index.html</code> для отсутствующего JavaScript chunk?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер запросил JavaScript:

```text
/assets/app-missing.js
```

но получил HTML:

```html
<!doctype html>
```

со статусом `200`.

В зависимости от типа script браузер может сообщить:

```text
Unexpected token '<'
```

```text
MIME type text/html
```

```text
Failed to load module script
```

Кроме того, HTTP monitoring не увидит настоящий `404`.

Поэтому каталог assets отделяют:

```nginx
location ^~ /assets/ {
    try_files $uri =404;
}
```

Если файл отсутствует, ошибка должна быть честной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>index.html</code> не кэшируют на год?</strong></summary>

<dl>
<dd>
<h2></h2>

`index.html` содержит ссылки на текущую версию chunks.

Старый HTML может ссылаться на:

```text
app.old-hash.js
```

тогда как новый release использует:

```text
app.new-hash.js
```

При годовом freshness lifetime браузер может долго не проверять HTML и продолжать запускать старую версию.

Для HTML обычно применяют:

```http
Cache-Control: no-cache
```

или небольшой `max-age` с обязательной revalidation.

Долгий cache оставляют для content-hashed assets, а не для указателя на текущий release.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>no-cache</code> отличается от <code>no-store</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`no-cache` разрешает сохранить ответ, но требует проверить его свежесть перед повторным использованием.

Проверка может использовать:

```text
ETag
Last-Modified
```

и завершиться ответом:

```http
304 Not Modified
```

`no-store` запрещает сохранять ответ в HTTP cache.

Кратко:

```text
no-cache
→ хранить можно, использовать без проверки нельзя

no-store
→ хранить нельзя
```

Для публичного `index.html` обычно достаточно `no-cache`.

`no-store` используют для чувствительных или строго одноразовых ответов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему JS и CSS с хешем в имени можно кэшировать надолго?</strong></summary>

<dl>
<dd>
<h2></h2>

Content hash зависит от содержимого файла:

```text
app.a84f31.js
```

При изменении кода появляется другой URL:

```text
app.b91c20.js
```

Старый URL продолжает обозначать старое неизменное содержимое.

Поэтому для него можно использовать:

```http
Cache-Control: public, max-age=31536000, immutable
```

Это работает только при настоящем content hash.

Если сервер перезаписывает:

```text
app.a84f31.js
```

другим содержимым, гарантия нарушается, а браузеры и CDN продолжат использовать старый response.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как кэшировать <code>config.js</code>, manifest и Service Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Runtime config с постоянным именем может меняться независимо от frontend bundle.

Для него обычно выбирают:

```http
Cache-Control: no-store
```

или:

```http
Cache-Control: no-cache
```

в зависимости от допустимости хранения.

`manifest.webmanifest` также часто имеет постоянный URL, поэтому для него используют короткий срок или revalidation.

Service Worker script не следует отдавать с годовым immutable cache.

Обычно используют:

```http
Cache-Control: no-cache
```

чтобы обновления проверялись предсказуемо.

Если Service Worker импортирует дополнительные scripts, нужно учитывать их URL и политику обновления отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем хранить assets предыдущих версий после deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользователь мог открыть страницу до deploy.

Позже он открывает lazy route, и runtime старой вкладки запрашивает:

```text
settings.old-hash.js
```

Если файл уже удалён, возникает `ChunkLoadError`.

Старый HTML также может оставаться:

- в browser cache;
- в CDN;
- в Service Worker Cache Storage;
- в открытой вкладке.

Поэтому hashed assets предыдущих релизов хранят с запасом.

Их можно безопасно хранить долго, потому что уникальный URL не конфликтует с новой версией.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое атомарный deploy статической SPA?</strong></summary>

<dl>
<dd>
<h2></h2>

При атомарном deploy пользователю не показывается частично опубликованная версия.

Сначала новый release полностью размещают отдельно:

```text
/releases/42/
```

Затем проверяют:

- `index.html`;
- наличие всех chunks;
- cache headers;
- client route fallback;
- основные HTTP-запросы.

После этого одним переключением новая директория становится активной.

Например:

```text
current → /releases/42/
```

Предыдущая версия остаётся доступной для rollback и старых вкладок.

Перезапись файлов активного каталога по одному не является атомарной и может временно создать смесь нескольких версий.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как CDN влияет на cache headers?</strong></summary>

<dl>
<dd>
<h2></h2>

CDN является shared cache между пользователем и origin.

Он может:

- соблюдать origin `Cache-Control`;
- применять собственный TTL;
- использовать `s-maxage`;
- отдавать stale response;
- переопределять заголовки;
- требовать явный purge.

Например:

```http
Cache-Control: public, max-age=0, s-maxage=60
```

может заставить браузер проверять ответ сразу, но разрешить CDN хранить его 60 секунд.

После deploy нужно понимать, когда CDN перестанет отдавать старый HTML.

Фактический ответ проверяют через CDN URL, а не только напрямую у origin.

Hashed assets обычно не требуют purge, потому что новая версия использует новый URL.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что ломается при неверном <code>base</code> или <code>publicPath</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

HTML и runtime bundler формируют неправильные URL для:

- JavaScript;
- CSS;
- шрифтов;
- изображений;
- динамических imports;
- Service Worker.

Приложение может работать локально в `/`, но быть опубликовано в:

```text
/admin/
```

При неверной конфигурации браузер запросит:

```text
/assets/app.js
```

вместо:

```text
/admin/assets/app.js
```

Нужно согласовать:

- Vite `base`;
- Webpack `publicPath`;
- router basename;
- Nginx fallback;
- путь публикации assets.

Проверку выполняют production-сборкой по реальному subpath.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему после исправления Nginx пользователь всё равно видит старую версию?</strong></summary>

<dl>
<dd>
<h2></h2>

Ответ может приходить не из текущей конфигурации origin.

Возможные источники:

- browser HTTP cache;
- CDN;
- Service Worker;
- Cache API;
- старая открытая вкладка;
- другой container или instance;
- ещё не завершившийся rollout.

Service Worker способен вернуть старый response, вообще не обращаясь к Nginx.

Нужно проверить:

- вкладку Network;
- отметку Service Worker;
- response headers;
- Cache Storage;
- текущий release ID;
- active/waiting worker;
- CDN cache status.

Принудительный `skipWaiting()` без согласованного reload способен смешать старый JavaScript страницы с новой версией worker.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем Nginx может проксировать <code>/api</code> на backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер обращается к тому же origin:

```text
https://example.com/api/orders
```

а Nginx перенаправляет запрос внутреннему backend.

Это:

- упрощает frontend URL;
- скрывает внутренний адрес сервиса;
- часто исключает cross-origin CORS-сценарий;
- централизует TLS и routing.

Но reverse proxy не отменяет:

- аутентификацию;
- авторизацию;
- CSRF-защиту;
- rate limits;
- backend validation.

API должен иметь отдельный `location`, чтобы его ошибки не превращались в SPA fallback.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем отличаются варианты <code>proxy_pass</code> с завершающим <code>/</code> и без него?</strong></summary>

<dl>
<dd>
<h2></h2>

В конфигурации:

```nginx
location /api/ {
    proxy_pass http://backend;
}
```

исходный URI обычно сохраняется:

```text
/api/users
→
http://backend/api/users
```

Если написать:

```nginx
location /api/ {
    proxy_pass http://backend/;
}
```

совпавший prefix заменяется:

```text
/api/users
→
http://backend/users
```

Неправильный вариант приводит к:

- двойному `/api`;
- неожиданному удалению prefix;
- backend `404`;
- несовпадению маршрутов.

Поведение нужно проверить реальным запросом и upstream logs.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить Nginx-конфигурацию до выпуска?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала проверяют синтаксис:

```bash
nginx -t
```

Затем запускают реальный image и выполняют HTTP smoke tests.

Нужно проверить:

```text
/
→ HTML

/client-route
→ HTML

/assets/existing.js
→ JavaScript и immutable cache

/assets/missing.js
→ 404

/config.js
→ правильная cache policy

/api/missing
→ API 404

gzip request
→ Content-Encoding и Vary
```

Полезно использовать:

```bash
curl -I http://localhost/
```

```bash
curl -I http://localhost/assets/app.js
```

Для проверки body и Content-Type применяют обычный `curl`, browser Network panel или автоматический smoke test.

Проверка только открытого TCP-порта не подтверждает, что SPA routes, MIME types и cache headers настроены правильно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Настройка |
| --- | --- |
| Прямой вход на client route | Fallback на `index.html` |
| Отсутствующий chunk | Отдельный `location` и честный `404` |
| Актуальная версия | Revalidation для HTML |
| Быстрая повторная загрузка | Долгий immutable cache для файлов с хешем |
| Runtime config | `no-store` или обязательная revalidation |
| Service Worker script | Отдельная короткая cache policy |
| Публикация под `/admin/` | Совпадающие `base`, basename и Nginx fallback |
| API того же origin | Reverse proxy с отдельным `location` |
| CDN | Согласованные origin headers, TTL и purge |
| PWA | Отдельный жизненный цикл Service Worker cache |
| Новый релиз | Атомарная публикация и сохранение старых chunks |
| Проверка image | HTTP smoke test маршрутов, assets и headers |

## Связанные темы

- [04 Docker-сборка frontend-приложения](<./04 Docker-сборка frontend-приложения.md>)
- [09 Проверка production-сборки](<../Tooling/09 Проверка production-сборки.md>)
- [08 Сетевая производительность и кеширование](<../Performance/08 Сетевая производительность и кеширование.md>)
- [07 Service Worker и стратегии кеширования](<../Browser Internals/07 Service Worker и стратегии кеширования.md>)

## Источники

- [Nginx: try_files](https://nginx.org/en/docs/http/ngx_http_core_module.html#try_files)
- [Nginx: Headers module](https://nginx.org/en/docs/http/ngx_http_headers_module.html)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
- [Vite: Building for production](https://vite.dev/guide/build.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Docker-сборка frontend-приложения](<./04 Docker-сборка frontend-приложения.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Переменные окружения и secrets в CI CD →](<./06 Переменные окружения и secrets в CI CD.md>)
<!-- CARD-NAV-BOTTOM:END -->
