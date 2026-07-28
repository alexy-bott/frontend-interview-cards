# postMessage iframe open redirect tabnabbing

<!-- CARD-NAV-TOP:START -->
[← 10 JWT sessions OAuth authorization basics](<./10 JWT sessions OAuth authorization basics.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как безопасно работать с `postMessage`, iframe, внешними перенаправлениями и ссылками, открывающими новую вкладку?**

<h2></h2>

<br>
<dl>
<dd>

`window.postMessage` позволяет документам из разных origins обмениваться данными, несмотря на same-origin policy. Механизм используют OAuth popup, платежный iframe, встроенный внешний виджет и связь между приложением и контейнером. Безопасность не возникает автоматически: отправитель ограничивает получателя, а получатель проверяет источник и содержимое каждого сообщения.

При отправке указывают точный `targetOrigin`, например `https://pay.example`, а не `*`. Браузер доставит сообщение только если окно-получатель в этот момент имеет ожидаемый origin.

Получатель проверяет:

1. `event.origin` по точному allowlist схемы, host и port.
2. `event.source`, чтобы подтвердить конкретное окно или iframe, с которым установлен процесс обмена.
3. Тип и структуру `event.data` с помощью проверки во время выполнения или валидатора схемы (schema validator).
4. Допустимость действия в текущем состоянии: например, нельзя дважды подтвердить уже завершенный платеж.

```ts
const paymentOrigin = 'https://pay.example';
const paymentWindow = iframe.contentWindow;

paymentWindow?.postMessage(
  { type: 'payment:status:request', orderId },
  paymentOrigin,
);

window.addEventListener('message', (event) => {
  if (event.origin !== paymentOrigin) return;
  if (event.source !== paymentWindow) return;
  if (!isPaymentResult(event.data)) return;

  applyPaymentResult(event.data);
});
```

Проверенное сообщение все равно остается данными. Строку из `event.data` не передают в `innerHTML`, `eval` или URL без соответствующей проверки. `postMessage` может стать source для DOM XSS, если доверие к отправителю ошибочно или его данные используются как код.

Iframe ограничивают атрибутом `sandbox` и выдают только необходимые возможности. Пустой `sandbox` максимально ограничивает вложенный документ; флаги вроде `allow-forms`, `allow-popups` и `allow-scripts` возвращают отдельные возможности. Сочетание `allow-scripts` и `allow-same-origin` особенно опасно для содержимого того же origin: такой документ может получить достаточно полномочий, чтобы снять `sandbox`. Для независимого виджета предпочтителен отдельный origin.

**Open redirect**, или открытое перенаправление, возникает, когда приложение принимает URL пользователя и без ограничений выполняет redirect. Ссылка на доверенный домен может отправить жертву на фишинговый сайт, а в процессе OAuth через перенаправление иногда утекают code или другие данные. Безопаснее принимать относительный внутренний path либо выбирать внешний адрес по точному allowlist после разбора через `URL`.

**Reverse tabnabbing** использует доступ новой вкладки к `window.opener`: открытая внешняя страница заменяет исходную вкладку фишинговой. Для недоверенных ссылок, открывающих новый контекст окна, применяют `rel="noopener"`; `noreferrer` дополнительно не передает `Referer`. Современные браузеры обычно трактуют `target="_blank"` как неявный `noopener`, но явный атрибут фиксирует намерение и поддерживает старые окружения и нестандартные способы открытия.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что такое <code>postMessage</code> и зачем он нужен?</strong></summary>

<dl>
<dd>
<h2></h2>

Same-origin policy не дает странице напрямую читать DOM другого origin. `postMessage` создает контролируемый канал: окно отправляет сериализуемые данные другому window object, а получатель обрабатывает событие `message`. Доступ к данным разрешает код получателя, поэтому обе стороны обязаны явно проверить контекст.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему опасно использовать <code>targetOrigin: '*'</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Ссылка на окно может сохранить тот же window object после навигации на другой сайт. `*` разрешает доставку независимо от текущего origin, и чувствительное сообщение может получить новая страница. Точный `targetOrigin` заставляет браузер проверить назначение в момент отправки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему проверки только <code>event.origin</code> недостаточно?</strong></summary>

<dl>
<dd>
<h2></h2>

На разрешенном origin может быть несколько окон, iframe или параллельных процессов, а доверенный сайт сам может содержать менее надежную страницу. `event.source` связывает сообщение с конкретным открытым popup или `iframe.contentWindow`. Идентификатор операции и текущее состояние дополнительно не позволяют применить правильное по форме сообщение к чужому процессу.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как правильно сравнивать <code>event.origin</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

С точным ожидаемым значением вида `https://pay.example` или с элементом небольшого allowlist. Нельзя проверять через `includes('example.com')`: `https://example.com.attacker.test` пройдет такую проверку. Если origins настраиваются динамически, их разбирают через `URL` и сравнивают схему, hostname и port по явным правилам.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем валидировать <code>event.data</code>, если origin доверенный?</strong></summary>

<dl>
<dd>
<h2></h2>

Доверенный отправитель может иметь баг, другую версию протокола или собственную компрометацию. Получатель не должен падать или выполнять произвольное действие из-за неизвестного `type`, отсутствующего поля или слишком большого значения. Проверка схемы превращает внешнее значение типа `unknown` в известную структуру до изменения state.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли использовать <code>JSON.stringify</code> для <code>postMessage</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно нет. API использует алгоритм структурированного клонирования (structured clone) и передает объекты, массивы и многие встроенные типы без ручной JSON-сериализации. Однако передаваемое значение все равно приходит во время выполнения и требует проверки. Алгоритм не поддерживает функции и DOM-узлы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как <code>postMessage</code> может привести к XSS?</strong></summary>

<dl>
<dd>
<h2></h2>

Если обработчик принимает сообщение от любого origin или без проверки вставляет `event.data.html` в `innerHTML`, атакующий превращает межоконный канал в source для DOM XSS. Защита включает точный origin и source, schema validation и безопасный sink, например `textContent` или обычный React render для текста.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает атрибут <code>sandbox</code> у iframe?</strong></summary>

<dl>
<dd>
<h2></h2>

Без флагов он помещает вложенный документ в уникальный origin и ограничивает scripts, forms, popups, навигацию родителя и другие возможности. Каждый `allow-*` возвращает конкретное право. Нужные флаги выбирают от сценария, а не начинают с полного набора разрешений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему сочетание <code>allow-scripts</code> и <code>allow-same-origin</code> опасно?</strong></summary>

<dl>
<dd>
<h2></h2>

Для iframe с содержимым того же origin scripts получают обычный origin и могут обращаться к родительскому DOM. Тогда вложенный код способен удалить свой атрибут `sandbox` или обойти ожидаемую изоляцию. Ненадежное активное содержимое размещают на отдельном origin и не выдают ему одновременно обе возможности без строгой причины.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем CSP <code>frame-src</code> и <code>frame-ancestors</code> связаны с iframe?</strong></summary>

<dl>
<dd>
<h2></h2>

`frame-src` ограничивает origins, которые текущая страница может загрузить во вложенный frame. `frame-ancestors` определяет, кто может встроить саму текущую страницу, и защищает ее от clickjacking. `sandbox` ограничивает возможности уже загруженного iframe, поэтому три механизма решают разные задачи.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое open redirect и чем он опасен?</strong></summary>

<dl>
<dd>
<h2></h2>

Endpoint или client route перенаправляет на адрес из `next`, `returnUrl` или похожего параметра без проверки. Атакующий создает ссылку на доверенный домен, которая ведет на фишинговый сайт. В процессе аутентификации открытый redirect также может участвовать в краже authorization response или обходе allowlist.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как безопасно обрабатывать <code>returnUrl</code> после login?</strong></summary>

<dl>
<dd>
<h2></h2>

Самый надежный вариант - принимать только внутренний относительный path, начинающийся с одного `/`, но не с `//`, и исключать служебные callback routes. Если нужны внешние адреса, сервер выбирает их из точного allowlist origins. Проверка `startsWith` по сырой строке недостаточна из-за разных представлений URL и пользовательской части адреса.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое reverse tabnabbing?</strong></summary>

<dl>
<dd>
<h2></h2>

Внешняя страница, открытая из приложения в новой вкладке, получает ссылку `window.opener` и пытается перенаправить исходную вкладку на поддельную форму входа. Пользователь возвращается и видит знакомую вкладку с другим адресом. `noopener` разрывает эту ссылку между вкладками.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>noopener</code> отличается от <code>noreferrer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`noopener` не предоставляет новой странице доступ к `window.opener`. `noreferrer` также скрывает адрес исходной страницы в HTTP `Referer` и в современных браузерах подразумевает поведение `noopener`. Если referrer нужен системе аналитики, но opener не нужен, достаточно `noopener`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли проверить, что ссылка начинается с <code>https://</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Это исключает часть опасных схем URL, но позволяет любой HTTPS-домен, включая фишинговый сайт. Правило зависит от назначения: для произвольной внешней ссылки проверяют безопасный протокол и показывают понятный адрес, а для перенаправления или привилегированной интеграции разрешают только точные origins и paths.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Безопасное решение |
| --- | --- |
| OAuth login через popup | Точные origins, проверка popup через `event.source`, `state` и закрытие процесса после одного ответа |
| Платежный виджет в iframe | Отдельный origin, минимальный `sandbox`, схема сообщений и ID текущей операции |
| Переход после login | Внутренний относительный path или точный allowlist адресов перенаправления |
| Ссылка на пользовательский сайт | Проверка протокола, `target="_blank"` и `rel="noopener noreferrer"` с учетом требований к `Referer` |
| Встроенное стороннее содержимое | CSP `frame-src`, iframe `sandbox` и ограниченный `Permissions-Policy` |

## Связанные темы

- [01 Frontend threat model](<./01 Frontend threat model.md>)
- [02 XSS reflected stored DOM React](<./02 XSS reflected stored DOM React.md>)
- [05 CORS same-origin preflight credentials](<./05 CORS same-origin preflight credentials.md>)
- [06 CSP security headers clickjacking](<./06 CSP security headers clickjacking.md>)
- [10 JWT sessions OAuth authorization basics](<./10 JWT sessions OAuth authorization basics.md>)

## Источники

- [WHATWG HTML: Cross-document messaging](https://html.spec.whatwg.org/multipage/web-messaging.html#web-messaging)
- [WHATWG HTML: The iframe element](https://html.spec.whatwg.org/multipage/iframe-embed-object.html#the-iframe-element)
- [OWASP: HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)
- [OWASP: Unvalidated Redirects and Forwards Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)
- [WHATWG HTML: Link type noopener](https://html.spec.whatwg.org/multipage/links.html#link-type-noopener)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 10 JWT sessions OAuth authorization basics](<./10 JWT sessions OAuth authorization basics.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
