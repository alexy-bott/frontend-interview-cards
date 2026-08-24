# Безопасность iframe

<!-- CARD-NAV-TOP:START -->
[← 08 Загрузка скриптов в HTML](<./08 Загрузка скриптов в HTML.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Shadow DOM и Web Components →](<./10 Shadow DOM и Web Components.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое `iframe` и какие нюансы безопасности у него есть?**

<h2></h2>

<br>
<dl>
<dd>

`<iframe>` встраивает отдельный HTML-документ и создаёт для него вложенный browsing context со своими `window`, `document`, навигацией и загрузкой ресурсов. Его origin может совпадать с origin родителя или отличаться от него.

Если документы same-origin и sandbox не вводит дополнительное ограничение origin, страницы могут обращаться к доступному DOM и `Window` друг друга. Для cross-origin документов same-origin policy запрещает прямое чтение чужого `document`, DOM, хранилищ и большинства чувствительных JavaScript-свойств.

Когда двум окнам нужно взаимодействовать независимо от origin, используют `postMessage`. При таком обмене отправитель ограничивает получателя ожидаемым origin, когда он известен, а получатель проверяет отправителя и структуру сообщения. Данные из сообщения всё равно считаются внешним вводом и валидируются перед опасными операциями.

`sandbox` добавляет к встроенному документу набор ограничений. Пустой `sandbox` включает строгий режим, а токены `allow-*` снимают отдельные запреты, поэтому разрешения выдают по принципу минимально необходимого. Sandbox уменьшает возможности документа, но не исправляет уязвимости его кода и не превращает недоверенный HTML в безопасный.

Для недоверенного содержимого особенно важны отдельный origin и минимальный sandbox. Опасность конкретного набора разрешений зависит от origin документа и от того, какой код способен выполняться внутри iframe.

Атрибут `allow` задаёт container policy для Permissions Policy и может делегировать или дополнительно ограничивать отдельные browser features в пределах политики родителя. Он не может восстановить возможность, уже запрещённую у родителя, и не отменяет пользовательское разрешение, если оно требуется соответствующей API.

`referrerpolicy` управляет данными `Referer` для навигации iframe, `loading="lazy"` позволяет отложить его загрузку по lazy-loading правилам браузера, а понятный `title` помогает пользователям вспомогательных технологий различать встроенные документы.

Безопасность iframe работает и в обратную сторону: нужно контролировать не только возможности встроенного документа, но и то, кто имеет право встроить вашу собственную страницу. Это задаётся политикой ответа защищаемой страницы, а не sandbox на стороне embedder.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Как безопасно общаться с iframe?</strong></summary>

<dl>
<dd>
<h2></h2>

Через `postMessage`, указывая конкретный `targetOrigin`, а не `"*"`, если origin получателя известен.

Получатель проверяет:

- `event.origin` — origin отправителя;
- `event.source` — ожидаемое окно;
- `event.data` — тип, структуру и допустимые значения сообщения.

После проверки сообщение передают только тем операциям, которые разрешены протоколом взаимодействия. Нельзя считать данные безопасными только потому, что они пришли через `postMessage`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем опасно <code>allow-scripts allow-same-origin</code> вместе?</strong></summary>

<dl>
<dd>
<h2></h2>

`allow-scripts` возвращает выполнение JavaScript, а `allow-same-origin` не позволяет sandbox заменить обычный origin документа на opaque origin.

Если встроенный документ имеет тот же origin, что и родитель, эта комбинация может восстановить доступ к DOM родителя. Скрипт сможет найти свой элемент `iframe`, удалить у него атрибут `sandbox` и перезагрузить документ уже без ограничений.

Для недоверенного содержимого используют отдельный origin и выдают только необходимые разрешения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>sandbox</code> отличается от <code>allow</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`sandbox` ограничивает скрипты, формы, навигацию, origin, всплывающие окна и другие базовые возможности встроенного документа.

`allow` задаёт Permissions Policy для отдельных браузерных возможностей, например камеры, микрофона или полноэкранного режима.

Атрибут `allow` может только дополнительно ограничить разрешения, заданные политикой родительской страницы. Он не может включить возможность, которую родитель запретил через заголовок `Permissions-Policy`.

Даже разрешённая возможность может потребовать отдельного согласия пользователя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Безопасно ли передавать пользовательский HTML через <code>srcdoc</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет, если передавать непроверенную строку напрямую. `srcdoc` разбирает значение как полноценный HTML-документ, поэтому вредоносная разметка может стать источником XSS.

Без sandbox документ из `srcdoc` обычно имеет тот же origin, что и родитель, и способен получить доступ к его данным.

Для недоверенного HTML используют строгий sandbox без `allow-same-origin`, отдельный origin, проверенную очистку HTML и при возможности CSP с Trusted Types.

```html
<iframe
  sandbox
  title="Предпросмотр пользовательского документа"
></iframe>
```

Sandbox уменьшает последствия атаки, но не заменяет проверку и очистку входных данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое clickjacking?</strong></summary>

<dl>
<dd>
<h2></h2>

Это атака, при которой важную страницу помещают в прозрачный или замаскированный `iframe` и подставляют её элементы под ожидаемый клик пользователя.

Сервер защищаемой страницы должен запретить нежелательное встраивание директивой CSP `frame-ancestors`:

```http
Content-Security-Policy: frame-ancestors 'none'
```

`frame-ancestors` задаётся в HTTP-заголовке ответа, а не через `<meta>`.

`X-Frame-Options` остаётся более старым и менее гибким заголовком для ограничения встраивания.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем CSP <code>frame-src</code> отличается от <code>frame-ancestors</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`frame-src` ограничивает, какие источники текущая страница может загружать в `<iframe>`.

`frame-ancestors` задаётся защищаемой страницей и определяет, какие родительские документы имеют право встроить её.

От clickjacking защищает именно `frame-ancestors`, потому что он контролирует родителей защищаемой страницы.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что важно |
| --- | --- |
| Платёжная форма | Изоляция, разрешения, безопасный `postMessage` |
| Видео/карта | `loading="lazy"`, размеры, разрешённые возможности |
| Предпросмотр HTML | Строгий `sandbox`, проверка содержимого |
| Виджет партнёра | Проверка origin и схемы сообщений |
| Защита админки | CSP `frame-ancestors 'none'` |

## Связанные темы

- [41 Обмен сообщениями в браузере](<../JavaScript/41 Обмен сообщениями в браузере.md>)
- [06 CSP и защитные HTTP-заголовки](<../Security/06 CSP и защитные HTTP-заголовки.md>)
- [05 Same-origin policy и CORS](<../Security/05 Same-origin policy и CORS.md>)
- [11 Безопасность окон iframe и внешних ссылок](<../Security/11 Безопасность окон iframe и внешних ссылок.md>)

## Источники

- [MDN: iframe](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)
- [MDN: postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [MDN: iframe sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe#sandbox)
- [MDN: iframe srcdoc](https://developer.mozilla.org/en-US/docs/Web/API/HTMLIFrameElement/srcdoc)
- [MDN: Permissions Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Permissions_Policy)
- [MDN: CSP frame-ancestors](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors)
- [WHATWG HTML: The iframe element](https://html.spec.whatwg.org/multipage/iframe-embed-object.html#the-iframe-element)
- [W3C: Content Security Policy](https://www.w3.org/TR/CSP/)
- [W3C: Permissions Policy](https://www.w3.org/TR/permissions-policy/)
- [W3C: Trusted Types](https://www.w3.org/TR/trusted-types/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Загрузка скриптов в HTML](<./08 Загрузка скриптов в HTML.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Shadow DOM и Web Components →](<./10 Shadow DOM и Web Components.md>)
<!-- CARD-NAV-BOTTOM:END -->
