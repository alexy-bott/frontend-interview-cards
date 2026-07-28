# 06 Head meta SEO Open Graph resource hints

<!-- CARD-NAV-TOP:START -->
[← 05 HTML формы labels validation disabled readonly](<./05 HTML формы labels validation disabled readonly.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Images responsive media alt lazy loading →](<./07 Images responsive media alt lazy loading.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Что важно размещать в `<head>`: meta-теги, SEO, Open Graph и подсказки загрузки ресурсов?

#### Ответ

`<head>` содержит сведения о документе и связи с внешними ресурсами. Они не являются основным содержимым страницы, но нужны браузеру, поисковым системам и сервисам, которые создают предпросмотр ссылки.

Минимальная основа - кодировка `<meta charset="utf-8">`, уникальный `<title>` и настройка мобильной области просмотра `<meta name="viewport" content="width=device-width, initial-scale=1">`. `title` отображается во вкладке и может стать заголовком поискового результата. `viewport` сообщает мобильному браузеру, что ширина раскладки должна соответствовать ширине устройства, иначе адаптивная страница может выглядеть как уменьшенная версия для настольного экрана.

Для поисковой выдачи добавляют содержательное `meta description`, а при нескольких URL с одинаковым контентом - `<link rel="canonical">` с адресом основной версии. `meta robots` управляет индексированием и переходом по ссылкам. Эти элементы помогают поисковой системе понять страницу, но сами по себе не гарантируют высокую позицию.

Метаданные Open Graph описывают, как страница выглядит при отправке ссылки в соцсетях и мессенджерах: `og:title`, `og:description`, `og:image`, `og:url`. Для продуктовых и контентных страниц это важно для предпросмотра ссылки.

Подсказки загрузки решают разные задачи:

- `preload` рано загружает ресурс, который точно понадобится текущей странице, например критичный шрифт или главное изображение первого экрана. Он только загружает ресурс, а применяет его обычный `<link>`, CSS, `<img>` или JavaScript;
- `modulepreload` заранее готовит JavaScript-модуль к использованию;
- `preconnect` заранее выполняет DNS-поиск и устанавливает TCP/TLS-соединение с важным внешним origin, то есть сочетанием протокола, домена и порта;
- `dns-prefetch` заранее узнаёт IP-адрес домена, но не устанавливает полное соединение;
- `prefetch` загружает с низким приоритетом ресурс, который может понадобиться при следующем переходе.

Эти подсказки используют точечно. Лишние соединения и ранние загрузки занимают пропускную способность и могут задержать действительно критичные ресурсы.

В Next.js 14 с App Router метаданные обычно задают через Metadata API: статический объект `metadata`, функцию `generateMetadata` для данных конкретного маршрута и специальные файлы вроде `opengraph-image`. Эти API доступны в Server Components. Экспорты во вложенных `layout` и `page` формируют итоговые метаданные маршрута, поэтому нужно учитывать их наследование и замещение.

#### Встречные вопросы

> [!followup] viewport
> **Вопрос:** Зачем нужен `meta viewport`?
>
> **Ответ:** Он говорит мобильному браузеру, как масштабировать страницу. Без корректного `viewport` адаптивная верстка может отображаться как уменьшенная версия страницы для настольного экрана.

> [!followup] Canonical
> **Вопрос:** Что такое canonical link?
>
> **Ответ:** `<link rel="canonical" href="...">` указывает предпочтительный URL документа. Он нужен, когда одинаковый или почти одинаковый контент доступен, например, по URL с фильтрами, рекламными параметрами или разным написанием адреса. Это подсказка поисковой системе для объединения дублей, а не перенаправление пользователя.

> [!followup] Preload
> **Вопрос:** Когда `preload` может навредить?
>
> **Ответ:** Если заранее загружать много ресурсов или ресурс, который не понадобится сразу, браузер потратит сеть на неверный приоритет. У `preload` должны совпадать URL, тип назначения в `as` и режим CORS с последующим реальным запросом. Иначе браузер может не переиспользовать результат и скачать файл повторно. Особенно часто это заметно у шрифтов, для которых обычно нужен `crossorigin`.

> [!followup] Preload prefetch
> **Вопрос:** Чем `preload` отличается от `prefetch`?
>
> **Ответ:** `preload` сообщает, что ресурс с высоким приоритетом нужен текущей странице. `prefetch` предполагает, что ресурс может понадобиться позже, например после следующего перехода, поэтому браузер загружает его с более низким приоритетом и вправе не выполнять подсказку.

> [!followup] Open Graph
> **Вопрос:** Open Graph улучшает SEO?
>
> **Ответ:** Его основная задача - управлять карточкой ссылки в социальных сетях и мессенджерах. Корректный предпросмотр может повысить число переходов, но Open Graph не заменяет `title`, основной контент, доступность страницы для индексирования и остальные факторы поиска.

> [!followup] Next metadata
> **Вопрос:** Как это связано с Next.js?
>
> **Ответ:** В App Router статические значения задают объектом `metadata`, а зависящие от `params` или загруженных данных - функцией `generateMetadata`. Next.js преобразует их в элементы документа. Начиная с Next.js 14 настройку viewport не помещают в объект `metadata`: для неё используют отдельный экспорт `viewport` или `generateViewport`.

#### Где это встречается во frontend

> [!context] Практика
> | Элемент | Зачем |
> | --- | --- |
> | `title` | Название вкладки и поисковой выдачи |
> | `meta viewport` | Адаптивность на мобильных устройствах |
> | `meta description` | Описание страницы |
> | `og:image` | Предпросмотр при отправке ссылки |
> | `preconnect` | Быстрее подключиться к важному источнику |
> | `preload` | Рано загрузить критичный ресурс |
> | `prefetch` | Подготовить вероятный ресурс следующей страницы |

#### Связанные темы

- Head meta и resource hints
- App Router
- [09 Dynamic routes params searchParams metadata](<../Next.js/09 Dynamic routes params searchParams metadata.md>)
- [Performance: Core Web Vitals](<../Performance/02 Core Web Vitals LCP INP CLS.md>)

#### Источники

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
