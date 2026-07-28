# 02 XSS reflected stored DOM React

<!-- CARD-NAV-TOP:START -->
[← 01 Frontend threat model](<./01 Frontend threat model.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 CSRF cookies SameSite tokens →](<./03 CSRF cookies SameSite tokens.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Что такое XSS, чем reflected, stored и DOM XSS отличаются и где React перестает защищать приложение?

<details>
<summary><strong>Показать ответ</strong></summary>

**XSS (Cross-Site Scripting)** - уязвимость, при которой данные атакующего становятся исполняемым HTML или JavaScript в origin доверенного приложения. Origin, или источник, определяется схемой, именем хоста и портом. Внедренный код получает возможности страницы: читает данные DOM и хранилищ браузера, отправляет запросы от имени пользователя, подменяет интерфейс и перехватывает введенные данные.

Названия reflected, stored и DOM описывают путь вредоносных данных:

| Вид | Откуда приходят вредоносные данные | Как они достигают браузера |
| --- | --- | --- |
| Reflected XSS | Query-параметр, форма или другой текущий запрос | Сервер сразу вставляет значение в HTML-ответ |
| Stored XSS | Комментарий, профиль, CMS или другой сохраненный контент | Сервер хранит значение и позже показывает одному или многим пользователям |
| DOM XSS | URL, `postMessage`, storage, API или DOM | Клиентский JavaScript передает значение в опасный DOM API |

Эти категории могут пересекаться: сохраненная на сервере строка способна вызвать DOM XSS, если клиент получит ее как данные и передаст в `innerHTML`.

Для анализа DOM XSS используют модель **source -> sink**. Source - источник данных, который может контролировать атакующий, например `location.search`, `location.hash`, `event.data`, `localStorage` или поле API. Sink - API, способный интерпретировать строку как HTML, JavaScript или опасный URL: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function` или строковый аргумент `setTimeout`.

React по умолчанию экранирует строковые значения в JSX. Значение `{comment}` становится текстом, поэтому символы `<` и `>` не превращаются в тег. Защита заканчивается, когда приложение обходит этот механизм: использует `dangerouslySetInnerHTML`, передает непроверенный URL, вызывает опасный DOM API через ref, подключает небезопасный Markdown/CMS renderer или доверяет стороннему компоненту.

```tsx
// Строка отображается как текст.
return <p>{comment}</p>;

// HTML будет разобран браузером. До этого нужна sanitization.
return <div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />;
```

**Контекстное экранирование** превращает управляющие символы в обычный текст для конкретного контекста: HTML-текст, атрибут, URL, CSS и JavaScript имеют разные правила. **Sanitization**, или очистка HTML, нужна, когда разметку действительно требуется сохранить. Проверенная библиотека разбирает HTML и оставляет только разрешенные теги, атрибуты и протоколы. Регулярное выражение не является полноценным синтаксическим анализатором HTML и легко пропускает обходы.

CSP и Trusted Types служат дополнительными слоями. CSP ограничивает источники скриптов и inline-код. Trusted Types может запретить передавать обычные строки в DOM XSS sinks без утвержденной policy. Они уменьшают последствия ошибки, но не заменяют безопасный вывод данных и sanitization.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Что атакующий получает при XSS?</summary>

Код выполняется в origin уязвимого приложения и может делать то, что доступно его JavaScript: читать страницу и незащищенное storage, вызывать same-origin API с сессией пользователя, менять реквизиты формы и отправлять введенные данные наружу. `HttpOnly` скроет cookie от чтения, но не запретит XSS-коду отправлять запросы через браузер пользователя.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем server XSS отличается от DOM XSS?</summary>

При server XSS небезопасная строка уже включена сервером в HTML-ответ. При DOM XSS сервер может вернуть безопасный документ, но клиентский JavaScript позже берет недоверенные данные и передает их в исполняемый sink. Reflected и stored описывают место появления данных, поэтому могут сочетаться с клиентским или серверным способом выполнения.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое source и sink?</summary>

Source - место получения потенциально недоверенных данных. Sink - операция, которая при неправильном значении меняет контекст с «данные» на «код или разметка». Уязвимость возникает не от самого `location.hash`, а от потока значения из него в `innerHTML`, `eval` или другой опасный sink без подходящей защиты.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему <code>textContent</code> безопаснее <code>innerHTML</code>?</summary>

`textContent` создает текст: строка `<img onerror=...>` останется видимыми символами. `innerHTML` запускает синтаксический анализатор HTML, создает элементы и обрабатывает атрибуты и URL. Если разметка не нужна, безопасный текстовый API устраняет целый класс ошибок.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему React защищает не от любого XSS?</summary>

React экранирует значения, которые вставляет как текст или обычные атрибуты, но не может определить намерение приложения во всех API. `dangerouslySetInnerHTML` явно передает строку HTML parser. Код через ref может вызвать `innerHTML`, сторонняя библиотека может использовать опасный sink, а URL требует отдельной проверки допустимого протокола и назначения.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда допустим <code>dangerouslySetInnerHTML</code>?</summary>

Когда продукт действительно должен отображать HTML, например ограниченный форматированный текст (rich text) из CMS, и содержимое прошло sanitization по явному allowlist. Очищенное значение желательно создавать в одном контролируемом модуле, тестировать на опасных конструкциях и не смешивать с необработанными строками после очистки.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем encoding отличается от sanitization?</summary>

Encoding, или экранирование, сохраняет всю строку как данные и заменяет управляющие символы безопасным представлением для конкретного контекста. Sanitization разбирает HTML и удаляет запрещенные части, сохраняя разрешенную разметку. Для обычного текста выбирают экранирование; sanitization нужна только при осознанной поддержке HTML.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему нельзя очищать HTML регулярным выражением?</summary>

HTML имеет сложный parser, разные пространства имен, поврежденную разметку, кодировки, URL и множество исполняемых контекстов. Браузер может разобрать строку иначе, чем ожидает регулярное выражение. Нужен sanitizer, который строит DOM и применяет проверенный allowlist с учетом поведения браузера.

</details>

<details>
<summary><strong>Вопрос:</strong> Почему URL может стать XSS-вектором?</summary>

URL в `href`, `src` или перенаправлении влияет не только на адрес. Опасный протокол вроде `javascript:` способен выполнить код в подходящем контексте, а `data:` может содержать активный документ. Для внешних ссылок проверяют протокол и, когда требуется, host по точному allowlist; значение строят через `URL`, а не проверяют подстрокой.

</details>

<details>
<summary><strong>Вопрос:</strong> Как безопасно отображать Markdown?</summary>

Нужно знать, разрешает ли обработчик Markdown встроенный HTML и какие расширения он поддерживает. Сам Markdown не гарантирует безопасность итогового HTML. Обычно raw HTML отключают либо результат пропускают через sanitizer, отдельно проверяют ссылки и изображения и безопасно настраивают открытие внешних вкладок.

</details>

<details>
<summary><strong>Вопрос:</strong> Возможен ли XSS при SSR React-приложения?</summary>

Да. React экранирует JSX, но серверный шаблон может небезопасно вставить начальное состояние приложения в `<script>`, HTML из CMS или значение в заголовок и URL. Сериализацию данных для script-контекста выполняют специализированным способом, не конкатенируют пользовательскую строку с HTML и применяют ту же контекстную модель, что на клиенте.

</details>

<details>
<summary><strong>Вопрос:</strong> Защищает ли CSP от XSS полностью?</summary>

Нет. Строгая CSP может заблокировать inline script и неизвестный источник, но слабый allowlist, `unsafe-inline`, разрешенный опасный скрипт или DOM-gadget позволяют обход. DOM-gadget - уже присутствующий код страницы, который передает контролируемые данные в опасный sink. CSP применяют как дополнительный слой после безопасных DOM API, экранирования и sanitization.

</details>

<details>
<summary><strong>Вопрос:</strong> Что дают Trusted Types?</summary>

При включенной директиве `require-trusted-types-for 'script'` поддерживающий браузер отклоняет обычные строки в известных injection sinks. Значение должно быть создано зарегистрированной policy, где централизуется sanitization или построение доверенного URL. Это помогает найти и перекрыть DOM XSS sinks, но policy, которая без проверки возвращает входную строку, уничтожает защиту.

</details>

## Где это встречается во frontend

| Сценарий | Безопасное направление |
| --- | --- |
| Показ поисковой строки из URL | Рендерить как JSX-текст, не через HTML |
| Форматированный текст из CMS | Sanitizer с allowlist перед `dangerouslySetInnerHTML` |
| Ссылка из API | Разобрать через `URL` и проверить допустимый протокол и host |
| Сообщение `postMessage` | Проверить `origin`, схему данных и не передавать строку в HTML sink |
| Начальное состояние при SSR | Использовать безопасную сериализацию для script-контекста |

## Связанные темы

- [06 CSP security headers clickjacking](<./06 CSP security headers clickjacking.md>)
- [04 Token storage cookies localStorage refresh access tokens](<./04 Token storage cookies localStorage refresh access tokens.md>)
- [11 postMessage iframe open redirect tabnabbing](<./11 postMessage iframe open redirect tabnabbing.md>)
- [01 Что такое React и зачем он нужен](<../React/01 Что такое React и зачем он нужен.md>)
- [45 DOM API innerHTML layout thrashing](<../JavaScript/45 DOM API innerHTML layout thrashing.md>)

## Источники

- [OWASP: Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP: DOM based XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
- [React: dangerously setting inner HTML](https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html)
- [W3C: Trusted Types](https://www.w3.org/TR/trusted-types/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Frontend threat model](<./01 Frontend threat model.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 CSRF cookies SameSite tokens →](<./03 CSRF cookies SameSite tokens.md>)
<!-- CARD-NAV-BOTTOM:END -->
