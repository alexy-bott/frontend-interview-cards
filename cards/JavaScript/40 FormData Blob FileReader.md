# 40 FormData Blob FileReader

<!-- CARD-NAV-TOP:START -->
[← 39 Cookies document.cookie SameSite credentials](<./39 Cookies document.cookie SameSite credentials.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [41 postMessage BroadcastChannel →](<./41 postMessage BroadcastChannel.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Как связаны `FormData`, `Blob`, `File`, object URL и `FileReader`? Как безопасно отправлять и читать файлы?

<details>
<summary><strong>Показать ответ</strong></summary>

`Blob` представляет неизменяемую последовательность bytes с `size` и необязательным MIME type. Его можно создать из строк, buffers и других blobs, получить часть через `slice` и читать через Promise-методы `text()`, `arrayBuffer()` или поток `stream()`.

`File` наследует `Blob` и добавляет метаданные пользовательского файла: `name`, `lastModified` и иногда относительный путь. Обычно File приходит из `<input type="file">`, drag-and-drop или File System API. Имя и `type` контролируются клиентской средой и не являются доказательством содержимого.

`FormData` хранит упорядоченный набор полей, где значение является строкой или `Blob`/`File`. Он используется как request body для `multipart/form-data`, когда вместе отправляются поля и бинарные файлы.

```js
const formData = new FormData();
formData.set("title", "Avatar");
formData.append("files", firstFile);
formData.append("files", secondFile);

await fetch("/api/upload", {
  method: "POST",
  body: formData,
});
```

При отправке FormData через `fetch` не нужно вручную устанавливать `Content-Type`. Браузер добавляет `multipart/form-data` вместе с уникальным boundary, то есть разделителем частей. Header без правильного boundary не сможет корректно описать body.

`new FormData(form)` собирает successful controls: элементы с `name`, которые не disabled и подходят по состоянию. Unchecked checkbox/radio и кнопки без роли submitter обычно не попадают. Значения нескольких controls с одним name сохраняются и читаются через `getAll`.

`FileReader` является event-based API чтения Blob как text, ArrayBuffer или data URL. Для нового Promise-кода методы Blob обычно проще. FileReader остаётся полезен для старых сред, progress events чтения и `readAsDataURL`.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Чем <code>append</code> отличается от <code>set</code> у FormData?</summary>

`append(name, value)` добавляет ещё одно значение и сохраняет предыдущие. `set` удаляет существующие значения этого имени и оставляет одно новое. Для нескольких файлов одного поля используют `append`; для одиночного редактируемого значения чаще подходит `set`.

</details>

<details>
<summary><strong>Вопрос:</strong> Какие элементы формы не попадут в <code>new FormData(form)</code>?</summary>

Controls без `name`, disabled controls, unchecked checkbox/radio и часть button controls. Значение file input представлено File. Если важна конкретная submit button с её name/value, современный constructor может получить submitter вторым аргументом или обработчик использует `SubmitEvent.submitter`.

</details>

<details>
<summary><strong>Вопрос:</strong> Когда отправлять JSON, а когда FormData?</summary>

JSON удобен для структурированных текстовых данных и явного API contract. FormData нужен для browser-compatible multipart, особенно при File/Blob. Вложенный объект внутри FormData не сериализуется автоматически: обычный объект превратится в строку `"[object Object]"`, поэтому его явно записывают JSON-строкой или раскладывают по согласованной схеме.

</details>

<details>
<summary><strong>Вопрос:</strong> Как показать preview изображения?</summary>

Создать `URL.createObjectURL(file)` и назначить URL элементу `img`, video или ссылке. Object URL удерживает ресурс до `URL.revokeObjectURL(url)` или завершения document. Старый URL освобождают после загрузки или замены, а не сразу после назначения, иначе потребитель может не успеть прочитать его.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем object URL отличается от data URL?</summary>

Object URL является короткой ссылкой браузера на Blob без base64-копии. Data URL содержит сами bytes в строке, увеличивает размер примерно из-за base64 и занимает JavaScript memory. Для preview большого файла object URL обычно дешевле; data URL нужен, когда данные действительно должны быть встроены в текстовый формат.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли доверять <code>file.type</code>, extension и атрибуту <code>accept</code>?</summary>

Нет. `accept` является подсказкой file picker, а MIME и filename могут быть неточными или подменёнными. Client validation улучшает UX, но сервер повторно проверяет размер, фактический формат, допустимые расширения, имя хранения и security policy. Загруженный пользовательский файл нельзя бездумно отдавать как активный HTML.

</details>

<details>
<summary><strong>Вопрос:</strong> Как показать upload progress с <code>fetch</code>?</summary>

Обычный `fetch` не предоставляет простой стабильный progress event загрузки request body во всех целевых браузерах. Если progress обязателен, используют `XMLHttpRequest.upload`, поддерживаемую библиотеку или контролируемую chunk/resumable upload схему. Download progress можно считать, читая `response.body` как stream, если известен общий размер.

</details>

<details>
<summary><strong>Вопрос:</strong> Как обрабатывать большой файл?</summary>

Не читать весь файл в строку и не хранить base64 в React state. Использовать `Blob.stream`, chunks, Worker для CPU-heavy parse, incremental upload или серверную обработку. Нужно поддержать отмену, progress, лимиты памяти и partial failure. Выбранная библиотека parser должна уметь работать с chunks, иначе stream только переносит место полной буферизации.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли программно установить путь file input?</summary>

Нет. Browser не позволяет странице выбрать локальный файл без действия пользователя. Значение file input можно очистить, но нельзя назначить произвольный File path. В React file input остаётся uncontrolled, а выбранный `FileList` читают из event или ref.

</details>

<details>
<summary><strong>Вопрос:</strong> Что происходит с File при structured clone?</summary>

Blob и File поддерживаются structured clone и могут передаваться Worker без преобразования в JSON. Это не означает, что тяжёлый parse бесплатен: worker всё равно должен прочитать bytes. Для `ArrayBuffer` после чтения можно использовать transfer, если нужно переместить владение без копирования.

</details>

<details>
<summary><strong>Вопрос:</strong> Как скачать созданный на клиенте файл?</summary>

Создать Blob, object URL и ссылку `<a download>`, инициировать ожидаемый пользовательский сценарий, затем удалить ссылку и revoke URL. Имя из `download` является подсказкой. Для очень больших экспортов лучше генерировать поток на сервере или использовать streaming-подход, чтобы не собрать весь файл в памяти страницы.

</details>

## Мини-задача

```js
const formData = new FormData();

formData.append("tag", "js");
formData.append("tag", "react");
formData.set("tag", "web");

console.log(formData.getAll("tag"));
```

<details>
<summary><strong>Вопрос:</strong> Что будет выведено?</summary>

`["web"]`. Два `append` создали повторяющиеся значения, после чего `set` заменил все записи с именем `tag` одной новой.

</details>

## Где это встречается во frontend

| Ситуация | API | Главный нюанс |
| --- | --- | --- |
| Multipart upload | FormData | Не задавать boundary вручную |
| Несколько файлов | `append` | Сервер должен ожидать повторяющийся key |
| Preview | Object URL | Revoke при замене или cleanup |
| Маленький текстовый файл | `blob.text()` | Обработать encoding и размер |
| Большой import | Stream и Worker | Не буферизовать всё без необходимости |
| File validation | Client и server | MIME/extension не являются доказательством |

## Связанные темы

- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>)
- [46 Streams API ReadableStream](<./46 Streams API ReadableStream.md>)
- [55 ArrayBuffer TypedArray DataView](<./55 ArrayBuffer TypedArray DataView.md>)
- [01 Формы во frontend](<../Forms/01 Формы во frontend.md>)
- [02 Controlled uncontrolled и FormData](<../Forms/02 Controlled uncontrolled и FormData.md>)

## Источники

- [MDN: `FormData`](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [MDN: `Blob`](https://developer.mozilla.org/en-US/docs/Web/API/Blob)
- [MDN: `File`](https://developer.mozilla.org/en-US/docs/Web/API/File)
- [MDN: `FileReader`](https://developer.mozilla.org/en-US/docs/Web/API/FileReader)
- [MDN: `URL.createObjectURL`](https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 39 Cookies document.cookie SameSite credentials](<./39 Cookies document.cookie SameSite credentials.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [41 postMessage BroadcastChannel →](<./41 postMessage BroadcastChannel.md>)
<!-- CARD-NAV-BOTTOM:END -->
