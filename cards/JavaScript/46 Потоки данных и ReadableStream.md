# Потоки данных и ReadableStream

<!-- CARD-NAV-TOP:START -->
[← 45 Безопасная и производительная работа с DOM](<./45 Безопасная и производительная работа с DOM.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [47 Service Worker и кеширование в PWA →](<./47 Service Worker и кеширование в PWA.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое Streams API? Как читать `ReadableStream`, учитывать backpressure и разбирать данные, разделённые произвольными chunks?**

<h2></h2>

<br>
<dl>
<dd>

Streams API позволяет обрабатывать данные постепенно, не ожидая полного результата в памяти. `ReadableStream` предоставляет chunks для чтения, `WritableStream` принимает chunks, а `TransformStream` преобразует поток между ними. Chunk может быть bytes, строкой или объектом в зависимости от источника.

У `fetch` свойство `response.body` обычно является `ReadableStream<Uint8Array>`, но может быть `null`, если у ответа нет доступного body. Reader получают через `getReader`; в этот момент поток становится locked, и другой reader не может читать его одновременно.

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

Методы `response.text()`, `json()`, `blob()` и `arrayBuffer()` сами полностью читают body. После начала чтения stream становится disturbed. После получения reader он дополнительно становится locked.

`releaseLock()` снимает блокировку reader, но не отменяет уже выполненное чтение и не делает disturbed stream доступным для повторного чтения. Повторно использовать тот же body обычно невозможно.

Backpressure, или обратное давление, означает, что медленный consumer не должен бесконтрольно накапливать всё, что производит быстрый source. Stream хранит chunks во внутренней очереди до настроенного `highWaterMark`, размер которого рассчитывается согласно стратегии очереди и не обязательно измеряется в байтах.

Значение `desiredSize` показывает source приблизительную оставшуюся ёмкость очереди. Реальный network stack имеет дополнительные buffers, поэтому Streams API контролирует накопление на своём уровне, но не гарантирует нулевое потребление памяти или немедленную остановку удалённого сервера.

Границы chunks являются техническими и не совпадают с границами Unicode-символов, строк или JSON-сообщений. `TextDecoder` в streaming mode сохраняет неполную последовательность bytes между вызовами.

Поверх текстового потока протокол должен задавать framing, например newline-delimited JSON, длину сообщения или SSE format.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем stream отличается от <code>await response.json()</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`json()` сначала полностью читает body, а затем запускает обычный JSON parser. Это проще для небольшого ответа.

Stream позволяет раньше начать обработку данных, показывать progress и не обязательно хранить весь ответ одновременно.

Стандартный JSON-документ трудно разбирать по частям без специализированного streaming parser, потому что одна структура может продолжаться до конца ответа. Для настоящего streaming сервер часто использует NDJSON, SSE или другой framed format.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя считать один chunk одной строкой?</strong></summary>

<dl>
<dd>
<h2></h2>

Размер и границы chunk определяются источником, сетью и реализацией stream.

Одна строка может прийти в нескольких chunks, а один chunk может содержать сразу несколько строк. Даже bytes одного UTF-8 символа могут оказаться в разных chunks.

Parser должен хранить остаток неполной записи, добавлять к нему новый декодированный текст, извлекать только полные frames и оставлять хвост до следующего чтения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как правильно декодировать UTF-8 stream?</strong></summary>

<dl>
<dd>
<h2></h2>

Для промежуточных chunks используют `TextDecoder.decode(bytes, { stream: true })`. Такой режим сохраняет внутри decoder неполную последовательность bytes до следующего вызова.

После завершения потока вызывают финальный `decoder.decode()`, чтобы сбросить оставшееся внутреннее состояние.

Другой вариант — пропустить byte stream через `new TextDecoderStream()`.

Независимый decode каждого chunk без streaming mode может заменить разделённый Unicode-символ на replacement character.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужны <code>pipeThrough</code> и <code>pipeTo</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`readable.pipeThrough(transform)` подключает readable к `TransformStream` и возвращает преобразованный readable.

`readable.pipeTo(writable)` передаёт chunks в destination и возвращает Promise, который завершается после окончания pipeline.

Pipeline автоматически передаёт backpressure между стадиями. По умолчанию закрытие, ошибки и отмена также распространяются между связанными сторонами, если это поведение не отключено соответствующими options.

```js
const textStream = response.body.pipeThrough(new TextDecoderStream());
for await (const textChunk of textStream) {
  consumeText(textChunk);
}
```

Для последовательности стандартных преобразований pipeline обычно надёжнее ручной передачи chunks между несколькими readers и writers.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как отменить чтение?</strong></summary>

<dl>
<dd>
<h2></h2>

`reader.cancel(reason)` сообщает stream и его underlying source, что consumer больше не нуждается в данных.

Если stream принадлежит `fetch`, для управления всей сетевой операцией обычно используют исходный `AbortController`. Его сигнал отменяет запрос и чтение response body.

Освобождение блокировки через `releaseLock()` само по себе ничего не отменяет. Оно только позволяет получить другой reader, если состояние stream ещё допускает дальнейшее чтение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как показать download progress?</strong></summary>

<dl>
<dd>
<h2></h2>

При чтении суммируют `value.byteLength` полученных byte chunks.

Общий размер можно взять из `Content-Length`, если header присутствует, доступен клиентскому коду и действительно соответствует измеряемым данным.

Header может отсутствовать. Кроме того, при compression размер передаваемого ответа и размер декодированных bytes могут различаться. Поэтому иногда можно показать только количество полученных данных или indeterminate progress без точного процента.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при ошибке stream?</strong></summary>

<dl>
<dd>
<h2></h2>

`reader.read()` и `pipeTo()` завершаются rejected Promise. При async iteration ошибка выбрасывается в месте выполнения цикла `for await...of`.

Pipeline по умолчанию отменяет или abort-ит связанные стороны согласно направлению ошибки и используемым options.

Consumer должен учитывать уже частично обработанные данные: удалить незавершённую запись, пометить результат как incomplete или уметь продолжить загрузку с cursor.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли читать stream двумя consumers?</strong></summary>

<dl>
<dd>
<h2></h2>

Один stream может иметь только один активный reader.

Метод `stream.tee()` создаёт две ветки, а `response.clone()` позволяет отдельно читать две версии response body с похожей моделью разделения потока.

Backpressure определяется более быстрой веткой. Если второй consumer читает медленно, непрочитанные chunks могут продолжать накапливаться во внутренней очереди этой ветки без жёсткого ограничения.

Поэтому `tee` большого потока не является бесплатным broadcast и может значительно увеличить потребление памяти.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Уменьшает ли stream память автоматически?</strong></summary>

<dl>
<dd>
<h2></h2>

Только если весь pipeline действительно обрабатывает и освобождает chunks постепенно.

Если consumer сохраняет каждую часть в массиве, собирает одну гигантскую строку или передаёт данные библиотеке, которая в конце буферизует всё содержимое, peak memory всё равно останется большим.

Потоковый API сам по себе не гарантирует потоковую обработку всех последующих стадий. Нужно анализировать чтение, декодирование, parsing, хранение результата и обновление UI.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое BYOB reader?</strong></summary>

<dl>
<dd>
<h2></h2>

Bring Your Own Buffer reader позволяет consumer передать заранее выделенную область памяти для чтения bytes. Это может уменьшить количество allocations и копирований в бинарном pipeline.

Он создаётся через `getReader({ mode: "byob" })` и работает только с `ReadableStream`, созданным как byte stream.

Поддержка конкретным источником и средой должна проверяться отдельно. Для обычной обработки небольшого fetch-ответа BYOB обычно не является необходимым.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда обработку chunks переносить в Worker?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда декодирование, decompression, parsing или aggregation создают long tasks на main thread.

Само постепенное чтение network stream не гарантирует отзывчивость интерфейса: тяжёлая синхронная обработка каждого chunk всё равно может блокировать rendering и пользовательский ввод.

При переносе нужно учитывать стоимость сообщений. Для бинарных данных можно передавать `ArrayBuffer` через transfer list, а в подходящей архитектуре использовать transferable streams, если они поддерживаются целевой средой.

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

Последний элемент после `split` может быть неполной NDJSON-строкой. Его сохраняют в `buffer`, чтобы добавить продолжение из следующего chunk.

`TextDecoder` также может хранить внутри bytes незавершённой UTF-8 последовательности. Финальный вызов `decoder.decode()` сбрасывает это внутреннее состояние после окончания stream.

После этого оставшийся в `buffer` последний полный frame обрабатывается отдельно.

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

- [29 fetch отмена запросов и обработка ошибок](<./29 fetch отмена запросов и обработка ошибок.md>)
- [38 Web Workers и передача данных](<./38 Web Workers и передача данных.md>)
- [40 Работа с файлами в браузере](<./40 Работа с файлами в браузере.md>)
- [48 WebSocket и обновления данных в реальном времени](<./48 WebSocket и обновления данных в реальном времени.md>)
- [54 Строки Unicode и кодировки](<./54 Строки Unicode и кодировки.md>)
- [55 Бинарные данные в JavaScript](<./55 Бинарные данные в JavaScript.md>)

## Источники

- [MDN: Streams API](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API)
- [MDN: `ReadableStream`](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream)
- [MDN: using readable streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams)
- [MDN: `TextDecoderStream`](https://developer.mozilla.org/en-US/docs/Web/API/TextDecoderStream)
- [Streams Standard](https://streams.spec.whatwg.org/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 45 Безопасная и производительная работа с DOM](<./45 Безопасная и производительная работа с DOM.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [47 Service Worker и кеширование в PWA →](<./47 Service Worker и кеширование в PWA.md>)
<!-- CARD-NAV-BOTTOM:END -->
