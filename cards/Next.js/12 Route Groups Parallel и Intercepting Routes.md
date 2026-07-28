# 12 Route Groups Parallel и Intercepting Routes

<!-- CARD-NAV-TOP:START -->
[← 11 Pages Router getServerSideProps getStaticProps getStaticPaths](<./11 Pages Router getServerSideProps getStaticProps getStaticPaths.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Image Font Link Script и оптимизация →](<./13 Image Font Link Script и оптимизация.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Для чего в App Router нужны Route Groups, Parallel Routes и Intercepting Routes? Как с их помощью сделать модальное окно с отдельным URL?

#### Ответ

Route Groups, Parallel Routes и Intercepting Routes управляют структурой интерфейса, не добавляя обычные видимые части URL. Они решают разные задачи и часто используются вместе в сложной навигации.

Route Group, то есть группа маршрутов, обозначается каталогом в круглых скобках: `app/(shop)/products/page.tsx`. Имя `(shop)` не попадает в URL, поэтому страница остаётся доступна по `/products`. Группы позволяют упорядочить большой каталог `app`, применить разные layouts к группам страниц или создать несколько корневых layouts.

Если приложение имеет несколько корневых layouts, переход между ними приводит к полной загрузке документа. Кроме того, две группы не могут создать один и тот же итоговый URL: `(shop)/about/page.tsx` и `(marketing)/about/page.tsx` конфликтуют.

Parallel Routes, то есть параллельные маршруты, обозначаются именованными slots вида `@analytics` и `@team`. Slot является независимой областью маршрутизации и не создаёт сегмент URL. Next.js передаёт его содержимое в layout как отдельный prop, поэтому одна страница может независимо показывать несколько областей:

```tsx
export default function DashboardLayout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  team: React.ReactNode;
}) {
  return (
    <>
      {children}
      {analytics}
      {team}
    </>
  );
}
```

При мягкой клиентской навигации Next.js сохраняет активное состояние slot, который не совпал с новым URL. При полной перезагрузке восстановить его невозможно, поэтому для каждого такого slot нужен `default.tsx`. Он показывает fallback, то есть запасное содержимое, либо вызывает `notFound()`.

Intercepting Route, то есть перехватывающий маршрут, позволяет показать страницу другого URL внутри текущего layout. Обозначения `(.)`, `(..)`, `(..)(..)` и `(...)` указывают путь относительно сегментов маршрута, а не количества каталогов в файловой системе. `(.)photo` перехватывает соседний сегмент `photo`, `(..)photo` поднимается на один сегмент, а `(...)photo` начинает поиск от корня `app`.

Типичный пример объединяет Parallel и Intercepting Routes. В layout есть slot `@modal`. При переходе из галереи по ссылке `/photo/42` перехватывающий маршрут показывает карточку в модальном окне поверх галереи, сохраняя её состояние. Если пользователь сразу откроет `/photo/42` или обновит страницу, обычный маршрут покажет полноценную страницу. URL в обоих случаях остаётся настоящим и подходит для истории браузера и прямой ссылки.

Закрытие такого модального окна обычно вызывает `router.back()`: история возвращает пользователя к исходной галерее. Дополнительно slot должен иметь маршрут, который возвращает `null`, чтобы модальное окно исчезало при навигации, не связанной с историей открытия.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Чем Route Group отличается от обычного каталога?
>
> **Ответ:** Обычный каталог создаёт сегмент URL, а имя группы в круглых скобках из URL удаляется. Группа влияет только на организацию файлов и наследование layouts. Это позволяет иметь `(marketing)/pricing` и получать `/pricing`, но итоговые URL во всех группах всё равно должны быть уникальными.

> [!followup]
> **Вопрос:** Что такое slot в Parallel Routes?
>
> **Ответ:** Slot является именованной областью layout, созданной каталогом `@name`. Next.js передаёт её как React prop рядом с `children`. Slot позволяет независимо выбирать маршрут и состояния loading/error для части экрана, но его имя не отображается в адресной строке.

> [!followup]
> **Вопрос:** Зачем slot нужен `default.tsx`?
>
> **Ответ:** При клиентской навигации Next.js помнит предыдущее состояние несовпавшего slot. После полной перезагрузки этой памяти нет, и по одному URL фреймворк не всегда может определить содержимое всех slots. `default.tsx` задаёт безопасный fallback вместо ошибки 404 для всей страницы.

> [!followup]
> **Вопрос:** Чем Parallel Routes отличаются от обычных React-компонентов в layout?
>
> **Ответ:** Обычные компоненты не имеют собственной маршрутизации. Slot может содержать собственные pages, loading, error и состояние навигации, которые Next.js выбирает по URL. Parallel Routes оправданы, когда область действительно должна жить как независимое маршрутное поддерево, а не просто когда layout содержит несколько блоков.

> [!followup]
> **Вопрос:** Что именно перехватывает Intercepting Route?
>
> **Ответ:** Он перехватывает навигацию к другому маршруту и отображает его содержимое внутри текущего layout при мягком переходе через router Next.js. Прямое открытие или перезагрузка обходят этот вариант и показывают каноническую страницу целевого URL. Поэтому один ресурс получает контекстное и самостоятельное представление.

> [!followup]
> **Вопрос:** Почему обозначение `(..)` считает сегменты маршрута, а не каталоги?
>
> **Ответ:** Каталоги `@slot` и `(group)` не добавляют сегменты URL. Если считать физические уровни, путь зависел бы от технической организации файлов. Next.js считает только сегменты маршрута, поэтому рефакторинг групп и slots не должен менять смысл перехвата.

> [!followup]
> **Вопрос:** Что нужно учесть при реализации модального окна через маршрутизацию?
>
> **Ответ:** Нужно управлять focus, закрытием по Escape, возвратом focus к элементу открытия и блокировкой фонового взаимодействия. Модальное окно должно корректно закрываться при back/forward и при переходе на другую страницу. Для этого обычно используют доступный Dialog из Radix UI и отдельный маршрут, который возвращает `null` для slot.

#### Где это встречается во frontend

| Сценарий | Механизм |
| --- | --- |
| Разные layouts для магазина и личного кабинета | Route Groups |
| Dashboard с независимо меняющимися областями | Parallel Routes |
| Фото поверх галереи с сохраняемым URL | Parallel и Intercepting Routes |
| Login modal поверх текущей страницы | Intercepting Route |
| Прямая ссылка на содержимое modal | Обычный канонический маршрут |

#### Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>)
- [06 Dialog dropdown overlay accessibility](<../Accessibility/06 Dialog dropdown overlay accessibility.md>)
- [13 Portal](<../React/13 Portal.md>)

#### Источники

- [Next.js 14 docs: Route Groups](https://nextjs.org/docs/14/app/building-your-application/routing/route-groups)
- [Next.js 14 docs: Parallel Routes](https://nextjs.org/docs/14/app/building-your-application/routing/parallel-routes)
- [Next.js 14 docs: Intercepting Routes](https://nextjs.org/docs/14/app/building-your-application/routing/intercepting-routes)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 11 Pages Router getServerSideProps getStaticProps getStaticPaths](<./11 Pages Router getServerSideProps getStaticProps getStaticPaths.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Image Font Link Script и оптимизация →](<./13 Image Font Link Script и оптимизация.md>)
<!-- CARD-NAV-BOTTOM:END -->
