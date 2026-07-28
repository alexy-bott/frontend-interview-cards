# Streams API ReadableStream

<!-- CARD-NAV-TOP:START -->
[← 45 DOM API innerHTML layout thrashing](<./45 DOM API innerHTML layout thrashing.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [47 Service Worker Cache API PWA →](<./47 Service Worker Cache API PWA.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Streams API? Как читать `ReadableStream`, учитывать backpressure и разбирать данные, разделённые произвольными chunks?**

<h2></h2>

<br>
<dl>
<dd>

Streams API обрабатывает данные постепенно, не ожидая полного результата в памяти. `ReadableStream` предоставляет chunks для чтения, `WritableStream` принимает chunks, а `TransformStream` преобразует поток между ними. Chunk может быть bytes, строкой или объектом в зависимости от источника.

У `fetch` свойство `response.body` обычно является `ReadableStream<Uint8Array>`. Reader получают через `getReader`; в этот момент поток locked и другой reader не может читать его одновременно.

```js
const response = await fetch("/api/logs");
const reader = response.body.getReader();

try {
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    consumeBytes(value);
  }
} finally {
  reader.releaseLock();
}
```

Методы `response.text()`, `json()`, `blob()` и `arrayBuffer()` сами полностью читают body. После начала чтения stream становится disturbed, а после получения reader ещё и locked. Повторное чтение того же body обычно невозможно.

Backpressure, или обратное давление, означает, что медленный consumer не должен бесконтрольно накапливать всё, что производит быстрый source. Stream хранит внутреннюю очередь до настроенного high water mark и сигнализирует source через `desiredSize`. Реальный network stack имеет дополнительные buffers, поэтому Streams API ограничивает накопление на своём уровне, но не обещает нулевую память.

Границы chunks технические и не совпадают с границами Unicode-символов, строк или JSON-сообщений. TextDecoder в streaming mode сохраняет неполную последовательность bytes между вызовами. Поверх текста протокол должен задать framing, например newline-delimited JSON, длину сообщения или SSE format.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем stream отличается от <code>await response.json()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`json()` сначала читает body целиком, затем вызывает обычный JSON parser. Это проще для небольшого ответа. Stream позволяет показать progress или обработать записи раньше, но стандартный JSON-документ всё равно трудно разбирать по частям без специализированного streaming parser. Для настоящего streaming сервер часто использует NDJSON, SSE или другой framed format.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя считать один chunk одной строкой?</strong></summary>

<dl>
<dd>
<h2></h2>

Размер chunk выбирают сеть и stream implementation. Одна строка может прийти частями, а несколько строк одним chunk. Даже один UTF-8 символ может разделиться между chunks. Parser хранит остаток неполной записи, добавляет новый decoded text, извлекает только полные frames и оставляет хвост до следующего чтения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как правильно декодировать UTF-8 stream?</strong></summary>

<dl>
<dd>
<h2></h2>

Использовать `TextDecoder.decode(bytes, { stream: true })` для промежуточных chunks и финальный `decoder.decode()` после завершения либо пропустить поток через `new TextDecoderStream()`. Обычный независимый decode каждого chunk может заменить разделённый символ на replacement character.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужны <code>pipeThrough</code> и <code>pipeTo</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`readable.pipeThrough(transform)` связывает readable с TransformStream и возвращает преобразованный readable. `pipeTo(writable)` передаёт chunks в destination и возвращает Promise завершения. Pipeline автоматически распространяет backpressure и по умолчанию errors/cancellation, что надёжнее ручного цикла для последовательности стандартных transforms.

```js
const textStream = response.body.pipeThrough(new TextDecoderStream());
for await (const textChunk of textStream) {
  consumeText(textChunk);
}
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить чтение?</strong></summary>

<dl>
<dd>
<h2></h2>

`reader.cancel(reason)` сообщает stream, что consumer больше не нужен. Если stream принадлежит `fetch`, надёжнее также отменить request через исходный `AbortController`, чтобы прекратить network operation. Освобождение lock через `releaseLock` само по себе не отменяет source.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как показать download progress?</strong></summary>

<dl>
<dd>
<h2></h2>

Суммировать `value.byteLength` при чтении. Общий размер можно взять из `Content-Length`, если header доступен и присутствует. Он может отсутствовать, а при compression размер передаваемого и декодированного body может различаться, поэтому progress иногда бывает только indeterminate.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при ошибке stream?</strong></summary>

<dl>
<dd>
<h2></h2>

`reader.read`, `pipeTo` или async iteration завершаются rejected Promise. Pipeline отменяет или abort-ит связанные стороны по правилам options. Consumer должен обработать частично применённые данные: удалить незавершённую запись, пометить результат incomplete или уметь продолжить с cursor.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли читать stream двумя consumers?</strong></summary>

<dl>
<dd>
<h2></h2>

Один stream может иметь только один активный reader. `stream.tee()` создаёт две branches, а `response.clone()` использует похожую идею для body. Если один consumer медленный, данные могут буферизоваться для него без жёсткого ограничения, поэтому tee большого потока не является бесплатным broadcast.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Уменьшает ли stream память автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

Только если весь pipeline действительно обрабатывает и освобождает chunks постепенно. Если consumer складывает каждую часть в массив, собирает одну гигантскую строку или библиотека в конце буферизует всё, peak memory остаётся большой. Нужно анализировать каждую стадию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое BYOB reader?</strong></summary>

<dl>
<dd>
<h2></h2>

Bring Your Own Buffer reader позволяет consumer передавать заранее выделенный buffer для byte stream, уменьшая число allocations и копирований. Он создаётся через `getReader({ mode: "byob" })` только для подходящего readable byte stream. Это оптимизация бинарных pipelines, а не обязательный API для обычного fetch.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда обработку chunks переносить в Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда decode, decompression, parsing или aggregation создают long tasks на main thread. Само чтение network stream не гарантирует отзывчивость. Нужно учесть цену пересылки chunks; transferable `ArrayBuffer` или transferable streams в поддерживаемой архитектуре снижают копирование.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const decoder = new TextDecoder();
let buffer = "";

for await (const chunk of response.body) {
  buffer += decoder.decode(chunk, { stream: true });

  const lines = buffer.split("\n");
  buffer = lines.pop();

  for (const line of lines) {
    if (line) consume(JSON.parse(line));
  }
}

buffer += decoder.decode();
if (buffer) consume(JSON.parse(buffer));
```

<details>
<summary><strong>Зачем хранить <code>buffer</code> и вызывать финальный <code>decode()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Последний элемент после `split` может быть неполной NDJSON-строкой и должен дождаться следующего chunk. Финальный `decode()` сбрасывает bytes незавершённой UTF-8 последовательности внутри decoder. После конца stream оставшийся frame обрабатывается отдельно.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Stream-подход | Главный риск |
| --- | --- | --- |
| AI/log streaming | Framed text и incremental UI | Chunk не равен сообщению |
| Большой download | Подсчёт bytes | Общий размер может быть неизвестен |
| NDJSON | Decoder и line buffer | Неполная строка между chunks |
| Transform pipeline | `pipeThrough`/`pipeTo` | Распространение error/cancel |
| Два consumers | `tee`/clone | Буферизация медленной branch |
| CPU-heavy parse | Worker | Цена передачи chunks |

## Связанные темы

- [29 Fetch AbortController и ошибки API](<./29 Fetch AbortController и ошибки API.md>)
- [38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>)
- [40 FormData Blob FileReader](<./40 FormData Blob FileReader.md>)
- [48 WebSocket EventSource realtime](<./48 WebSocket EventSource realtime.md>)
- [54 Строки Unicode и кодировки](<./54 Строки Unicode и кодировки.md>)
- [55 ArrayBuffer TypedArray DataView](<./55 ArrayBuffer TypedArray DataView.md>)

## Источники

- [MDN: Streams API](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API)
- [MDN: `ReadableStream`](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream)
- [MDN: using readable streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams)
- [MDN: `TextDecoderStream`](https://developer.mozilla.org/en-US/docs/Web/API/TextDecoderStream)
- [Streams Standard](https://streams.spec.whatwg.org/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 45 DOM API innerHTML layout thrashing](<./45 DOM API innerHTML layout thrashing.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [47 Service Worker Cache API PWA →](<./47 Service Worker Cache API PWA.md>)
<!-- CARD-NAV-BOTTOM:END -->
