# Next.js 14 15 16 версии Turbopack Cache Components PPR

<!-- CARD-NAV-TOP:START -->
[← 09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Pages Router getServerSideProps getStaticProps getStaticPaths →](<./11 Pages Router getServerSideProps getStaticProps getStaticPaths.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Что важно знать о Next.js 14 и какие изменения в Next.js 15 и 16 нельзя смешивать с этой версией?**

<h2></h2>

<br>
<dl>
<dd>

Ответ о Next.js должен быть привязан к версии, потому что между 14, 15 и 16 изменились значения по умолчанию, серверные API, сборщик модулей и модель кэширования. Для проекта на Next.js 14 основной ответ строится вокруг поведения этой версии, а более новые возможности называются отдельно.

| Тема | Next.js 14 | Next.js 15 | Next.js 16 |
| --- | --- | --- | --- |
| Server Actions | Стабильны | Интегрированы с API форм React 19 | Поддерживаются |
| Серверный `fetch` | Обычно кэшируется | Не кэшируется по умолчанию | Не кэшируется без явной настройки или Cache Components |
| GET Route Handler | Кэшируется при выполнении условий | Не кэшируется по умолчанию | Не кэшируется по умолчанию |
| `params`, `searchParams`, `cookies`, `headers` | Синхронные API | Переходят к `Promise` | Синхронная совместимость удалена |
| Turbopack | В основном `next dev --turbo` | Стабилен для разработки | По умолчанию для `dev` и `build` |
| PPR | Экспериментальная возможность | Остаётся экспериментальным | Входит в модель Cache Components |
| Middleware | `middleware.ts`, Edge Runtime | Middleware | `proxy.ts`, Node.js Runtime |
| React Compiler | Не является возможностью Next.js 14 | Экспериментальная интеграция | Стабильная настройка, выключена по умолчанию |

В Next.js 14 App Router уже поддерживает React Server Components, вложенные layouts, streaming, Route Handlers и стабильные Server Actions. Кэширование описывается четырьмя отдельными механизмами: Request Memoization, Data Cache, Full Route Cache и Router Cache. Серверный `fetch` обычно участвует в Data Cache, а для отказа от кэширования используют `no-store`.

Turbopack является bundler, то есть сборщиком модулей, написанным на Rust. В Next.js 14 его прежде всего включали для локальной разработки командой `next dev --turbo`; production-сборка продолжала опираться на webpack. Поэтому совместимость webpack loaders и plugins с Turbopack нужно проверять отдельно.

PPR, Partial Prerendering или частичный предварительный рендеринг, объединяет статическую оболочку страницы и динамические участки под `Suspense`. Оболочка быстро отдаётся из статического результата, а динамические части формируются для запроса и передаются потоком. В Next.js 14 PPR был экспериментальным и не должен описываться как обычное поведение App Router.

Next.js 15 перешёл на React 19 и сделал API запроса асинхронными. `params`, `searchParams`, `cookies()`, `headers()` и `draftMode()` стали возвращать Promise. Серверный `fetch` и GET Route Handlers перестали кэшироваться по умолчанию. `useFormState` заменён React hook `useActionState`. При миграции эти изменения способны повлиять на корректность и число запросов даже без изменения бизнес-логики.

В Next.js 16 Turbopack стал стандартным сборщиком для `next dev` и `next build`, а webpack выбирается явно через `--webpack`. Минимальная версия Node.js поднята до 20.9. `middleware.ts` переименован в `proxy.ts`; новый Proxy использует Node.js Runtime, а не Edge Runtime.

Next.js 16 также ввёл Cache Components как единую явную модель для PPR и кэшируемых участков. Её включают через `cacheComponents: true`, а функции или компоненты отмечают директивой `"use cache"`. Срок и tags, то есть метки кэша, задают через `cacheLife` и `cacheTag`. Это не синтаксис Next.js 14 и его нельзя использовать для объяснения старой модели без оговорки.

React Compiler анализирует React-код во время сборки и может автоматически добавлять эквивалент мемоизации там, где это безопасно. В Next.js 16 интеграция доступна через стабильную настройку `reactCompiler`, но она выключена по умолчанию. React Compiler не является частью Next.js 14 и не отменяет необходимость правильно проектировать состояние, эффекты и границы компонентов.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему ответы о кэшировании <code>fetch</code> в Next.js 14 и 15 различаются?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 14 серверный `fetch` обычно кэшируется в Data Cache, если код не перешёл в динамический контекст. В Next.js 15 запрос не кэшируется по умолчанию и требует явного `cache: "force-cache"` или настройки сегмента. Поэтому совет без названной версии может быть прямо противоположным нужному поведению.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему в новых примерах <code>params</code> нужно <code>await</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В Next.js 15 API, зависящие от запроса, стали асинхронными. В Next.js 14 `params` и `searchParams` являются обычными объектами. Версия 15 временно сохраняла совместимый синхронный доступ с предупреждениями, а в Next.js 16 эта совместимость удалена.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Turbopack и полностью ли он заменил webpack?</strong></summary>

<dl>
<dd>
<h2></h2>

Turbopack является сборщиком модулей, оптимизированным для быстрой разработки и инкрементальной работы. В Next.js 14 он применялся прежде всего в `next dev --turbo`, а production-сборка использовала webpack. В Next.js 16 Turbopack стал стандартным и для сборки, но webpack всё ещё можно выбрать флагом `--webpack`, если проект зависит от его конфигурации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое PPR и чем он отличается от обычного streaming?</strong></summary>

<dl>
<dd>
<h2></h2>

Streaming передаёт готовые части серверного ответа по мере их формирования. PPR дополнительно сохраняет статическую оболочку заранее, а динамические участки формирует на запросе под границами `Suspense`. То есть streaming является способом доставки, а PPR определяет сочетание статического и динамического рендеринга одной страницы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Cache Components в Next.js 16?</strong></summary>

<dl>
<dd>
<h2></h2>

Это модель, в которой маршрут по умолчанию может содержать динамический код, а выбранные функции и компоненты явно помещаются в кэш через `"use cache"`. `cacheLife` задаёт срок, `cacheTag` связывает данные с меткой, а границы `Suspense` отделяют динамические части. Она заменяет прежнюю экспериментальную настройку PPR, но не относится к Next.js 14.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>revalidateTag</code> и <code>updateTag</code> в Next.js 16 отличаются по назначению?</strong></summary>

<dl>
<dd>
<h2></h2>

`revalidateTag` с cache profile, то есть профилем кэша, применяет модель stale-while-revalidate: устаревшее значение можно показать, пока новое загружается в фоне. `updateTag` разрешён только в Server Actions и немедленно помечает tag истёкшим, чтобы следующее чтение после изменения данных увидело новую запись. Это различие появилось в новой модели, а не в Next.js 14.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>middleware.ts</code> переименовали в <code>proxy.ts</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Новое имя подчёркивает, что код работает на сетевой границе перед маршрутом и не должен превращаться в универсальный слой бизнес-логики. Для Next.js 14 корректно говорить Middleware и Edge Runtime. В Next.js 16 Proxy выполняется в Node.js Runtime, поэтому миграция требует проверки зависимостей и инфраструктуры.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Является ли React Compiler частью Next.js 14?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. В Next.js 16 появилась стабильная, но выключенная по умолчанию настройка интеграции. Compiler выполняет статический анализ и сокращает необходимость в ручных `useMemo`, `useCallback` и `memo` там, где может доказать безопасность, но не исправляет неправильную архитектуру состояния или побочные эффекты.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Что проверить первым |
| --- | --- |
| Пример из свежей документации не собирается в проекте | Версию Next.js |
| После миграции выросло число запросов | Значения по умолчанию у `fetch` и GET handlers |
| TypeScript требует `await params` | Переход на Next.js 15/16 |
| Пользовательская webpack config перестала работать | Фактический сборщик |
| В статье используется `"use cache"` | Это модель Next.js 16 |
| Проект содержит `middleware.ts` | Для Next.js 14 это ожидаемо |

## Связанные темы

- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [06 Кэширование Data Cache Full Route Cache Router Cache](<./06 Кэширование Data Cache Full Route Cache Router Cache.md>)
- [07 Server Actions forms mutations revalidatePath revalidateTag](<./07 Server Actions forms mutations revalidatePath revalidateTag.md>)
- [08 Route Handlers Middleware Edge и Node runtime](<./08 Route Handlers Middleware Edge и Node runtime.md>)
- [19 React 18 19 и 19.2](<../React/19 React 18 19 и 19.2.md>)

## Источники

- [Next.js 14 announcement](https://nextjs.org/blog/next-14)
- [Next.js docs: Upgrading to version 15](https://nextjs.org/docs/app/guides/upgrading/version-15)
- [Next.js docs: Upgrading to version 16](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Next.js docs: Cache Components](https://nextjs.org/docs/app/getting-started/cache-components)
- [Next.js docs: React Compiler](https://nextjs.org/docs/app/api-reference/config/next-config-js/reactCompiler)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [11 Pages Router getServerSideProps getStaticProps getStaticPaths →](<./11 Pages Router getServerSideProps getStaticProps getStaticPaths.md>)
<!-- CARD-NAV-BOTTOM:END -->
