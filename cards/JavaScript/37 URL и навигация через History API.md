# URL и навигация через History API

<!-- CARD-NAV-TOP:START -->
[← 36 EventTarget и пользовательские события](<./36 EventTarget и пользовательские события.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [38 Web Workers и передача данных →](<./38 Web Workers и передача данных.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работать с URL и query parameters? Как History API меняет адрес SPA без перезагрузки?**

<h2></h2>

<br>
<dl>
<dd>

`URL` разбирает адрес по стандартным правилам и предоставляет доступ к его частям: `protocol`, `origin`, `hostname`, `port`, `pathname`, `search` и `hash`.

Второй аргумент задаёт базовый адрес, относительно которого разрешается первый аргумент. Это надёжнее ручной склейки строк:

```js
const url = new URL("/catalog?sort=price", "https://example.com");

url.searchParams.set("page", "2");
console.log(url.href);
// https://example.com/catalog?sort=price&page=2
```

Объект `URL` изменяемый. При изменении `pathname`, `hash` или `searchParams` итоговое значение `href` обновляется автоматически.

`URLSearchParams` управляет query string и предоставляет методы `get`, `getAll`, `has`, `set`, `append`, `delete` и `sort`.

`set` заменяет все существующие значения параметра одним новым значением. `append` добавляет ещё одно значение и сохраняет повторяющиеся параметры:

```js
const params = new URLSearchParams();

params.append("tag", "js");
params.append("tag", "react");

console.log(params.getAll("tag")); // ["js", "react"]
```

При сериализации имена и значения кодируются по правилам `application/x-www-form-urlencoded`. Например, пробел обычно превращается в `+`.

Значения передают в `URLSearchParams` в обычном виде. Не нужно заранее применять к ним `encodeURIComponent`, иначе уже закодированные символы могут быть закодированы повторно.

Query parameters подходят для состояния, которое должно:

- переживать перезагрузку страницы;
- восстанавливаться после Back и Forward;
- открываться по прямой ссылке;
- передаваться другому пользователю.

К такому состоянию относятся фильтры, сортировка, pagination, поисковая строка и активная вкладка. Интерфейс должен уметь восстановиться из URL, а не считать адрес только побочным результатом внутреннего state.

`history.pushState(state, "", url)` добавляет новую запись в историю текущей вкладки. `history.replaceState(state, "", url)` изменяет текущую запись.

Оба метода:

- требуют URL того же origin;
- не выполняют полную сетевую навигацию;
- не перезагружают документ;
- не обновляют интерфейс автоматически.

```js
history.pushState(
  { page: 2 },
  "",
  "/catalog?page=2",
);
```

После изменения адреса приложение или router должны самостоятельно прочитать новый URL, обновить route state, загрузить необходимые данные и перерисовать интерфейс.

Событие `popstate` возникает, когда браузер переходит к другой записи истории, например после Back, Forward или `history.go()`.

Непосредственные вызовы `pushState` и `replaceState` не создают `popstate`. Код, который сам изменил историю, должен сразу обновить интерфейс, а `popstate` использовать для будущих переходов пользователя по истории.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>pushState</code> отличается от <code>replaceState</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`pushState` создаёт новую запись в истории. После такого изменения кнопка Back возвращает пользователя к предыдущему адресу.

`replaceState` изменяет текущую запись, не добавляя новый шаг.

`pushState` обычно используют для пользовательской навигации, например перехода:

```text
/catalog → /catalog?page=2
```

`replaceState` подходит для технической нормализации адреса: удаления одноразового параметра, исправления некорректного значения или записи default-параметров без создания лишнего шага Back.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что хранится в <code>history.state</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`history.state` содержит данные, связанные с текущей записью истории через `pushState` или `replaceState`.

Значение должно поддерживать structured serialization. Например, нельзя передать функцию или DOM-узел. При неподдерживаемом значении браузер может выбросить `DataCloneError`.

Размер state может быть ограничен браузером, поэтому в нём не следует хранить большие объёмы данных.

Воспроизводимое состояние лучше помещать в сам URL. Тогда страницу можно открыть по ссылке или восстановить после reload.

`history.state` подходит для дополнительных данных конкретного перехода, которые не должны отображаться в адресной строке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>popstate</code> отличается от <code>hashchange</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`popstate` сообщает о переходе к другой записи session history, например после Back или Forward.

`hashchange` возникает, когда fragment URL изменяется через обычную навигацию или присваивание `location.hash`.

```js
location.hash = "reviews";
```

Вызов `pushState` не вызывает ни `popstate`, ни `hashchange`, даже если переданный URL содержит другой hash.

Приложение, которое самостоятельно вызвало `pushState`, должно само обработать изменение. Событие `popstate` понадобится позднее, когда пользователь вернётся к другой записи истории.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>location.assign</code>, <code>replace</code> и изменение <code>href</code> отличаются от History API?</strong></summary>

<dl>
<dd>
<h2></h2>

`location.assign(url)` и присваивание `location.href` запускают обычную навигацию браузера и добавляют новую запись в историю:

```js
location.href = "/catalog";
```

`location.replace(url)` тоже запускает навигацию, но заменяет текущую запись, поэтому вернуться к ней через Back нельзя.

`pushState` и `replaceState` меняют URL текущего документа без полной сетевой навигации. После такого изменения приложение само отвечает за обновление экрана.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работать с повторяющимися query parameters?</strong></summary>

<dl>
<dd>
<h2></h2>

URL может содержать несколько параметров с одинаковым именем:

```text
?tag=js&tag=react
```

`get("tag")` вернёт только первое значение:

```js
params.get("tag"); // "js"
```

`getAll("tag")` вернёт все значения:

```js
params.getAll("tag"); // ["js", "react"]
```

`set("tag", value)` удалит остальные значения этого имени и оставит одно. `append("tag", value)` добавит ещё один параметр.

Клиент и backend должны заранее договориться, как кодируется список: повторением ключа, строкой с разделителем, индексированными параметрами или другим способом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя собирать query string вручную?</strong></summary>

<dl>
<dd>
<h2></h2>

Значения могут содержать пробелы, `&`, `=`, `#`, Unicode и другие символы, имеющие специальное значение в URL.

Ручная склейка смешивает структуру query string с пользовательскими данными:

```js
const search = `?query=${value}`;
```

Если `value` содержит `&page=10`, результат может быть разобран как несколько параметров.

`URLSearchParams` отделяет имя и значение от синтаксиса URL и выполняет необходимое кодирование:

```js
const params = new URLSearchParams({
  query: value,
});
```

Также не следует заранее кодировать значение перед передачей в `URLSearchParams`, иначе можно получить double encoding.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли передать полный URL прямо в <code>new URLSearchParams(...)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Конструктор `URLSearchParams` не разбирает переданную строку как полный URL. Он ожидает query string или набор пар ключей и значений.

```js
new URLSearchParams("https://example.com/?page=2");
```

В таком случае часть `https://example.com/?page` будет воспринята как имя параметра, а не как адрес.

Для полного URL сначала создают объект `URL`:

```js
const url = new URL("https://example.com/?page=2");
const params = url.searchParams;
```

Начальный символ `?` у обычной query string можно передавать: конструктор удалит его при разборе.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему изменение <code>searchParams</code> иногда меняет вид кодирования URL?</strong></summary>

<dl>
<dd>
<h2></h2>

`URL.search` и `URLSearchParams` используют совместимые, но не полностью одинаковые правила сериализации.

После изменения или сортировки параметров URL может быть нормализован. Например, пробел, первоначально записанный как `%20`, после сериализации через `URLSearchParams` может стать `+`.

```js
url.searchParams.sort();
```

Смысл параметра при этом не меняется, но строковое представление URL может отличаться.

Поэтому подпись запроса, cache key или сравнение URL нельзя строить на предположении, что исходный текст сохранится байт в байт после изменения `searchParams`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что произойдёт при reload или прямом открытии SPA URL?</strong></summary>

<dl>
<dd>
<h2></h2>

`pushState` меняет путь только в уже загруженном документе и в этот момент не отправляет запрос серверу.

Но при reload или прямом открытии адреса браузер выполняет обычный запрос по текущему пути:

```text
/catalog/items?page=2
```

Сервер должен уметь обработать этот адрес: вернуть соответствующую серверную страницу или entry HTML SPA, после чего клиентский router восстановит нужный экран.

Если сервер знает только путь `/`, прямое открытие вложенного маршрута может закончиться `404`.

Для SPA на статическом сервере обычно настраивают fallback всех клиентских маршрутов на основной HTML-файл. Альтернативой может быть hash routing, потому что fragment после `#` не отправляется серверу, но у такого подхода другая структура URL и свои ограничения.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли напрямую вызывать History API в React или Next.js?</strong></summary>

<dl>
<dd>
<h2></h2>

Если приложение использует router, обычно применяют его публичный API навигации.

Router может дополнительно управлять:

- состоянием React;
- вложенными layouts;
- загрузкой данных;
- scroll position;
- prefetch;
- server/client routing.

Прямой вызов `pushState` меняет адрес, но сам по себе не сообщает прикладной логике, какие компоненты и данные нужно обновить.

Поведение интеграции нативного History API зависит от router и его версии, поэтому следует использовать поддерживаемый им способ навигации.

History API всё равно важно понимать: router строит поверх него клиентскую историю, а Back и Forward приводят к переходам между её записями.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие security-ошибки бывают при работе с URL?</strong></summary>

<dl>
<dd>
<h2></h2>

Нельзя без проверки перенаправлять пользователя на адрес из query parameter:

```text
/login?redirect=https://attacker.example
```

Такой код может создать open redirect. Для внутренней навигации обычно разрешают только относительные same-origin paths. Если нужны внешние адреса, используют allowlist разрешённых origins.

Недостаточно только выполнить percent-encoding. Кодирование защищает структуру параметров, но не определяет, безопасно ли само назначение URL.

Перед использованием внешнего адреса его разбирают через `URL` и проверяют `protocol`, `origin` и назначение:

```js
const url = new URL(value, location.origin);

if (url.origin !== location.origin) {
  throw new Error("Недопустимый redirect");
}
```

Особенно важно не разрешать опасные схемы вроде `javascript:` там, где строка будет использоваться как адрес ссылки или перехода.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать конфликта URL state и component state?</strong></summary>

<dl>
<dd>
<h2></h2>

Для состояния, которое должно воспроизводиться по ссылке, назначают один источник истины — URL.

Router читает параметры адреса, проверяет значения, подставляет defaults и на их основе строит интерфейс.

Действие пользователя сначала формирует следующий URL:

```text
/catalog?sort=price&page=2
```

После этого интерфейс получает состояние из нового адреса.

Если независимо изменять URL и локальный component state, они могут разойтись. Например, Back изменит адрес, но фильтры останутся в предыдущем состоянии.

Локальный state можно использовать для временного состояния, которое не должно сохраняться в ссылке: открытого tooltip, состояния hover или незавершённого ввода до применения фильтра.

<h2></h2>
</dd>
</dl>

</details>

## Мини-задача

```js
const url = new URL("https://example.com/items?tag=js&tag=react&page=1");

url.searchParams.append("tag", "web api");
url.searchParams.set("page", "2");

console.log(url.searchParams.getAll("tag"));
console.log(url.search);
```

<details>
<summary><strong>Что важно в результате?</strong></summary>

<dl>
<dd>
<h2></h2>

`getAll("tag")` вернёт:

```js
["js", "react", "web api"]
```

`append` сохранит два существующих параметра `tag` и добавит третий в конец списка параметров.

`set("page", "2")` заменит существующее значение `page=1`, не создавая второй параметр `page`.

Пробел в значении `"web api"` будет сериализован как `+`. Значение `url.search` будет:

```text
?tag=js&tag=react&page=2&tag=web+api
```

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Источник истины | Что учитывать |
| --- | --- | --- |
| Фильтры и pagination | Query parameters | Валидация, defaults, повторяющиеся keys |
| SPA navigation | Framework router | Back/Forward и scroll behavior |
| Техническая нормализация | `replaceState` через router | Не создавать лишний history step |
| Shareable view | URL | Экран должен восстановиться после reload |
| Redirect | Проверенный URL | Same-origin или allowlist |
| SSR | URL запроса | Не использовать `window.location` на сервере |

## Связанные темы

- [19 JSON serialization](<./19 JSON serialization.md>)
- [35 localStorage sessionStorage IndexedDB](<./35 localStorage sessionStorage IndexedDB.md>)
- [04 Структура URL и origin](<../Web Basics/04 Структура URL и origin.md>)
- [09 SPA MPA и способы рендеринга](<../Web Basics/09 SPA MPA и способы рендеринга.md>)
- [09 Динамические маршруты и metadata](<../Next.js/09 Динамические маршруты и metadata.md>)
- [11 Безопасность окон iframe и внешних ссылок](<../Security/11 Безопасность окон iframe и внешних ссылок.md>)

## Источники

- [MDN: `URL`](https://developer.mozilla.org/en-US/docs/Web/API/URL)
- [MDN: `URLSearchParams`](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)
- [MDN: History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API)
- [MDN: `popstate`](https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event)
- [HTML Standard: session history](https://html.spec.whatwg.org/multipage/nav-history-apis.html#the-history-interface)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 36 EventTarget и пользовательские события](<./36 EventTarget и пользовательские события.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [38 Web Workers и передача данных →](<./38 Web Workers и передача данных.md>)
<!-- CARD-NAV-BOTTOM:END -->
