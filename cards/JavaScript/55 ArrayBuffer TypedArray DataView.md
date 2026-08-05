# ArrayBuffer TypedArray DataView

<!-- CARD-NAV-TOP:START -->
[← 54 Строки Unicode и кодировки](<./54 Строки Unicode и кодировки.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что такое `ArrayBuffer`, типизированные массивы и `DataView`? Как JavaScript работает с бинарными данными?**

<h2></h2>

<br>
<dl>
<dd>

`ArrayBuffer` представляет непрерывную область памяти заданного размера. Он хранит только последовательность байтов и сам не определяет, являются ли они целыми числами, дробями, текстом, изображением или частью файла.

Напрямую читать и изменять отдельные байты через `ArrayBuffer` нельзя. Для этого поверх буфера создают представление, или view, которое интерпретирует его память по определённым правилам.

Типизированные массивы, например `Uint8Array`, `Int32Array` и `Float64Array`, являются представлениями над `ArrayBuffer`. Название определяет тип и размер одного элемента:

- `Uint8Array` — целые без знака по одному байту;
- `Int32Array` — целые со знаком по четыре байта;
- `Float64Array` — числа IEEE 754 по восемь байтов.

Представление не хранит отдельную копию данных. Несколько views могут ссылаться на один или пересекающиеся участки одного буфера. Тогда запись через одно представление сразу становится видна через другое.

```js
const buffer = new ArrayBuffer(4);
const bytes = new Uint8Array(buffer);
const numbers = new Uint16Array(buffer);

bytes[0] = 255;
console.log(numbers.buffer === buffer); // true
```

У представления есть:

- `buffer` — исходный `ArrayBuffer`;
- `byteOffset` — смещение начала view относительно буфера в байтах;
- `byteLength` — размер view в байтах;
- `length` — количество элементов типизированного массива.

Количество байтов на один элемент доступно через `BYTES_PER_ELEMENT`:

```js
Uint16Array.BYTES_PER_ELEMENT; // 2
```

Типизированный массив имеет фиксированный тип элементов. При записи JavaScript преобразует значение к этому типу. Например, `Uint8Array` хранит целые от `0` до `255`: дробная часть отбрасывается, а значения за диапазоном преобразуются по правилам 8-битного целого.

`DataView` является более низкоуровневым представлением. Оно позволяет читать и записывать разные числовые типы по заданным смещениям в байтах:

```js
const view = new DataView(buffer);

view.setUint16(0, 500, true);
const value = view.getUint16(0, true);
```

В отличие от типизированного массива, `DataView` не привязан к одному типу элементов и позволяет явно задавать порядок байтов при каждой многобайтовой операции.

Порядок байтов, или endianness, определяет, какой байт многобайтового числа записывается первым:

- big-endian — сначала старший байт;
- little-endian — сначала младший байт.

Типизированные массивы используют порядок байтов текущей платформы. `DataView` позволяет явно выбрать порядок, поэтому лучше подходит для разбора сетевых протоколов и форматов файлов.

Для однобайтовых типов вроде `Uint8Array` порядок байтов значения не имеет.

Бинарные данные встречаются в `fetch`, WebSocket, файлах, Canvas, Web Audio, WebAssembly и сообщениях Worker.

Бинарный протокол должен точно задавать:

- положение каждого поля;
- его размер и числовой тип;
- signed или unsigned формат;
- порядок байтов;
- кодировку текста;
- допустимую длину данных.

Без такого соглашения один и тот же набор байтов можно интерпретировать разными способами.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем обычный <code>Array</code> отличается от типизированного массива?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный `Array` хранит произвольные JavaScript-значения:

```js
const values = [1, "text", null, {}];
```

Он может динамически менять длину и содержать пропуски между индексами.

Типизированный массив является представлением над бинарным буфером. Он имеет фиксированный тип элементов и не может содержать произвольные объекты или строки:

```js
const values = new Uint8Array(4);
```

Его длина после создания обычно фиксирована размером соответствующего участка буфера.

При записи значение преобразуется к выбранному числовому формату. Например, `Float32Array` округляет число до 32-битного формата с плавающей точкой, а `Uint8Array` преобразует его к 8-битному целому без знака.

У типизированных массивов нет разреженных элементов: каждый индекс соответствующего диапазона связан с конкретными байтами памяти.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>Uint8Array</code> отличается от <code>Uint8ClampedArray</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Оба представления хранят по одному байту на элемент и представляют значения от `0` до `255`.

`Uint8Array` преобразует значение к 8-битному целому без знака. Дробная часть отбрасывается, а значения за диапазоном циклически преобразуются:

```js
const values = new Uint8Array(2);

values[0] = 256;
values[1] = -1;

console.log(values); // Uint8Array [0, 255]
```

`Uint8ClampedArray` сначала ограничивает значение диапазоном от `0` до `255`, а дробные значения округляет по специальным правилам:

```js
const values = new Uint8ClampedArray(2);

values[0] = 300;
values[1] = -10;

console.log(values); // Uint8ClampedArray [255, 0]
```

Такое поведение удобно для цветовых каналов пикселей Canvas, где значение не должно циклически переходить от `255` к `0`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>subarray</code> отличается от <code>slice</code> у типизированного массива?</strong></summary>

<dl>
<dd>
<h2></h2>

`subarray(begin, end)` создаёт новое представление над тем же `ArrayBuffer`:

```js
const source = new Uint8Array([10, 20, 30]);
const part = source.subarray(0, 2);

part[0] = 99;

console.log(source[0]); // 99
```

Изменение `part` видно в `source`, потому что оба typed arrays используют одну память.

`slice(begin, end)` создаёт новый типизированный массив и копирует выбранные элементы:

```js
const source = new Uint8Array([10, 20, 30]);
const copy = source.slice(0, 2);

copy[0] = 99;

console.log(source[0]); // 10
```

`subarray` дешевле и подходит для работы с участком общего буфера. `slice` используют, когда нужна независимая копия.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие операции создают view, а какие копируют данные?</strong></summary>

<dl>
<dd>
<h2></h2>

Создание typed array непосредственно из `ArrayBuffer` создаёт view над существующей памятью:

```js
const buffer = new ArrayBuffer(8);
const view = new Uint8Array(buffer);
```

Метод `subarray` также создаёт новое представление без копирования:

```js
const part = view.subarray(2, 6);
```

Создание typed array из массива JavaScript выделяет новый буфер и копирует преобразованные значения:

```js
const values = new Uint8Array([1, 2, 3]);
```

Создание typed array из другого typed array также создаёт новый буфер и копирует элементы:

```js
const source = new Uint8Array([1, 2, 3]);
const copy = new Uint8Array(source);

copy[0] = 100;
console.log(source[0]); // 1
```

Метод `slice` копирует выбранные элементы, а `set` копирует элементы в уже существующий typed array.

Поэтому для понимания изменений важно проверить, используют ли значения один `buffer` или независимые буферы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда нужен <code>DataView</code>, а когда достаточно <code>Uint8Array</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Uint8Array` удобен, когда данные рассматриваются как последовательность отдельных байтов:

- копирование диапазонов;
- чтение chunks потока;
- передача данных в Web API;
- обработка кодированного текста;
- изменение отдельных байтов.

`DataView` нужен для разбора структуры, в которой по известным смещениям находятся значения разных типов:

```text
bytes 0–1: длина сообщения, Uint16, big-endian
bytes 2–5: идентификатор, Uint32, little-endian
byte 6: флаги, Uint8
```

`DataView` позволяет читать каждое поле с нужным типом и порядком байтов:

```js
const length = view.getUint16(0, false);
const id = view.getUint32(2, true);
const flags = view.getUint8(6);
```

Смещения `DataView` всегда указываются в байтах, а не в количестве условных элементов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему для typed array важна кратность <code>byteOffset</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Typed array интерпретирует память как последовательность элементов фиксированного размера.

Поэтому начальное смещение должно быть кратно размеру элемента:

```js
const buffer = new ArrayBuffer(8);

new Uint16Array(buffer, 2); // допустимо
new Uint16Array(buffer, 1); // RangeError
```

Один элемент `Uint16Array` занимает два байта, поэтому `byteOffset` должен быть кратен двум. Для `Uint32Array` он должен быть кратен четырём.

Кроме того, оставшийся участок буфера должен вмещать указанное количество целых элементов.

`DataView` не требует такого выравнивания:

```js
const view = new DataView(buffer);
view.getUint32(1);
```

Это позволяет разбирать бинарные форматы, в которых многобайтовое поле начинается с произвольного байта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое big-endian и little-endian?</strong></summary>

<dl>
<dd>
<h2></h2>

Это два порядка хранения многобайтового числа.

В big-endian сначала записывается старший байт. В little-endian первым записывается младший байт.

Число `0x1234` занимает два байта:

```text
big-endian:    0x12 0x34
little-endian: 0x34 0x12
```

`DataView` принимает порядок байтов последним аргументом:

```js
view.setUint16(0, 0x1234, false); // big-endian
view.setUint16(0, 0x1234, true);  // little-endian
```

Если аргумент отсутствует или равен `false`, используется big-endian.

Порядок байтов должен быть явно определён форматом файла или сетевым протоколом. Надёжно угадать его только по содержимому данных нельзя.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит при передаче <code>ArrayBuffer</code> в Worker через список передаваемых объектов (transfer list)?</strong></summary>

<dl>
<dd>
<h2></h2>

Буфер передаётся во владение другому контексту без обычного копирования его содержимого:

```js
worker.postMessage({ buffer }, [buffer]);
```

В передаваемом сообщении может находиться typed array, но в transfer list указывают его `ArrayBuffer`:

```js
worker.postMessage(
  { bytes },
  [bytes.buffer],
);
```

После передачи исходный `ArrayBuffer` становится detached — отсоединённым от своей памяти:

```js
buffer.byteLength; // 0
```

Views, созданные поверх этого буфера, больше нельзя использовать как прежние представления данных. Их длина и доступное содержимое исчезают или операции завершаются ошибкой в зависимости от конкретного API.

Передача подходит для больших бинарных данных, когда копирование слишком дорого. Но она требует явной модели владения: после `postMessage` отправитель больше не должен продолжать работать с переданным буфером.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем передача ресурса отличается от алгоритма structured clone?</strong></summary>

<dl>
<dd>
<h2></h2>

При обычном structured clone поддерживаемые данные копируются в другой контекст.

Для обычного `ArrayBuffer` создаётся независимый буфер с тем же содержимым:

```js
worker.postMessage({ buffer });
```

После этого исходный буфер остаётся доступен отправителю, но копирование большого объёма данных требует дополнительной памяти и времени.

Transfer list не копирует содержимое обычного `ArrayBuffer`, а переносит его:

```js
worker.postMessage({ buffer }, [buffer]);
```

После переноса исходный буфер становится detached.

Передаваемый ресурс должен присутствовать и в значении сообщения, и в transfer list. Само добавление объекта только в transfer list не делает его доступным получателю.

Не все structured-clone значения становятся полностью независимыми. Например, `SharedArrayBuffer` сохраняет общую разделяемую память между контекстами.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>SharedArrayBuffer</code> отличается от <code>ArrayBuffer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный `ArrayBuffer` при обмене либо копируется, либо передаётся одному новому владельцу.

`SharedArrayBuffer` позволяет нескольким JavaScript-контекстам обращаться к одной области памяти одновременно:

```js
const buffer = new SharedArrayBuffer(4);
const values = new Int32Array(buffer);
```

Изменение, выполненное Worker, может сразу стать доступно main thread.

При одновременном чтении и записи возникает риск гонки данных. Для координации используют `Atomics`:

```js
Atomics.store(values, 0, 1);
Atomics.load(values, 0);
```

В браузере доступ к `SharedArrayBuffer` обычно требует cross-origin isolation. Она настраивается подходящими заголовками `Cross-Origin-Opener-Policy` и `Cross-Origin-Embedder-Policy`.

Состояние можно проверить через:

```js
crossOriginIsolated;
```

Общая память усложняет модель программы, поэтому её применяют только там, где действительно нужна производительность совместного доступа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>Blob</code> отличается от <code>ArrayBuffer</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`Blob` представляет неизменяемый объект бинарных данных. У него есть размер и необязательный MIME-тип:

```js
const blob = new Blob([data], {
  type: "application/octet-stream",
});
```

Он удобен для файлов, загрузок, object URL и передачи больших бинарных объектов между Web API.

`ArrayBuffer` представляет изменяемую область памяти, которую JavaScript читает и записывает через typed arrays или `DataView`.

Получить буфер из `Blob` можно асинхронно:

```js
const buffer = await blob.arrayBuffer();
```

Этот вызов читает данные Blob в память. Для очень большого объекта нужно учитывать дополнительное потребление памяти.

Обратное преобразование создаёт Blob из буфера или view:

```js
const blob = new Blob([buffer]);
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как преобразовать строку в байты и обратно?</strong></summary>

<dl>
<dd>
<h2></h2>

`TextEncoder` преобразует строку в байты UTF-8:

```js
const bytes = new TextEncoder().encode(text);
```

Результатом является `Uint8Array`.

`TextDecoder` выполняет обратное преобразование:

```js
const text = new TextDecoder("utf-8").decode(bytes);
```

Нельзя считать, что один элемент JavaScript-строки соответствует одному байту. Кириллица и эмодзи в UTF-8 занимают несколько байтов.

При потоковой обработке граница chunk может находиться внутри многобайтового символа. В таком случае decoder используют в streaming-режиме:

```js
decoder.decode(chunk, { stream: true });
```

После последнего chunk вызывают `decode()` без данных, чтобы завершить декодирование оставшегося состояния.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как получить бинарный ответ <code>fetch</code> или бинарное сообщение WebSocket?</strong></summary>

<dl>
<dd>
<h2></h2>

Для небольшого ответа `fetch` можно прочитать тело целиком:

```js
const response = await fetch(url);
const buffer = await response.arrayBuffer();
```

`arrayBuffer()` дожидается всего тела и сохраняет его в памяти.

Для большого ответа используют `response.body` как `ReadableStream`. Его chunks обычно представлены значениями `Uint8Array`, что позволяет обрабатывать данные постепенно.

У браузерного WebSocket свойство `binaryType` задают как `"arraybuffer"`, если бинарное сообщение нужно получить в виде `ArrayBuffer`:

```js
socket.binaryType = "arraybuffer";
```

Без этого бинарное сообщение в браузере обычно приходит как `Blob`.

Полученные байты нужно разбирать по правилам конкретного протокола. Сам `ArrayBuffer` не содержит информации о структуре полей или кодировке текста.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Подходит ли Base64 для хранения произвольных бинарных данных?</strong></summary>

<dl>
<dd>
<h2></h2>

Base64 преобразует байты в печатные ASCII-символы. Это позволяет поместить бинарные данные в текстовый формат, например в отдельное JSON-поле.

Размер Base64-представления примерно на треть больше исходных данных без учёта дополнительной JSON-разметки.

Для обычной загрузки файла эффективнее использовать бинарное тело запроса, `Blob`, `ArrayBuffer` или `multipart/form-data`.

Base64:

- не шифрует данные;
- не скрывает их содержимое;
- не сжимает данные;
- создаёт дополнительную работу при кодировании и декодировании.

Поэтому его используют только тогда, когда транспорт или формат действительно требуют текстового представления.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const buffer = new ArrayBuffer(4);
const bytes = new Uint8Array(buffer);
const view = new DataView(buffer);

view.setUint16(0, 0x1234, false);

console.log(bytes[0].toString(16));
console.log(bytes[1].toString(16));
```

<details>
<summary><strong>Что будет выведено и что означает третий аргумент <code>false</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Будут выведены строки:

```text
12
34
```

Метод записал 16-битное число `0x1234` в big-endian:

```text
старший байт: 0x12
младший байт: 0x34
```

Третий аргумент `false` явно выбирает big-endian. Такое же поведение используется, если аргумент не передан.

Значение `true` выбрало бы little-endian, и порядок байтов поменялся бы:

```text
34
12
```

`Uint8Array` читает память по одному байту, поэтому показывает фактическое расположение байтов, записанных через `DataView`.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Подходящий API | Что учитывать |
| --- | --- | --- |
| Бинарный ответ `fetch` | `ArrayBuffer` или `ReadableStream<Uint8Array>` | Размер ответа и потоковая обработка |
| Бинарный WebSocket-протокол | `ArrayBuffer` и `DataView` | Формат полей и порядок байтов |
| Работа с пикселями Canvas | `Uint8ClampedArray` | Четыре цветовых канала на пиксель |
| Передача в Worker | Передаваемый `ArrayBuffer` | Исходный буфер отсоединяется |
| Декодирование текста | `TextDecoder` | Кодировка и границы символов |
| WebAssembly и Web Audio | Типизированные массивы | Общая память и формат элементов |

## Связанные темы

- [38 Web Workers postMessage structured clone](<./38 Web Workers postMessage structured clone.md>)
- [40 FormData Blob FileReader](<./40 FormData Blob FileReader.md>)
- [46 Streams API ReadableStream](<./46 Streams API ReadableStream.md>)
- [48 WebSocket EventSource realtime](<./48 WebSocket EventSource realtime.md>)
- [54 Строки Unicode и кодировки](<./54 Строки Unicode и кодировки.md>)

## Источники

- [MDN: `ArrayBuffer`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer)
- [MDN: JavaScript typed arrays](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Typed_arrays)
- [MDN: `DataView`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/DataView)
- [MDN: transferable objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)
- [MDN: `SharedArrayBuffer`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer)
- [ECMAScript: structured data](https://tc39.es/ecma262/multipage/structured-data.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 54 Строки Unicode и кодировки](<./54 Строки Unicode и кодировки.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
