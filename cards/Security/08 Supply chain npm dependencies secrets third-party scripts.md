# Supply chain npm dependencies secrets third-party scripts

<!-- CARD-NAV-TOP:START -->
[← 07 Auth permissions frontend backend responsibility](<./07 Auth permissions frontend backend responsibility.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 WebSocket security auth origin reconnect →](<./09 WebSocket security auth origin reconnect.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Какие supply chain риски есть во frontend и как защищать npm dependencies, сборку, secrets и third-party scripts?**

<h2></h2>

<br>
<dl>
<dd>

**Supply chain attack**, или атака через цепочку поставки, затрагивает приложение не через его исходный код, а через инструменты и компоненты, которым команда доверяет: npm-пакет, транзитивную зависимость (зависимость установленного пакета), реестр пакетов (registry), аккаунт сопровождающего (maintainer), скрипт установки, задачу CI (CI action), CDN или внешний script.

Frontend-проекты особенно чувствительны к таким атакам. Дерево зависимостей содержит много пакетов, код сборочных devDependencies выполняется в CI, а скомпрометированная runtime dependency или внешний script получает возможности JavaScript приложения. Runtime dependency - зависимость, код которой нужен работающему приложению, а не только инструментам разработки.

Возможные сценарии:

- злоумышленник захватил аккаунт maintainer и выпустил вредоносную версию;
- разработчик установил пакет с похожим именем, созданный для обмана (typosquatting);
- публичный package подменил внутреннюю зависимость из-за dependency confusion, то есть ошибки выбора между публичным и private registry;
- скрипт жизненного цикла (lifecycle script) выполнил код во время `npm install`;
- CDN или script системы аналитики изменился после проверки изменений (review);
- secret попал в bundle, source map, CI log или опубликованный npm package.

Lock-файл фиксирует точное дерево версий и контрольные хеши целостности (`integrity`) загруженных архивов. `npm ci` устанавливает дерево из lock-файла, не обновляет его и завершает работу при существенном расхождении с `package.json`. Это делает установку воспроизводимой и не позволяет CI незаметно выбрать более новую совместимую версию. Но lock-файл не доказывает, что зафиксированный код безопасен, и не спасает, если вредоносная версия уже попала в него после неосторожного обновления.

Практическая защита включает:

1. Коммитить lock-файл и в CI устанавливать только зафиксированное дерево, например через `npm ci`.
2. Фиксировать версию Node.js и package manager, проверять изменения `package.json` и lock-файла при review.
3. Явно настраивать registry для private scopes, использовать publish tokens с минимальными правами и многофакторную аутентификацию (MFA) для публикации.
4. Проверять новые пакеты: назначение, владельцев, частоту обновлений, install scripts, число зависимостей и возможность обойтись уже имеющимся кодом.
5. Обновлять зависимости небольшими порциями, запускать тесты и сборку, читать описание релиза (release notes) и оценивать, достигает ли приложение уязвимого кода.
6. Не передавать клиентской сборке настоящие secrets. Все переменные, использованные клиентским кодом, считаются публичными.
7. Минимизировать сторонние scripts, ограничивать их CSP, а для неизменяемых CDN-файлов применять Subresource Integrity.

Автоматический scanner уязвимостей показывает известные проблемы по версиям, но не определяет полный риск. Он может не знать о новой атаке, не понимать достижимость уязвимого пути или сообщать о пакете, который используется только при сборке. Результат нужно классифицировать, а не игнорировать или исправлять бесконтрольным обновлением major version.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что именно гарантирует lock-файл?</strong></summary>

<dl>
<dd>
<h2></h2>

Он описывает выбранные версии прямых и транзитивных зависимостей, источники архивов и значения `integrity`. При неизменном registry и поддерживаемом менеджере пакетов это позволяет повторить одно дерево. Lock-файл не проводит аудит содержимого, не гарантирует отсутствие вредоносного кода и требует такой же проверки, как другой исполняемый вход проекта.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>npm ci</code> отличается от <code>npm install</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`npm ci` предназначен для воспроизводимой чистой установки: требует lock-файл, удаляет существующий `node_modules`, устанавливает зафиксированное дерево и не переписывает `package.json` или lock-файл. `npm install` разрешает зависимости и может обновить lock в соответствии с ranges. Поэтому в CI обычно используют `npm ci`, а изменение зависимостей выполняют осознанно локально.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему недостаточно зафиксировать версии только в <code>package.json</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Диапазон вроде `^1.4.0` разрешает более новые версии, а транзитивные зависимости часто вообще не перечислены в корневом `package.json`. Две установки в разное время могут получить разные деревья. Lock-файл фиксирует фактически выбранные версии всего дерева.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как сделать версии Node.js и package manager одинаковыми в команде и CI?</strong></summary>

<dl>
<dd>
<h2></h2>

Версию Node фиксируют файлом менеджера окружения, например `.nvmrc` или `.node-version`, и тем же образом задают ее в образе CI. Поле `engines` документирует допустимый диапазон, а `packageManager` в `package.json` фиксирует manager и версию для процесса с Corepack. CI должен проверять версии и использовать lock-файл, иначе локальная договоренность остается необязательной.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем опасны npm lifecycle scripts?</strong></summary>

<dl>
<dd>
<h2></h2>

Пакет может выполнить `preinstall`, `install` или `postinstall` во время установки. Такой код видит файлы проекта, окружение и доступные учетные данные CI. Установку запускают с минимальными правами, не передают лишние secrets и проверяют пакеты со scripts. `--ignore-scripts` снижает риск, но способен сломать зависимости, которым script нужен для сборки native module или загрузки бинарного файла.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое dependency confusion?</strong></summary>

<dl>
<dd>
<h2></h2>

Менеджер пакетов выбирает публичный package с именем, совпадающим с внутренним, вместо private package компании. Атакующий публикует такое имя в общедоступном registry и рассчитывает на неверный порядок разрешения или более высокую версию. Защита - private scopes, явная настройка registry для scope, контроль конфигурации и запрет случайной публикации внутренних имен.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое typosquatting?</strong></summary>

<dl>
<dd>
<h2></h2>

Это публикация вредоносного пакета с именем, похожим на популярный: переставленная буква, дефис или другой scope. Разработчик ошибается при установке, и пакет получает возможность выполнить install script или попасть в bundle. Имя и владельца новой зависимости проверяют до установки и commit.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему devDependency тоже может быть риском безопасности?</strong></summary>

<dl>
<dd>
<h2></h2>

DevDependency выполняется на машине разработчика и в CI, читает исходный код и участвует в сборке production bundle. Скомпрометированный plugin для bundler может внедрить код в артефакт или украсть CI token, даже если сам пакет не отправляется браузеру отдельным модулем.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что проверять при добавлении новой зависимости?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала подтверждают, что задача не закрывается уже установленным API или небольшим локальным кодом. Затем смотрят владельцев, repository и историю релизов, число и качество dependencies, lifecycle scripts, влияние на browser bundle, лицензию и политику обновлений. После установки review включает `package.json`, lock-файл и результат сборки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать при сообщении об уязвимости в зависимости?</strong></summary>

<dl>
<dd>
<h2></h2>

Определить затронутые версии, путь зависимости и достижимость уязвимого кода в конкретной среде. Затем выбрать минимальное безопасное обновление, override, удаление функции или замену пакета, прогнать тесты и проверить bundle. Риск зависимости production runtime, инструмента сборки и неиспользуемого optional package оценивается по-разному, но решение фиксируется, а не откладывается без срока.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>npm audit fix --force</code> нельзя запускать вслепую?</strong></summary>

<dl>
<dd>
<h2></h2>

Команда может установить новые major versions и изменить поведение приложения, не доказав, что исходная уязвимость была достижима или что обновление безопасно. Автоматический отчет является входом для анализа. Исправление проходит обычный review, тесты, сборку и при необходимости ручную миграцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое package provenance?</strong></summary>

<dl>
<dd>
<h2></h2>

Provenance связывает опубликованный package с конкретным source repository и CI workflow с помощью проверяемого подтверждения происхождения (attestation). Это помогает подтвердить источник артефакта и затрудняет незаметную ручную публикацию из другого места. Provenance не доказывает безопасность исходного кода и не заменяет review владельцев и изменений.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему frontend environment variables не являются secrets?</strong></summary>

<dl>
<dd>
<h2></h2>

Bundler заменяет используемые переменные значениями при сборке или код получает их из публичной runtime-конфигурации. Пользователь может прочитать bundle, Network panel и память страницы. Настоящие пароли баз данных, private API keys и ключи подписи хранятся на backend или в хранилище секретов CI и никогда не передаются браузеру.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли публичный API key находиться во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Иногда да, если провайдер специально создал browser key как идентификатор проекта, а не как доказательство доверия. Его ограничивают допустимыми origins, API, квотой и минимальными permissions. Backend не должен принимать такой key как единственное подтверждение личности или права на чувствительную операцию.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем опасен third-party script?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный `<script>` выполняется в origin страницы и может читать DOM, перехватывать ввод, обращаться к доступному storage и отправлять запросы. Browser sandbox разделяет разные origins, но не изолирует script системы аналитики от кода той же страницы. Поэтому каждый внешний script становится доверенной частью threat model и требует владельца, цели, минимального доступа и плана удаления.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Subresource Integrity?</strong></summary>

<dl>
<dd>
<h2></h2>

Атрибут `integrity` содержит криптографический hash ожидаемого внешнего script или style. Браузер выполняет ресурс только при совпадении содержимого. SRI подходит для неизменяемого URL с зафиксированной версией; при каждом обновлении файла hash нужно обновлять. Для cross-origin ресурса также требуется корректная CORS-настройка и обычно атрибут `crossorigin`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли CSP для безопасного third-party script?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. CSP разрешает загрузку источника, но доверенный script после загрузки получает широкие возможности страницы. CSP помогает запретить неожиданные domains и исходящие соединения, SRI фиксирует содержимое конкретного файла, а iframe с `sandbox` может изолировать отдельный виджет. Главная мера - не подключать ненужный код в основной контекст выполнения страницы.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Изменение | Что проверить |
| --- | --- |
| Добавили npm package | Владельцы, scripts, dependencies, bundle impact, license и lock diff |
| Dependabot или Renovate открыл update | Changelog, затронутый код, tests, build и изменение дерева зависимостей |
| CI устанавливает зависимости | Зафиксированные Node и package manager, `npm ci`, минимальные учетные данные |
| Добавили SDK аналитики или платежной системы | Доступ к данным, CSP, SRI или изоляция через iframe, владелец интеграции |
| Создали `.env.production` | Какие значения попадут в client bundle и где остаются server secrets |

## Связанные темы

- [01 package.json scripts dependencies devDependencies](<../Tooling/01 package.json scripts dependencies devDependencies.md>)
- [02 lock files npm ci и воспроизводимая установка](<../Tooling/02 lock files npm ci и воспроизводимая установка.md>)
- [06 Env variables secrets build-time runtime](<../DevOps/06 Env variables secrets build-time runtime.md>)
- [06 CSP security headers clickjacking](<./06 CSP security headers clickjacking.md>)
- [11 postMessage iframe open redirect tabnabbing](<./11 postMessage iframe open redirect tabnabbing.md>)

## Источники

- [npm Docs: npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)
- [npm Docs: package-lock.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json)
- [npm Docs: Scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts/)
- [npm Docs: Generating provenance statements](https://docs.npmjs.com/generating-provenance-statements/)
- [OWASP: Software Supply Chain Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html)
- [W3C: Subresource Integrity](https://www.w3.org/TR/SRI/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Auth permissions frontend backend responsibility](<./07 Auth permissions frontend backend responsibility.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 WebSocket security auth origin reconnect →](<./09 WebSocket security auth origin reconnect.md>)
<!-- CARD-NAV-BOTTOM:END -->
