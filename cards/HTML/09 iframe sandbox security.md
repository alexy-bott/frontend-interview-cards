# iframe sandbox security

<!-- CARD-NAV-TOP:START -->
[← 08 Script defer async module preload](<./08 Script defer async module preload.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Shadow DOM Web Components slots →](<./10 Shadow DOM Web Components slots.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое `iframe` и какие нюансы безопасности у него есть?**

<h2></h2>

<br>
<dl>
<dd>

`<iframe>` встраивает в страницу отдельный HTML-документ и создаёт для него вложенный browsing context. У него собственные `window`, `document`, навигация и загрузка ресурсов. Его origin — источник, определяемый протоколом, доменом и портом URL, — может совпадать с origin родителя или отличаться от него.

В `iframe` часто помещают карты, видео, платёжные формы, документы, внешние виджеты и изолированный пользовательский контент.

Главное отличие от обычного компонента в том, что содержимое `iframe` не входит в DOM родителя. Если документы имеют одинаковый origin и не ограничены sandbox, они могут обращаться к DOM и JavaScript-состоянию друг друга.

Если документы cross-origin, same-origin policy запрещает прямое чтение чужого `document`, DOM, хранилищ и большинства JavaScript-свойств. Родитель может иметь ссылку на `contentWindow`, но это не даёт ему доступ к содержимому чужого документа.

Для контролируемого общения между окнами используют `postMessage`. Отправитель указывает точный `targetOrigin`, а получатель проверяет `event.origin`, ожидаемое окно в `event.source` и структуру `event.data`.

Сообщение считается внешними данными: перед использованием его нужно валидировать, как ответ API, и не передавать без проверки в опасные операции вроде вставки HTML или выполнения команды.

Атрибут `sandbox` без значений включает строгий набор ограничений: блокирует скрипты, отправку форм, всплывающие окна и ряд навигаций. Без токена `allow-same-origin` встроенный документ получает opaque origin для проверок same-origin вместо своего обычного origin.

Токены `allow-scripts`, `allow-forms`, `allow-popups`, `allow-same-origin` снимают отдельные ограничения. Это список исключений из запретов, а не перечень запретов, поэтому добавляют только действительно необходимые токены.

Комбинация `allow-scripts` и `allow-same-origin` особенно опасна, если встроенный документ имеет тот же origin, что и родитель. Скрипт получает возможность обратиться к DOM родителя, удалить атрибут `sandbox` у своего `iframe` и после перезагрузки уйти от ограничений.

Недоверенный HTML безопаснее размещать на отдельном origin и давать ему минимальный sandbox. Сам sandbox не исправляет уязвимости содержимого и не должен быть единственной линией защиты.

Атрибут `allow` задаёт Permissions Policy — какие возможности браузера доступны документу, например камера, микрофон или полноэкранный режим. Он может дополнительно ограничить политику родителя, но не может вернуть возможность, уже запрещённую через HTTP-заголовок `Permissions-Policy`.

Разрешение возможности через `allow` также не отменяет запрос согласия пользователя, если он требуется браузером.

`referrerpolicy` управляет содержимым заголовка `Referer`, `loading="lazy"` позволяет отложить загрузку `iframe` за пределами первого экрана, а понятный `title` помогает пользователю скринридера различать встроенные документы.

Отдельный риск — clickjacking: злоумышленник может встроить вашу страницу в прозрачный или замаскированный `iframe` и обманом заставить пользователя взаимодействовать с ней.

От нежелательного встраивания защищаются через директиву CSP `frame-ancestors` в HTTP-заголовке ответа. Для совместимости также может использоваться более старый и менее гибкий заголовок `X-Frame-Options`.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Можно ли читать DOM cross-origin iframe?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Same-origin policy запрещает родительской странице читать `document`, DOM, `document.cookie`, Web Storage и JavaScript-состояние `iframe` другого origin.

Родитель может получить ссылку на `iframe.contentWindow`, но доступные действия с cross-origin окном сильно ограничены.

Общаться можно через `postMessage`, если обе стороны поддерживают согласованный протокол сообщений.

<h2></h2>
</dd>
</dl>

</details>

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
<summary><strong>Что делает <code>sandbox</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он включает набор ограничений для встроенного документа.

Пустой атрибут применяет все sandbox-ограничения:

```html
<iframe src="/preview" sandbox></iframe>
```

Отдельные возможности возвращаются через токены вроде `allow-scripts`, `allow-forms`, `allow-popups` и `allow-same-origin`.

По умолчанию sandbox делают максимально строгим и снимают только те ограничения, без которых сценарий действительно не работает.

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

- [41 postMessage BroadcastChannel](<../JavaScript/41 postMessage BroadcastChannel.md>)
- [06 CSP security headers clickjacking](<../Security/06 CSP security headers clickjacking.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)
- [11 postMessage iframe open redirect tabnabbing](<../Security/11 postMessage iframe open redirect tabnabbing.md>)

## Источники

- [MDN: iframe](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)
- [MDN: postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [MDN: iframe sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe#sandbox)
- [MDN: iframe srcdoc](https://developer.mozilla.org/en-US/docs/Web/API/HTMLIFrameElement/srcdoc)
- [MDN: Permissions Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Permissions_Policy)
- [MDN: CSP frame-ancestors](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 08 Script defer async module preload](<./08 Script defer async module preload.md>) · [↑ HTML](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [10 Shadow DOM Web Components slots →](<./10 Shadow DOM Web Components slots.md>)
<!-- CARD-NAV-BOTTOM:END -->
