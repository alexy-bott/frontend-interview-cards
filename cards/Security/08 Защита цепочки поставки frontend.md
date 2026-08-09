# Защита цепочки поставки frontend

<!-- CARD-NAV-TOP:START -->
[← 07 Ответственность frontend и backend в авторизации](<./07 Ответственность frontend и backend в авторизации.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Безопасность WebSocket →](<./09 Безопасность WebSocket.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Какие supply chain риски есть во frontend и как защищать npm dependencies, сборку, secrets и third-party scripts?**

<h2></h2>

<br>
<dl>
<dd>

**Supply chain attack**, или атака через цепочку поставки, воздействует на приложение через компонент или процесс, которому команда доверяет.

Атакующий может не изменять исходный код приложения напрямую.

Вместо этого он компрометирует:

- npm-пакет;
- транзитивную dependency;
- аккаунт maintainer;
- package registry;
- lifecycle script;
- CI action;
- build plugin;
- publish token;
- artifact storage;
- CDN;
- tag manager;
- внешний script;
- систему обновления dependencies.

Упрощённая цепочка frontend-проекта:

```text
source code

→ dependencies

→ package manager

→ install scripts

→ build tools

→ CI environment

→ production artifact

→ CDN / hosting

→ browser

→ third-party runtime scripts
```

Уязвимость или компрометация на любом этапе может повлиять на конечное приложение.

### Почему frontend особенно чувствителен

Frontend-проект обычно использует большое дерево JavaScript-зависимостей.

Один прямой package может установить десятки или сотни транзитивных dependencies:

```text
application
→ package A
→ package B
→ package C
→ package D
```

При этом код dependencies может выполняться в разных средах:

| Вид кода | Где выполняется | Что может получить |
| --- | --- | --- |
| Runtime dependency | В browser пользователя | DOM, JavaScript storage, пользовательский ввод, API |
| Build dependency | В CI или на машине разработчика | Source code, environment, build artifact |
| Lifecycle script | Во время установки | Filesystem, environment variables, network |
| CI action | В pipeline | Repository, artifacts, CI permissions, secrets |
| Third-party script | В browser как код страницы | Возможности origin приложения |

Поэтому `devDependency` не обязательно безопаснее runtime dependency.

Она может:

- прочитать source code;
- украсть CI credentials;
- внедрить код в production bundle;
- изменить source map;
- подменить build artifact;
- выполнить произвольную команду во время установки.

### Основные этапы риска

Удобно разделять цепочку на несколько этапов.

#### 1. Выбор dependency

Риски:

- typosquatting;
- заброшенный package;
- неизвестные maintainers;
- чрезмерное число dependencies;
- package с install scripts;
- package, который решает слишком маленькую задачу ценой большого доверия.

#### 2. Разрешение и установка

Риски:

- dependency confusion;
- изменение транзитивной версии;
- подмена registry;
- lifecycle script;
- Git dependency с mutable branch;
- установка tarball по изменяемому URL.

#### 3. Сборка

Риски:

- скомпрометированный bundler plugin;
- утечка CI secrets;
- изменение output после tests;
- запуск untrusted pull request с привилегиями;
- mutable CI action или container image.

#### 4. Публикация

Риски:

- кража npm publish token;
- захват maintainer account;
- ручная публикация не того commit;
- публикация лишних файлов;
- подмена package перед upload.

#### 5. Доставка artifact

Риски:

- изменение файлов на CDN;
- повторная сборка с другим набором dependencies;
- публикация непроверенного artifact;
- неправильные cache или deployment permissions.

#### 6. Runtime в browser

Риски:

- скомпрометированный third-party script;
- изменение tag manager configuration;
- чтение DOM и пользовательского ввода;
- отправка данных внешнему provider;
- выполнение кода с полномочиями origin приложения.

### Типичные сценарии атаки

| Сценарий | Что происходит |
| --- | --- |
| Захват maintainer account | Выпускается вредоносная версия популярного package |
| Typosquatting | Разработчик устанавливает package с похожим именем |
| Dependency confusion | Публичный package подменяет внутреннюю dependency |
| Lifecycle script | Код выполняется во время установки и читает CI environment |
| Compromised build plugin | В production bundle внедряется вредоносный JavaScript |
| Украденный publish token | Атакующий публикует новую версию package |
| Compromised CDN | Browser получает изменённый внешний script |
| Tag manager compromise | Новый script добавляется без изменения application repository |
| Secret in bundle | Server credential становится доступен любому пользователю |
| Secret in published package | `.env`, `.npmrc` или private key попадает в tarball |

### Прямые и транзитивные dependencies

**Прямая dependency** указана в корневом `package.json`:

```json
{
  "dependencies": {
    "library-a": "1.4.2"
  }
}
```

**Транзитивная dependency** устанавливается другой dependency:

```text
application
→ library-a
→ library-b
```

Команда могла никогда не выбирать `library-b` напрямую, но её код всё равно:

- устанавливается;
- может выполнять lifecycle script;
- может попасть в bundle;
- может содержать известную уязвимость;
- может быть скомпрометирован.

Поэтому анализировать нужно полное дерево, а не только корневой `package.json`.

### Runtime и devDependencies

`dependencies` и `devDependencies` описывают назначение package, но не границу безопасности.

Runtime dependency может попасть в browser:

```text
react component library
analytics client
markdown renderer
```

DevDependency может выполняться в CI:

```text
bundler
transpiler
test runner
linter plugin
code generator
```

Скомпрометированный build plugin способен:

```text
прочитать source code

→ прочитать CI environment

→ изменить production bundle

→ скрыть изменение от обычного review
```

Поэтому обе группы входят в supply chain threat model.

### Минимизировать количество dependencies

Каждый новый package добавляет доверие к:

- maintainer;
- release process;
- registry account;
- транзитивному дереву;
- update mechanism;
- install scripts;
- лицензии;
- будущим владельцам проекта.

Перед добавлением dependency нужно спросить:

```text
Нужна ли она вообще?

Есть ли подходящий Web API?

Есть ли уже установленный package?

Можно ли написать небольшой
локальный helper без сложной логики?

Насколько критична эта функция?
```

Не нужно самостоятельно реализовывать:

- криптографию;
- sanitization HTML;
- parser сложного формата;
- authentication protocol;

только ради уменьшения числа dependencies.

Но package для одной тривиальной функции также может быть неоправданным риском.

### Что проверять перед добавлением package

Минимальная проверка:

- точное имя package;
- scope;
- repository;
- связь repository с registry package;
- maintainers;
- история владельцев;
- дата и характер последних releases;
- security policy;
- способ сообщения об уязвимостях;
- число dependencies;
- lifecycle scripts;
- bundle impact;
- license;
- качество документации;
- наличие tests;
- открытые security issues;
- provenance, если она доступна;
- возможность замены уже используемым API.

Автоматическая оценка вроде OpenSSF Scorecard может дать дополнительные сигналы:

- branch protection;
- pinning dependencies;
- release process;
- security policy;
- code review.

Но один score не доказывает безопасность package.

### Lock-файл

`package-lock.json` описывает выбранное дерево:

- прямые versions;
- транзитивные versions;
- resolved sources;
- integrity values;
- связи между packages.

Он предназначен для commit в repository.

Пример упрощённой записи:

```json
{
  "node_modules/library-a": {
    "version": "1.4.2",
    "resolved": "https://registry.npmjs.org/library-a/-/library-a-1.4.2.tgz",
    "integrity": "sha512-..."
  }
}
```

Lock-файл помогает получить одинаковое дерево:

```text
developer A
CI
production build
```

при одинаковых:

- package manager;
- configuration;
- platform conditions;
- registry content;
- lock-файле.

### Что гарантирует `integrity`

Поле `integrity` содержит hash ожидаемого package tarball.

Package manager проверяет:

```text
загруженные bytes
→ вычисленный hash
→ значение в lock-файле
```

Если содержимое не совпадает, установка должна завершиться ошибкой.

Это защищает от части подмен:

```text
registry mirror вернул
другой tarball

→ hash не совпал
→ установка остановлена
```

Но integrity не отвечает на вопросы:

```text
Безопасен ли этот код?

Кто его опубликовал?

Был ли maintainer скомпрометирован?

Не была ли вредоносная версия
осознанно добавлена в lock-файл?
```

Если атакующий изменил одновременно:

```text
package version
+
lock-файл
+
integrity
```

обычная hash-проверка не обнаружит злой умысел.

### Lock-файл не является подписью издателя

Нужно различать:

```text
integrity hash
→ загружены ожидаемые bytes

registry signature
→ registry подтверждает
  опубликованный tarball

provenance
→ artifact связан
  с repository и build workflow

code review
→ команда оценила изменение
```

Эти механизмы дополняют друг друга.

Ни один из них отдельно не доказывает, что package не содержит уязвимостей или вредоносной логики.

### Review lock-файла

Большой lock diff сложно проверить построчно, но его нельзя считать автоматически безопасным.

При review смотрят:

- какие прямые dependencies изменились;
- сколько транзитивных packages добавлено;
- изменился ли registry;
- появились ли Git или URL dependencies;
- появились ли lifecycle scripts;
- изменился ли major version;
- исчезли ли ожидаемые integrity values;
- появились ли packages с похожими именами;
- не обновилось ли значительно больше дерева, чем ожидалось.

Изменение одной dependency не должно без причины переписывать весь lock-файл.

### `npm ci`

`npm ci` предназначен для чистой воспроизводимой установки.

Он:

- требует `package-lock.json` или `npm-shrinkwrap.json`;
- проверяет соответствие lock-файла `package.json`;
- завершает работу при существенном расхождении;
- удаляет существующий `node_modules`;
- устанавливает полное зафиксированное дерево;
- не переписывает manifests.

В CI типичное направление:

```bash
npm ci
```

а не:

```bash
npm install
```

который способен разрешать ranges и изменять lock-файл.

### Конфигурация тоже влияет на дерево

Если lock-файл был создан с настройками:

```text
legacy-peer-deps

install-links

omit

platform-specific options
```

CI должен использовать совместимую configuration.

Проектные значения фиксируют в repository, например через `.npmrc`, если они действительно нужны.

Иначе возможна ситуация:

```text
локально npm install работает

CI npm ci завершается ошибкой

или:

разные environments
получают разное дерево
```

### Фиксировать Node.js и package manager

Нужно зафиксировать и проверять:

- Node.js version;
- npm version;
- project configuration;
- lockfile version.

Поле:

```json
{
  "packageManager": "npm@12.0.2"
}
```

документирует ожидаемый manager и version.

Но одно поле не гарантирует enforcement.

CI должен явно:

- использовать нужный Node image;
- установить или активировать ожидаемый package manager;
- вывести versions в log;
- завершить job при несовпадении.

Пример проверки:

```bash
node --version
npm --version
npm ci
```

Та же идея применяется к pnpm и Yarn, хотя команды и формат lock-файла отличаются.

### Lifecycle scripts

npm packages могут определять scripts:

```text
preinstall

install

postinstall

prepare
```

Такой script выполняет обычную системную команду с правами процесса package manager.

Он может получить доступ к:

- source repository;
- домашней директории runner;
- environment variables;
- registry credentials;
- network;
- build workspace;
- другим установленным packages.

Пример:

```json
{
  "scripts": {
    "postinstall": "node setup.js"
  }
}
```

Script может быть легитимным:

- собрать native module;
- скачать binary;
- сгенерировать файлы.

Но с точки зрения security это выполнение стороннего кода.

### Поведение install scripts зависит от npm version

В npm 11 `allowScripts` используется как review policy, но непросмотренные dependency scripts ещё могут выполняться по умолчанию с предупреждением.

В npm 12 dependency install scripts блокируются по умолчанию, пока package явно не разрешён в `allowScripts`.

Концептуально:

```json
{
  "allowScripts": {
    "sharp@1.2.3": true,
    "unknown-telemetry-package": false
  }
}
```

Для текущего npm 12 approvals управляются через documented workflow:

```bash
npm install-scripts ls

npm install-scripts approve sharp

npm install-scripts deny unknown-package
```

Approval желательно pin к проверенной version.

Разрешение только по имени:

```text
package: true
```

автоматически доверяет и будущим versions, поэтому имеет большую область риска.

Перед изменением policy нужно сверяться с документацией конкретной major version npm.

### `--ignore-scripts`

Для анализа dependency можно выполнить установку без lifecycle scripts:

```bash
npm ci --ignore-scripts
```

Это уменьшает риск немедленного выполнения стороннего install-кода.

Но режим может сломать packages, которым script действительно нужен:

- native modules;
- binary download;
- code generation;
- framework setup.

Практический подход:

```text
1. Установить без scripts.
2. Определить packages со scripts.
3. Проверить назначение.
4. Разрешить только необходимые.
5. Выполнить нужный rebuild
   в ограниченной среде.
```

Нельзя использовать:

```text
разрешить все scripts
```

как постоянный способ убрать предупреждение.

### `npx`, `npm exec` и global installation

Команда:

```bash
npx unknown-tool
```

может загрузить и выполнить package, который не проходил обычный dependency review.

То же относится к:

- `npm exec`;
- global install;
- GitHub gist command;
- `curl | shell`;
- случайной CLI из issue comment.

Для CI:

- фиксируют package и version;
- не запускают `latest`;
- предпочитают dependency из lock-файла;
- проверяют source;
- не дают команде лишние secrets.

Опасно:

```bash
npx some-tool@latest
```

в release job с publish permissions.

### Git и URL dependencies

Dependency может ссылаться не только на registry version:

```json
{
  "dependencies": {
    "library": "github:org/repository#main"
  }
}
```

Branch:

```text
main
```

является mutable reference.

Один и тот же manifest в разное время способен получить другой code.

Для Git dependency используют immutable commit SHA:

```text
github:org/repository#2f34c8...
```

Но commit pin не обеспечивает:

- registry signature;
- обычную package provenance;
- проверку содержимого;
- безопасность build scripts.

Удалённые tarball URLs также должны быть immutable и integrity-protected.

### Dependency confusion

Dependency confusion возникает, когда package manager выбирает публичный package вместо внутреннего.

Например, организация использует внутреннее имя:

```text
company-utils
```

Атакующий публикует:

```text
company-utils
```

в public registry с более высокой version.

При неправильной registry configuration CI устанавливает package атакующего.

Защита:

- использовать private scope;
- явно связать scope с private registry;
- не использовать непроверенные unscoped internal names;
- контролировать `.npmrc`;
- ограничить fallback на public registry;
- резервировать критичные package names;
- проверять `resolved` в lock-файле;
- не передавать private registry token другим hosts.

Пример project configuration:

```text
@company:registry=https://registry.company.example
```

### Registry credentials

Credential должен быть привязан к минимальному registry scope.

Нельзя отправлять token каждому registry или host.

Проверяют:

- URL registry;
- scope package;
- read или write permissions;
- срок действия;
- environment, где token доступен;
- попадание `.npmrc` в artifacts;
- маскирование logs.

CI job, который только выполняет tests, обычно не нуждается в publish token.

Read token private registry не должен автоматически иметь publish permissions.

### Typosquatting

Typosquatting использует похожее имя:

```text
react-query

reactquery

react-qeury

@company/package

@compаny/package
```

Различие может состоять в:

- одной букве;
- дефисе;
- scope;
- похожем Unicode symbol;
- перестановке символов.

До установки проверяют:

- точное имя;
- официальный repository;
- владельца;
- ссылку из официальной документации;
- дату создания package;
- число downloads как слабый дополнительный сигнал.

Количество downloads само по себе не доказывает безопасность.

### CI как часть supply chain

CI выполняет код:

- repository;
- dependencies;
- build tools;
- CI actions;
- container images;
- shell scripts.

Поэтому pipeline является security boundary.

У CI могут быть:

- package publish permissions;
- cloud credentials;
- signing keys;
- deployment access;
- access к private registry;
- production secrets.

### Разделять jobs по правам

Типичное разделение:

```text
pull request job
→ install, lint, test
→ без production secrets

build job
→ создаёт artifact
→ минимальные read permissions

publish job
→ запускается только
  для защищённого tag/release
→ получает publish authority

deploy job
→ продвигает
  проверенный artifact
```

Не нужно выдавать publish credential job, которая только запускает unit tests.

### Untrusted pull requests

Code из pull request может изменить:

- npm scripts;
- test command;
- build plugin;
- CI workflow;
- dependency;
- файл, который выводит environment.

Поэтому untrusted PR не должен выполняться с production secrets.

Особенно опасно сочетание:

```text
code из fork

+

write permissions

+

publish/deploy secrets
```

Approval workflow должен отделять review кода от job с привилегиями.

### Pinning CI actions и images

Mutable reference:

```yaml
uses: vendor/action@main
```

или:

```yaml
uses: vendor/action@v3
```

может начать указывать на другой code.

Для чувствительного pipeline action фиксируют immutable commit SHA и обновляют через review.

То же относится к container image:

```text
node:latest
```

может меняться.

Для воспроизводимости фиксируют version, а для более строгой integrity — digest.

Pinning не доказывает безопасность выбранного code, но предотвращает незаметную замену reference.

### Минимальные CI permissions

CI identity получает только нужные права.

Например:

```text
test job:
repository contents read

publish job:
OIDC id-token write
package publish

deploy job:
access только к нужному environment
```

Не нужно использовать:

- общий admin token;
- постоянный cloud key;
- один credential для всех repositories;
- write permission по умолчанию.

Краткоживущие credentials предпочтительнее постоянных secrets.

### Trusted publishing

Для публикации npm package предпочтительно использовать **trusted publishing** через OIDC, если выбранные registry и CI provider это поддерживают.

Схема:

```text
CI workflow
→ получает краткоживущий OIDC identity token
→ npm проверяет repository и workflow
→ разрешает publish
```

Преимущества:

- нет постоянного npm publish token в CI;
- credential создаётся для конкретного workflow;
- его нельзя повторно использовать как обычный long-lived token;
- уменьшается необходимость ручной rotation;
- publish можно привязать к repository и environment.

После настройки trusted publishing старые automation tokens нужно отозвать, если они больше не нужны.

### MFA и publish permissions

Для maintainer accounts включают MFA.

Publish permissions ограничивают:

- конкретными packages;
- organisation;
- read/write operation;
- временем;
- release workflow.

Для особо чувствительного package полезна схема:

```text
CI создаёт staged release

→ maintainer проверяет artifact

→ подтверждает публикацию через MFA
```

Release нельзя считать доверенным только потому, что его создал authenticated maintainer account: аккаунт также может быть скомпрометирован.

### Package provenance

**Provenance** — проверяемое attestation о том, где и как был создан package artifact.

Она может связать package с:

- source repository;
- commit;
- CI workflow;
- build platform.

Потребитель получает дополнительный ответ на вопрос:

```text
Этот package действительно
был опубликован ожидаемым workflow
из заявленного repository?
```

Provenance затрудняет незаметную ручную публикацию другого artifact.

Но она не доказывает:

- безопасность source code;
- отсутствие malicious dependency;
- корректность build script;
- отсутствие уязвимости;
- честность всех maintainers;
- корректность review.

Скомпрометированный trusted workflow может создать package с корректной provenance.

### Registry signatures

Public registry может подписывать package metadata и tarball integrity.

Проверка:

```bash
npm audit signatures
```

может подтвердить registry signatures и доступные provenance attestations.

Это помогает обнаружить:

- подменённый tarball;
- некорректную signature;
- часть атак через registry mirror или proxy.

Но registry signature не доказывает, что publisher не выпустил вредоносную version.

### SBOM

**SBOM, Software Bill of Materials**, — инвентаризация компонентов artifact.

Она может содержать:

- package name;
- version;
- dependency relationships;
- license;
- hashes;
- package URL.

SBOM помогает быстро ответить:

```text
Есть ли у нас уязвимая library?

В каких applications?

В каком production artifact?

Прямая она или транзитивная?
```

SBOM желательно генерировать автоматически в CI и связывать с конкретным release.

Она не заменяет:

- vulnerability monitoring;
- reachability analysis;
- package review;
- provenance;
- incident response.

### Build once, promote the same artifact

Опасная схема:

```text
CI tests build A

→ production повторно собирает build B

→ зависимости или environment изменились
```

В production может попасть artifact, который не проходил tests.

Надёжнее:

```text
commit

→ один controlled build

→ tests и scans

→ immutable artifact

→ staging

→ production
```

Между environments меняют configuration, но не пересобирают application без необходимости.

Для artifact сохраняют:

- checksum;
- build metadata;
- source commit;
- dependency inventory;
- provenance;
- release ID.

### Build environment

Build должен выполняться в изолированной среде с минимальными правами.

Ограничивают:

- filesystem;
- network;
- secrets;
- cloud metadata;
- package publish permissions;
- доступ к другим builds;
- возможность изменять предыдущие artifacts.

Ephemeral runner уменьшает риск, что одна job оставит malicious state для следующей.

Cache также считается недоверенным входом:

```text
dependency cache
build cache
Docker layer cache
```

Cache key должен учитывать lock-файл и toolchain.

Artifact после build не должен изменяться вручную на runner.

### Vulnerability scanning

Scanner сравнивает dependency versions с известными advisories.

Например:

```bash
npm audit
```

может найти известную vulnerability в зафиксированном дереве.

Но scanner не определяет автоматически:

- достижим ли уязвимый code;
- используется ли package только при build;
- есть ли exploit в текущем environment;
- является ли package malicious без зарегистрированной CVE;
- скомпрометирован ли maintainer;
- правильно ли настроена library.

Результат требует triage.

### Три разных типа проблемы

#### Known vulnerability

Есть опубликованный advisory для определённых versions.

Действия:

- проверить affected range;
- определить dependency path;
- проверить reachability;
- обновить или применить mitigation.

#### Malicious package

Package изначально содержит вредоносную логику.

У него может не быть CVE.

Сигналы:

- подозрительный install script;
- exfiltration;
- typosquatting;
- неожиданная смена maintainer;
- obfuscated code;
- новая dependency без понятного назначения.

#### Supply-chain compromise

Легитимный package или build process был скомпрометирован.

Например:

- украден publish credential;
- изменён release workflow;
- CDN отдаёт другой script;
- registry mirror подменяет artifact.

Обычный vulnerability scanner может этого не увидеть.

### Что делать при advisory

Практический порядок:

```text
1. Определить affected package и versions.
2. Найти все dependency paths.
3. Проверить production/dev usage.
4. Проверить достижимость.
5. Оценить возможный ущерб.
6. Найти минимальное исправление.
7. Обновить package или удалить feature.
8. Проверить lock diff.
9. Запустить tests и build.
10. Проверить production artifact.
11. Зафиксировать решение и срок.
```

Если исправленной version нет:

- заменить package;
- удалить уязвимую функцию;
- ограничить входные данные;
- применить override;
- изолировать code;
- принять временный риск с owner и deadline.

### `overrides`

npm позволяет принудительно выбрать version транзитивной dependency через `overrides`.

Это может быть временной мерой:

```json
{
  "overrides": {
    "vulnerable-package": "2.4.1"
  }
}
```

Но нужно проверить:

- совместимость;
- tests;
- изменение lock-файла;
- действительно ли patched version используется;
- не осталось ли второго dependency path.

Override не должен превращаться в забытый постоянный patch без owner.

### Почему нельзя запускать `npm audit fix --force` вслепую

Force update способен:

- установить major versions;
- изменить public API;
- изменить runtime behaviour;
- обновить большое транзитивное дерево;
- добавить новые vulnerabilities;
- сломать build;
- скрыть исходную причину.

Автоматическое исправление должно проходить:

- review;
- tests;
- bundle comparison;
- release notes;
- migration;
- controlled rollout.

Цель:

```text
не получить зелёный scanner,

а реально уменьшить риск
без новой регрессии
```

### Обновлять небольшими порциями

Большой update сразу меняет:

- framework;
- bundler;
- test runner;
- runtime dependencies;
- lockfile format;
- CI tools.

Такой diff сложно проверить и откатить.

Предпочтительно:

- небольшие update groups;
- отдельный major upgrade;
- автоматические tests;
- preview deployment;
- lock diff;
- bundle analysis;
- rollback plan.

Автоматический dependency bot полезен как механизм обнаружения и подготовки PR.

Он не должен бесконтрольно merge-ить любое security или major update без политики проекта.

### Release age

Совершенно новая version может ещё не успеть пройти широкое использование и анализ.

Для некритичных updates организация может вводить минимальный release age:

```text
не устанавливать version
в первые N часов или дней
```

Это даёт время обнаружить:

- compromised release;
- accidental publish;
- regression;
- malicious update.

Но задержка не применяется слепо к срочному security patch.

Политика должна позволять осознанное исключение.

### Secrets во frontend

Всё, что передано browser, доступно пользователю.

Значение может быть найдено в:

- JavaScript bundle;
- HTML;
- source map;
- Network;
- runtime configuration;
- JavaScript memory;
- DevTools.

Поэтому переменные вроде:

```text
VITE_*

NEXT_PUBLIC_*

PUBLIC_*
```

считаются публичными.

Название `.env.production` не делает значение секретным.

Нельзя помещать во frontend:

- database password;
- private API key;
- cloud secret;
- npm publish token;
- JWT signing key;
- OAuth client secret confidential client;
- private encryption key.

### Public browser key

Некоторые providers выдают key, специально предназначенный для browser.

Он является идентификатором проекта, а не настоящим secret.

Его ограничивают:

- точными origins;
- разрешёнными APIs;
- quota;
- environment;
- минимальными permissions.

Backend не должен считать public key доказательством личности пользователя или права на чувствительную операцию.

### Secrets в CI

CI secrets нужны только jobs, которым они действительно требуются.

Правила:

- least privilege;
- short-lived credentials;
- OIDC вместо постоянных cloud keys;
- отдельные credentials для environments;
- запрет secrets в untrusted PR;
- masking logs;
- rotation;
- audit доступа;
- protected environments;
- manual approval для production при необходимости.

Нельзя выводить в log:

```bash
echo "$NPM_TOKEN"
```

Даже masked secret может утечь через:

- encoding;
- substring;
- exception;
- generated file;
- uploaded artifact;
- debug trace.

### `.npmrc`

`.npmrc` может содержать registry token:

```text
//registry.example.com/:_authToken=...
```

Такой файл не должен:

- попадать в Git;
- публиковаться в npm package;
- включаться в Docker image;
- сохраняться как CI artifact;
- оставаться на shared runner.

Предпочтительнее генерировать temporary configuration внутри job и удалять её после использования.

Credential привязывают к конкретному registry host.

### Docker layers

Удаление secret в следующем Docker layer не гарантирует, что его нет в предыдущем layer.

Опасно:

```dockerfile
COPY .npmrc .
RUN npm ci
RUN rm .npmrc
```

Secret мог сохраниться в image history.

Используют:

- BuildKit secret mounts;
- multi-stage build;
- отдельный dependency fetch mechanism;
- image scanning;
- минимальный final image.

Frontend static artifact не должен содержать package registry credentials.

### Публикация собственного npm package

Перед `npm publish` нужно проверить, какие files попадут в tarball.

Команда:

```bash
npm pack --dry-run
```

показывает publish contents.

Поле `files` задаёт allowlist:

```json
{
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ]
}
```

Allowlist обычно безопаснее надежды только на `.npmignore`.

Проверяют отсутствие:

- `.env`;
- `.npmrc`;
- private keys;
- source maps с чувствительным содержимым;
- internal configs;
- test fixtures с credentials;
- debug dumps;
- private documentation;
- unnecessary source files.

Tarball можно дополнительно распаковать и проверить как обычный release artifact.

### Third-party script

Внешний script:

```html
<script
  src="https://analytics.example/sdk.js"
></script>
```

выполняется в контексте страницы.

Он обычно получает возможности JavaScript приложения:

- читать DOM;
- перехватывать input;
- читать JavaScript-доступное storage;
- вызывать same-origin API;
- изменять интерфейс;
- загружать дополнительные scripts;
- отправлять данные provider.

Same Origin Policy не изолирует внешний script от страницы.

После загрузки это code приложения, полученный из другого источника.

### Runtime dependency и third-party script

Есть важное различие.

#### npm runtime dependency

Code загружается во время build и попадает в проверяемый artifact:

```text
npm package
→ bundle
→ application CDN
```

Команда может:

- зафиксировать version;
- проверить lock diff;
- просканировать bundle;
- протестировать artifact.

#### Remote third-party script

Code загружается browser напрямую при каждом посещении:

```text
browser
→ vendor CDN
→ текущая version script
```

Vendor может изменить содержимое без нового application deployment.

Поэтому часть review и tests перестаёт соответствовать реально исполняемому code.

### Tag manager

Tag manager является supply-chain multiplier.

Один разрешённый loader способен подключать множество vendor scripts.

Configuration может меняться:

- через web UI;
- сотрудником marketing;
- без pull request;
- без application release;
- без обычных tests.

Для tag manager нужны:

- отдельные roles;
- MFA;
- approval workflow;
- audit history;
- минимальный список vendors;
- запрет custom JavaScript без review;
- CSP;
- inventory активных tags;
- план аварийного отключения.

Доступ администратора tag manager может быть сопоставим по риску с правом выкатывать frontend code.

### Минимизировать third-party scripts

Для каждого внешнего script фиксируют:

- business owner;
- назначение;
- routes, где он нужен;
- данные, которые он получает;
- destinations;
- срок использования;
- способ обновления;
- incident contact;
- способ отключения.

Script не нужно загружать на всех страницах, если он требуется только:

- checkout;
- support page;
- consented analytics;
- отдельному widget.

Удаление script полностью надёжнее попытки ограничить ненужный code.

### Subresource Integrity

**Subresource Integrity, SRI**, позволяет browser проверить hash external script или stylesheet.

Пример:

```html
<script
  src="https://cdn.example/library-1.4.2.js"
  integrity="sha384-..."
  crossorigin="anonymous"
></script>
```

Browser:

1. Загружает resource.
2. Вычисляет cryptographic hash.
3. Сравнивает его с `integrity`.
4. Выполняет resource только при совпадении.

SRI защищает от неожиданного изменения содержимого по тому же URL.

### Ограничения SRI

SRI подходит, когда resource:

- имеет immutable versioned URL;
- обновляется контролируемо;
- возвращает стабильные bytes;
- поддерживает необходимую CORS configuration.

Если vendor изменяет script без изменения URL:

```text
https://vendor.example/latest.js
```

старый hash перестанет совпадать, и интеграция сломается.

Разработчик должен:

- проверить новую version;
- обновить URL или hash;
- выполнить tests;
- развернуть изменение.

Это желаемое поведение с точки зрения integrity.

SRI не подходит для script, который намеренно генерируется по-разному для каждого request.

### SRI и CORS

Для cross-origin integrity-protected resource server должен участвовать в CORS protocol.

Обычно используется:

```html
crossorigin="anonymous"
```

а server возвращает подходящий:

```http
Access-Control-Allow-Origin
```

Без корректной CORS-настройки cross-origin SRI resource может быть заблокирован.

SRI также не защищает от:

- вредоносного code, hash которого команда сама одобрила;
- XSS в application;
- API compromise vendor;
- утечки данных через разрешённую функциональность script.

### CSP и third-party code

CSP может ограничить:

- `script-src`;
- `connect-src`;
- `img-src`;
- `frame-src`;
- динамическую загрузку scripts.

Но после разрешения:

```http
script-src https://vendor.example
```

любой подходящий script с этого origin может стать доверенным в рамках policy.

CSP не анализирует бизнес-поведение code.

Поэтому host allowlist не заменяет:

- version pinning;
- SRI;
- vendor review;
- minimization;
- isolation.

### Self-hosting

Можно загрузить vendor script, проверить его и раздавать со своего origin.

Преимущества:

- vendor не меняет исполняемый файл без deployment;
- нет runtime request к vendor CDN;
- проще применить собственный cache и SRI-like artifact checks;
- уменьшается часть утечки request metadata vendor.

Но ответственность переходит команде:

- отслеживать security updates;
- соблюдать license;
- проверять release;
- своевременно обновлять;
- не модифицировать code неправильно.

Self-hosting фиксирует delivery, но не делает исходный vendor code автоматически безопасным.

### Изоляция через iframe

Обычный external script выполняется в основном origin приложения.

Cross-origin iframe изолирован Same Origin Policy значительно сильнее.

Для отдельного widget можно использовать:

```html
<iframe
  src="https://widget.example"
  sandbox="allow-scripts"
></iframe>
```

Точные sandbox permissions зависят от функции.

Обмен выполняют через:

```text
postMessage
+
точный targetOrigin
+
проверка event.origin
+
schema validation
```

Iframe не является универсальной заменой script:

- некоторые SDK требуют доступ к DOM;
- неправильный sandbox может быть слишком широким;
- iframe видит переданные ему данные;
- остаются clickjacking и messaging risks.

Но для изолируемого vendor UI iframe обычно создаёт более сильную границу, чем `<script>`.

### Dependency monitoring

После добавления package работа не заканчивается.

Нужно отслеживать:

- новые advisories;
- изменение maintainer ownership;
- deprecation;
- прекращение поддержки;
- malicious releases;
- license changes;
- новые dependencies;
- новые lifecycle scripts;
- изменение provenance;
- обновления runtime.

Inventory должен связывать dependency с:

- application;
- release;
- environment;
- owner.

Без owner advisory может оставаться открытым неопределённо долго.

### Incident response

При подозрении на компрометацию dependency:

```text
1. Остановить новые deployments.
2. Определить affected versions.
3. Найти все applications и artifacts.
4. Проверить install/build/runtime exposure.
5. Отозвать CI, registry и cloud credentials.
6. Заблокировать package/version.
7. Восстановить trusted lock-файл.
8. Пересобрать artifact
   в чистой environment.
9. Проверить production bundle.
10. Откатить или развернуть
    исправленную version.
11. Проверить возможную
    утечку пользовательских данных.
12. Добавить monitoring
    и сохранить forensic evidence.
```

Если malicious install script выполнялся в CI, недостаточно просто удалить package.

Нужно предположить, что могли быть прочитаны:

- npm token;
- cloud credentials;
- source code;
- signing keys;
- deployment secrets.

Такие credentials отзывают и ротируют.

### Практический порядок защиты

```text
1. Минимизировать dependencies.
2. Проверять новый package до установки.
3. Коммитить lock-файл.
4. Review package и lock diffs.
5. Фиксировать Node и package manager.
6. Использовать npm ci в CI.
7. Контролировать lifecycle scripts.
8. Явно настраивать private scopes.
9. Ограничить registry credentials.
10. Изолировать untrusted pull requests.
11. Pin CI actions и build images.
12. Разделить test, publish и deploy jobs.
13. Использовать short-lived credentials.
14. Для npm publish использовать
    trusted publishing, если доступно.
15. Проверять provenance и signatures.
16. Генерировать SBOM.
17. Build один immutable artifact.
18. Автоматически искать advisories.
19. Обновлять небольшими порциями.
20. Не передавать secrets browser.
21. Проверять npm package tarball.
22. Минимизировать third-party scripts.
23. Использовать SRI для immutable files.
24. Ограничивать code через CSP.
25. Изолировать widgets через iframe,
    если архитектура это позволяет.
26. Иметь owner, rollback
    и incident response plan.
```

Главный принцип:

```text
Dependency — это не просто code,
который экономит время разработки.

Это передача части доверия
чужому проекту,
его maintainers,
registry и release process.
```

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Что именно гарантирует lock-файл?</strong></summary>

<dl>
<dd>
<h2></h2>

Lock-файл фиксирует выбранное dependency tree:

- versions;
- resolved locations;
- integrity values;
- отношения между packages.

Это позволяет воспроизвести одно дерево при совместимом package manager и configuration.

Он не гарантирует:

- безопасность code;
- отсутствие malicious logic;
- честность maintainer;
- корректность выбранной version;
- отсутствие уязвимости;
- безопасность изменённого lock-файла.

Lock-файл является важным контролем воспроизводимости и integrity, но не самостоятельным security review.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>npm ci</code> отличается от <code>npm install</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

`npm ci`:

- требует lock-файл;
- проверяет его соответствие `package.json`;
- удаляет существующий `node_modules`;
- устанавливает полное зафиксированное дерево;
- не переписывает manifests;
- предназначен для CI и controlled builds.

`npm install` может:

- разрешать ranges;
- добавлять dependency;
- обновлять lock-файл;
- использоваться для осознанного изменения дерева.

В CI обычно используют `npm ci`.

Настройки, влияющие на дерево, должны совпадать с настройками, при которых создан lock-файл.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему недостаточно зафиксировать версии только в <code>package.json</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Range:

```text
^1.4.0
```

разрешает несколько versions.

Транзитивные dependencies обычно вообще не перечислены в корневом `package.json`.

Две установки в разное время могут выбрать разные деревья.

Lock-файл фиксирует фактически разрешённые versions всех уровней.

Даже точные прямые versions не фиксируют автоматически транзитивное дерево без lock-файла.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как сделать версии Node.js и package manager одинаковыми в команде и CI?</strong></summary>

<dl>
<dd>
<h2></h2>

Версию Node фиксируют через:

- CI image;
- `.nvmrc`;
- `.node-version`;
- выбранный version manager;
- project documentation.

Ожидаемый package manager можно записать:

```json
{
  "packageManager": "npm@12.0.2"
}
```

Но CI должен фактически проверить или установить эту version.

Поле `engines` описывает совместимый диапазон, но само по себе не гарантирует, что разработчик использует нужную version.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем опасны npm lifecycle scripts?</strong></summary>

<dl>
<dd>
<h2></h2>

Script выполняет системную команду с правами package manager process.

Он может получить доступ к:

- source files;
- environment variables;
- registry token;
- network;
- CI workspace;
- build artifacts.

Легитимные packages используют scripts для native build и binary download.

Поэтому scripts не запрещают вслепую, а разрешают точечно после review.

Поведение default policy зависит от npm major version.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как изменилось выполнение install scripts в npm 12?</strong></summary>

<dl>
<dd>
<h2></h2>

В npm 12 dependency lifecycle scripts блокируются по умолчанию, если package не разрешён через `allowScripts`.

Для управления approvals используются команды вида:

```bash
npm install-scripts ls

npm install-scripts approve package-name

npm install-scripts deny package-name
```

Approval по умолчанию можно привязать к установленной version.

В npm 11 эта policy ещё была advisory: непросмотренные scripts выполнялись с предупреждением.

Поэтому команда должна фиксировать npm version и не предполагать одинаковое поведение всех major versions.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое dependency confusion?</strong></summary>

<dl>
<dd>
<h2></h2>

Package manager выбирает публичный package вместо внутреннего package организации.

Причиной может быть:

- одинаковое имя;
- неправильный registry;
- fallback на public registry;
- более высокая public version;
- утечка internal package names.

Защита:

- private scopes;
- точное registry mapping;
- проверка `.npmrc`;
- host-scoped credentials;
- review `resolved` в lock-файле;
- отсутствие unscoped internal names без защиты.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое typosquatting?</strong></summary>

<dl>
<dd>
<h2></h2>

Атакующий публикует package с именем, похожим на популярное или внутреннее.

Различие может быть в:

- одной букве;
- дефисе;
- scope;
- перестановке символов;
- похожем Unicode character.

Разработчик ошибается при установке, после чего package может:

- выполнить install script;
- попасть в bundle;
- украсть данные CI.

До установки проверяют точное имя, repository и maintainers.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему devDependency тоже может быть риском безопасности?</strong></summary>

<dl>
<dd>
<h2></h2>

DevDependency выполняется:

- на машине разработчика;
- в CI;
- во время tests;
- при production build.

Bundler plugin может:

- прочитать source;
- украсть secrets;
- внедрить JavaScript в bundle;
- изменить source map;
- подменить artifact.

Отсутствие package в runtime `node_modules` не означает, что он не мог повлиять на production application.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что проверять при добавлении новой зависимости?</strong></summary>

<dl>
<dd>
<h2></h2>

Проверяют:

- необходимость;
- точное имя;
- maintainers;
- repository;
- release history;
- dependencies;
- lifecycle scripts;
- security policy;
- license;
- bundle impact;
- provenance;
- maintenance status;
- возможность использовать Web API или уже установленный package.

После установки проверяют `package.json`, lock diff, build и итоговый bundle.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать при сообщении об уязвимости в зависимости?</strong></summary>

<dl>
<dd>
<h2></h2>

Нужно определить:

- affected versions;
- dependency path;
- runtime или build usage;
- достижимость;
- возможный ущерб;
- наличие patched version;
- временные mitigations.

Затем применяют минимальное безопасное изменение, запускают tests, проверяют lock diff и production artifact.

Если риск временно принимается, ему назначают owner, deadline и monitoring.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>npm audit fix --force</code> нельзя запускать вслепую?</strong></summary>

<dl>
<dd>
<h2></h2>

Команда способна установить major versions и значительно изменить dependency tree.

Она не доказывает:

- достижимость исходной vulnerability;
- совместимость update;
- отсутствие новой проблемы;
- безопасность нового package.

Исправление проходит обычные review, tests, build и controlled rollout.

Зелёный audit report не является единственной целью.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое package provenance?</strong></summary>

<dl>
<dd>
<h2></h2>

Provenance связывает опубликованный artifact с:

- source repository;
- commit;
- CI workflow;
- build platform.

Она помогает проверить, что package создан ожидаемым процессом, а не вручную опубликован из неизвестного места.

Provenance не доказывает:

- безопасность source code;
- отсутствие vulnerability;
- честность dependency;
- корректность build logic.

Это доказательство происхождения, а не сертификат безопасности.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое trusted publishing?</strong></summary>

<dl>
<dd>
<h2></h2>

Trusted publishing использует OIDC identity CI workflow вместо постоянного npm publish token.

Registry проверяет:

- provider;
- repository;
- workflow;
- дополнительные настроенные ограничения.

Для publish создаётся краткоживущее credential.

Это уменьшает риск:

- утечки long-lived token;
- ручной rotation;
- повторного использования украденного credential.

После миграции ненужные publish tokens отзывают.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем registry signature отличается от provenance?</strong></summary>

<dl>
<dd>
<h2></h2>

Registry signature подтверждает integrity опубликованного package tarball относительно registry metadata.

Provenance связывает artifact с source repository и build workflow.

Упрощённо:

```text
signature:
registry подтверждает artifact

provenance:
build process объясняет,
откуда artifact появился
```

Обе проверки не доказывают, что code безопасен по смыслу.

Для npm доступные signatures и attestations можно проверять через:

```bash
npm audit signatures
```

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое SBOM и зачем он frontend-проекту?</strong></summary>

<dl>
<dd>
<h2></h2>

SBOM — список компонентов конкретного artifact.

Он помогает быстро определить:

- используется ли уязвимый package;
- в каких applications;
- в каких releases;
- какой dependency path его добавил;
- какая version попала в production.

SBOM генерируют автоматически и связывают с release.

Он не заменяет vulnerability scanning, provenance и dependency review.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему frontend environment variables не являются secrets?</strong></summary>

<dl>
<dd>
<h2></h2>

Bundler подставляет используемые значения в browser code либо application получает их через публичную runtime configuration.

Пользователь может прочитать:

- bundle;
- HTML;
- Network;
- source map;
- JavaScript memory.

Поэтому client variables считаются публичными.

Настоящие secrets остаются на backend или в CI secret storage и никогда не передаются browser.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Может ли публичный API key находиться во frontend?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, если provider специально определил key как public browser identifier.

Его ограничивают:

- origins;
- APIs;
- quota;
- environment;
- минимальными permissions.

Такой key нельзя использовать как единственное доказательство identity или authorization для чувствительной операции.

Любой пользователь может извлечь его из application.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как проверить, что попадет в публикуемый npm package?</strong></summary>

<dl>
<dd>
<h2></h2>

Перед публикацией запускают:

```bash
npm pack --dry-run
```

и проверяют список files.

В `package.json` желательно задать allowlist:

```json
{
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ]
}
```

Проверяют отсутствие:

- `.env`;
- `.npmrc`;
- private keys;
- debug dumps;
- internal configs;
- test credentials;
- лишних source maps.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему CI action нужно фиксировать по commit SHA?</strong></summary>

<dl>
<dd>
<h2></h2>

Reference:

```text
vendor/action@main
```

или mutable tag может начать указывать на другой code без изменения repository приложения.

Immutable commit SHA фиксирует проверенную revision.

То же относится к container images и другим build tools.

Pinning не доказывает безопасность revision, но предотвращает незаметное изменение reference.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем опасны Git dependencies?</strong></summary>

<dl>
<dd>
<h2></h2>

Git dependency может ссылаться на mutable branch или tag:

```text
repository#main
```

Одинаковый manifest способен получить другой code при следующей установке.

Безопаснее фиксировать commit SHA.

При этом остаются риски:

- lifecycle scripts;
- отсутствие registry signature;
- отсутствие обычной provenance;
- компрометация repository;
- сложность dependency review.

Registry version с lock-файлом обычно проще контролировать.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем опасен third-party script?</strong></summary>

<dl>
<dd>
<h2></h2>

Обычный `<script>` выполняется с возможностями JavaScript страницы.

Он может:

- читать DOM;
- перехватывать input;
- читать JavaScript storage;
- выполнять same-origin requests;
- загружать другие scripts;
- отправлять данные provider.

Изменение vendor file способно попасть пользователям без нового deployment приложения.

Поэтому внешний script является доверенной частью runtime threat model.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему tag manager является отдельным supply chain риском?</strong></summary>

<dl>
<dd>
<h2></h2>

Tag manager может подключать scripts через configuration, которая изменяется вне application repository.

Новый code может появиться:

- без pull request;
- без frontend release;
- без обычных tests;
- через скомпрометированный marketing account.

Для tag manager нужны MFA, roles, approvals, audit history, CSP, inventory tags и аварийное отключение.

Право менять tag manager сопоставимо с правом менять frontend runtime.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Subresource Integrity?</strong></summary>

<dl>
<dd>
<h2></h2>

SRI задаёт cryptographic hash ожидаемого external script или stylesheet.

Browser выполняет resource только при совпадении содержимого.

Пример:

```html
<script
  src="https://cdn.example/library.js"
  integrity="sha384-..."
  crossorigin="anonymous"
></script>
```

SRI подходит для immutable versioned file.

При обновлении content нужно осознанно обновить hash.

Cross-origin resource требует корректной CORS-настройки.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Достаточно ли CSP для безопасного third-party script?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет.

CSP решает:

```text
с какого origin
можно загрузить code
```

Но разрешённый script после загрузки получает широкие возможности страницы.

CSP не проверяет, какие данные script читает и куда отправляет.

Дополнительные меры:

- минимизация scripts;
- SRI;
- version pinning;
- self-hosting;
- vendor review;
- sandboxed iframe;
- ограничение `connect-src`;
- monitoring.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Делает ли self-hosting сторонний script безопасным?</strong></summary>

<dl>
<dd>
<h2></h2>

Не автоматически.

Self-hosting предотвращает незаметное runtime-изменение файла vendor и уменьшает прямые requests к его CDN.

Но команда должна самостоятельно:

- проверять source;
- следить за security updates;
- обновлять version;
- соблюдать license;
- тестировать интеграцию.

Если проверенная копия уже содержит вредоносную логику, self-hosting её не устранит.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что делать после обнаружения malicious dependency?</strong></summary>

<dl>
<dd>
<h2></h2>

Недостаточно только удалить package.

Нужно:

- остановить deployments;
- определить affected versions и artifacts;
- проверить, выполнялся ли install script;
- найти все environments;
- отозвать registry, CI и cloud credentials;
- восстановить trusted lock-файл;
- пересобрать application на чистом runner;
- проверить production bundle;
- выполнить rollback или release;
- оценить утечку пользовательских данных;
- сохранить logs и forensic evidence.

Если вредоносный code выполнялся с secrets, credentials считают потенциально скомпрометированными.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Изменение | Что проверить |
| --- | --- |
| Добавили npm package | Назначение, owners, repository, lifecycle scripts, dependencies, bundle impact, license и lock diff |
| Добавили транзитивное дерево из сотен packages | Действительно ли оправдана dependency и какие новые scripts появились |
| Dependabot или Renovate открыл update | Advisory, release notes, affected code, tests, build и изменение дерева |
| Обновляется major version | Migration, security changes, bundle, preview deployment и rollback |
| CI устанавливает dependencies | Зафиксированные Node/npm, `npm ci`, `.npmrc` и install-script policy |
| Проект перешёл на npm 12 | `allowScripts`, список заблокированных scripts и точечные approvals |
| CI запускает `npx tool@latest` | Зафиксировать version и не выполнять неизвестный code с secrets |
| Используется private npm registry | Scope mapping, host-scoped credentials и защита от dependency confusion |
| В workflow используется сторонняя action | Pin commit SHA, проверить permissions и владельца |
| Build image использует `latest` | Зафиксировать version или digest |
| Pull request приходит из fork | Не передавать production secrets и write permissions |
| Публикуется собственный package | Trusted publishing, MFA, provenance и `npm pack --dry-run` |
| Release собирается отдельно для production | Продвигать тот же проверенный immutable artifact |
| Генерируется SBOM | Связать inventory с commit, artifact и release |
| Создали `.env.production` | Какие значения попадут в client bundle и где остаются server secrets |
| Registry token записывается в `.npmrc` | Не включить файл в Git, Docker layer, artifact или npm tarball |
| Добавили SDK аналитики | Какие DOM-данные он видит, куда отправляет requests и на каких routes нужен |
| Добавили tag manager | Roles, MFA, approvals, audit, CSP и emergency disable |
| Подключили CDN-script | Immutable URL, SRI, CORS и controlled update |
| Vendor script меняется без version URL | SRI неприменим без фиксации content; рассмотреть self-hosting |
| Встроили third-party widget | Предпочесть sandboxed iframe, если прямой доступ к DOM не нужен |
| Scanner нашёл vulnerability | Проверить version, path, reachability, mitigation и owner |
| Обнаружен malicious install script | Остановить releases, ротировать secrets и пересобрать artifact в чистой среде |

## Связанные темы

- [01 package.json и зависимости](<../Tooling/01 package.json и зависимости.md>)
- [02 Lock-файлы и воспроизводимая установка](<../Tooling/02 Lock-файлы и воспроизводимая установка.md>)
- [06 Переменные окружения и secrets в CI CD](<../DevOps/06 Переменные окружения и secrets в CI CD.md>)
- [06 CSP и защитные HTTP-заголовки](<./06 CSP и защитные HTTP-заголовки.md>)
- [11 Безопасность окон iframe и внешних ссылок](<./11 Безопасность окон iframe и внешних ссылок.md>)

## Источники

- [npm Docs: npm ci](https://docs.npmjs.com/cli/v12/commands/npm-ci/)
- [npm Docs: package-lock.json](https://docs.npmjs.com/cli/v12/configuring-npm/package-lock-json)
- [npm Docs: Managing install scripts](https://docs.npmjs.com/cli/v12/commands/npm-install-scripts/)
- [npm Docs: Scripts](https://docs.npmjs.com/cli/v12/using-npm/scripts/)
- [npm Docs: Trusted publishing](https://docs.npmjs.com/trusted-publishers/)
- [npm Docs: Generating provenance statements](https://docs.npmjs.com/generating-provenance-statements/)
- [npm Docs: Viewing package provenance](https://docs.npmjs.com/viewing-package-provenance/)
- [npm Docs: Registry signatures](https://docs.npmjs.com/about-registry-signatures/)
- [npm Docs: npm publish](https://docs.npmjs.com/cli/v12/commands/npm-publish/)
- [npm Docs: Requiring 2FA for publishing](https://docs.npmjs.com/requiring-2fa-for-package-publishing-and-settings-modification/)
- [OWASP: Software Supply Chain Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html)
- [OWASP: NPM Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/NPM_Security_Cheat_Sheet.html)
- [OWASP: Vulnerable Dependency Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html)
- [OWASP: Third Party JavaScript Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html)
- [OWASP: Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [OpenSSF: Scorecard](https://openssf.org/projects/scorecard/)
- [SLSA: Build provenance](https://slsa.dev/spec/draft/build-provenance)
- [W3C: Subresource Integrity](https://www.w3.org/TR/sri-2/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 07 Ответственность frontend и backend в авторизации](<./07 Ответственность frontend и backend в авторизации.md>) · [↑ Security](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [09 Безопасность WebSocket →](<./09 Безопасность WebSocket.md>)
<!-- CARD-NAV-BOTTOM:END -->
