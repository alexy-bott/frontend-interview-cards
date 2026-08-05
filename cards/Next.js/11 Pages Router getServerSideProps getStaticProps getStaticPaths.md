# Pages Router getServerSideProps getStaticProps getStaticPaths

<!-- CARD-NAV-TOP:START -->
[← 10 Next.js 14 15 16 версии Turbopack Cache Components PPR](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Route Groups Parallel и Intercepting Routes →](<./12 Route Groups Parallel и Intercepting Routes.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как работает Pages Router и для чего нужны `getServerSideProps`, `getStaticProps` и `getStaticPaths`?**

<h2></h2>

<br>
<dl>
<dd>

Pages Router — файловая система маршрутизации Next.js на основе каталога `pages`.

Каждый page-файл создаёт URL:

```text
pages/index.tsx
→ /

pages/about.tsx
→ /about

pages/users/index.tsx
→ /users

pages/users/[id].tsx
→ /users/:id

pages/docs/[...slug].tsx
→ /docs/*
```

Файлы внутри:

```text
pages/api/*
```

создают API Routes, а не React-страницы.

Например:

```text
pages/api/users.ts
→ /api/users
```

Pages Router появился раньше App Router, но продолжает поддерживаться и часто встречается в production-проектах.

Для новых маршрутов Next.js рекомендует App Router, однако существующий Pages Router не требуется переписывать целиком только из-за появления нового router.

В Pages Router нужно разделять три понятия:

```text
файл в pages
→ определяет URL

page component
→ определяет интерфейс

data-fetching function
→ определяет способ предварительного рендеринга
```

Основные серверные функции:

| Функция | Когда выполняется | Основной результат |
| --- | --- | --- |
| `getServerSideProps` | При каждом запросе страницы | SSR |
| `getStaticProps` | Во время static generation | SSG или ISR |
| `getStaticPaths` | Во время build для динамического SSG-маршрута | Список предварительно создаваемых путей |

Эти функции:

- выполняются только на серверной стороне;
- экспортируются из page-файла;
- не экспортируются из обычного компонента;
- не входят в клиентский bundle;
- передают сериализуемые props page-компоненту.

Они не используются в каталоге `app`.

### Automatic Static Optimization

Если page не экспортирует:

```text
getServerSideProps
getInitialProps
```

Next.js может автоматически предварительно создать её как статическую страницу.

Например:

```tsx
export default function AboutPage() {
  return <h1>О компании</h1>;
}
```

Для неё не требуется отдельная data-функция.

Упрощённо:

```text
нет request-time зависимости
→ static optimization

есть getServerSideProps
→ SSR на каждый запрос
```

`getStaticProps` явно задаёт static generation с данными.

Наличие клиентского state, `useEffect` или обработчиков событий само по себе не запрещает предварительный HTML.

После загрузки страница всё равно проходит hydration и становится интерактивной.

### `getServerSideProps`

`getServerSideProps` используется для Server-Side Rendering.

Она выполняется на сервере при каждом запросе страницы:

```text
request
→ getServerSideProps
→ render page
→ HTML и props
→ browser
→ hydration
```

Пример:

```ts
import type {
  GetServerSideProps,
  InferGetServerSidePropsType,
} from "next";

type User = {
  id: string;
  name: string;
};

type PageProps = {
  user: User;
};

export const getServerSideProps = (async (
  context,
) => {
  const userId = context.params?.id;

  if (
    typeof userId !== "string"
  ) {
    return {
      notFound: true,
    };
  }

  const user = await getUser(
    userId,
    context.req.cookies.session,
  );

  if (!user) {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      user,
    },
  };
}) satisfies GetServerSideProps<
  PageProps
>;

export default function UserPage({
  user,
}: InferGetServerSidePropsType<
  typeof getServerSideProps
>) {
  return <h1>{user.name}</h1>;
}
```

`context` содержит данные конкретного запроса.

Основные поля:

```text
params
→ параметры динамического маршрута

query
→ query string и параметры маршрута

req
→ Node.js HTTP request

res
→ Node.js HTTP response

req.cookies
→ cookies запроса

resolvedUrl
→ нормализованный исходный URL

draftMode
→ активен ли Draft Mode

locale
locales
defaultLocale
→ данные i18n, если оно настроено
```

Например, для URL:

```text
/users/42?tab=orders
```

в `pages/users/[id].tsx`:

```text
params.id
→ "42"

query.id
→ "42"

query.tab
→ "orders"
```

`getServerSideProps` подходит, когда HTML зависит от конкретного запроса:

- текущей сессии;
- cookies;
- authorization header;
- permissions;
- tenant;
- геолокации запроса;
- часто изменяющихся данных;
- информации, которая должна быть актуальной при каждом открытии.

Например:

```text
личный кабинет
закрытый dashboard
страница с серверной проверкой прав
```

Цена SSR:

- серверная работа на каждый запрос;
- ожидание базы данных или API;
- более высокая нагрузка;
- зависимость времени ответа от backend;
- невозможность раздавать один общий HTML всем пользователям.

Если данные публичные и допускают небольшую задержку обновления, SSG или ISR обычно дешевле.

#### Прямая и клиентская навигация

При прямом открытии URL:

```text
browser запрашивает страницу
→ сервер запускает getServerSideProps
→ возвращает HTML
```

При переходе через:

```tsx
<Link href="/users/42">
  Пользователь
</Link>
```

или:

```ts
router.push("/users/42");
```

Next.js выполняет внутренний запрос данных к серверу.

Сервер снова запускает `getServerSideProps`, но браузеру не требуется полностью перезагружать документ.

Упрощённо:

```text
client navigation
→ Next.js data request
→ getServerSideProps
→ JSON props
→ React обновляет page
```

Функция всё равно выполняется на сервере, а не в браузере.

#### Результат `getServerSideProps`

Функция возвращает один из основных вариантов:

```text
props
redirect
notFound
```

Успешный результат:

```ts
return {
  props: {
    user,
  },
};
```

Страница не найдена:

```ts
return {
  notFound: true,
};
```

Redirect:

```ts
return {
  redirect: {
    destination: "/login",
    permanent: false,
  },
};
```

Можно также изменить HTTP-response через `context.res`, например задать заголовок.

Но ручное управление response не должно конфликтовать с тем, что Next.js ещё должен отрендерить страницу.

Если функция выбрасывает необработанную ошибку, production-приложение использует страницу ошибки `500`, если она настроена.

#### Безопасность props

Код `getServerSideProps` остаётся на сервере.

Внутри можно использовать:

- секретный API key;
- серверный access token;
- database client;
- private environment variables.

Но возвращённые props отправляются браузеру.

Например:

```ts
return {
  props: {
    user,
    secretToken,
  },
};
```

раскроет `secretToken` пользователю.

Упрощённо:

```text
код функции
→ server-only

возвращённые props
→ доступны browser
```

В props возвращают только данные, которые разрешено показать клиенту.

### Сериализация props

Значения props должны быть сериализуемыми.

Подходят:

```text
string
number
boolean
null
array
plain object
```

Нельзя напрямую рассчитывать на передачу:

```text
Date
Map
Set
class instance
function
BigInt
циклический объект
```

Например, `Date` преобразуют в строку:

```ts
return {
  props: {
    createdAt:
      user.createdAt.toISOString(),
  },
};
```

На клиенте при необходимости создают новый `Date`.

Требование относится как к `getServerSideProps`, так и к `getStaticProps`.

### Вызов API Route из `getServerSideProps`

Технически `getServerSideProps` может вызвать:

```text
/api/users
```

через HTTP.

Но обычно это лишний промежуточный запрос.

```text
getServerSideProps
→ API Route
→ service
→ database
```

Проще вызвать общий server-side слой напрямую:

```text
getServerSideProps
→ service
→ database
```

Например:

```ts
const user =
  await userRepository.getById(
    userId,
  );
```

Это уменьшает:

- сетевую задержку;
- повторную сериализацию;
- необходимость вычислять server origin;
- дублирование обработки ошибок.

API Route нужен браузеру или внешнему клиенту.

Две серверные части одного приложения обычно могут использовать общую функцию или repository напрямую.

### `getStaticProps`

`getStaticProps` используется для Static Site Generation.

Для обычной статической страницы она выполняется во время production build:

```text
next build
→ getStaticProps
→ HTML
→ JSON props
→ готовый static artifact
```

Пример:

```ts
import type {
  GetStaticProps,
  InferGetStaticPropsType,
} from "next";

type Post = {
  id: string;
  title: string;
};

type PageProps = {
  posts: Post[];
};

export const getStaticProps = (async () => {
  const posts =
    await getPosts();

  return {
    props: {
      posts,
    },
  };
}) satisfies GetStaticProps<
  PageProps
>;

export default function PostsPage({
  posts,
}: InferGetStaticPropsType<
  typeof getStaticProps
>) {
  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>
          {post.title}
        </li>
      ))}
    </ul>
  );
}
```

Next.js создаёт:

```text
HTML страницы
+
JSON с результатом getStaticProps
```

HTML используется при первоначальном запросе.

JSON используется при клиентской навигации через `next/link` или `next/router`.

Браузер не запускает `getStaticProps`.

Он получает уже сформированные данные:

```text
client navigation
→ загрузить static JSON
→ отрендерить page
```

`getStaticProps` подходит для публичных данных:

- статьи;
- документация;
- маркетинговые страницы;
- каталог;
- данные CMS;
- публичный профиль;
- список товаров.

Преимущества:

- HTML создаётся заранее;
- один результат можно раздавать многим пользователям;
- CDN может кэшировать HTML и JSON;
- нет обязательного запроса к backend при каждом открытии;
- меньше нагрузка на application server.

Ограничение:

```text
страница не знает данные
конкретного HTTP-request
во время build
```

В `getStaticProps` нет обычных:

```text
req
res
cookies конкретного посетителя
```

Потому что один результат должен подходить нескольким пользователям.

Персональные данные после загрузки можно получать отдельно на клиенте либо использовать SSR.

#### Когда выполняется `getStaticProps`

В production возможны несколько случаев:

```text
обычный SSG
→ во время next build

ISR
→ во время build и последующей regeneration

fallback
→ при первом запросе ещё не созданного пути

Draft Mode
→ во время request для preview
```

В development:

```text
next dev
```

`getStaticProps` может выполняться при каждом запросе, чтобы разработчик сразу видел изменения.

Поэтому поведение `next dev` не следует использовать как доказательство production-стратегии.

#### Результат `getStaticProps`

Она также может вернуть:

```text
props
notFound
redirect
revalidate
```

Например:

```ts
return {
  props: {
    post,
  },
  revalidate: 60,
};
```

### SSG и ISR

Без `revalidate` страница остаётся неизменной до следующего build и deployment:

```text
build
→ static page
→ новый build нужен для обновления
```

С `revalidate` используется Incremental Static Regeneration:

```ts
return {
  props: {
    posts,
  },
  revalidate: 60,
};
```

Значение задаётся в секундах.

Это не означает:

```text
Next.js обязательно пересобирает страницу
ровно каждые 60 секунд
```

Упрощённый процесс:

```text
1. Страница была создана и сохранена.
2. В течение 60 секунд отдаётся сохранённая версия.
3. После истечения интервала приходит новый запрос.
4. Next.js может отдать предыдущую версию.
5. В фоне запускается regeneration.
6. После успеха новая версия заменяет старую.
7. Следующие запросы получают обновлённую страницу.
```

Это модель stale-while-revalidate.

Если regeneration завершилась ошибкой, последняя успешно созданная версия продолжает использоваться, а следующая попытка может произойти позже.

ISR подходит, когда:

- данные обновляются периодически;
- не требуется точность на каждый запрос;
- rebuild всего приложения слишком дорогой;
- страницу полезно кэшировать как статическую.

Например:

```text
каталог товаров
новостные статьи
публичные профили
страницы CMS
```

#### On-demand revalidation

Кроме интервала можно запускать обновление по событию.

Например, CMS отправляет webhook после публикации статьи, а API Route вызывает revalidation.

Концептуально:

```text
CMS update
→ webhook
→ res.revalidate("/posts/article")
→ новая версия страницы
```

В таком случае `revalidate` с интервалом может не требоваться.

On-demand revalidation удобна, когда источник данных способен сообщить об изменении.

Необходимо защищать revalidation endpoint секретом или другой серверной авторизацией, иначе посторонний пользователь сможет создавать лишнюю нагрузку.

### Draft Mode

Статическая страница обычно показывает опубликованные данные.

Для предварительного просмотра черновика CMS используется Draft Mode.

Упрощённо:

```text
редактор открывает preview URL
→ устанавливается специальная cookie
→ getStaticProps видит draftMode
→ получает draft content
→ страница рендерится по request
```

Черновик не должен попадать в общий статический кэш для остальных пользователей.

### `getStaticPaths`

`getStaticPaths` используется для динамического маршрута, который также экспортирует `getStaticProps`.

Например:

```text
pages/posts/[slug].tsx
```

Во время build Next.js не знает, какие значения может принимать `[slug]`.

`getStaticPaths` возвращает пути, которые нужно создать заранее:

```ts
import type {
  GetStaticPaths,
  GetStaticProps,
  InferGetStaticPropsType,
} from "next";

type Params = {
  slug: string;
};

type PageProps = {
  post: Post;
};

export const getStaticPaths = (async () => {
  const posts =
    await getPosts();

  return {
    paths: posts.map((post) => ({
      params: {
        slug: post.slug,
      },
    })),
    fallback: false,
  };
}) satisfies GetStaticPaths<
  Params
>;

export const getStaticProps = (async (
  context,
) => {
  const slug =
    context.params?.slug;

  if (
    typeof slug !== "string"
  ) {
    return {
      notFound: true,
    };
  }

  const post =
    await getPost(slug);

  if (!post) {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      post,
    },
  };
}) satisfies GetStaticProps<
  PageProps,
  Params
>;

export default function PostPage({
  post,
}: InferGetStaticPropsType<
  typeof getStaticProps
>) {
  return (
    <article>
      <h1>{post.title}</h1>
    </article>
  );
}
```

Процесс build:

```text
getStaticPaths
→ slug A
→ slug B
→ slug C

для каждого slug
→ getStaticProps
→ HTML и JSON
```

`getStaticPaths`:

- используется только в dynamic page;
- используется со `getStaticProps`;
- не используется с `getServerSideProps`;
- не выполняется в браузере;
- в production выполняется во время build;
- не запускается заново при ISR regeneration.

При запросе неизвестного пути выполняется поведение `fallback`, но сам `getStaticPaths` повторно не вызывается.

Параметры должны совпадать с именами dynamic segments.

Для:

```text
pages/posts/[slug].tsx
```

нужно вернуть:

```ts
{
  params: {
    slug: "hello",
  },
}
```

Для:

```text
pages/docs/[...slug].tsx
```

может использоваться массив:

```ts
{
  params: {
    slug: [
      "react",
      "hooks",
    ],
  },
}
```

Значения параметров должны соответствовать ожидаемым строкам и регистру URL.

### `fallback`

`fallback` определяет поведение пути, который не был возвращён из `getStaticPaths`.

| `fallback` | Неизвестный путь |
| --- | --- |
| `false` | Возвращается 404 |
| `true` | Путь генерируется при первом обращении; возможен fallback UI |
| `"blocking"` | Первый запрос ждёт готовый HTML |

#### `fallback: false`

```ts
return {
  paths,
  fallback: false,
};
```

Next.js создаёт только перечисленные пути.

Неизвестный URL:

```text
/posts/unknown
→ 404
```

Подходит, когда:

- набор страниц небольшой;
- все пути известны при build;
- новые пути появляются только вместе с deployment;
- неизвестный путь должен сразу считаться отсутствующим.

#### `fallback: true`

```ts
return {
  paths,
  fallback: true,
};
```

Для прямого первого запроса ещё не созданного пути Next.js может сначала вернуть fallback-версию страницы.

Компонент проверяет:

```ts
import {
  useRouter,
} from "next/router";

export default function PostPage({
  post,
}: PageProps) {
  const router =
    useRouter();

  if (router.isFallback) {
    return (
      <div>
        Загружаем статью…
      </div>
    );
  }

  return (
    <article>
      <h1>{post.title}</h1>
    </article>
  );
}
```

Процесс:

```text
первый прямой запрос неизвестного пути
→ fallback HTML
→ getStaticProps выполняется в фоне
→ браузер получает готовые props
→ полная страница заменяет fallback
→ результат сохраняется
```

Важное исключение:

```text
переход через next/link или next/router
→ fallback UI не показывается
→ поведение похоже на "blocking"
```

Поисковые роботы также обычно получают blocking-поведение вместо временного fallback UI.

Поэтому `router.isFallback` нужен для прямого запроса, при котором fallback действительно может быть отрендерен.

`fallback: true` полезен для очень большого числа страниц:

```text
миллионы товаров
```

Можно создать популярные пути во время build, а остальные генерировать по обращению.

#### `fallback: "blocking"`

```ts
return {
  paths,
  fallback: "blocking",
};
```

Первый запрос неизвестного пути ждёт выполнения `getStaticProps`:

```text
первый request
→ getStaticProps
→ полный HTML
→ сохранить результат
```

Пользователь не видит промежуточный fallback UI.

Преимущество:

- page component проще;
- сразу возвращается полноценный HTML;
- подходит для SEO;
- результат кэшируется для следующих запросов.

Цена:

- первый посетитель нового пути ждёт генерацию;
- медленный источник данных увеличит TTFB первого запроса.

Само создание пути по fallback не обновляет его в дальнейшем.

Для последующих обновлений добавляют ISR:

```ts
return {
  props: {
    post,
  },
  revalidate: 60,
};
```

### `notFound` у динамической страницы

Даже если путь разрешён `fallback`, `getStaticProps` может выяснить, что сущность не существует:

```ts
if (!post) {
  return {
    notFound: true,
  };
}
```

Например:

```text
/posts/deleted-post
→ getStaticProps
→ post отсутствует
→ 404
```

Существование URL определяет источник данных, а не только формат dynamic route.

### Состояния страницы

Для `getServerSideProps` первоначальная загрузка происходит до получения page props.

Поэтому page не получает промежуточное состояние самой функции.

Но после hydration она может отдельно выполнять client-side запросы.

Для `fallback: true` нужен явный fallback UI через:

```text
router.isFallback
```

Ошибки следует разделять:

```text
notFound
→ сущность отсутствует

redirect
→ пользователь должен перейти на другой URL

throw
→ неожиданная серверная ошибка
```

Не следует возвращать:

```text
props: {
  error: "not found",
}
```

если корректным HTTP-результатом является 404.

### Где разрешены data-функции

`getServerSideProps` и `getStaticProps` экспортируются только из page-файла:

```text
pages/users/[id].tsx
```

Их нельзя экспортировать из:

- обычного child-компонента;
- layout-компонента;
- `_app`;
- `_document`;
- `_error`;
- custom hook.

Например, такой компонент не может самостоятельно экспортировать `getStaticProps`:

```text
components/UserCard.tsx
```

Page получает данные и передаёт их дочерним компонентам.

Если несколько pages используют одну server-side операцию, общую логику выносят в функцию или service:

```text
page A ─┐
        ├→ loadUser()
page B ─┘
```

### `getInitialProps`

`getInitialProps` — более старый API Pages Router.

Он может выполняться:

```text
при первом открытии
→ на сервере

при клиентской навигации
→ в браузере
```

Из-за этого код должен учитывать обе среды.

Например, нельзя без проверки использовать внутри только server-side секреты, если функция способна выполниться в браузере.

Для нового кода обычно выбирают более конкретный API:

```text
request-time data
→ getServerSideProps

static data
→ getStaticProps
```

Использование `getInitialProps` в custom `_app` отключает Automatic Static Optimization для страниц без собственного `getStaticProps`.

Это может неожиданно превратить множество страниц в request-time rendering.

Поэтому `_app.getInitialProps` используют только при осознанной необходимости.

### Shallow routing

В Pages Router shallow routing позволяет изменить query текущей страницы без повторного запуска page data-функций.

Например:

```ts
router.push(
  "/products?page=2",
  undefined,
  {
    shallow: true,
  },
);
```

При shallow-переходе в пределах той же page:

```text
URL изменяется
→ getServerSideProps не запускается
→ getStaticProps не запускается
→ getInitialProps не запускается
```

Компонент самостоятельно реагирует на новое значение `router.query`.

Shallow routing не является способом перейти на другую page без data fetching.

### Static export

При конфигурации:

```ts
const nextConfig = {
  output: "export",
};
```

приложение должно быть полностью экспортируемым в статические HTML, CSS и JavaScript.

Нельзя использовать request-time возможности:

```text
getServerSideProps
server-only API Routes
ISR на работающем Next.js server
```

Для динамического SSG должны быть известны экспортируемые пути.

Режимы:

```text
fallback: true
fallback: "blocking"
```

не подходят для полностью статического export, потому что требуют генерации новых страниц после build.

### Кэширование

`getStaticProps` создаёт общий результат, который удобно кэшировать.

`getServerSideProps` создаёт результат для конкретного запроса.

При необходимости SSR-response можно кэшировать через HTTP-заголовки, если данные действительно безопасно разделять между пользователями.

Но нельзя задавать публичный общий cache для персональной страницы с:

- cookies;
- пользовательскими правами;
- приватными данными.

Правило:

```text
персональный response
→ не должен попасть
в общий публичный cache
```

### Pages Router и App Router

В App Router функций:

```text
getServerSideProps
getStaticProps
getStaticPaths
```

нет.

Получение данных выполняется непосредственно в Server Components, Route Handlers и других server-side границах.

Приблизительное сопоставление:

| Pages Router | App Router |
| --- | --- |
| `getServerSideProps` | Динамический Server Component и request-time data |
| `getStaticProps` | Static rendering и cache APIs |
| `revalidate` | Time-based или on-demand revalidation |
| `getStaticPaths` | `generateStaticParams` |
| `fallback` | `dynamicParams` и правила генерации динамических сегментов |
| API Routes | Route Handlers |

Это не замена один к одному.

App Router использует другую модель:

- Server Components;
- nested layouts;
- loading boundaries;
- streaming;
- Suspense;
- отдельные cache layers;
- server/client boundaries.

Поэтому миграция требует проверить поведение маршрута, а не просто переименовать функции.

### Постепенная миграция

Каталоги:

```text
pages
app
```

могут существовать в одном проекте.

Например:

```text
pages/legacy-dashboard.tsx
app/new-dashboard/page.tsx
```

Но они не должны создавать один и тот же URL.

Конфликт:

```text
pages/about.tsx
→ /about

app/about/page.tsx
→ /about
```

приведёт к ошибке маршрутизации или build.

Обычно миграция выполняется по маршрутам:

```text
1. Выбрать один URL.
2. Зафиксировать текущее поведение.
3. Перенести page в app.
4. Перенести data fetching.
5. Определить cache и revalidation.
6. Добавить loading/error boundaries.
7. Проверить metadata и SEO.
8. Проверить hydration и client components.
9. Удалить старый pages-маршрут.
```

Необязательно одновременно переписывать все pages.

### Практический выбор

```text
данные зависят от request,
cookies или permissions
→ getServerSideProps

данные известны при build
и обновляются только с deployment
→ getStaticProps

публичные данные обновляются периодически
→ getStaticProps + revalidate

dynamic SSG route
→ getStaticPaths + getStaticProps

очень много dynamic paths
→ fallback true или blocking

нужен только browser-side state
после первоначального HTML
→ client-side fetching
```

Главная модель:

```text
getServerSideProps
→ новый server render
  для каждого запроса

getStaticProps
→ общий предварительно
  созданный HTML и JSON

getStaticPaths
→ какие dynamic paths
  создать заранее

revalidate
→ когда static page
  разрешено обновить
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Когда использовать <code>getServerSideProps</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда HTML должен учитывать конкретный request:

- сессию;
- cookies;
- authorization;
- permissions;
- headers;
- tenant;
- данные, актуальные на каждое открытие.

Например:

```text
закрытый личный кабинет
```

При прямом запросе возвращается HTML.

При переходе через `next/link` Next.js выполняет серверный data-request и получает JSON props.

Если страница публичная и допускает небольшую задержку обновления, SSG или ISR обычно быстрее и дешевле.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Видит ли браузер код и данные из <code>getServerSideProps</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Код функции и используемые только ею server imports не входят в клиентский bundle.

Внутри можно обращаться к database и secret environment variables.

Но объект `props` сериализуется и отправляется браузеру для render и hydration.

Поэтому правило:

```text
секрет можно использовать
для server-side запроса

секрет нельзя вернуть
в props
```

Пользователь способен прочитать полученные props через HTML, внутренние Next.js-данные или DevTools.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли вызвать собственный API Route из <code>getServerSideProps</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Технически можно, но обычно не нужно.

Обе части выполняются на сервере.

Внутренний HTTP добавляет:

- сетевой переход;
- сериализацию;
- обработку URL;
- лишнюю задержку;
- ещё одну точку ошибки.

Обычно page и API Route вызывают общий service или repository:

```text
getServerSideProps ─┐
                    ├→ userService
API Route ──────────┘
```

API Route остаётся HTTP-границей для браузера или внешних клиентов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем SSG с <code>getStaticProps</code> отличается от ISR?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный SSG:

```text
getStaticProps выполняется при build
→ страница меняется после нового build
```

ISR:

```text
getStaticProps
+
revalidate
→ сохранённую страницу можно обновить
  после deployment
```

При time-based ISR интервал задаёт минимальное время до следующей допустимой regeneration, а не строгий таймер обновления.

До успешного обновления пользователи получают последнюю рабочую версию страницы.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>getStaticPaths</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Dynamic page:

```text
pages/posts/[slug].tsx
```

не сообщает Next.js все реальные значения `[slug]`.

`getStaticPaths` возвращает пути, которые нужно создать во время build:

```text
/posts/a
/posts/b
/posts/c
```

`fallback` определяет поведение остальных путей.

Функция используется только вместе с dynamic page и `getStaticProps`.

Она не требуется для `getServerSideProps`, потому что SSR может обработать любой подходящий URL при запросе.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>fallback: true</code> отличается от <code>fallback: "blocking"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

При `true` прямой первый запрос неизвестного пути может получить временный fallback UI:

```text
fallback HTML
→ генерация
→ готовые props
→ полная page
```

Компонент проверяет:

```text
router.isFallback
```

Но клиентский переход через `next/link` или `next/router` ведёт себя как `"blocking"` и не показывает fallback.

При `"blocking"` первый запрос сразу ждёт готовый HTML:

```text
request
→ generation
→ полный HTML
```

Оба режима сохраняют созданный путь для последующих запросов.

Для дальнейшего обновления страницы отдельно настраивают ISR.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>getInitialProps</code> отличается от этих функций?</strong></summary>

<dl>
<dd>
<h2></h2>

`getInitialProps` — legacy API.

Он выполняется:

```text
при первом открытии
→ на сервере

при client-side navigation
→ может выполняться в браузере
```

`getServerSideProps` всегда выполняется на сервере.

`getStaticProps` выполняется в процессе static generation.

Использование `getInitialProps` в custom `_app` отключает Automatic Static Optimization для страниц без `getStaticProps`.

Поэтому в новом Pages Router коде обычно выбирают более конкретную функцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли постепенно мигрировать с Pages Router на App Router?</strong></summary>

<dl>
<dd>
<h2></h2>

Да.

`pages` и `app` могут сосуществовать, если не создают одинаковый URL.

Миграцию выполняют по маршрутам и отдельно проверяют:

- data fetching;
- cache;
- revalidation;
- layouts;
- loading;
- errors;
- metadata;
- client components;
- hydration;
- navigation.

Прямого соответствия старых и новых API один к одному нет.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Automatic Static Optimization?</strong></summary>

<dl>
<dd>
<h2></h2>

Если page не использует request-time data-функцию, Next.js может предварительно создать её как статический HTML.

Например:

```tsx
export default function Page() {
  return <h1>About</h1>;
}
```

не требует `getStaticProps`, если внешние build-time данные не нужны.

`getServerSideProps` и `getInitialProps` переводят соответствующую page в request-time rendering.

`getInitialProps` в custom `_app` также влияет на pages без собственного `getStaticProps`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Какие значения можно вернуть в <code>props</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Props должны безопасно сериализоваться.

Подходят:

```text
plain object
array
string
number
boolean
null
```

Сложные значения преобразуют:

```text
Date
→ ISO string

Map
→ array или object

class instance
→ plain DTO
```

Функции и циклические структуры передать нельзя.

Props также должны содержать только данные, которые разрешено показать браузеру.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Выполняются ли data-функции при клиентской навигации?</strong></summary>

<dl>
<dd>
<h2></h2>

`getServerSideProps` выполняется на сервере при каждом обычном клиентском переходе на соответствующую page.

Браузер получает JSON props.

Для `getStaticProps` браузер обычно загружает заранее созданный JSON.

Сама функция в браузере не выполняется.

Исключение — shallow routing в пределах текущей page: он изменяет URL без повторного запуска page data-функций.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Обновляет ли <code>revalidate: 60</code> страницу строго каждую минуту?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

Значение означает, что после указанного интервала страница получает право на regeneration.

Обычно нужен последующий request:

```text
интервал истёк
→ пришёл request
→ возвращена сохранённая версия
→ началась regeneration
```

Если запросов нет, обязательное фоновое обновление строго по таймеру не происходит.

Для обновления сразу после изменения данных можно использовать on-demand revalidation.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Для чего нужен Draft Mode?</strong></summary>

<dl>
<dd>
<h2></h2>

Draft Mode позволяет временно обойти обычную статическую версию и показать черновые данные CMS конкретному редактору.

Специальная cookie сообщает `getStaticProps`, что нужно получить preview content.

Обычные пользователи продолжают получать опубликованную статическую страницу.

Preview endpoint должен быть защищён, чтобы посторонний пользователь не получил доступ к черновикам.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Можно ли использовать эти функции с <code>output: "export"</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Полностью статический export не имеет работающего Next.js server после build.

Поэтому он не поддерживает возможности, требующие request-time выполнения:

```text
getServerSideProps
ISR на сервере
fallback: true
fallback: "blocking"
```

`getStaticProps` и `getStaticPaths` можно использовать для путей, полностью создаваемых во время build.

Все необходимые dynamic paths должны быть заранее известны.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как shallow routing влияет на data-функции?</strong></summary>

<dl>
<dd>
<h2></h2>

Shallow routing меняет URL текущей page без повторного запуска:

```text
getServerSideProps
getStaticProps
getInitialProps
```

Компонент продолжает использовать существующий state и props, но получает обновлённый `router.query`.

Подход подходит, например, для UI-фильтра, если приложение самостоятельно синхронизирует данные.

При переходе на другую page shallow routing не отменяет её обычный lifecycle.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Сценарий | Pages Router API |
| --- | --- |
| Персональная SSR-страница | `getServerSideProps` |
| Публичная статья | `getStaticProps` |
| Периодически обновляемый каталог | `getStaticProps` с `revalidate` |
| Обновление страницы после CMS webhook | On-demand revalidation |
| Статьи по `[slug]` | `getStaticPaths` и `getStaticProps` |
| Миллионы динамических товаров | Частичный `paths` и fallback |
| Предпросмотр черновика CMS | Draft Mode и `getStaticProps` |
| Backend endpoint | `pages/api/*` |
| Полностью статический hosting | SSG без request-time возможностей |
| Постепенная миграция | Одновременные `pages` и `app` без конфликта URL |

## Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [04 SSR SSG ISR Streaming и hydration](<./04 SSR SSG ISR Streaming и hydration.md>)
- [05 Data fetching fetch cache no-store revalidate](<./05 Data fetching fetch cache no-store revalidate.md>)
- [09 Dynamic routes params searchParams metadata](<./09 Dynamic routes params searchParams metadata.md>)
- [17 Hydration SSR и SSG](<../React/17 Hydration SSR и SSG.md>)

## Источники

- [Next.js docs: Pages Router](https://nextjs.org/docs/pages)
- [Next.js docs: getServerSideProps](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-server-side-props)
- [Next.js docs: getStaticProps](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-static-props)
- [Next.js docs: getStaticPaths](https://nextjs.org/docs/pages/building-your-application/data-fetching/get-static-paths)
- [Next.js docs: Incremental Static Regeneration](https://nextjs.org/docs/pages/guides/incremental-static-regeneration)
- [Next.js docs: Automatic Static Optimization](https://nextjs.org/docs/pages/building-your-application/rendering/automatic-static-optimization)
- [Next.js docs: getInitialProps](https://nextjs.org/docs/pages/api-reference/functions/get-initial-props)
- [Next.js docs: App Router migration](https://nextjs.org/docs/app/guides/migrating/app-router-migration)
- [Next.js docs: Static exports](https://nextjs.org/docs/pages/guides/static-exports)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 10 Next.js 14 15 16 версии Turbopack Cache Components PPR](<./10 Next.js 14 15 16 версии Turbopack Cache Components PPR.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [12 Route Groups Parallel и Intercepting Routes →](<./12 Route Groups Parallel и Intercepting Routes.md>)
<!-- CARD-NAV-BOTTOM:END -->
