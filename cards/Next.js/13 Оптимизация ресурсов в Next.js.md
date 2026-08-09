# Оптимизация ресурсов в Next.js

<!-- CARD-NAV-TOP:START -->
[← 12 Сложные маршруты в App Router](<./12 Сложные маршруты в App Router.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 Настройка и развёртывание Next.js →](<./14 Настройка и развёртывание Next.js.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как Next.js оптимизирует изображения, шрифты, навигацию и сторонние скрипты через `next/image`, `next/font`, `next/link` и `next/script`?**

<h2></h2>

<br>
<dl>
<dd>

Next.js предоставляет специальные компоненты для ресурсов, которые заметно влияют на:

- Largest Contentful Paint;
- Cumulative Layout Shift;
- объём загружаемых данных;
- выполнение JavaScript на главном потоке;
- скорость переходов между маршрутами;
- приватность и безопасность.

Основные инструменты:

| Инструмент | Основная задача |
| --- | --- |
| `next/image` | Размеры, responsive-версии, lazy loading и визуальная стабильность изображений |
| `next/font` | Self-hosting, preload и стабильные метрики шрифтов |
| `next/link` | Client-side navigation и prefetch маршрутов |
| `next/script` | Управление моментом и областью загрузки стороннего JavaScript |

Они не делают страницу быстрой автоматически.

Разработчик всё равно определяет:

- какой ресурс действительно нужен;
- какой размер подходит;
- когда начинать загрузку;
- где подключать скрипт;
- сколько вариантов шрифта использовать;
- оправдан ли автоматический prefetch;
- какие сторонние домены разрешены.

### `next/image`

`next/image` расширяет обычный HTML-элемент `<img>`.

```tsx
import Image from "next/image";

export function ProductImage() {
  return (
    <Image
      src="/products/phone.jpg"
      alt="Смартфон спереди"
      width={800}
      height={600}
    />
  );
}
```

Компонент помогает с несколькими задачами:

```text
визуальная стабильность
→ резервирует место до загрузки

size optimization
→ создаёт варианты разных размеров

responsive loading
→ браузер выбирает подходящий srcset

format optimization
→ может отдавать современный формат

lazy loading
→ откладывает невидимые изображения
```

#### `width` и `height`

Props:

```tsx
width={800}
height={600}
```

задают intrinsic size — исходные пропорции изображения.

Они нужны браузеру, чтобы заранее определить соотношение сторон и зарезервировать место.

Это уменьшает CLS:

```text
HTML получен
→ место под изображение уже известно
→ изображение загрузилось
→ соседний контент не сдвинулся
```

`width` и `height` не обязаны совпадать с фактическим размером изображения на экране.

Размер отображения может задаваться CSS:

```tsx
<Image
  src="/photo.jpg"
  alt="Горный пейзаж"
  width={1200}
  height={800}
  sizes="100vw"
  style={{
    width: "100%",
    height: "auto",
  }}
/>
```

Здесь:

```text
1200 × 800
→ intrinsic-пропорции

width: 100%
→ фактическая ширина контейнера
```

Если CSS изменяет только ширину, высоту обычно задают как:

```css
height: auto;
```

чтобы сохранить пропорции.

#### Локальный static import

При статическом импорте Next.js может определить размеры файла во время сборки:

```tsx
import Image from "next/image";
import productImage from "./product.jpg";

export function ProductImage() {
  return (
    <Image
      src={productImage}
      alt="Смартфон"
    />
  );
}
```

Next.js получает из файла:

- ширину;
- высоту;
- соотношение сторон;
- данные для blur placeholder у поддерживаемых растровых форматов.

Import должен быть статически анализируемым.

Динамическая строка:

```ts
const image =
  await import(
    `./images/${name}.jpg`
  );
```

не даёт тех же гарантий анализа.

#### Remote image

Для внешнего URL Next.js не знает размеры файла во время build.

Поэтому обычно указывают:

```tsx
<Image
  src={product.imageUrl}
  alt={product.name}
  width={800}
  height={600}
/>
```

или используют `fill`.

Если размеры внешнего изображения неизвестны, приложение должно получить их:

- из API;
- из metadata CMS;
- из базы данных;
- при загрузке файла;
- через заранее известную геометрию контейнера.

#### `fill`

`fill` используют, когда геометрию изображения определяет контейнер:

```tsx
<div className={styles.imageContainer}>
  <Image
    src={product.imageUrl}
    alt={product.name}
    fill
    sizes="(max-width: 768px) 100vw, 33vw"
    style={{
      objectFit: "cover",
    }}
  />
</div>
```

Контейнер должен иметь:

- определённые размеры или aspect ratio;
- подходящий containing block;
- обычно `position: relative`.

```css
.imageContainer {
  position: relative;
  aspect-ratio: 4 / 3;
}
```

Само изображение с `fill` обычно позиционируется абсолютно внутри контейнера.

`objectFit` определяет способ вписывания:

```text
cover
→ заполнить контейнер с возможной обрезкой

contain
→ показать изображение целиком
```

`fill` не создаёт высоту контейнера автоматически.

Если родитель не имеет стабильной геометрии, изображение может:

- получить нулевую высоту;
- растянуть layout;
- вызвать layout shift;
- отображаться в неожиданном размере.

#### `sizes`

`sizes` сообщает браузеру, какую приблизительную ширину изображение займёт при разных размерах viewport.

```tsx
sizes="
  (max-width: 768px) 100vw,
  (max-width: 1200px) 50vw,
  33vw
"
```

Браузер использует это значение вместе с `srcset`:

```text
viewport и device pixel ratio
→ sizes
→ выбрать подходящий файл
```

`sizes` особенно нужен, если:

- используется `fill`;
- изображение responsive;
- ширина меняется по breakpoints;
- изображение занимает только часть grid.

Без `sizes` браузер может предположить:

```text
изображение занимает 100vw
```

и скачать файл значительно шире реального блока.

Например, карточка занимает треть desktop-экрана:

```text
реальная ширина
→ 33vw

без sizes
→ браузер может выбрать вариант для 100vw
```

Это увеличивает:

- сетевой трафик;
- время декодирования;
- память;
- LCP.

`sizes` также влияет на набор вариантов, создаваемых в `srcset`.

Без `sizes` Next.js обычно создаёт ограниченный набор для фиксированного изображения:

```text
1x
2x
```

С `sizes` создаётся более полный набор width-descriptor вариантов:

```text
640w
750w
828w
1080w
...
```

#### `alt`

`alt` обязателен:

```tsx
<Image
  src="/product.jpg"
  alt="Белая игровая приставка"
/>
```

Он описывает смысл изображения для пользователя, который не видит его.

Декоративное изображение получает пустой `alt`:

```tsx
<Image
  src="/decoration.svg"
  alt=""
/>
```

`alt` не должен:

- начинаться со слов «изображение» или «картинка» без необходимости;
- повторять соседний caption;
- содержать техническое имя файла;
- быть пустым у смыслового контента.

`next/image` оптимизирует загрузку, но не может самостоятельно определить правильное текстовое описание.

#### Lazy loading

По умолчанию некритические изображения загружаются лениво:

```text
изображение далеко от viewport
→ запрос откладывается

изображение приближается
→ браузер начинает загрузку
```

Это уменьшает первоначальный трафик.

Lazy loading не следует применять к главному LCP-изображению, если из-за этого его обнаружение начинается слишком поздно.

#### LCP, `priority` и `preload`

В Next.js 14 и 15 для критического изображения использовался prop:

```tsx
<Image
  src="/hero.jpg"
  alt="Главный экран"
  width={1600}
  height={900}
  priority
/>
```

Начиная с Next.js 16, `priority` deprecated. Вместо него появился более явный prop:

```tsx
<Image
  src="/hero.jpg"
  alt="Главный экран"
  width={1600}
  height={900}
  preload
/>
```

`preload` добавляет в `<head>`:

```html
<link
  rel="preload"
  as="image"
/>
```

Он подходит, когда изображение:

- является известным LCP;
- находится на первом экране;
- должно начать загружаться до обнаружения `<img>` в body.

Использовать `preload` для всей галереи нельзя.

Иначе критические ресурсы начинают конкурировать:

```text
hero image
fonts
CSS
route data
десятки других изображений
```

В большинстве случаев достаточно рассмотреть:

```tsx
loading="eager"
```

или:

```tsx
fetchPriority="high"
```

Различие:

```text
preload
→ начать загрузку через link в head

loading="eager"
→ не применять lazy loading

fetchPriority="high"
→ повысить сетевой приоритет обнаруженного img
```

Не следует без необходимости одновременно задавать:

```text
preload
loading
fetchPriority
```

Решение выбирают по реальному waterfall в Network и результатам LCP.

Если для разных viewport LCP становятся разные изображения, бездумный preload обоих может привести к загрузке ненужного ресурса.

#### Placeholder

Для улучшения воспринимаемой загрузки можно использовать blur placeholder:

```tsx
<Image
  src={productImage}
  alt="Смартфон"
  placeholder="blur"
/>
```

Для remote image обычно нужно самостоятельно передать маленький `blurDataURL`:

```tsx
<Image
  src={product.imageUrl}
  alt={product.name}
  width={800}
  height={600}
  placeholder="blur"
  blurDataURL={product.blurDataUrl}
/>
```

Placeholder:

- не уменьшает фактическое время загрузки;
- не заменяет правильный размер;
- должен быть очень маленьким;
- не должен заметно увеличивать HTML.

Большой base64 placeholder способен сам стать лишним payload.

#### `remotePatterns`

Внешние изображения разрешают в `next.config.js`:

```ts
import type {
  NextConfig,
} from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname:
          "images.example.com",
        port: "",
        pathname:
          "/products/**",
        search: "",
      },
    ],
  },
};

export default nextConfig;
```

Проверяться могут:

```text
protocol
hostname
port
pathname
search
```

Правило должно быть максимально узким.

Например:

```text
https://images.example.com/products/**
```

безопаснее:

```text
любой URL с любого домена
```

Next.js Image Optimization API:

```text
получает внешний URL
→ загружает изображение
→ изменяет размер и качество
→ возвращает результат
```

Если разрешить произвольный источник, endpoint можно превратить в открытый proxy для обработки чужих ресурсов.

Старое свойство:

```text
images.domains
```

deprecated в пользу более точного `remotePatterns`.

#### `qualities` в Next.js 16

Image Optimization API может принимать параметр качества.

В Next.js 16 список разрешённых значений задаётся явно:

```ts
const nextConfig = {
  images: {
    qualities: [
      50,
      75,
      90,
    ],
  },
};
```

Это ограничивает количество вариантов, которые серверу разрешено генерировать.

Если prop:

```tsx
quality={90}
```

не совпадает с разрешённым значением, Next.js использует ближайшее допустимое качество для компонента либо отклоняет прямой неподходящий запрос к optimizer API.

Обычно не нужен большой набор quality values.

Каждая дополнительная комбинация:

```text
src
width
quality
format
```

может создавать отдельный вариант в кэше.

#### Защищённые изображения

Default Image Optimizer не пересылает произвольные headers к внешнему источнику.

Поэтому URL, требующий:

```text
Authorization header
cookie
```

может не загрузиться через стандартный optimizer.

Варианты:

- использовать временный signed URL;
- выдавать изображение через безопасную server-side границу;
- применить собственный loader;
- использовать `unoptimized`, если это соответствует модели безопасности.

```tsx
<Image
  src={privateImageUrl}
  alt="Закрытый документ"
  width={800}
  height={600}
  unoptimized
/>
```

`unoptimized` означает:

```text
отдать исходный src
без resize, quality и format optimization
```

Секрет нельзя помещать в публичный URL.

#### Где выполняется Image Optimization

При стандартном loader оптимизация выполняется во время request, а не заранее для всех вариантов во время build.

```text
browser запрашивает размер
→ Image Optimization API
→ получает или создаёт вариант
→ сохраняет его в cache
```

Это означает:

- первый запрос варианта может быть дороже;
- self-hosted server должен иметь ресурсы на resize;
- нескольким экземплярам нужен согласованный cache;
- CDN и cache headers влияют на результат;
- количество разрешённых размеров и quality влияет на нагрузку.

Для:

```ts
output: "export"
```

нет работающего Next.js Image Optimization API после build.

Варианты:

- custom loader внешнего image CDN;
- заранее подготовленные изображения;
- `images.unoptimized: true`.

Пример custom loader:

```ts
const nextConfig = {
  output: "export",
  images: {
    loader: "custom",
    loaderFile:
      "./image-loader.ts",
  },
};
```

### `next/font`

`next/font` оптимизирует Google Fonts и локальные font files.

Основные варианты:

```ts
import {
  Inter,
} from "next/font/google";

import localFont
  from "next/font/local";
```

Google Font:

```ts
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});
```

Локальный font:

```ts
const brandFont =
  localFont({
    src:
      "./fonts/brand.woff2",
    display: "swap",
  });
```

`next/font`:

- загружает Google Font во время build;
- self-hosts файлы вместе с приложением;
- создаёт `@font-face`;
- формирует preload;
- предоставляет `className` и CSS variable;
- настраивает fallback metrics;
- исключает запрос браузера к Google Fonts.

Упрощённо:

```text
build
→ скачать или прочитать font files
→ добавить их в application assets
→ создать CSS

browser
→ загружает font с приложения
```

Это уменьшает внешние сетевые соединения и улучшает приватность.

#### Подключение в App Router

Глобальный шрифт обычно подключают в root layout:

```tsx
import {
  Inter,
} from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="ru"
      className={
        inter.className
      }
    >
      <body>
        {children}
      </body>
    </html>
  );
}
```

#### Подключение в Pages Router

В Pages Router общий шрифт обычно применяется в `_app`:

```tsx
import {
  Inter,
} from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
});

export default function App({
  Component,
  pageProps,
}: AppProps) {
  return (
    <main
      className={
        inter.className
      }
    >
      <Component
        {...pageProps}
      />
    </main>
  );
}
```

#### CSS variable

Для design system удобно получить CSS variable:

```ts
const inter = Inter({
  subsets: ["latin"],
  variable:
    "--font-inter",
});
```

```tsx
<html
  className={
    inter.variable
  }
>
```

Затем:

```css
body {
  font-family:
    var(--font-inter),
    sans-serif;
}
```

Так можно сочетать несколько шрифтов:

```text
body font
heading font
monospace font
```

без жёсткой привязки каждого компонента к сгенерированному class name.

#### Variable fonts

Если доступен variable font, он часто выгоднее нескольких отдельных файлов.

Вместо:

```text
400.woff2
500.woff2
600.woff2
700.woff2
```

можно загрузить один variable font с диапазоном:

```text
100–900
```

Но variable font не всегда автоматически меньше любой конкретной комбинации.

Нужно сравнивать фактические файлы и используемые axes.

#### `subsets`

Google Fonts можно разделять на subsets:

```ts
const inter = Inter({
  subsets: ["latin"],
});
```

Subset ограничивает набор символов и уменьшает размер файла.

Нужно выбирать набор, который действительно покрывает контент.

Для русскоязычного интерфейса font должен содержать Cyrillic.

Если выбрать только:

```text
latin
```

браузер будет использовать fallback для кириллицы либо потребуется другой файл.

При включённом preload нужно явно указать нужные subsets.

#### Preload scope

Font preload зависит от места вызова font loader.

```text
font вызван в page
→ preload только для этого маршрута

font вызван в layout
→ preload для маршрутов этого layout

font вызван в root layout
→ preload для всего приложения
```

Поэтому редкий display font не обязательно подключать в root layout.

Иначе он будет загружаться на страницах, где не используется.

#### Метрики fallback

`next/font` может подбирать fallback font и корректировать его метрики, чтобы уменьшить смещение текста при замене.

Связанные настройки:

```text
fallback
adjustFontFallback
display
```

Например:

```ts
const font = Inter({
  subsets: ["latin"],
  display: "swap",
  fallback: [
    "Arial",
    "sans-serif",
  ],
});
```

Оптимизация не отменяет необходимость ограничивать:

- количество font families;
- веса;
- начертания;
- subsets;
- дополнительные variable axes.

Если загрузить множество начертаний, общий сетевой вес останется большим.

### `next/link`

`next/link` расширяет HTML-ссылку для внутренних переходов Next.js.

```tsx
import Link
  from "next/link";

<Link href="/products">
  Товары
</Link>
```

Компонент создаёт обычный `<a>` и сохраняет:

- семантику ссылки;
- открытие в новой вкладке;
- копирование URL;
- keyboard navigation;
- работу без JavaScript через обычный `href`.

При обычном внутреннем переходе Next.js выполняет client-side navigation:

```text
пользователь нажал Link
→ нет полной перезагрузки документа
→ router загружает нужные данные и chunks
→ React обновляет маршрут
```

Это позволяет переиспользовать:

- JavaScript runtime;
- layouts;
- Client Components;
- Router Cache;
- уже загруженные ресурсы.

#### Automatic prefetch

В production Next.js может заранее загрузить маршрут, когда `Link` попадает в viewport.

```text
Link стал видимым
→ route prefetch
→ пользователь нажал
→ часть работы уже выполнена
```

В development автоматический prefetch обычно отключён, чтобы не создавать лишние запросы и не мешать отладке.

#### App Router

В App Router default-поведение зависит от типа маршрута.

**Статический маршрут:**

```text
Link видим
→ prefetch полного маршрута и данных
```

**Динамический маршрут:**

```text
есть loading.tsx
→ prefetch layout и сегментов
  до ближайшей loading boundary

нет подходящей границы
→ полные динамические данные
  могут ожидать перехода
```

Prefetch может включать:

- RSC Payload;
- JavaScript chunks Client Components;
- общие layouts;
- статическую оболочку маршрута.

Результат хранится в client Router Cache ограниченное время и может быть инвалидирован.

Prefetch не означает, что все backend-данные навсегда сохранены в браузере.

#### Pages Router

В Pages Router prefetch обычно получает:

- JavaScript page;
- JSON page data;
- другие необходимые route assets.

Поведение prop отличается от App Router.

```tsx
<Link
  href="/dashboard"
  prefetch={false}
>
  Dashboard
</Link>
```

В Pages Router это отключает prefetch при попадании ссылки во viewport, но загрузка по hover всё ещё может произойти.

В App Router `prefetch={false}` отключает prefetch и при viewport, и при hover.

#### Значения `prefetch` в App Router

```text
null или "auto"
→ default-поведение:
  static route полностью,
  dynamic route частично

true
→ полный prefetch,
  включая dynamic route

false
→ автоматический prefetch отключён
```

Принудительный:

```tsx
prefetch={true}
```

нужно использовать осторожно для динамических персонализированных маршрутов, потому что он способен вызвать лишнюю серверную работу.

#### Когда отключать prefetch

Автоматический prefetch полезен не для каждой ссылки.

Например:

- бесконечный список;
- сотни строк таблицы;
- footer с большим количеством URL;
- ссылки, по которым редко переходят;
- дорогие динамические маршруты;
- ограниченный мобильный трафик.

```tsx
<Link
  href={`/posts/${post.id}`}
  prefetch={false}
>
  {post.title}
</Link>
```

Это уменьшает фоновый трафик, но увеличивает работу после клика.

Решение принимают по:

- вероятности перехода;
- размеру маршрута;
- стоимости server render;
- числу ссылок;
- сетевым условиям;
- измеренной задержке навигации.

#### Manual prefetch

В App Router маршрут можно подготовить вручную:

```tsx
"use client";

import {
  useRouter,
} from "next/navigation";

export function ProductCard() {
  const router =
    useRouter();

  return (
    <div
      onMouseEnter={() => {
        router.prefetch(
          "/products/42",
        );
      }}
    >
      ...
    </div>
  );
}
```

Manual prefetch полезен, если намерение пользователя видно раньше клика:

- hover;
- focus;
- начало многошагового процесса;
- завершение предыдущего шага.

Создавать собственную систему prefetch стоит только тогда, когда default-поведения недостаточно.

#### Side effects во время prefetch

Server Component или layout может выполниться во время предварительной загрузки маршрута.

Поэтому нельзя размещать непосредственный side effect в render:

```tsx
export default function Layout({
  children,
}: Props) {
  trackPageView();

  return children;
}
```

Analytics может отправиться при prefetch, хотя пользователь ещё не открыл страницу.

Побочные действия привязывают к фактическому lifecycle:

- `useEffect` Client Component;
- пользовательскому действию;
- Server Action;
- другой явной границе.

Render страницы и layout должен оставаться чистым.

### `next/script`

`next/script` управляет загрузкой и выполнением стороннего JavaScript.

```tsx
import Script
  from "next/script";

<Script
  src="https://example.com/widget.js"
  strategy="lazyOnload"
/>
```

Он помогает:

- выбрать момент загрузки;
- разместить script в нужном route scope;
- избежать повторной загрузки при навигации;
- выполнять callback после готовности;
- контролировать inline script;
- уменьшить влияние third-party code на main thread.

#### Область загрузки

Скрипт можно подключить на уровне конкретной page:

```tsx
export default function CheckoutPage() {
  return (
    <>
      <Checkout />
      <Script src="..." />
    </>
  );
}
```

Тогда он нужен только соответствующему маршруту.

В layout:

```tsx
export default function DashboardLayout({
  children,
}: Props) {
  return (
    <>
      {children}
      <Script src="..." />
    </>
  );
}
```

он применяется ко всем вложенным маршрутам layout.

В root layout:

```tsx
export default function RootLayout({
  children,
}: Props) {
  return (
    <html lang="ru">
      <body>
        {children}
        <Script src="..." />
      </body>
    </html>
  );
}
```

он загружается для всего приложения.

Next.js отслеживает Script и не должен повторно загружать один и тот же ресурс при переходах между страницами в той же области layout.

Рекомендация:

```text
подключать script
на минимально необходимом уровне
```

Глобальный чат, analytics или SDK не должны автоматически попадать на каждую страницу только потому, что root layout является удобным местом.

#### Стратегии

| Стратегия | Поведение | Типичный сценарий |
| --- | --- | --- |
| `beforeInteractive` | Загружается до first-party Next.js-кода | Действительно критическая общесайтовая интеграция |
| `afterInteractive` | Загружается после начала hydration | Analytics, tag manager, функциональный SDK |
| `lazyOnload` | Загружается во время browser idle после основных ресурсов | Чат, social widget, низкоприоритетная интеграция |
| `worker` | Экспериментально переносит script в Web Worker | Совместимый тяжёлый third-party script в Pages Router |

#### `beforeInteractive`

```tsx
<Script
  src="https://example.com/critical.js"
  strategy="beforeInteractive"
/>
```

В App Router такой Script размещают в root layout.

Next.js:

- добавляет его в initial HTML;
- вставляет в `<head>`;
- предварительно загружает;
- получает до first-party Next.js modules;
- сохраняет порядок нескольких таких scripts.

Несмотря на раннюю загрузку, его выполнение не должно без необходимости блокировать hydration.

`beforeInteractive` используют редко.

Возможные кандидаты:

- bot detector;
- общесайтовый consent manager;
- критический security script.

Обычная аналитика, чат или social widget обычно не требуют настолько раннего запуска.

#### `afterInteractive`

Это default:

```tsx
<Script
  src="https://example.com/analytics.js"
  strategy="afterInteractive"
/>
```

Script загружается после начала hydration.

Он подходит, если интеграция нужна достаточно рано, но не должна конкурировать с first-party code до начала интерактивности.

#### `lazyOnload`

```tsx
<Script
  src="https://example.com/chat.js"
  strategy="lazyOnload"
/>
```

Script загружается во время browser idle после основных ресурсов страницы.

Подходит для:

- support chat;
- social widgets;
- feedback tools;
- необязательных embeds.

Цена:

```text
пользователь может начать взаимодействие
раньше готовности widget
```

UI должен корректно обрабатывать это состояние.

#### `worker`

```tsx
<Script
  src="https://example.com/script.js"
  strategy="worker"
/>
```

Стратегия экспериментальная.

Она:

- требует `experimental.nextScriptWorkers`;
- работает только в Pages Router;
- не поддерживается App Router;
- совместима не со всеми third-party scripts.

Многие сторонние scripts ожидают прямой доступ к:

- DOM;
- `window`;
- synchronous browser API;
- document lifecycle.

Перенос в Worker может изменить их поведение или полностью сломать интеграцию.

#### Callbacks

`Script` поддерживает:

```text
onLoad
onReady
onError
```

Если передаётся callback, компонент должен быть Client Component:

```tsx
"use client";

import Script
  from "next/script";

export function MapScript() {
  return (
    <Script
      src="https://example.com/map.js"
      onReady={() => {
        initializeMap();
      }}
    />
  );
}
```

Различие:

```text
onLoad
→ script впервые загрузился

onReady
→ script готов после загрузки
  и после повторного mount компонента

onError
→ загрузка завершилась ошибкой
```

`onLoad` не используется с `beforeInteractive`; для соответствующего сценария рассматривают `onReady`.

Callbacks нельзя бездумно помещать в Server Component, потому что функции не сериализуются в клиент.

#### Inline scripts

Inline Script должен иметь стабильный `id`:

```tsx
<Script id="theme-init">
  {`
    document.documentElement.dataset.theme =
      localStorage.getItem("theme") ?? "light";
  `}
</Script>
```

`id` нужен Next.js для отслеживания и оптимизации скрипта.

Другой вариант:

```tsx
<Script
  id="config"
  dangerouslySetInnerHTML={{
    __html:
      "window.appConfig = {};",
  }}
/>
```

Динамический пользовательский ввод нельзя вставлять в inline JavaScript.

Иначе возникает XSS.

#### CSP

`next/script` не заменяет Content Security Policy.

Script управляет:

```text
когда
где
как загружать
```

CSP управляет:

```text
каким источникам
разрешено выполнять код
```

Для сторонней интеграции могут потребоваться:

- `script-src`;
- `connect-src`;
- `img-src`;
- `frame-src`;
- nonce;
- hash.

Разрешать:

```text
script-src *
'unsafe-inline'
```

только ради быстрого подключения widget опасно.

Нужно проверить все ресурсы, которые third-party script загружает после старта.

#### `@next/third-parties`

Для некоторых известных интеграций Next.js предоставляет пакет:

```text
@next/third-parties
```

Например:

```tsx
import {
  GoogleAnalytics,
} from "@next/third-parties/google";

<GoogleAnalytics
  gaId="G-XYZ"
/>
```

или:

```tsx
import {
  GoogleTagManager,
} from "@next/third-parties/google";

<GoogleTagManager
  gtmId="GTM-XYZ"
/>
```

Компоненты скрывают часть рекомендуемой конфигурации конкретного поставщика.

Но пакет:

- не отменяет consent;
- не определяет analytics-события продукта;
- не заменяет CSP;
- не гарантирует отсутствие лишней нагрузки;
- остаётся third-party зависимостью.

### Как оценивать результат

Оптимизацию проверяют измерениями.

Для изображений:

- размер загруженного файла;
- выбранный `srcset`;
- `sizes`;
- время начала загрузки;
- LCP;
- CLS;
- cache hit;
- время decode.

Для шрифтов:

- количество font files;
- общий сетевой вес;
- preload;
- FOIT/FOUT;
- CLS;
- ненужные subsets и weights.

Для Link:

- количество prefetch-запросов;
- объём RSC/JSON/JS;
- задержка после клика;
- число неиспользованных prefetch;
- server load.

Для Script:

- transfer size;
- parse и execution time;
- long tasks;
- влияние на INP;
- запросы дочерних ресурсов;
- ошибки;
- privacy и CSP.

Практический порядок:

```text
1. Найти реальную проблему в Web Vitals и waterfall.
2. Определить критические ресурсы первого экрана.
3. Задать изображениям размеры и sizes.
4. Preload только подтверждённый LCP.
5. Ограничить fonts, subsets и weights.
6. Проверить стоимость Link prefetch.
7. Подключать Script в минимальном route scope.
8. Отложить некритичный third-party JavaScript.
9. Проверить CSP и внешние домены.
10. Снова измерить production build.
```

Главный принцип:

```text
next/image
→ оптимизирует доставку изображений

next/font
→ оптимизирует доставку шрифтов

next/link
→ подготавливает клиентскую навигацию

next/script
→ управляет сторонним JavaScript
```

Но Next.js не может определить вместо разработчика:

```text
нужен ли ресурс
какой размер правильный
что является LCP
какой prefetch окупается
какому стороннему коду можно доверять
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Зачем <code>Image</code> нужны <code>width</code> и <code>height</code>, если CSS всё равно меняет размер?</strong></summary>

<dl>
<dd>
<h2></h2>

Они задают intrinsic-размер и соотношение сторон.

Браузер может зарезервировать место до загрузки:

```text
width / height
→ aspect ratio
→ стабильный layout
```

CSS определяет отображаемый размер.

Например:

```tsx
<Image
  width={1200}
  height={800}
  style={{
    width: "100%",
    height: "auto",
  }}
/>
```

отображается по ширине контейнера, сохраняя исходные пропорции.

Без известного соотношения сторон загрузка изображения может сдвинуть соседний контент и ухудшить CLS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>fill</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда размер изображения задаётся контейнером:

- обложка карточки;
- hero;
- gallery tile;
- background-like image.

Родитель должен иметь стабильную геометрию и обычно:

```css
position: relative;
```

Например:

```css
.image {
  position: relative;
  aspect-ratio: 4 / 3;
}
```

Дополнительно задают:

```text
object-fit
sizes
```

`fill` не создаёт высоту родителя самостоятельно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем ограничивать <code>remotePatterns</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Next.js server загружает и обрабатывает внешний URL.

Слишком широкое правило может превратить Image Optimization API в открытый proxy для чужих изображений.

Нужно ограничивать:

```text
protocol
hostname
port
pathname
search
```

Например:

```text
https://images.example.com/products/**
```

безопаснее разрешения всего домена или произвольных URL.

Несовпадающий источник получает ошибку вместо обработки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя ставить <code>priority</code> всем изображениям?</strong></summary>

<dl>
<dd>
<h2></h2>

`priority` использовался в Next.js 14–15 для ранней загрузки критического изображения.

В Next.js 16 он deprecated, вместо него используется:

```tsx
preload
```

Если пометить критическими все изображения, они начнут конкурировать:

- друг с другом;
- с CSS;
- со шрифтами;
- с JavaScript;
- с route data.

Ранний приоритет нужен только подтверждённому изображению первого экрана, обычно LCP.

Для остальных сохраняют lazy loading.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>next/font</code> лучше обычной ссылки на Google Fonts?</strong></summary>

<dl>
<dd>
<h2></h2>

Google Font загружается во время build и self-hosted вместе с приложением.

Браузеру не нужен отдельный запрос к Google:

```text
нет дополнительного DNS и connection
нет browser request к Google
```

Next.js также:

- создаёт `@font-face`;
- управляет preload;
- предоставляет `className` и CSS variable;
- корректирует fallback metrics для уменьшения CLS.

Это не отменяет необходимости ограничивать количество font families, weights, styles и subsets.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно prefetch делает для <code>Link</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

В App Router prefetch может заранее получить:

- RSC Payload;
- JavaScript chunks Client Components;
- общие layouts;
- статическую оболочку маршрута.

Для static route обычно загружается полный маршрут.

Для dynamic route default-поведение может ограничиться ближайшей `loading.tsx`-границей.

В Pages Router заранее загружаются page bundle и JSON page data.

Результат помещается в клиентский cache, но не хранится там бесконечно.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбрать стратегию для стороннего скрипта?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала проверяют, нужен ли script вообще и на каких маршрутах.

```text
нужен до first-party кода
→ beforeInteractive

нужен вскоре после hydration
→ afterInteractive

необязательный низкоприоритетный widget
→ lazyOnload

тяжёлый совместимый script в Pages Router
→ experimental worker
```

Стратегию выбирают по требованиям интеграции и измерениям, а не по категории «analytics» или «widget» автоматически.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Заменяет ли <code>next/script</code> Content Security Policy?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

`next/script` определяет момент и область загрузки.

CSP определяет, каким источникам разрешено выполнять код и загружать связанные ресурсы.

Могут потребоваться:

```text
script-src
connect-src
img-src
frame-src
nonce
hash
```

Сторонний script может после запуска обращаться к дополнительным доменам, которые также нужно учитывать в политике.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>preload</code>, <code>loading="eager"</code> и <code>fetchPriority="high"</code> отличаются у <code>Image</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`preload` добавляет ранний запрос через `<link>` в `<head>`.

`loading="eager"` отключает lazy loading для самого `<img>`.

`fetchPriority="high"` сообщает браузеру, что обнаруженный image request имеет высокий приоритет.

```text
preload
→ раннее обнаружение

eager
→ не откладывать загрузку

fetchPriority
→ приоритет запроса
```

Не нужно автоматически включать все три параметра.

Выбирают минимальное решение, которое улучшает фактический LCP waterfall.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Оптимизирует ли <code>next/image</code> все изображения во время build?</strong></summary>

<dl>
<dd>
<h2></h2>

Default Image Optimizer обычно создаёт варианты во время request.

```text
запрос конкретной ширины
→ resize и encoding
→ cache
```

Static import позволяет заранее определить metadata, но не означает генерацию всех возможных размеров во время build.

При self-hosting нужно учитывать CPU, память и общий cache нескольких server instances.

При `output: "export"` default optimizer недоступен: нужен custom loader или `unoptimized`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать, если внешнее изображение требует cookie или Authorization header?</strong></summary>

<dl>
<dd>
<h2></h2>

Default Image Optimizer не пересылает произвольные headers к source.

Возможные решения:

- временный signed URL;
- собственный защищённый image endpoint;
- custom loader;
- `unoptimized`.

Секрет нельзя помещать в URL, который получает браузер.

Также нужно проверить cache policy, чтобы приватное изображение не стало публично доступным через общий cache.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>От чего зависит область preload шрифта?</strong></summary>

<dl>
<dd>
<h2></h2>

От файла, в котором вызывается font loader.

```text
page
→ только конкретный маршрут

layout
→ маршруты внутри layout

root layout
→ всё приложение
```

Редкий декоративный шрифт не следует вызывать в root layout, если он нужен только одной странице.

Иначе browser будет получать его preload на лишних маршрутах.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем prefetch <code>Link</code> отличается в App Router и Pages Router?</strong></summary>

<dl>
<dd>
<h2></h2>

В App Router default зависит от static или dynamic route и может использовать частичный RSC prefetch до `loading.tsx`.

```text
prefetch={false}
→ отключает viewport и hover prefetch
```

В Pages Router обычно загружаются page JavaScript и JSON data.

```text
prefetch={false}
→ отключает viewport prefetch,
  но hover prefetch может сохраниться
```

Поэтому одинаковый prop не всегда означает полностью одинаковое поведение двух Router-ов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя выполнять аналитику прямо в Server Component или layout?</strong></summary>

<dl>
<dd>
<h2></h2>

Маршрут может быть отрендерен во время prefetch до фактического перехода пользователя.

Если render выполняет:

```ts
trackPageView();
```

аналитика зафиксирует просмотр страницы, которую пользователь не открыл.

Side effects связывают с фактическим lifecycle:

- `useEffect` Client Component;
- пользовательским действием;
- Server Action;
- другой явной операцией.

Render Server Component должен оставаться чистым.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему inline <code>Script</code> нужен <code>id</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

У inline script нет внешнего `src`, по которому Next.js мог бы его идентифицировать.

Стабильный `id` позволяет:

- отслеживать script;
- не вставлять его повторно;
- корректно управлять lifecycle;
- применять оптимизацию.

```tsx
<Script id="theme-init">
  {"..."}
</Script>
```

Динамические данные нельзя вставлять в script без безопасного экранирования: это создаёт риск XSS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>@next/third-parties</code> вместо прямого <code>Script</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда пакет содержит готовую интеграцию нужного поставщика, например Google Analytics или Google Tag Manager.

Он может предоставить:

- рекомендуемый способ загрузки;
- готовые props;
- helper отправки событий;
- меньше ручного inline-кода.

Но он не заменяет:

- consent;
- CSP;
- предметную схему analytics events;
- проверку сетевого и CPU-веса;
- правила приватности продукта.

Для неподдерживаемой интеграции используют `next/script` или собственную Client Component-обёртку.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Проблема | Что проверить |
| --- | --- |
| Высокий CLS у карточек | Intrinsic-размеры `Image` и стабильный контейнер |
| Мобильный браузер скачивает большой файл | `sizes`, `srcset` и реальные breakpoints |
| LCP-изображение начинает грузиться поздно | `preload`, `loading` или `fetchPriority` по версии Next.js |
| Image Optimizer создаёт слишком много вариантов | `deviceSizes`, `imageSizes` и `qualities` |
| Private image не загружается | Headers, signed URL, custom loader или `unoptimized` |
| Static export падает из-за Image Optimizer | Custom loader или отключение optimization |
| Текст сдвигается после загрузки шрифта | `next/font`, fallback metrics и `display` |
| Загружается слишком много font files | Variable font, subsets, weights и preload scope |
| Переход по ссылке долго ждёт | `Link`, prefetch, `loading.tsx` и Router Cache |
| Страница создаёт слишком много background-запросов | Отключить prefetch у маловероятных ссылок |
| Analytics срабатывает до посещения страницы | Убрать side effect из Server Component render |
| Third-party widget блокирует главный поток | Route scope и стратегия `Script` |
| Script загружается повторно | Размещение в layout и стабильные `src` или `id` |
| CSP блокирует интеграцию | Необходимые directives, nonce и внешние источники |

## Связанные темы

- [02 Структура App Router](<./02 Структура App Router.md>)
- [02 Метрики Core Web Vitals](<../Performance/02 Метрики Core Web Vitals.md>)
- [05 Оптимизация изображений и шрифтов](<../Performance/05 Оптимизация изображений и шрифтов.md>)
- [07 Доступность изображений и медиа](<../Accessibility/07 Доступность изображений и медиа.md>)
- [06 CSP и защитные HTTP-заголовки](<../Security/06 CSP и защитные HTTP-заголовки.md>)

## Источники

- [Next.js docs: Image Component](https://nextjs.org/docs/app/api-reference/components/image)
- [Next.js docs: Image Optimization](https://nextjs.org/docs/app/getting-started/images)
- [Next.js docs: Font Module](https://nextjs.org/docs/app/api-reference/components/font)
- [Next.js docs: Font Optimization](https://nextjs.org/docs/app/getting-started/fonts)
- [Next.js docs: Link Component](https://nextjs.org/docs/app/api-reference/components/link)
- [Next.js docs: Prefetching](https://nextjs.org/docs/app/guides/prefetching)
- [Next.js docs: Script Component](https://nextjs.org/docs/app/api-reference/components/script)
- [Next.js docs: Script Optimization](https://nextjs.org/docs/app/guides/scripts)
- [Next.js docs: Third Party Libraries](https://nextjs.org/docs/app/guides/third-party-libraries)
- [Next.js docs: Content Security Policy](https://nextjs.org/docs/app/guides/content-security-policy)
- [Next.js docs: Static Exports](https://nextjs.org/docs/app/guides/static-exports)
- [Next.js docs: Upgrading to Next.js 16](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Next.js 14 docs: Image Optimization](https://nextjs.org/docs/14/app/building-your-application/optimizing/images)
- [Next.js 14 docs: Font Optimization](https://nextjs.org/docs/14/app/building-your-application/optimizing/fonts)
- [Next.js 14 docs: Link](https://nextjs.org/docs/14/app/api-reference/components/link)
- [Next.js 14 docs: Script Optimization](https://nextjs.org/docs/14/app/building-your-application/optimizing/scripts)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 12 Сложные маршруты в App Router](<./12 Сложные маршруты в App Router.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 Настройка и развёртывание Next.js →](<./14 Настройка и развёртывание Next.js.md>)
<!-- CARD-NAV-BOTTOM:END -->
