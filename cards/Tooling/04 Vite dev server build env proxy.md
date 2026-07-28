# 04 Vite dev server build env proxy

<!-- CARD-NAV-TOP:START -->
[← 03 Semver caret tilde exact versions](<./03 Semver caret tilde exact versions.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Webpack entry loaders plugins optimization →](<./05 Webpack entry loaders plugins optimization.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как Vite работает во время разработки и production-сборки? Что обычно настраивают в `vite.config`?

#### Ответ

Vite является сервером разработки (dev server) и инструментом production-сборки frontend-приложений. Во время разработки он отдаёт исходные модули через нативную поддержку ESM в браузере и преобразует файл по запросу. При сборке Vite объединяет и оптимизирует граф модулей в готовые HTML, JavaScript, CSS и другие ресурсы.

В режиме разработки браузер начинает с `index.html` и запрашивает импортированные ESM-модули. Vite преобразует TypeScript, JSX, CSS и другие поддерживаемые форматы только тогда, когда они понадобились. Он хранит граф модулей и при изменении файла выполняет HMR (Hot Module Replacement), то есть заменяет затронутый модуль без полной перезагрузки страницы, если плагин и модуль поддерживают такое обновление.

Зависимости из `node_modules` Vite предварительно объединяет. Это решает две задачи: преобразует CommonJS/UMD в ESM для браузера и сокращает сотни внутренних запросов у пакета до небольшого числа модулей. Результат хранится в `node_modules/.vite`; изменение lock-файла или значимой конфигурации сбрасывает этот кэш.

Архитектура зависит от версии:

| Версия | Разработка | Production-сборка |
| --- | --- | --- |
| Vite 7 и старше | ESM-сервер разработки, esbuild для части преобразований и предварительного объединения зависимостей | Rollup |
| Vite 8 | ESM-сервер разработки, Rolldown и Oxc | Rolldown и Oxc |

Vite 8 выпущен в марте 2026 года и использует единый сборщик Rolldown, написанный на Rust. Настройка production-сборки переехала в `build.rolldownOptions`; прежняя `build.rollupOptions` пока работает как устаревший псевдоним. Поэтому ответ «Vite всегда собирает через Rollup» верен для прежних версий, но не для Vite 8.

В `vite.config.ts` обычно подключают плагины, задают псевдонимы путей, локальное проксирование API, `base`, переменные окружения, параметры сборки и карты исходного кода:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": "/src",
    },
  },
  server: {
    proxy: {
      "/api": "http://localhost:3000",
    },
  },
  build: {
    sourcemap: "hidden",
  },
});
```

`server.proxy` действует только на локальном сервере разработки. Браузер обращается к `/api` по тому же origin, то есть сочетанию схемы, хоста и порта, с которого открыт Vite. Затем Vite пересылает запрос backend-серверу. В рабочей среде такое проксирование настраивают в Nginx, ingress, правилах хостинга или на backend. Конфигурация Vite туда не переносится.

Клиентские переменные доступны через `import.meta.env`. Только значения с разрешённым префиксом, по умолчанию `VITE_`, попадают в клиентский код. Они подставляются во время сборки и являются публичными. Режим (`mode`), например `development`, `staging` или `production`, определяет набор файлов `.env.[mode]` и не равен автоматически значению `NODE_ENV`.

`base` задаёт базовый публичный путь ресурсов. Если SPA размещено в `/cabinet/`, неверный `base` создаст ссылки на `/assets/...` вместо `/cabinet/assets/...` и сломает загрузку JavaScript, CSS или лениво загружаемых чанков после развёртывания.

`vite preview` локально раздаёт уже собранный каталог. Это не production-сервер и не замена Nginx или платформе размещения. Команда нужна для быстрой проверки путей, загрузки чанков и поведения собранной версии.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Почему Vite быстро запускается в режиме разработки?
>
> **Ответ:** Он не собирает всё приложение перед первым показом. Браузер запрашивает ESM-модули по мере обхода импортов, а Vite преобразует только нужные файлы. Зависимости предварительно объединяются и кэшируются, поэтому повторный запуск не обрабатывает их без причины.

> [!followup]
> **Вопрос:** Что такое HMR и чем он отличается от полной перезагрузки?
>
> **Ответ:** HMR заменяет изменившийся модуль и сообщает принимающей границе обновить интерфейс, сохраняя остальное состояние страницы. Полная перезагрузка заново создаёт документ и теряет состояние. Если изменение нельзя безопасно принять, Vite перезагружает страницу целиком.

> [!followup]
> **Вопрос:** Что делает `optimizeDeps`?
>
> **Ответ:** Он управляет предварительным объединением зависимостей только в режиме разработки. `include` принудительно добавляет проблемный или локально связанный пакет, `exclude` исключает ESM-пакет, а `--force` перестраивает кеш. CommonJS-зависимость нельзя исключать без проверки, потому что браузеру может понадобиться её преобразование для совместимости с ESM.

> [!followup]
> **Вопрос:** Решает ли `server.proxy` проблему CORS в рабочей среде?
>
> **Ответ:** Нет. Во время разработки браузер обращается к API по origin Vite, а сервер разработки пересылает запрос. После развёртывания этого сервера нет. Нужен настоящий reverse proxy, общий origin приложения и API либо корректная CORS-политика backend-сервера.

> [!followup]
> **Вопрос:** Почему секрет нельзя хранить в `VITE_*`?
>
> **Ответ:** Значение подставляется в клиентский JavaScript во время сборки. Пользователь может скачать бандл и прочитать его независимо от того, показывается значение в интерфейсе или нет. Префикс разрешает публикацию переменной, а не защищает её.

> [!followup]
> **Вопрос:** Зачем настраивать `base`?
>
> **Ответ:** Vite использует его при формировании URL для точки входа, ресурсов и динамических импортов. Значение `/` подходит корню домена, а `/cabinet/` нужно для подкаталога. Оно должно согласовываться с адресом хостинга и fallback-правилом маршрутизации.

> [!followup]
> **Вопрос:** При чём здесь Rollup, если проект использует Vite?
>
> **Ответ:** В Vite 7 и предыдущих версиях Rollup выполнял production-сборку, поэтому расширенные настройки находились в `build.rollupOptions`. В Vite 8 эту роль получил Rolldown, а актуальное поле называется `build.rolldownOptions`. Версию проекта нужно назвать до объяснения внутренней цепочки.

> [!followup]
> **Вопрос:** Зачем запускать `vite preview`, если dev server уже работает?
>
> **Ответ:** Сервер разработки отдаёт преобразованные исходники, а `vite preview` раздаёт результат `vite build`. Так обнаруживаются неверный `base`, отсутствующие ресурсы, ошибка динамического импорта и различия переменных окружения. Проверка не заменяет рабочий хостинг, но ближе к нему, чем режим разработки.

#### Где это встречается во frontend

| Задача | Настройка |
| --- | --- |
| React и Fast Refresh | `@vitejs/plugin-react` |
| Alias для `src` | `resolve.alias` |
| Локальный backend-сервер | `server.proxy` |
| Размещение в подкаталоге | `base` |
| Закрытая загрузка карт исходного кода | `build.sourcemap: "hidden"` |
| Публичная конфигурация | `import.meta.env.VITE_*` |
| Настройка чанков в Vite 8 | `build.rolldownOptions` |

#### Связанные темы

- [06 Bundle code splitting tree shaking size budgets](<./06 Bundle code splitting tree shaking size budgets.md>)
- [07 Env variables frontend build runtime secrets](<./07 Env variables frontend build runtime secrets.md>)
- [09 Production build assets hashing base publicPath](<./09 Production build assets hashing base publicPath.md>)
- [10 Babel transpilation polyfills browserslist](<./10 Babel transpilation polyfills browserslist.md>)
- [04 URL origin domain path query fragment](<../Web Basics/04 URL origin domain path query fragment.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)

#### Источники

- [Vite Guide](https://vite.dev/guide/)
- [Vite: Dependency Pre-Bundling](https://vite.dev/guide/dep-pre-bundling.html)
- [Vite: Config](https://vite.dev/config/)
- [Vite 8 announcement](https://vite.dev/blog/announcing-vite8)
- [Vite 8 migration guide](https://vite.dev/guide/migration.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Semver caret tilde exact versions](<./03 Semver caret tilde exact versions.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Webpack entry loaders plugins optimization →](<./05 Webpack entry loaders plugins optimization.md>)
<!-- CARD-NAV-BOTTOM:END -->
