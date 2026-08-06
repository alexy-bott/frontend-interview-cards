# Vite dev server build env proxy

<!-- CARD-NAV-TOP:START -->
[← 03 Semver caret tilde exact versions](<./03 Semver caret tilde exact versions.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Webpack entry loaders plugins optimization →](<./05 Webpack entry loaders plugins optimization.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как Vite работает во время разработки и production-сборки? Что обычно настраивают в `vite.config`?**

<h2></h2>

<br>
<dl>
<dd>

Vite объединяет две основные задачи: запускает локальный сервер разработки и создаёт production-сборку приложения.

Во время разработки Vite по умолчанию не собирает всё приложение в один бандл перед запуском. Браузер начинает с `index.html`, запрашивает импортированные ESM-модули, а Vite преобразует TypeScript, JSX, CSS и другие поддерживаемые форматы по мере необходимости.

При production-сборке Vite обходит весь граф импортов, объединяет и оптимизирует модули, разделяет код на чанки и создаёт готовые HTML, JavaScript, CSS и другие ресурсы для размещения на сервере.

Во время разработки Vite хранит граф модулей и следит за изменениями файлов. При изменении он запускает HMR (Hot Module Replacement): отправляет браузеру обновление затронутого модуля без обязательной полной перезагрузки страницы. Сохранится ли состояние конкретного компонента, зависит от framework-плагина, типа изменения и наличия подходящей границы HMR. Например, React-плагин использует Fast Refresh и старается сохранять состояние компонента, когда это безопасно.

Зависимости из `node_modules` Vite предварительно объединяет в режиме разработки. Это решает две основные задачи:

1. Преобразует зависимости из CommonJS или UMD в формат ESM, который может использовать браузер.
2. Объединяет пакеты с большим количеством внутренних модулей, чтобы браузеру не приходилось выполнять сотни отдельных запросов.

Результат сохраняется в `node_modules/.vite`. Vite заново выполняет оптимизацию, если изменился lock-файл, связанные настройки конфигурации или другие данные, влияющие на дерево зависимостей. Принудительно сбросить этот кэш можно запуском Vite с флагом `--force`.

Используемые внутренние инструменты зависят от версии Vite:

| Версия | Разработка | Production-сборка |
| --- | --- | --- |
| Vite 7 и старше | Нативные ESM-модули, esbuild для преобразования JavaScript, TypeScript, JSX и оптимизации зависимостей | Rollup для объединения модулей, чанков и оптимизации |
| Vite 8 | Нативные ESM-модули, Rolldown для оптимизации зависимостей и Oxc для JavaScript-преобразований | Rolldown для сборки и Oxc для JavaScript-преобразований |

Vite 8 выпущен в марте 2026 года и заменил прежнюю связку esbuild и Rollup инструментами на основе Rolldown и Oxc. Настройки underlying-сборщика теперь передаются через `build.rolldownOptions`. Прежнее поле `build.rollupOptions` пока поддерживается как устаревший псевдоним, но для новой конфигурации следует использовать актуальное название.

В `vite.config.ts` обычно подключают плагины, задают alias путей, настройки локального сервера и proxy, публичный `base`, параметры production-сборки и source maps:

```ts
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
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

Alias должен указывать на абсолютный путь файловой системы. В примере путь к `src` формируется относительно `vite.config.ts`, поэтому конфигурация одинаково работает на Windows, Linux и macOS.

Значение `build.sourcemap: "hidden"` создаёт отдельные `.map`-файлы, но не добавляет ссылку на них в итоговый JavaScript. Это удобно для загрузки карт в систему мониторинга ошибок. Однако сами карты не становятся секретными: если опубликовать `.map`-файлы вместе с приложением, их всё равно можно будет скачать.

`server.proxy` действует на локальном сервере разработки. Браузер обращается к `/api` по тому же origin, то есть сочетанию схемы, хоста и порта, с которого открыто приложение. Затем Vite пересылает запрос backend-серверу.

После production-развёртывания dev server Vite не работает, поэтому его proxy-настройка не переносится в рабочую среду. Там маршрутизацию на backend настраивают через Nginx, ingress, серверную платформу или сам backend.

Клиентские переменные доступны через `import.meta.env`. Только значения с разрешённым префиксом, по умолчанию `VITE_`, попадают в клиентский код. Они публичны и не должны содержать пароли, приватные ключи или другие секреты.

Пользовательские значения из `.env` передаются в приложение как строки. Поэтому числа и логические значения нужно преобразовывать явно.

Режим (`mode`), например `development`, `staging` или `production`, определяет, какие файлы `.env.[mode]` будут загружены, и доступен через `import.meta.env.MODE`. Он связан с выбором конфигурации окружения, но не равен автоматически значению `NODE_ENV`.

`base` задаёт базовый публичный путь ресурсов. Если SPA размещено в `/cabinet/`, неверный `base` создаст ссылки на `/assets/...` вместо `/cabinet/assets/...` и сломает загрузку JavaScript, CSS или лениво загружаемых чанков после развёртывания.

`vite preview` локально раздаёт уже созданный каталог сборки, по умолчанию `dist`. Команда нужна для проверки путей, ресурсов, чанков и env-значений production-сборки. Это не production-сервер и не замена Nginx или платформе размещения.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему Vite быстро запускается в режиме разработки?</strong></summary>

<dl>
<dd>
<h2></h2>

Vite по умолчанию не собирает всё приложение перед первым показом страницы. Браузер запрашивает ESM-модули по мере обхода импортов, а Vite преобразует только действительно запрошенные файлы.

Зависимости предварительно объединяются и кэшируются отдельно. Поэтому при повторном запуске Vite не обрабатывает их заново, пока не изменятся данные, влияющие на кэш.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое HMR и чем он отличается от полной перезагрузки?</strong></summary>

<dl>
<dd>
<h2></h2>

HMR позволяет заменить изменившийся модуль без полной перезагрузки HTML-документа. Vite отправляет обновление браузеру, а модуль или framework-плагин решает, можно ли принять его локально.

Полная перезагрузка заново создаёт страницу и сбрасывает её текущее состояние. HMR может сохранить остальную часть приложения, но сохранение состояния конкретного компонента не гарантируется. Например, React Fast Refresh сохраняет его только для поддерживаемых изменений.

Если обновление невозможно безопасно принять через HMR, Vite перезагружает страницу целиком.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делает <code>optimizeDeps</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`optimizeDeps` управляет предварительным объединением зависимостей в режиме разработки.

`include` принудительно добавляет пакет в оптимизацию. Это может понадобиться для локально связанной зависимости или пакета, который Vite не обнаружил автоматически.

`exclude` исключает зависимость из предварительного объединения. Обычно так поступают с корректным ESM-пакетом, которому оптимизация не нужна. CommonJS- или UMD-зависимость не следует исключать без причины, потому что браузеру может потребоваться её преобразование в ESM.

Флаг `--force` заставляет Vite проигнорировать существующий кэш и заново оптимизировать зависимости.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Решает ли <code>server.proxy</code> проблему CORS в рабочей среде?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Во время разработки браузер обращается к API через origin Vite, а dev server пересылает запрос на backend. Для браузера такой запрос выглядит same-origin, поэтому локальная разработка может работать без отдельной CORS-настройки.

После production-развёртывания dev server отсутствует. Нужен настоящий reverse proxy, общий origin приложения и API либо корректная CORS-политика backend-сервера.

У `vite preview` может быть собственная настройка `preview.proxy`, но это также только локальная проверка сборки, а не production-инфраструктура.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему секрет нельзя хранить в <code>VITE_*</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Переменные с префиксом `VITE_` становятся частью клиентского кода. Пользователь может скачать JavaScript-бандл и прочитать эти значения независимо от того, отображаются они в интерфейсе или нет.

Префикс разрешает передать переменную в браузер, а не защищает её. Секреты должны оставаться на backend, в serverless-функции или в защищённой конфигурации серверной инфраструктуры.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>mode</code> отличается от <code>NODE_ENV</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`mode` определяет набор env-файлов и значение `import.meta.env.MODE`. Например, команда `vite build --mode staging` загружает `.env.staging`, а `import.meta.env.MODE` будет равно `"staging"`.

`NODE_ENV` влияет на то, считается ли запуск development- или production-режимом, и отражается в `import.meta.env.DEV` и `import.meta.env.PROD`.

Эти значения могут различаться. Например, `vite build --mode staging` по-прежнему выполняет production-сборку: `MODE` будет равен `"staging"`, а `PROD` — `true`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем настраивать <code>base</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Vite использует `base` при формировании URL для JavaScript, CSS, статических ресурсов и динамических импортов.

Значение `/` подходит для размещения в корне домена, а `/cabinet/` — для размещения приложения в соответствующем подкаталоге. Значение должно совпадать с реальным путём хостинга и настройками маршрутизации сервера.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>При чём здесь Rollup, если проект использует Vite?</strong></summary>

<dl>
<dd>
<h2></h2>

В Vite 7 и предыдущих версиях Rollup выполнял production-сборку. Поэтому расширенные настройки сборщика передавались через `build.rollupOptions`.

Начиная с Vite 8 production-сборку выполняет Rolldown, а актуальное поле называется `build.rolldownOptions`. Поле `build.rollupOptions` временно сохранено как устаревший псевдоним для облегчения миграции.

Поэтому перед объяснением внутренней цепочки Vite важно уточнить версию проекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем запускать <code>vite preview</code>, если dev server уже работает?</strong></summary>

<dl>
<dd>
<h2></h2>

Dev server отдаёт преобразованные исходные модули, а `vite preview` раздаёт файлы, которые уже создала команда `vite build`.

Это позволяет проверить production-сборку локально и обнаружить неверный `base`, отсутствующие ресурсы, ошибки динамических импортов и различия env-конфигурации.

`vite preview` ближе к рабочей сборке, чем dev server, но не заменяет проверку на настоящем production-хостинге.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Настройка |
| --- | --- |
| React и Fast Refresh | `@vitejs/plugin-react` |
| Alias для `src` | `resolve.alias` |
| Локальный backend-сервер | `server.proxy` |
| Размещение в подкаталоге | `base` |
| Source maps без ссылки из бандла | `build.sourcemap: "hidden"` |
| Публичная конфигурация | `import.meta.env.VITE_*` |
| Настройка чанков в Vite 8 | `build.rolldownOptions` |

## Связанные темы

- [06 Bundle code splitting tree shaking size budgets](<./06 Bundle code splitting tree shaking size budgets.md>)
- [07 Env variables frontend build runtime secrets](<./07 Env variables frontend build runtime secrets.md>)
- [09 Production build assets hashing base publicPath](<./09 Production build assets hashing base publicPath.md>)
- [10 Babel transpilation polyfills browserslist](<./10 Babel transpilation polyfills browserslist.md>)
- [04 URL origin domain path query fragment](<../Web Basics/04 URL origin domain path query fragment.md>)
- [05 CORS same-origin preflight credentials](<../Security/05 CORS same-origin preflight credentials.md>)

## Источники

- [Vite Guide](https://vite.dev/guide/)
- [Vite: Dependency Pre-Bundling](https://vite.dev/guide/dep-pre-bundling.html)
- [Vite: Config](https://vite.dev/config/)
- [Vite: Env Variables and Modes](https://vite.dev/guide/env-and-mode)
- [Vite: Deploying a Static Site](https://vite.dev/guide/static-deploy)
- [Vite 8 announcement](https://vite.dev/blog/announcing-vite8)
- [Vite 8 migration guide](https://vite.dev/guide/migration.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 03 Semver caret tilde exact versions](<./03 Semver caret tilde exact versions.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [05 Webpack entry loaders plugins optimization →](<./05 Webpack entry loaders plugins optimization.md>)
<!-- CARD-NAV-BOTTOM:END -->
