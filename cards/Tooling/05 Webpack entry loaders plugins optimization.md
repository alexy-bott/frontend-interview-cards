# 05 Webpack entry loaders plugins optimization

<!-- CARD-NAV-TOP:START -->
[← 04 Vite dev server build env proxy](<./04 Vite dev server build env proxy.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Bundle code splitting tree shaking size budgets →](<./06 Bundle code splitting tree shaking size budgets.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

Как устроена конфигурация Webpack? Чем отличаются `entry`, loaders, plugins, `output` и `optimization`?

#### Ответ

Webpack является сборщиком модулей (module bundler). Он начинает с точки входа `entry`, проходит по импортам, строит граф зависимостей и формирует один или несколько chunks, то есть частей бандла, с JavaScript, CSS и другими ресурсами для браузера.

Основные части конфигурации решают разные задачи:

| Раздел | Назначение |
| --- | --- |
| `entry` | Начальные модули графа |
| `module.rules` | Правила преобразования импортированных файлов через loaders |
| `plugins` | Расширение процесса сборки через плагины |
| `output` | Каталог, имена и публичные URL результатов |
| `resolve` | Поиск модулей, расширений и псевдонимов путей |
| `optimization` | Разделение чанков, runtime, минификация и стабильность идентификаторов |
| `devServer` | Локальный сервер, HMR, проксирование и fallback для SPA |

Упрощённая production-конфигурация выглядит так:

```js
const path = require("node:path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  mode: "production",
  entry: "./src/index.tsx",
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "assets/[name].[contenthash].js",
    chunkFilename: "assets/[name].[contenthash].js",
    publicPath: "/",
    clean: true,
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        exclude: /node_modules/,
        use: "babel-loader",
      },
      {
        test: /\.scss$/,
        use: ["style-loader", "css-loader", "sass-loader"],
      },
    ],
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
  plugins: [new HtmlWebpackPlugin({ template: "./public/index.html" })],
  optimization: {
    splitChunks: { chunks: "all" },
    runtimeChunk: "single",
  },
};
```

Loader преобразует содержимое конкретного импортированного модуля. В цепочке `use` loaders выполняются справа налево: `sass-loader` превращает SCSS в CSS, `css-loader` разбирает CSS-импорты, затем `style-loader` вставляет стили в документ. В production-сборке вместо `style-loader` CSS часто извлекают в отдельный файл с помощью плагина.

Plugin подключается к hooks, то есть точкам расширения процесса сборки, и работает шире одного файла. Он может создать HTML, извлечь CSS, определить константы времени сборки, скопировать ресурсы, показать ход выполнения или построить отчёт о бандле. Loader преобразует отдельный модуль, а plugin управляет процессом сборки.

`output.filename` задаёт имена начальных чанков, `chunkFilename` имена асинхронных чанков, `path` физический каталог, а `publicPath` URL-префикс для загрузки ресурсов во время выполнения. Неверный `publicPath` часто проявляется только после развёртывания: точка входа загружается, но динамический импорт запрашивает чанк по неправильному адресу.

`mode: "development"` и `mode: "production"` включают разные настройки по умолчанию. Режим `production` включает минификацию, задаёт `process.env.NODE_ENV` и активирует оптимизации, но не заменяет явную настройку путей, карт исходного кода, кеширования и стратегии разделения кода.

`optimization.splitChunks` выделяет общий код между точками входа и асинхронными импортами. `runtimeChunk` может вынести webpack runtime, то есть служебный код для связывания модулей и загрузки чанков, в отдельный файл. Стабильные идентификаторы модулей и чанков вместе с `contenthash` помогают не менять имена неизменившихся файлов при каждой сборке.

Tree shaking удаляет неиспользуемый код из production-бандла. Для него нужны ESM и экспорты, которые можно определить статически. `optimization.usedExports` отмечает используемые значения, поле `sideEffects` сообщает, какие модули можно безопасно удалить, а минификатор окончательно убирает мёртвый код. CommonJS, динамический доступ и неверное описание побочных эффектов ограничивают оптимизацию.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Чем loader отличается от plugin?
>
> **Ответ:** Loader преобразует импортируемый файл и возвращает JavaScript либо результат для следующего loader. Plugin подключается к точкам расширения сборки и может влиять на граф, чанки, ресурсы и итоговые файлы. SCSS обрабатывает цепочка loaders, а HTML-файл обычно создаёт plugin.

> [!followup]
> **Вопрос:** В каком порядке выполняются loaders?
>
> **Ответ:** Обычная цепочка `use` выполняется справа налево. Для `use: ["style-loader", "css-loader", "sass-loader"]` сначала работает `sass-loader`, затем `css-loader`, затем `style-loader`. У loader также есть фазы `pitch` и `normal`, но для настройки типовой цепочки достаточно помнить направление преобразования.

> [!followup]
> **Вопрос:** Что такое `publicPath`?
>
> **Ответ:** Это базовый URL, который служебный код Webpack использует для ресурсов и лениво загружаемых чанков. Физический `output.path` может быть `dist`, а публичный путь `/app/assets/` или адрес CDN. Ошибка приводит к 404 при динамическом импорте, даже если файл присутствует на сервере.

> [!followup]
> **Вопрос:** Что изменили Asset Modules в Webpack 5?
>
> **Ответ:** Они добавили встроенную обработку ресурсов без обязательных `file-loader`, `url-loader` и `raw-loader`. `asset/resource` создаёт отдельный файл, `asset/inline` возвращает data URL, `asset/source` отдаёт текст, а `asset` выбирает между встраиванием и отдельным файлом по размеру.

> [!followup]
> **Вопрос:** Что делает `splitChunks`?
>
> **Ответ:** Он анализирует общий код и формирует переиспользуемые чанки по условиям размера, числа использований и правилам `cacheGroups`. Это уменьшает дублирование и помогает кешу браузера, но чрезмерное объединение в один vendor-чанк может заставить пользователя скачать код всех экранов сразу.

> [!followup]
> **Вопрос:** Зачем выносить `runtimeChunk`?
>
> **Ответ:** Webpack runtime содержит таблицу модулей и логику загрузки чанков. Отдельный файл может улучшить долгосрочное кеширование: изменение кода приложения не обязано менять vendor-чанк только из-за служебных данных runtime. Польза зависит от количества точек входа и стратегии HTTP-кеширования.

> [!followup]
> **Вопрос:** Работает ли `devServer.proxy` в production?
>
> **Ответ:** Нет. Webpack Dev Server работает только во время разработки. После развёртывания проксирование, раздачу статических файлов, заголовки кеширования и fallback для SPA настраивают в Nginx, ingress, CDN или на backend-сервере.

> [!followup]
> **Вопрос:** Почему import одной функции иногда включает почти всю библиотеку?
>
> **Ответ:** Сборщик может использовать CommonJS-точку входа, импорт пространства имён, barrel-файл с побочными эффектами или пакет без корректного ESM и поля `sideEffects`. Нужно проверить фактическую точку входа из `exports` и результат в анализаторе бандла. Замена синтаксиса импорта помогает только тогда, когда пакет предоставляет подходящую модульную структуру.

#### Где это встречается во frontend

| Симптом | Что проверить |
| --- | --- |
| SCSS не импортируется | `module.rules` и порядок loaders |
| Lazy chunk даёт 404 | `output.publicPath` и хостинг |
| Общий код дублируется | `optimization.splitChunks` |
| Хеш меняется у неизменного vendor-чанка | Runtime и стабильность идентификаторов |
| Большой начальный бандл | Точки входа, `cacheGroups` и импорты |
| Медленная повторная сборка | Постоянный кеш, loaders и карты исходного кода |

#### Связанные темы

- [06 Bundle code splitting tree shaking size budgets](<./06 Bundle code splitting tree shaking size budgets.md>)
- [08 Source maps production debugging security](<./08 Source maps production debugging security.md>)
- [09 Production build assets hashing base publicPath](<./09 Production build assets hashing base publicPath.md>)
- [12 SCSS modules use forward architecture](<../CSS/12 SCSS modules use forward architecture.md>)

#### Источники

- [Webpack: Concepts](https://webpack.js.org/concepts/)
- [Webpack: Loaders](https://webpack.js.org/concepts/loaders/)
- [Webpack: Plugins](https://webpack.js.org/concepts/plugins/)
- [Webpack: Output](https://webpack.js.org/configuration/output/)
- [Webpack: Optimization](https://webpack.js.org/configuration/optimization/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 04 Vite dev server build env proxy](<./04 Vite dev server build env proxy.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [06 Bundle code splitting tree shaking size budgets →](<./06 Bundle code splitting tree shaking size budgets.md>)
<!-- CARD-NAV-BOTTOM:END -->
