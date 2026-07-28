# Что происходит после ввода URL

<!-- CARD-NAV-TOP:START -->
[↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 Rendering pipeline reflow repaint composite →](<./02 Rendering pipeline reflow repaint composite.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что происходит в браузере после того, как пользователь ввёл URL и нажал Enter?**

<h2></h2>

<br>
<dl>
<dd>

Браузер начинает навигацию: разбирает адрес, получает документ из кэша, Service Worker или сети, передаёт его процессу рендеринга и превращает HTML, CSS и JavaScript в интерактивную страницу. Конкретная архитектура различается между браузерами; ниже описана общая последовательность с названиями процессов Chromium.

1. **Browser process принимает ввод.** Адресная строка относится к интерфейсу браузера, а не к JavaScript текущей страницы. Browser process определяет, введён URL или поисковый запрос, и начинает навигацию. Если открытая страница зарегистрировала `beforeunload`, браузер может сначала запросить у неё подтверждение ухода.

2. **Браузер разбирает URL.** В `https://example.com/products?page=2#reviews` часть `https` называется **scheme**, или схемой, `example.com` - host (хост), `/products` - path (путь), `?page=2` - query (строка запроса), `#reviews` - fragment (фрагмент). Fragment не входит в HTTP-запрос: браузер использует его для перехода к части документа или клиентской маршрутизации. Политика HSTS может ещё до сетевого запроса заменить `http` на `https` для известного домена.

3. **Определяется источник ответа.** Если URL контролирует активный Service Worker, событие `fetch` позволяет ему вернуть ответ из Cache API или обратиться в сеть. Сетевой запрос, в свою очередь, может использовать HTTP-кэш по правилам заголовков кэширования. `bfcache` здесь не является обычным сетевым кэшем: он восстанавливает целую страницу при переходах Back/Forward. Предварительный рендер (prerender) используется только тогда, когда браузер заранее подготовил именно эту страницу.

4. **Выполняется DNS lookup.** Браузер и операционная система сначала проверяют свои DNS-кэши, а при отсутствии записи обращаются к DNS-resolver - службе разрешения доменных имён. Результатом становятся один или несколько IP-адресов сервера либо балансировщика, к которым можно установить соединение.

5. **Устанавливается защищённое соединение.** HTTP/1.1 и HTTP/2 обычно работают поверх TCP, а HTTP/3 - поверх QUIC, использующего UDP. Для HTTPS выполняется TLS handshake: сервер предъявляет сертификат, браузер проверяет доверенную цепочку, доменное имя и срок действия, после чего стороны получают ключи защищённого соединения. В QUIC согласование TLS встроено в установку соединения.

6. **Отправляется HTTP-запрос.** Для обычного ввода URL это, как правило, `GET`. В request target, то есть адрес ресурса внутри HTTP-запроса, входят path и query; host передаётся отдельно в заголовке `Host` для HTTP/1.1 или псевдозаголовке `:authority` для HTTP/2 и HTTP/3. Браузер также добавляет подходящие заголовки и cookie. Fragment после `#` не отправляется.

7. **Сервер возвращает HTTP-ответ.** В нём есть код статуса (status code), заголовки (headers) и тело (body). Статус сообщает результат, `Content-Type` - тип содержимого, `Content-Encoding` - сжатие, а `Cache-Control` - правила кэширования. При ответе `3xx` с `Location` браузер начинает переход по новому адресу. Если ответ является HTML-документом, браузер выбирает или запускает renderer process, то есть процесс рендеринга, и передаёт ему поток данных. В Chromium разделение сайтов по renderer-процессам является частью Site Isolation; browser process и renderer общаются через IPC - межпроцессные сообщения.

8. **Renderer process разбирает документ.** Ему не нужно ждать всего body: HTML parser, или HTML-парсер, читает поступающий поток и строит DOM - объектное дерево документа. Preload scanner, или сканер предварительной загрузки, параллельно обнаруживает ссылки на CSS, JavaScript, шрифты и изображения, чтобы запросить их раньше.

9. **CSS и JavaScript влияют на парсинг и отображение.** CSS преобразуется в CSSOM - объектную модель таблиц стилей. CSS обычно не останавливает построение DOM, но блокирует первый рендер до получения необходимых стилей. Обычный `<script>` без `defer`, `async` или `type="module"` останавливает HTML parser на время загрузки и выполнения. `defer` загружается параллельно, выполняется после разбора HTML в порядке документа и до `DOMContentLoaded`. `async` выполняется сразу после готовности файла, поэтому порядок нескольких таких скриптов не гарантирован. Модули по умолчанию ведут себя подобно `defer` и сначала загружают граф импортов.

10. **Браузер формирует кадр.** Style calculation вычисляет итоговые стили, layout - размеры и координаты элементов, paint - список команд рисования. Затем rasterization превращает команды в пиксели отдельных плиток или слоёв, а composite собирает их в кадр и передаёт его для вывода на экран. Не каждое изменение проходит все стадии: например, анимация `transform` уже подготовленного слоя может потребовать только compositing.

После первого кадра работа не заканчивается. JavaScript-задачи, сетевые ответы, пользовательский ввод, анимации и изменения DOM могут запускать новые вычисления и кадры. В SSR-приложении HTML может быть виден до загрузки клиентского JavaScript. Во время hydration React сопоставляет своё дерево с серверной разметкой и подключает логику, необходимую для интерактивности.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое URL и какие части URL реально уходят на сервер?</strong></summary>

<dl>
<dd>
<h2></h2>

URL - адрес ресурса. При HTTP-запросе path и query входят в request target, host передаётся заголовком `Host` или `:authority`, а scheme определяет способ подключения. Fragment после `#` остаётся в браузере. Например, сервер получит `/products?page=2`, но не `#reviews`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое DNS lookup?</strong></summary>

<dl>
<dd>
<h2></h2>

Это получение IP-адресов по доменному имени. Сначала проверяются кэши браузера и операционной системы, затем системный resolver при необходимости обращается к DNS-серверам. Записи имеют TTL - срок, в течение которого результат можно использовать без нового поиска. Один домен может вернуть несколько IPv4- и IPv6-адресов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое TLS handshake?</strong></summary>

<dl>
<dd>
<h2></h2>

Это согласование защищённого HTTPS-соединения. Сервер предъявляет сертификат, а браузер проверяет доменное имя, срок действия и цепочку до доверенного центра сертификации. Затем стороны согласуют ключевой материал и получают симметричные ключи, которыми шифруют дальнейший обмен. TLS защищает данные в пути, но не делает сам сервер или его содержимое безопасными.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое HTTP request и HTTP response?</strong></summary>

<dl>
<dd>
<h2></h2>

HTTP request, или запрос, содержит метод, адрес операции, заголовки и при необходимости тело. HTTP response, или ответ, содержит код статуса, заголовки и тело: например, HTML, JSON или изображение. Для ввода URL браузер обычно отправляет `GET` без тела, а для отправки формы или API-вызова метод и тело могут быть другими.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при redirect?</strong></summary>

<dl>
<dd>
<h2></h2>

Сервер отвечает кодом `3xx` и заголовком `Location`, после чего браузер разрешает новый URL и выполняет следующий запрос. Цепочка может включать смену домена, пути или протокола; слишком много переходов увеличивает задержку, а цикл заканчивается ошибкой. Для запросов не-`GET` важно различие статусов: `307` и `308` сохраняют метод и тело, тогда как `301` и `302` в браузерной практике могут привести к повторному `GET`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда подключается Service Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Если для origin уже установлен активный Service Worker и URL входит в его scope, браузер может передать навигационный запрос в обработчик `fetch`. Тот возвращает сетевой ответ, запись из Cache API или offline-страницу. Регистрация сама по себе недостаточна: при первой загрузке Service Worker обычно ещё устанавливается и начинает контролировать страницы только после активации и следующей подходящей навигации. Метод `clients.claim()` позволяет активному worker взять под контроль уже открытые подходящие страницы, но не перехватывает навигацию, которая началась до его установки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем DOM отличается от HTML?</strong></summary>

<dl>
<dd>
<h2></h2>

HTML - текст документа, который пришёл с сервера. DOM - дерево объектов, построенное браузером из этого HTML. JavaScript работает именно с DOM, а не с исходной строкой HTML.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое CSSOM?</strong></summary>

<dl>
<dd>
<h2></h2>

CSSOM - объектная модель загруженных таблиц стилей и их правил. Браузер сопоставляет CSS-селекторы с DOM-элементами и вычисляет итоговые значения свойств. После этого можно определить, какие визуальные объекты участвуют в layout и как они выглядят.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему обычный script может блокировать загрузку страницы?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный script может изменить ещё не достроенный документ, в том числе через `document.write`. Поэтому HTML parser останавливается, пока скрипт не загрузится и не выполнится. `defer` и модули откладывают выполнение до завершения разбора HTML, а `async` выполняется сразу после готовности и при выполнении тоже ненадолго останавливает parser.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое layout, paint и composite?</strong></summary>

<dl>
<dd>
<h2></h2>

Layout рассчитывает геометрию: размеры и координаты. Paint создаёт упорядоченные команды для текста, фонов, границ и теней. Rasterization превращает эти команды в пиксели, а composite объединяет подготовленные слои в итоговый кадр. Браузер создаёт отдельные compositing layers не для каждого DOM-элемента, а по внутренним правилам и потребностям отображения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему HTML уже виден, но кнопки ещё не работают?</strong></summary>

<dl>
<dd>
<h2></h2>

Серверный HTML и CSS могут быть отрисованы раньше, чем загрузится и выполнится клиентский JavaScript. В React/Next.js hydration должна сопоставить React-дерево с этой разметкой и подключить клиентскую логику. До обработки нужной области действие может быть отложено или ещё не дать ожидаемого результата.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие процессы браузера участвуют в навигации?</strong></summary>

<dl>
<dd>
<h2></h2>

В модели Chromium browser process обслуживает адресную строку, историю и координирует навигацию; сетевой сервис выполняет DNS, соединения и HTTP; renderer process разбирает и выполняет содержимое страницы в ограниченной среде; GPU process участвует в выводе кадров. Процессы обмениваются IPC-сообщениями. Это устройство Chromium, а не обязательное требование веб-стандартов: другой браузер может распределять работу иначе.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно понимать |
| --- | --- |
| Маршрутизация SPA | Path, query и fragment могут управлять экраном без полной перезагрузки |
| SSR/Next.js | HTML приходит с сервера, интерактивность зависит от клиентского JavaScript и hydration |
| Service Worker/PWA | Ответ может прийти из Cache API через Service Worker, а не с сервера |
| Производительность | CSS, блокирующие скрипты, шрифты и изображения влияют на первое отображение |
| Ошибки загрузки | Ошибка DNS, TLS или соединения отличается от HTTP `404` или `500` |
| Безопасность | HTTPS, HSTS, cookie, CSP и CORS влияют на загрузку и выполнение ресурсов |

## Связанные темы

- [04 URL origin domain path query fragment](<../Web Basics/04 URL origin domain path query fragment.md>)
- [08 DNS TCP UDP HTTP2 basics](<../Web Basics/08 DNS TCP UDP HTTP2 basics.md>)
- [01 REST API и ресурсная модель](<../Web API/01 REST API и ресурсная модель.md>)
- [08 Script defer async module preload](<../HTML/08 Script defer async module preload.md>)
- [03 Critical rendering path render pipeline](<../Performance/03 Critical rendering path render pipeline.md>)
- [37 URL URLSearchParams History API](<../JavaScript/37 URL URLSearchParams History API.md>)
- [17 Hydration SSR и SSG](<../React/17 Hydration SSR и SSG.md>)
- [07 Service Worker PWA lifecycle cache network](<./07 Service Worker PWA lifecycle cache network.md>)

## Источники

- [MDN: What is a URL](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_URL)
- [MDN: How the web works](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works)
- [MDN: HTTP messages](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages)
- [web.dev: Critical rendering path](https://web.dev/articles/critical-rendering-path)
- [Chrome for Developers: Inside look at a modern web browser, part 1](https://developer.chrome.com/blog/inside-browser-part1)
- [Chrome for Developers: Inside look at a modern web browser, part 2](https://developer.chrome.com/blog/inside-browser-part2)
- [Chrome for Developers: Inside look at a modern web browser, part 3](https://developer.chrome.com/blog/inside-browser-part3)

---

<!-- CARD-NAV-BOTTOM:START -->
[↑ Browser Internals](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [02 Rendering pipeline reflow repaint composite →](<./02 Rendering pipeline reflow repaint composite.md>)
<!-- CARD-NAV-BOTTOM:END -->
