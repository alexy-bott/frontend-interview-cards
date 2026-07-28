# Кэширование Data Cache Full Route Cache Router Cache

<!-- CARD-NAV-TOP:START -->
[← 05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Server Actions forms mutations revalidatePath revalidateTag →](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Какие уровни кэширования есть в Next.js 14 App Router и как они связаны?**

<h2></h2>

<br>
<dl>
<dd>

В Next.js 14 нужно различать четыре механизма. Они хранят разные результаты, живут в разных местах и обновляются разными API.

| Механизм | Что хранит | Где | Срок |
| --- | --- | --- | --- |
| Request Memoization | Результат одинакового GET `fetch` | Память серверного рендеринга | Один проход рендеринга |
| Data Cache | Результаты загрузки данных | Сервер или платформа | Между запросами и развёртываниями |
| Full Route Cache | HTML и RSC Payload статического маршрута | Сервер или платформа | До revalidation или нового развёртывания |
| Router Cache | RSC Payload посещённых и предварительно загруженных сегментов | Память браузера | Сессия или внутренний таймер |

Request Memoization, или мемоизация запроса, является возможностью React. Во время рендеринга дерева одинаковый GET `fetch` выполняется один раз. После завершения серверного рендеринга запись исчезает. Механизм работает в React-компонентах и функциях metadata, но не в Route Handlers.

Data Cache хранит данные между запросами. В Next.js 14 серверный `fetch` по умолчанию кэшируется, если маршрут не переведён в динамический контекст. Кэш обновляют через `next.revalidate`, `revalidateTag`, `revalidatePath` или обходят через `no-store`.

Full Route Cache хранит результат статического рендеринга: HTML и RSC Payload. Динамические маршруты в него не попадают. При обновлении Data Cache зависимый маршрут выполняется заново и его Full Route Cache заменяется. Новое развёртывание очищает Full Route Cache, но Data Cache может сохраниться, если это поддерживает платформа.

Router Cache находится в браузере и разбит по сегментам маршрута. Он ускоряет переходы, prefetch, возврат назад и сохраняет общие layouts без полной перезагрузки. В Next.js 14 автоматически сохранённые динамические сегменты обычно жили 30 секунд, а статические 5 минут; полная перезагрузка страницы очищает этот кэш в памяти.

`router.refresh()` очищает Router Cache текущего маршрута, запрашивает новый RSC Payload и объединяет его с клиентским деревом. Он не очищает Data Cache и Full Route Cache. Если сервер снова вернул закэшированные данные, refresh не сделает их свежими.

`revalidatePath` или `revalidateTag` в Server Action обновляют Data Cache, Full Route Cache и связанный Router Cache. Тот же вызов из Route Handler не может немедленно очистить Router Cache конкретной открытой страницы, потому что handler не связан с её клиентской сессией; результат обновится при следующем посещении или `router.refresh()`.

Кэш Next.js не заменяет HTTP-кэш браузера, CDN-кэш и клиентский кэш серверного состояния RTK Query. Каждому уровню нужны собственные правила. Частая ошибка состоит в вызове `router.refresh()` при устаревшем Data Cache или в хранении персональных данных под общим ключом кэша.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Data Cache отличается от Full Route Cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Data Cache хранит результат получения данных. Full Route Cache хранит уже сформированные HTML и RSC Payload статического маршрута. Динамический маршрут может использовать Data Cache без Full Route Cache. Обновление данных вызывает повторный серверный рендеринг и тем самым обновляет результат зависимого маршрута.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Request Memoization отличается от Data Cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Memoization устраняет одинаковую работу только внутри текущего рендеринга и затем исчезает. Data Cache переиспользуется разными серверными запросами. Memoization не требует revalidation, а Data Cache должен иметь правило срока жизни или событийного обновления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что хранит Router Cache?</strong></summary>

<dl>
<dd>
<h2></h2>

Он хранит RSC Payload посещённых и предварительно загруженных сегментов маршрута в памяти браузера. Это позволяет менять только изменившиеся части дерева, сохранять layouts и не выполнять полную загрузку документа. Он не является исходным хранилищем backend-данных.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>router.refresh()</code> может не показать новые данные?</strong></summary>

<dl>
<dd>
<h2></h2>

Он запрашивает новый результат серверного рендеринга, но не очищает Data Cache. Если `fetch` всё ещё возвращает сохранённое значение, новый RSC Payload будет содержать те же данные. Сначала нужно корректно выполнить `revalidateTag`, `revalidatePath` или не кэшировать источник.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли динамический route все его <code>fetch</code> динамическими?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Маршрут не хранится в Full Route Cache и выполняется на каждый запрос, но отдельный `fetch` с `force-cache` может продолжать использовать Data Cache. Это позволяет сочетать персональную оболочку и общие кэшируемые данные.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что происходит с кэшем после deployment?</strong></summary>

<dl>
<dd>
<h2></h2>

Full Route Cache очищается, потому что он относится к конкретной сборке. Data Cache по модели Next.js 14 может переживать развёртывание, если платформа это поддерживает. При self-hosting, то есть самостоятельном размещении, поведение зависит от хранилища и числа экземпляров, поэтому общий cache handler настраивают отдельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли отключить Router Cache?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 14 полностью отключить его нельзя. Можно отказаться от автоматического prefetch у `Link`, но посещённые сегменты всё равно временно сохраняются для клиентской навигации. Для текущего маршрута доступен `router.refresh()`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем кэш Next.js отличается от RTK Query?</strong></summary>

<dl>
<dd>
<h2></h2>

Next.js кэширует серверные данные и результат рендеринга до или во время отдачи страницы. RTK Query хранит серверное состояние в клиентском Redux store после загрузки JavaScript и управляет подписками компонентов. Один и тот же ресурс не нужно бессистемно копировать во все уровни без правил инвалидации, то есть признания данных устаревшими.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Симптом | Что проверить |
| --- | --- |
| Один GET повторяется внутри page и layout | Request Memoization |
| Backend вызывается на каждый серверный запрос | Data Cache и `no-store` |
| Маршрут не выполняется заново | Full Route Cache |
| После навигации виден прежний сегмент | Router Cache |
| `router.refresh()` не обновил данные | Data Cache |
| Разные containers показывают разные версии | Общее хранилище кэша |

## Связанные темы

- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [10 Next.js 14 15 16 версии Turbopack Cache Components PPR](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>)
- [06 RTK Query createApi query mutation tags](<../State Management/06 RTK Query createApi query mutation tags.md>)

## Источники

- [Next.js 14 docs: Caching](https://nextjs.org/docs/14/app/building-your-application/caching)
- [Next.js 14 docs: Fetching, Caching, and Revalidating](https://nextjs.org/docs/14/app/building-your-application/data-fetching/fetching-caching-and-revalidating)
- [Next.js 14 docs: useRouter](https://nextjs.org/docs/14/app/api-reference/functions/use-router)
- [Next.js 14 docs: Deploying](https://nextjs.org/docs/14/app/building-your-application/deploying)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [07 Server Actions forms mutations revalidatePath revalidateTag →](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
<!-- CARD-NAV-BOTTOM:END -->
