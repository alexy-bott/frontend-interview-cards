# Nginx static serving SPA fallback cache headers

<!-- CARD-NAV-TOP:START -->
[← 04 Docker для frontend multi-stage build](<./04 Docker для frontend multi-stage build.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Env variables secrets build-time runtime →](<./06 Env variables secrets build-time runtime.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как настроить Nginx для раздачи frontend SPA? Что важно в SPA fallback и cache headers?**

<h2></h2>

<br>
<dl>
<dd>

После production-сборки статическая SPA состоит из `index.html`, JavaScript- и CSS-файлов, изображений и шрифтов. Nginx сопоставляет URL с файлами внутри `root`, определяет `Content-Type`, применяет сжатие и заголовки кэша. Клиентский router начинает работать только после загрузки JavaScript, поэтому первый HTTP-запрос всё равно обрабатывает сервер.

Если пользователь открывает `/orders/42` напрямую, физического файла с таким путём обычно нет. SPA fallback - возврат основного HTML для клиентского маршрута - отдаёт `index.html`, после чего router показывает нужный экран. При этом fallback нельзя безусловно применять к любому отсутствующему URL. Запрос `/assets/app-missing.js` должен вернуть `404`, а не HTML со статусом `200`, иначе браузер попытается выполнить HTML как JavaScript и покажет ошибку MIME-типа или синтаксиса. API также выделяют отдельным `location`.

Пример нужно адаптировать к каталогам конкретного сборщика:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    include /etc/nginx/mime.types;

    location = /index.html {
        add_header Cache-Control "no-cache";
    }

    location /assets/ {
        try_files $uri =404;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

`try_files` проверяет существование файла по порядку. В `location /` он сначала отдаёт реальный файл или каталог, а затем использует `/index.html` как внутренний fallback. Отдельный `location /assets/` не позволяет скрыть ошибку публикации части сборки (`chunk`) под HTML-ответом.

Политику кэша разделяют по изменяемости. `index.html` содержит ссылки на актуальные имена файлов и должен быстро узнавать о новой версии. `Cache-Control: no-cache` не запрещает хранение: браузер может сохранить ответ, но перед повторным использованием обязан проверить его у сервера. Если HTML вообще нельзя хранить, используют `no-store`, но это лишает преимуществ кэша и обычно не требуется.

Файл с хешем содержимого (`content hash`) в имени, например `app.a84f31.js`, не меняет содержимое под тем же URL. Его можно отдавать с большим `max-age` и `immutable`: новая сборка создаст новое имя. Файлы без хеша, runtime config и service worker требуют отдельной короткой политики. Заголовки исходного сервера (`origin`) должны согласовываться с CDN, иначе CDN может переопределить срок или продолжить хранить старый ответ.

Даже правильные заголовки не исправляют неатомарный deploy. Если сначала удалить старые chunks, а потом опубликовать новый HTML, открытая вкладка или закэшированный HTML запросит исчезнувший файл. Версии публикуют атомарно, переключая каталог или релиз, а старые файлы с хешем содержимого хранят дольше максимального срока жизни HTML и активных вкладок.

Сжатие уменьшает передачу текстовых файлов. Nginx может сжимать ответы через gzip или отдавать заранее созданные `.gz` файлы через модуль `gzip_static`; Brotli требует отдельной поддержки Nginx или CDN. Изображения JPEG, PNG и WebP уже сжаты, поэтому повторное gzip обычно не помогает. Для каждого варианта сохраняют корректные `Content-Type`, `Content-Encoding` и `Vary: Accept-Encoding`.

Путь сборки должен совпадать с адресом публикации. В Vite параметр `base`, а в Webpack `publicPath` влияют на URL chunks и ресурсов. Если приложение доступно под `/admin/`, но собрано для `/`, браузер запросит файлы не по тому адресу. Для перехода между версиями также важно, чтобы динамически загружаемые chunks имели уникальные имена.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему обновление страницы на <code>/profile</code> возвращает <code>404</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Переход внутри SPA обработал клиентский router и не обращался к серверу за документом `/profile`. При обновлении браузер делает такой запрос напрямую, а Nginx пытается найти файл. `try_files $uri $uri/ /index.html` возвращает оболочку SPA, после чего router восстанавливает маршрут.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя возвращать <code>index.html</code> для отсутствующего JavaScript chunk?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер ожидает JavaScript, но получает HTML со статусом `200`. В результате появляется ошибка MIME-типа, `Unexpected token '<'` или отказ загрузки модуля, а мониторинг не видит честный `404`. Каталог файлов с хешем выделяют отдельно и завершают `try_files $uri =404`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>index.html</code> не кэшируют на год?</strong></summary>

<dl>
<dd>
<h2></h2>

Он является указателем на текущую версию chunks. Старый HTML может ссылаться на удалённые файлы или старую конфигурацию. Обычно его разрешают хранить только с обязательной revalidation - проверкой свежести - либо задают короткий срок.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>no-cache</code> отличается от <code>no-store</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`no-cache` разрешает сохранить ответ, но требует подтвердить его актуальность перед повторным использованием, например через `ETag` и условный запрос. `no-store` запрещает хранить ответ в HTTP-кэше. Для `index.html` часто достаточно `no-cache`; `no-store` нужен для чувствительных ответов или отдельной модели угроз.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему JS и CSS с хешем в имени можно кэшировать надолго?</strong></summary>

<dl>
<dd>
<h2></h2>

Хеш в имени зависит от содержимого. При изменении кода создаётся другой URL, а содержимое старого URL остаётся прежним. Директива `immutable` сообщает браузеру, что в пределах `max-age` повторная проверка не нужна. Это работает только при реальном content hash и запрете перезаписывать файл другим содержимым.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем хранить assets предыдущих версий после deploy?</strong></summary>

<dl>
<dd>
<h2></h2>

Пользователь мог открыть страницу до релиза, а динамический import запросить chunk позже. CDN или браузер также может держать прежний HTML. Если старый файл уже удалён, приложение сломается. Версионированные assets хранят с запасом, а новый релиз публикуют до переключения HTML.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что ломается при неверном <code>base</code> или <code>publicPath</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

HTML и runtime-код сборщика формируют неправильные URL для JavaScript, CSS, шрифтов или динамических imports. Приложение может открыться локально в корне, но получить `404` при публикации в `/admin/` или на CDN. Значение проверяют production-сборкой в том же базовом пути.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему после исправления Nginx пользователь всё равно видит старую версию?</strong></summary>

<dl>
<dd>
<h2></h2>

Service worker имеет собственный Cache Storage и может перехватывать запросы раньше сети. Нужно проверить активную версию worker, стратегию обновления, очистку старых cache names и момент перезагрузки вкладки. Принудительное `skipWaiting` без согласования может смешать старый интерфейс с новым runtime.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем Nginx может проксировать <code>/api</code> на backend?</strong></summary>

<dl>
<dd>
<h2></h2>

Браузер обращается к тому же origin, а Nginx перенаправляет запрос внутреннему сервису. Это упрощает адреса и часто исключает необходимость CORS между frontend и API, но не отменяет серверную аутентификацию и авторизацию. Proxy должен корректно передавать host, IP, протокол, cookies, timeout и WebSocket upgrade, если он используется.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить Nginx-конфигурацию до выпуска?</strong></summary>

<dl>
<dd>
<h2></h2>

`nginx -t` проверяет синтаксис. Затем image запускают и делают HTTP-проверки: `/` и клиентский маршрут возвращают HTML, реальный asset - правильный MIME и cache header, отсутствующий asset - `404`, а сжатие и API proxy работают ожидаемо. Smoke test должен проверять поведение, а не только открытый TCP-порт.

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
| Публикация под `/admin/` | Совпадающий Vite `base` или Webpack `publicPath` |
| API того же origin | Reverse proxy с корректными headers и timeout |
| PWA | Отдельный жизненный цикл service worker cache |

## Связанные темы

- [04 Docker для frontend multi-stage build](<./04 Docker для frontend multi-stage build.md>)
- [09 Production build assets hashing base publicPath](<../Tooling/09 Production build assets hashing base publicPath.md>)
- [08 Network caching CDN compression HTTP cache](<../Performance/08 Network caching CDN compression HTTP cache.md>)
- [07 Service Worker PWA lifecycle cache network](<../Browser Internals/07 Service Worker PWA lifecycle cache network.md>)

## Источники

- [Nginx: try_files](https://nginx.org/en/docs/http/ngx_http_core_module.html#try_files)
- [Nginx: Headers module](https://nginx.org/en/docs/http/ngx_http_headers_module.html)
- [MDN: HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
- [Vite: Building for production](https://vite.dev/guide/build.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Docker для frontend multi-stage build](<./04 Docker для frontend multi-stage build.md>) · [↑ DevOps](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Env variables secrets build-time runtime →](<./06 Env variables secrets build-time runtime.md>)
<!-- CARD-NAV-BOTTOM:END -->
