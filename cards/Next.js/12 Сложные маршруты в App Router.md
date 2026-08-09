# Сложные маршруты в App Router

<!-- CARD-NAV-TOP:START -->
[← 11 Pages Router и загрузка данных](<./11 Pages Router и загрузка данных.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Оптимизация ресурсов в Next.js →](<./13 Оптимизация ресурсов в Next.js.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Для чего в App Router нужны Route Groups, Parallel Routes и Intercepting Routes? Как с их помощью сделать модальное окно с отдельным URL?**

<h2></h2>

<br>
<dl>
<dd>

Route Groups, Parallel Routes и Intercepting Routes управляют структурой route tree и интерфейса, не добавляя свои служебные обозначения в URL.

Они решают разные задачи:

- Route Groups организуют маршруты и layouts;
- Parallel Routes одновременно показывают несколько независимых маршрутных областей;
- Intercepting Routes контекстно отображают существующий маршрут внутри другого layout.

Route Group, то есть группа маршрутов, обозначается каталогом в круглых скобках:

```text
app/(shop)/products/page.tsx
```

Имя `(shop)` не попадает в URL, поэтому страница доступна по адресу:

```text
/products
```

Route Groups позволяют:

- упорядочить большой каталог `app`;
- сгруппировать маршруты по разделу или команде;
- применить общий layout только к части маршрутов;
- создать несколько root layouts.

Например:

```text
app/
  (shop)/
    layout.tsx
    products/
      page.tsx
  (admin)/
    layout.tsx
    dashboard/
      page.tsx
```

Если приложение использует несколько root layouts без общего:

```text
app/layout.tsx
```

то корневой маршрут `/` должен находиться внутри одной из групп.

Переход между маршрутами разных root layouts приводит к полной загрузке документа.

Две группы также не могут создавать одинаковый итоговый URL:

```text
app/(shop)/about/page.tsx
app/(marketing)/about/page.tsx
```

Оба файла соответствуют `/about`, поэтому возникает конфликт маршрутов.

Parallel Routes, то есть параллельные маршруты, обозначаются именованными slots:

```text
@analytics
@team
@modal
```

Slot является независимой маршрутной областью и не создаёт сегмент URL.

Next.js передаёт slots в ближайший layout как React props:

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
      <main>{children}</main>
      <aside>{analytics}</aside>
      <section>{team}</section>
    </>
  );
}
```

`children` является неявным slot, соответствующим обычному дочернему маршруту.

Каждый именованный slot может иметь собственные:

- `page.tsx`;
- `loading.tsx`;
- `error.tsx`;
- `not-found.tsx`;
- вложенные маршруты.

Это позволяет независимо загружать, обрабатывать ошибки и отображать разные части одного экрана.

При soft navigation, то есть клиентском переходе через Next.js Router, фреймворк сохраняет активное состояние slot, который не совпал с новым URL.

Например, если изменился маршрут внутри `@team`, текущее содержимое `@analytics` может остаться на экране.

При hard navigation, то есть прямом открытии URL или полной перезагрузке, сохранённого клиентского состояния нет. Next.js не всегда может определить, какую страницу показать в несовпавшем slot.

Для такого случая используют:

```text
default.tsx
```

Он задаёт запасное содержимое:

```tsx
export default function Default() {
  return null;
}
```

Если `default.tsx` отсутствует для несовпавшего именованного slot, Next.js возвращает 404.

Intercepting Route, то есть перехватывающий маршрут, позволяет при клиентской навигации показать содержимое другого URL внутри текущего layout.

Используются обозначения:

| Обозначение | Что перехватывает |
| --- | --- |
| `(.)segment` | Сегмент на том же уровне |
| `(..)segment` | Сегмент на один уровень выше |
| `(..)(..)segment` | Сегмент на два уровня выше |
| `(...)segment` | Сегмент от корня `app` |

Эти уровни считаются относительно route segments, а не каталогов файловой системы.

Каталоги:

```text
@modal
(shop)
```

не добавляют сегменты URL и поэтому не учитываются как обычные уровни маршрута.

Обозначения `(.)` и `(..)` являются convention Intercepting Routes, а не Route Groups.

Типичный пример объединяет Parallel и Intercepting Routes, чтобы показать фотографию в modal с отдельным URL.

Структура может выглядеть так:

```text
app/
  layout.tsx
  page.tsx

  photo/
    [id]/
      page.tsx

  @modal/
    default.tsx

    (.)photo/
      [id]/
        page.tsx

    [...catchAll]/
      page.tsx
```

Обычный маршрут:

```text
app/photo/[id]/page.tsx
```

создаёт полноценную страницу:

```text
/photo/42
```

Перехваченный маршрут:

```text
app/@modal/(.)photo/[id]/page.tsx
```

использует тот же URL, но при клиентском переходе показывает содержимое внутри slot `@modal`.

Root layout принимает modal рядом с основной страницей:

```tsx
export default function RootLayout({
  children,
  modal,
}: {
  children: React.ReactNode;
  modal: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body>
        {children}
        {modal}
      </body>
    </html>
  );
}
```

Поведение зависит от вида навигации:

```text
Переход из галереи через <Link href="/photo/42">
→ URL меняется на /photo/42
→ галерея сохраняется
→ фотография открывается в modal

Прямое открытие /photo/42
→ показывается полноценная страница фотографии

Обновление /photo/42
→ показывается полноценная страница фотографии
```

Таким образом, URL остаётся настоящим:

- его можно скопировать;
- он участвует в истории браузера;
- back и forward восстанавливают навигацию;
- прямое открытие показывает самостоятельную страницу.

Канонический и перехваченный маршруты обычно используют общий компонент содержимого, чтобы не дублировать получение данных и разметку:

```tsx
// app/photo/[id]/page.tsx
import { PhotoDetails } from "@/features/photo/PhotoDetails";

export default function PhotoPage() {
  return <PhotoDetails />;
}
```

```tsx
// app/@modal/(.)photo/[id]/page.tsx
import { Modal } from "@/shared/ui/Modal";
import { PhotoDetails } from "@/features/photo/PhotoDetails";

export default function PhotoModalPage() {
  return (
    <Modal>
      <PhotoDetails />
    </Modal>
  );
}
```

Если modal был открыт через клиентскую навигацию, его обычно закрывают через:

```ts
router.back();
```

Это возвращает пользователя к исходной галерее и сохраняет корректную историю.

Для перехода на другой маршрут одного `router.back()` недостаточно. При soft navigation Next.js может сохранить прежнее содержимое несовпавшего slot.

Поэтому добавляют catch-all маршрут:

```text
app/@modal/[...catchAll]/page.tsx
```

который возвращает `null`:

```tsx
export default function CatchAll() {
  return null;
}
```

`default.tsx` задаёт неактивное состояние после hard navigation, а catch-all закрывает modal при soft navigation на другие маршруты.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Чем Route Group отличается от обычного каталога?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный каталог создаёт сегмент URL:

```text
app/shop/products/page.tsx
→ /shop/products
```

Имя Route Group в круглых скобках из URL исключается:

```text
app/(shop)/products/page.tsx
→ /products
```

Группа влияет только на:

- организацию файлов;
- наследование layouts;
- разделение приложения на root layouts.

Она не является частью адреса.

Это позволяет создать:

```text
app/(marketing)/pricing/page.tsx
```

и получить URL:

```text
/pricing
```

Итоговые URL во всех группах должны оставаться уникальными.

Если несколько групп имеют собственные root layouts, переход между ними вызывает полную загрузку документа.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое slot в Parallel Routes?</strong></summary>

<dl>
<dd>
<h2></h2>

Slot — именованная маршрутная область, созданная каталогом:

```text
@name
```

Например:

```text
app/dashboard/
  layout.tsx
  page.tsx
  @analytics/
    page.tsx
  @team/
    page.tsx
```

Layout получает slots как props:

```tsx
export default function Layout({
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

`children` является неявным slot.

Имя `@analytics` не отображается в адресной строке.

Slot может иметь собственные страницы, loading- и error-состояния и независимо участвовать в частичной навигации.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем slot нужен <code>default.tsx</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При soft navigation Next.js хранит активное состояние каждого slot в Router Cache.

Если новый URL не соответствует странице одного из slots, его прежнее содержимое может сохраниться.

После hard navigation этой памяти нет.

Next.js видит URL, но не всегда может определить прежнее состояние каждой параллельной области.

В таком случае он показывает:

```text
@slot/default.tsx
```

Например:

```tsx
export default function Default() {
  return null;
}
```

Если для несовпавшего именованного slot нет `default.tsx`, Next.js возвращает 404.

Для modal `default.tsx`, возвращающий `null`, означает, что при прямом открытии обычной страницы modal не должен отображаться.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем Parallel Routes отличаются от обычных React-компонентов в layout?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный React-компонент не имеет собственного маршрутного состояния.

Например:

```tsx
<Sidebar />
```

всегда выбирается непосредственно кодом layout.

Slot может содержать отдельное route tree:

```text
@analytics/
  page.tsx
  loading.tsx
  error.tsx
  reports/
    page.tsx
```

Next.js самостоятельно выбирает его содержимое в зависимости от навигации.

Parallel Routes позволяют каждой области иметь собственные:

- страницы;
- вложенные маршруты;
- loading-состояния;
- error boundaries;
- streaming;
- активное состояние.

Они оправданы, когда область действительно должна быть независимым маршрутным поддеревом.

Если layout просто содержит несколько статичных блоков, достаточно обычных React-компонентов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно перехватывает Intercepting Route?</strong></summary>

<dl>
<dd>
<h2></h2>

Intercepting Route перехватывает клиентскую навигацию к существующему маршруту.

Например, существует обычная страница:

```text
/photo/42
```

При переходе к ней через Next.js Router перехваченный вариант может отобразить её внутри modal текущего layout.

При этом:

- URL меняется на `/photo/42`;
- текущий контекст, например галерея, сохраняется;
- целевой интерфейс показывается поверх него.

При прямом открытии URL или полной перезагрузке перехват не применяется. Next.js показывает обычную каноническую страницу `/photo/42`.

Один ресурс таким образом получает два представления:

```text
soft navigation
→ контекстное представление в modal

hard navigation
→ самостоятельная страница
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему обозначение <code>(..)</code> считает сегменты маршрута, а не каталоги?</strong></summary>

<dl>
<dd>
<h2></h2>

Не каждый каталог в `app` создаёт часть URL.

Например:

- `@modal` является slot;
- `(shop)` является Route Group;
- оба каталога отсутствуют в URL.

Поэтому путь Intercepting Route рассчитывается относительно route segments.

Например:

```text
app/
  photo/
    [id]/
      page.tsx

  @modal/
    (.)photo/
      [id]/
        page.tsx
```

Хотя `photo` физически находится за пределами каталога `@modal`, используется `(.)photo`, потому что `@modal` не считается route segment.

Если бы Next.js считал физические каталоги, рефакторинг slots и Route Groups менял бы семантику URL.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что нужно учесть при реализации модального окна через маршрутизацию?</strong></summary>

<dl>
<dd>
<h2></h2>

Маршрутизация решает URL и историю, но не обеспечивает доступность modal автоматически.

Нужно реализовать:

- перевод focus внутрь modal;
- возврат focus к элементу открытия;
- закрытие по Escape;
- блокировку взаимодействия с фоном;
- корректную роль dialog;
- доступное название;
- блокировку или управление прокруткой;
- закрытие при back/forward;
- закрытие slot при переходе на другой маршрут.

Для открытия используют клиентскую навигацию через `Link` или Next.js Router.

Для возврата по истории:

```ts
router.back();
```

Для закрытия при переходе на произвольный другой маршрут slot должен сопоставиться с page, возвращающей `null`, например через:

```text
@modal/[...catchAll]/page.tsx
```

Чтобы не реализовывать focus management вручную, обычно используют готовый доступный Dialog, например Radix UI Dialog.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Механизм |
| --- | --- |
| Разные layouts для магазина и личного кабинета | Route Groups |
| Dashboard с независимо меняющимися областями | Parallel Routes |
| Фото поверх галереи с сохраняемым URL | Parallel и Intercepting Routes |
| Login modal поверх текущей страницы | Intercepting Route внутри slot |
| Прямая ссылка на содержимое modal | Обычный канонический маршрут |
| Закрытие modal при переходе на другой URL | Catch-all route в modal slot, возвращающий `null` |

## Связанные темы

- [02 Структура App Router](<./02 Структура App Router.md>)
- [09 Динамические маршруты и metadata](<./09 Динамические маршруты и metadata.md>)
- [06 Доступность модальных окон и меню](<../Accessibility/06 Доступность модальных окон и меню.md>)
- [13 Portal](<../React/13 Portal.md>)

## Источники

- [Next.js 14 docs: Route Groups](https://nextjs.org/docs/14/app/building-your-application/routing/route-groups)
- [Next.js 14 docs: Parallel Routes](https://nextjs.org/docs/14/app/building-your-application/routing/parallel-routes)
- [Next.js 14 docs: Intercepting Routes](https://nextjs.org/docs/14/app/building-your-application/routing/intercepting-routes)
- [Next.js 14 docs: Linking and Navigating](https://nextjs.org/docs/14/app/building-your-application/routing/linking-and-navigating)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 11 Pages Router и загрузка данных](<./11 Pages Router и загрузка данных.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [13 Оптимизация ресурсов в Next.js →](<./13 Оптимизация ресурсов в Next.js.md>)
<!-- CARD-NAV-BOTTOM:END -->
