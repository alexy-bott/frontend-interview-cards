# 09 iframe sandbox security

<!-- CARD-NAV-TOP:START -->
[← 08 Script defer async module preload](<./08 Script defer async module preload.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Shadow DOM Web Components slots →](<./10 Shadow DOM Web Components slots.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое `iframe` и какие нюансы безопасности у него есть?

<details>
<summary><strong>Показать ответ</strong></summary>

`<iframe>` встраивает в страницу отдельный HTML-документ. У него собственные `window`, DOM, навигация и загрузка ресурсов. Его origin - источник, определяемый протоколом, доменом и портом URL, - может совпадать с origin родителя или отличаться от него. В `iframe` часто помещают карты, видео, платёжные формы, документы, внешние виджеты и изолированный пользовательский контент.

Главное отличие от обычного компонента в том, что содержимое `iframe` не входит в DOM родителя. Если документы cross-origin, то есть имеют разный origin, same-origin policy (политика ограничения доступа между разными origin) запрещает им читать DOM и JavaScript-состояние друг друга. Сам факт встраивания не даёт родителю доступ к чужому документу.

Для контролируемого общения между окнами используют `postMessage`. Отправитель указывает точный `targetOrigin`, а получатель проверяет `event.origin`, при необходимости `event.source` и структуру `event.data`. Сообщение считается внешними данными: перед использованием его нужно валидировать, как ответ API.

Атрибут `sandbox` без значений включает строгий набор ограничений: блокирует скрипты, отправку форм, всплывающие окна и ряд навигаций, а документ получает непрозрачный origin вместо своего обычного origin. Токены `allow-scripts`, `allow-forms`, `allow-popups`, `allow-same-origin` снимают отдельные ограничения. Это список исключений из запретов, а не перечень запретов, поэтому добавляют только необходимые токены.

Комбинация `allow-scripts` и `allow-same-origin` особенно опасна, если встроенный документ имеет тот же origin, что и родитель. Скрипт снова получает same-origin-доступ, может добраться до элемента `iframe`, удалить `sandbox` и после перезагрузки уйти от ограничений. Недоверенный HTML безопаснее размещать на отдельном origin и давать ему минимальный sandbox.

Атрибут `allow` задаёт Permissions Policy (политику разрешений) - какие возможности браузера в принципе доступны документу, например камера, микрофон или полноэкранный режим. Он не отменяет запрос разрешения у пользователя. `referrerpolicy` управляет содержимым заголовка `Referer`, `loading="lazy"` откладывает загрузку `iframe` за пределами первого экрана, а понятный `title` помогает пользователю скринридера различать встроенные документы.

Отдельный риск - clickjacking: чужой сайт может попытаться встроить вашу страницу в `iframe` и обманом заставить пользователя кликнуть. От этого защищаются через CSP `frame-ancestors` или старый `X-Frame-Options`.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Можно ли читать DOM cross-origin iframe?</summary>

Нет. Политика same-origin запрещает родительской странице читать DOM, cookie, браузерные хранилища и JavaScript-состояние `iframe` другого origin. Можно общаться через `postMessage`, если обе стороны это поддерживают.

</details>

<details>
<summary><strong>Вопрос:</strong> Как безопасно общаться с iframe?</summary>

Через `postMessage`, указывая конкретный `targetOrigin`, а не `*`, если origin известен. Получатель проверяет `event.origin`, ожидаемое окно в `event.source` и структуру `event.data`. После проверки сообщение передают только тем операциям, которые разрешены протоколом взаимодействия.

</details>

<details>
<summary><strong>Вопрос:</strong> Что делает <code>sandbox</code>?</summary>

Включает набор ограничений для `iframe`. Отдельные возможности возвращаются через флаги вроде `allow-scripts`, `allow-forms`, `allow-popups`, `allow-same-origin`. По умолчанию `sandbox` лучше делать максимально строгим.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем опасно <code>allow-scripts allow-same-origin</code> вместе?</summary>

`allow-scripts` возвращает выполнение JavaScript, а `allow-same-origin` возвращает документу его обычный origin вместо непрозрачного. Для same-origin документа это может восстановить доступ к родителю и позволить скрипту удалить `sandbox`. Для недоверенного содержимого используют отдельный origin и выдают только необходимые разрешения.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем <code>sandbox</code> отличается от <code>allow</code>?</summary>

`sandbox` ограничивает выполнение скриптов, формы, навигацию, origin и другие базовые возможности встроенного документа. `allow` определяет верхнюю границу для отдельных возможностей браузера через Permissions Policy, например камеры или полноэкранного режима. Даже разрешённая камера всё равно может потребовать согласия пользователя.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое clickjacking?</summary>

Это атака, при которой важную страницу помещают в прозрачный или замаскированный `iframe` и подставляют её элементы под ожидаемый клик пользователя. Сервер защищаемой страницы должен запретить нежелательное встраивание директивой CSP `frame-ancestors`; `X-Frame-Options` остаётся более старым и менее гибким заголовком.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем CSP <code>frame-src</code> отличается от <code>frame-ancestors</code>?</summary>

`frame-src` ограничивает, какие источники текущая страница может загружать в `<iframe>`. `frame-ancestors` задаётся защищаемой страницей и определяет, какие родительские страницы имеют право встроить её. От clickjacking защищает именно `frame-ancestors`.

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Платёжная форма | Изоляция, разрешения, безопасный `postMessage` |
| Видео/карта | `loading="lazy"`, размеры, разрешённые возможности |
| Предпросмотр HTML | Строгий `sandbox` |
| Виджет партнёра | Проверка origin и схемы сообщений |
| Защита админки | CSP `frame-ancestors 'none'` |

## Связанные темы

- [41 postMessage BroadcastChannel](<../JavaScript/41 postMessage BroadcastChannel.md>)
- [06 CSP security headers clickjacking](<../Security/06 CSP security headers clickjacking.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)
- [07 Images responsive media alt lazy loading](<./07 Images responsive media alt lazy loading.md>)

## Источники

- [MDN: iframe](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)
- [MDN: postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [MDN: iframe sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe#sandbox)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Script defer async module preload](<./08 Script defer async module preload.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Shadow DOM Web Components slots →](<./10 Shadow DOM Web Components slots.md>)
<!-- CARD-NAV-BOTTOM:END -->
