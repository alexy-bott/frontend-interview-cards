# URL URLSearchParams History API

<!-- CARD-NAV-TOP:START -->
[← 36 CustomEvent EventTarget dispatchEvent](<./36 CustomEvent EventTarget dispatchEvent.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [38 Web Workers postMessage structured clone →](<./38 Web Workers postMessage structured clone.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работать с URL и query parameters? Как History API меняет адрес SPA без перезагрузки?**

<h2></h2>

<br>
<dl>
<dd>

`URL` разбирает адрес по стандартным правилам и предоставляет его части: `protocol`, `origin`, `hostname`, `port`, `pathname`, `search` и `hash`. Второй аргумент задаёт base для относительного адреса, что безопаснее ручной склейки строк.

```js
const url = new URL("/catalog?sort=price", "https://example.com");

url.searchParams.set("page", "2");
console.log(url.href);
// https://example.com/catalog?sort=price&page=2
```

`URLSearchParams` управляет query string: `get`, `getAll`, `has`, `set`, `append`, `delete`, `sort`. Он кодирует имена и значения по правилам `application/x-www-form-urlencoded`, где пробел при сериализации обычно становится `+`. `set` заменяет все значения имени одним, а `append` сохраняет повторяющийся параметр.

Query parameters хорошо подходят состоянию, которое должно переживать reload, участвовать в Back/Forward и открываться по ссылке: фильтры, pagination, sorting, активная вкладка. UI должен уметь восстановиться из URL, а не считать его только побочным выводом внутреннего state.

`history.pushState(state, "", url)` добавляет запись session history без полной navigation. `replaceState` меняет текущую запись. Оба метода требуют same-origin URL, не загружают страницу и сами не перерисовывают UI. Router обновляет route state и data loading поверх этих примитивов.

`popstate` возникает, когда пользователь или код переходит к другой history entry через Back, Forward или `history.go`. Непосредственный `pushState` и `replaceState` это событие не вызывают.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем <code>pushState</code> отличается от <code>replaceState</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`pushState` создаёт новый шаг, поэтому Back возвращает предыдущую запись. `replaceState` переписывает текущий шаг. Реальный переход, например смена карточки товара, обычно использует push; техническая нормализация, удаление одноразового параметра или исправление default `page=1` часто использует replace, чтобы не засорять историю.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что хранится в <code>history.state</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Данные, переданные в активную запись через `pushState` или `replaceState`. Они проходят structured serialization и должны быть сериализуемыми. Browser может ограничивать размер, а state относится к конкретной history entry. Воспроизводимое состояние лучше хранить в самом URL; state подходит дополнительным данным навигации, которые не должны попадать в адрес.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>popstate</code> отличается от <code>hashchange</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`popstate` сообщает переход между history entries. `hashchange` возникает при изменении fragment через navigation или `location.hash`. Вызов `pushState` не вызывает ни `popstate`, ни `hashchange`, даже если новый URL отличается hash; router сам обрабатывает свой вызов и отдельно слушает будущий Back/Forward.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>location.assign</code>, <code>replace</code> и изменение <code>href</code> отличаются от History API?</strong></summary>

<dl>
<dd>
<h2></h2>

`location.assign(url)` и присваивание `location.href` запускают navigation и добавляют запись. `location.replace(url)` запускает navigation, но заменяет текущую запись. History API меняет URL текущего document без сетевой navigation; приложение само обновляет экран.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как работать с повторяющимися query parameters?</strong></summary>

<dl>
<dd>
<h2></h2>

`?tag=js&tag=react` является допустимым URL. `get("tag")` вернёт первое значение, `getAll("tag")` оба. `set("tag", value)` удалит остальные, а `append` добавит ещё одно. Клиент и backend должны договориться, представляется ли список повторением ключа, строкой с разделителем или другим форматом.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя собирать query string вручную?</strong></summary>

<dl>
<dd>
<h2></h2>

Значения могут содержать пробел, `&`, `=`, `#`, Unicode и уже закодированные последовательности. Ручная склейка легко смешивает данные с синтаксисом URL и приводит к double encoding. `URL` и `URLSearchParams` отделяют структуру от значения и правильно сериализуют её.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли передать полный URL прямо в <code>new URLSearchParams(...)</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет в смысле автоматического разбора адреса. Конструктор ожидает только query string или набор пар и воспримет префикс `https://...` как часть имени первого параметра. Сначала создают `new URL(fullUrl)`, затем используют `.searchParams`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему изменение <code>searchParams</code> иногда меняет вид кодирования URL?</strong></summary>

<dl>
<dd>
<h2></h2>

`URL.search` и `URLSearchParams` используют совместимые, но не полностью одинаковые правила сериализации. Даже вызов `sort()` может нормализовать пробелы и часть символов, например `%20` в `+`, не меняя смысл параметров. Подпись URL и cache key нельзя строить на предположении, что исходное текстовое представление сохранится байт в байт.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли напрямую вызывать History API в React или Next.js?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычно используют router framework. Он синхронизирует React state, layouts, data fetching, scroll, prefetch и server/client routing. Прямой `pushState` может изменить address bar в обход router и оставить UI в старом route. Понимание History API всё равно нужно для Back/Forward и интеграций.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие security-ошибки бывают при работе с URL?</strong></summary>

<dl>
<dd>
<h2></h2>

Не следует без проверки перенаправлять пользователя на URL из query parameter: это создаёт open redirect. Для внутреннего redirect разрешают только same-origin path или allowlist origins. Также нельзя вставлять непроверенную строку в `href` и считать percent-encoding защитой от опасной схемы; URL нужно разобрать и проверить `protocol`, origin и назначение.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как избежать конфликта URL state и component state?</strong></summary>

<dl>
<dd>
<h2></h2>

Назначить один источник истины для воспроизводимых параметров. Router читает URL, валидирует значения, подставляет defaults и строит UI. Действие пользователя создаёт следующий URL, а не независимо меняет два state. Иначе Back меняет адрес, но фильтры остаются прежними.

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

`getAll("tag")` вернёт `['js', 'react', 'web api']`. `page=1` будет заменён на `page=2`, а пробел в новом значении сериализуется как `+`: `tag=web+api`. Повторяющиеся `tag` сохраняются, потому что использован `append`.

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
- [04 URL origin domain path query fragment](<../Web Basics/04 URL origin domain path query fragment.md>)
- [09 SPA MPA CSR routing](<../Web Basics/09 SPA MPA CSR routing.md>)
- [09 Dynamic routes params searchParams metadata](<../Next.js/09 Dynamic routes params searchParams metadata.md>)
- [11 postMessage iframe open redirect tabnabbing](<../Security/11 postMessage iframe open redirect tabnabbing.md>)

## Источники

- [MDN: `URL`](https://developer.mozilla.org/en-US/docs/Web/API/URL)
- [MDN: `URLSearchParams`](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)
- [MDN: History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API)
- [MDN: `popstate`](https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event)
- [HTML Standard: session history](https://html.spec.whatwg.org/multipage/nav-history-apis.html#the-history-interface)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 36 CustomEvent EventTarget dispatchEvent](<./36 CustomEvent EventTarget dispatchEvent.md>) · [↑ JavaScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [38 Web Workers postMessage structured clone →](<./38 Web Workers postMessage structured clone.md>)
<!-- CARD-NAV-BOTTOM:END -->
