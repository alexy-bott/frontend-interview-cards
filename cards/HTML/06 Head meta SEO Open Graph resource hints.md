# Head meta SEO Open Graph resource hints

<!-- CARD-NAV-TOP:START -->
[← 05 HTML формы labels validation disabled readonly](<./05 HTML формы labels validation disabled readonly.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Images responsive media alt lazy loading →](<./07 Images responsive media alt lazy loading.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что важно размещать в `<head>`: meta-теги, SEO, Open Graph и подсказки загрузки ресурсов?**

<h2></h2>

<br>
<dl>
<dd>

`<head>` содержит метаданные документа и связи с внешними ресурсами. Они не являются основным содержимым страницы, но нужны браузеру, поисковым системам и сервисам, которые создают предпросмотр ссылки.

Минимальная основа — объявление кодировки `<meta charset="utf-8">`, уникальный `<title>` и настройка мобильной области просмотра `<meta name="viewport" content="width=device-width, initial-scale=1">`.

Объявление кодировки желательно размещать в начале `<head>`, чтобы браузер определил её до разбора большого объёма текста. `title` отображается во вкладке и может стать заголовком поискового результата. Поисковая система при этом может заменить его собственным вариантом.

`viewport` сообщает мобильному браузеру, что ширина раскладки должна соответствовать ширине устройства. Без него адаптивная страница может выглядеть как уменьшенная версия страницы для настольного экрана.

Для поисковой выдачи добавляют содержательное `meta description`, а при нескольких URL с одинаковым или близким контентом — `<link rel="canonical">` с адресом предпочтительной версии.

`meta robots` управляет индексированием страницы и переходом по ссылкам для поисковых роботов, которые поддерживают эти инструкции. Он не ограничивает доступ к странице и не является механизмом безопасности.

`title`, description и canonical помогают поисковой системе интерпретировать страницу, но не гарантируют высокую позицию. Поисковая система также может сформировать собственный description из содержимого страницы.

Метаданные Open Graph описывают, как страница выглядит при отправке ссылки в социальных сетях и мессенджерах: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`.

Для `og:url` и `og:image` обычно используют абсолютные URL, чтобы внешний сервис мог однозначно получить ресурс.

Подсказки загрузки решают разные задачи:

- `preload` инициирует раннюю загрузку ресурса, который точно понадобится текущей странице, например критичного шрифта или главного изображения первого экрана. Он только загружает ресурс, а применяет его обычный `<link>`, CSS, `<img>` или JavaScript;
- `modulepreload` заранее загружает JavaScript-модуль и подготавливает его к последующему выполнению;
- `preconnect` заранее выполняет DNS-поиск и устанавливает TCP/TLS-соединение с важным внешним origin, то есть сочетанием протокола, домена и порта;
- `dns-prefetch` заранее узнаёт IP-адрес домена, но не устанавливает полное соединение;
- `prefetch` загружает с низким приоритетом ресурс, который может понадобиться при следующем переходе.

Реальный приоритет `preload` зависит от назначения ресурса, атрибута `as`, других настроек и решений браузера. Для `preconnect` указывают origin вроде `https://cdn.example.com`, а не полный URL конкретного файла.

Эти подсказки используют точечно. Лишние соединения и ранние загрузки занимают пропускную способность и могут задержать действительно критичные ресурсы.

В Next.js 14 с App Router метаданные обычно задают через Metadata API: статический объект `metadata`, функцию `generateMetadata` для данных конкретного маршрута и специальные файлы вроде `opengraph-image`.

Эти API доступны в Server Components. Экспорты во вложенных `layout` и `page` формируют итоговые метаданные маршрута.

Объекты metadata объединяются поверхностно: если дочерний маршрут задаёт вложенное поле, например `openGraph`, оно может заменить соответствующий объект родительского маршрута целиком. Поэтому общие вложенные значения при необходимости выносят и переиспользуют явно.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Зачем нужен <code>meta viewport</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он сообщает мобильному браузеру, как рассчитывать область просмотра и начальный масштаб страницы.

Без корректного `viewport` браузер может использовать широкую виртуальную область и отображать адаптивную вёрстку как уменьшенную страницу для настольного экрана.

Распространённая настройка:

```html
<meta
  name="viewport"
  content="width=device-width, initial-scale=1"
/>
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое canonical link?</strong></summary>

<dl>
<dd>
<h2></h2>

`<link rel="canonical" href="...">` указывает предпочтительный URL документа.

Он нужен, когда одинаковый или почти одинаковый контент доступен, например, по URL с фильтрами, рекламными параметрами или разным написанием адреса.

Это подсказка поисковой системе для объединения дублей, а не перенаправление пользователя. Canonical должен указывать на действительно эквивалентную основную версию страницы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда <code>preload</code> может навредить?</strong></summary>

<dl>
<dd>
<h2></h2>

Если заранее загружать много ресурсов или ресурс, который не понадобится сразу, браузер потратит сеть на неверно выбранную загрузку.

У `preload` должны совпадать URL, тип назначения в `as` и режим CORS с последующим реальным запросом. Иначе браузер может не переиспользовать результат и скачать файл повторно.

Особенно часто это заметно у шрифтов, для которых обычно нужен атрибут `crossorigin`, даже когда файл расположен на том же origin:

```html
<link
  rel="preload"
  href="/fonts/app.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>
```

Браузер также может предупредить, если предварительно загруженный ресурс вскоре не был использован.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>preload</code> отличается от <code>prefetch</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`preload` сообщает, что ресурс точно нужен текущей странице и его загрузку следует начать раньше.

`prefetch` предполагает, что ресурс может понадобиться позже, например после следующего перехода. Поэтому браузер обычно загружает его с более низким приоритетом и вправе полностью проигнорировать подсказку.

`preload` не выполняет и не применяет ресурс автоматически. Он только помещает его в cache для последующего запроса с совместимыми параметрами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Open Graph улучшает SEO?</strong></summary>

<dl>
<dd>
<h2></h2>

Его основная задача — управлять карточкой ссылки в социальных сетях и мессенджерах.

Корректный предпросмотр может косвенно увеличить количество переходов, но Open Graph не заменяет `title`, основной контент, canonical, доступность страницы для индексирования и остальные факторы поиска.

Следует проверять, что изображение доступно внешним сервисам, имеет подходящий размер и не требует авторизации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как это связано с Next.js?</strong></summary>

<dl>
<dd>
<h2></h2>

В App Router статические значения задают объектом `metadata`, а зависящие от `params` или загруженных данных — функцией `generateMetadata`.

Next.js преобразует эти значения в элементы `<head>` и поддерживает файловые соглашения для favicon, robots, sitemap и Open Graph images.

Начиная с Next.js 14 настройку viewport не помещают в объект `metadata`: для неё используют отдельный экспорт `viewport` или функцию `generateViewport`.

`metadata` и `generateMetadata` экспортируют только из Server Components. Дочерние сегменты маршрута могут дополнять или заменять метаданные родительских layout.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Элемент | Зачем |
| --- | --- |
| `title` | Название вкладки и возможный заголовок поисковой выдачи |
| `meta viewport` | Адаптивность на мобильных устройствах |
| `meta description` | Возможное описание страницы в поисковой выдаче |
| `og:image` | Предпросмотр при отправке ссылки |
| `preconnect` | Быстрее подключиться к важному внешнему origin |
| `preload` | Рано загрузить критичный ресурс текущей страницы |
| `prefetch` | Подготовить вероятный ресурс следующей страницы |

## Связанные темы

- [09 Dynamic routes params searchParams metadata](<../Next.js/09 Dynamic routes params searchParams metadata.md>)
- [Performance: Core Web Vitals](<../Performance/02 Core Web Vitals LCP INP CLS.md>)
- [05 Images fonts resource priority preload lazy loading](<../Performance/05 Images fonts resource priority preload lazy loading.md>)
- [13 Image Font Link Script и оптимизация](<../Next.js/13 Image Font Link Script и оптимизация.md>)

## Источники

- [MDN: What is in the head](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/Webpage_metadata)
- [MDN: rel=preload](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel/preload)
- [MDN: Speculative loading](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Speculative_loading)
- [web.dev: Preconnect and DNS-prefetch](https://web.dev/articles/preconnect-and-dns-prefetch)
- [Next.js docs: Metadata and OG images](https://nextjs.org/docs/app/getting-started/metadata-and-og-images)
- [Next.js docs: generateMetadata](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 HTML формы labels validation disabled readonly](<./05 HTML формы labels validation disabled readonly.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Images responsive media alt lazy loading →](<./07 Images responsive media alt lazy loading.md>)
<!-- CARD-NAV-BOTTOM:END -->
