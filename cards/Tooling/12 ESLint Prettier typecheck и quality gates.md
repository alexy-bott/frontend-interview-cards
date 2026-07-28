# ESLint Prettier typecheck и quality gates

<!-- CARD-NAV-TOP:START -->
[← 11 npm Yarn pnpm workspaces и monorepo](<./11 npm Yarn pnpm workspaces и monorepo.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Чем отличаются ESLint, Prettier, проверка типов TypeScript и тесты? Как настроить эти проверки локально и в CI?**

<h2></h2>

<br>
<dl>
<dd>

Эти инструменты проверяют разные свойства кода и не заменяют друг друга:

| Инструмент | Что проверяет |
| --- | --- |
| ESLint | Статические правила качества, возможные ошибки и соглашения проекта |
| Prettier | Единое форматирование |
| Проверка типов TypeScript | Совместимость типов и контрактов |
| Тесты | Наблюдаемое поведение кода |

ESLint разбирает исходный код с помощью parser, то есть синтаксического анализатора, и применяет встроенные правила и правила из плагинов. Он находит, например, неиспользуемые переменные, нарушения Rules of Hooks и запрещённые импорты. Часть правил для TypeScript анализирует только синтаксис. Правила с информацией о типах дополнительно используют модель программы TypeScript и могут обнаруживать более сложные ошибки, например floating Promise: вызов промиса, результат которого забыли дождаться или явно обработать.

Современный ESLint использует flat config, или плоскую конфигурацию, в `eslint.config.js` либо `eslint.config.mjs`. Файл экспортирует упорядоченный массив объектов конфигурации. Поля `files` и `ignores` задают область применения, `languageOptions` содержит настройки языка и parser, `plugins` подключает плагины, а `rules` задаёт правила с уровнем `off`, `warn` или `error`. Flat config стал форматом по умолчанию в ESLint 9.

Prettier заново печатает AST, то есть абстрактное синтаксическое дерево кода, в едином стиле и отвечает за форматирование: отступы, кавычки, переносы и запятые. Он не ищет большинство логических ошибок. ESLint проверяет правила качества, а Prettier форматирует код. Пакет `eslint-config-prettier` отключает стилистические правила ESLint, конфликтующие с форматированием Prettier.

Компилятор TypeScript проверяет типы отдельно. Vite, Babel или SWC могут удалить TypeScript-синтаксис и создать JavaScript, не проверяя совместимость типов. Поэтому `tsc --noEmit` или `tsc -b` запускают как отдельную обязательную проверку.

Минимальный набор scripts в `package.json`:

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings=0",
    "typecheck": "tsc --noEmit",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "test": "jest",
    "build": "vite build"
  }
}
```

Pre-commit hook, то есть команда перед созданием коммита, может через lint-staged запускать ESLint и Prettier только для подготовленных к коммиту файлов. Это даёт быструю обратную связь, но hook можно обойти, а проверка отдельных файлов не видит все межфайловые проблемы. Поэтому CI повторно запускает полный набор проверок на чистой установке и определяет итоговый результат.

Последовательность CI зависит от продолжительности команд. После установки зависимостей линтер и проверку типов можно запустить параллельно, тесты вынести в отдельную задачу, а production-сборку выполнять после обязательных проверок или параллельно при достаточных ресурсах. Сгенерированные файлы, `dist`, отчёты покрытия и сторонний код явно исключают, чтобы линтер не тратил на них время.

Версии форматтера и его плагинов фиксируют lock-файлом. Для Prettier часто указывают точную версию: даже патч-релиз может изменить форматирование многих файлов и создать большой несодержательный набор изменений. Интеграция с редактором должна использовать локальную версию Prettier из проекта, а не глобально установленную.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему Prettier не заменяет ESLint?</strong></summary>

<dl>
<dd>
<h2></h2>

Prettier отвечает за внешний вид кода и печатает его единообразно. ESLint анализирует правила качества и возможные ошибки: например, неправильное использование React Hooks, необработанные промисы и запрещённые импорты. Форматированный код всё ещё может содержать ошибку.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему ESLint не заменяет TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Большинство правил ESLint анализирует синтаксис одного файла. TypeScript строит граф типов между файлами, вычисляет generic-типы и проверяет совместимость присваиваний. ESLint может использовать информацию TypeScript для отдельных правил, но всё равно не заменяет полную проверку командой `tsc`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое flat config?</strong></summary>

<dl>
<dd>
<h2></h2>

Это современный формат ESLint, в котором `eslint.config.*` экспортирует упорядоченный массив объектов конфигурации. Для каждого объекта можно задать подходящие `files`, подключить плагины как JavaScript-модули и указать `ignores`. Начиная с ESLint 9 этот формат используется по умолчанию вместо каскада `.eslintrc`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем нужен <code>eslint-config-prettier</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он выключает правила ESLint, которые пытаются форматировать код и конфликтуют с результатом Prettier. Его конфигурацию применяют после остальных конфигураций. Сам пакет не запускает Prettier и не отключает правила, проверяющие качество кода.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему ESLint с информацией о типах работает медленнее?</strong></summary>

<dl>
<dd>
<h2></h2>

Синтаксический анализатор должен создать или переиспользовать модель программы TypeScript, прочитать `tsconfig` и вычислить типы между файлами. Это требует больше работы, чем анализ одного синтаксиса. Такие правила включают там, где их польза оправдывает затраты, а для ускорения правильно задают границы проектов и кеширование.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Нужно ли запускать проверки в pre-commit и CI?</strong></summary>

<dl>
<dd>
<h2></h2>

Да, но с разной целью. Pre-commit быстро проверяет подготовленные файлы и помогает исправить проблему до коммита. CI выполняет полный набор в чистой среде, не зависит от локальных hooks и не разрешает слияние ветки при ошибке.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему <code>vite build</code> может пройти при ошибках TypeScript?</strong></summary>

<dl>
<dd>
<h2></h2>

Vite преобразует TypeScript-синтаксис в JavaScript, но по умолчанию не выполняет полную проверку типов. Сборка отвечает на вопрос «можно ли создать рабочие файлы», а `tsc --noEmit` проверяет совместимость типов. Поэтому в CI запускают обе команды.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что означает <code>--max-warnings=0</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

ESLint завершает команду с ошибкой, если остались предупреждения. Это не позволяет постепенно накопить сотни сообщений, которые команда перестанет замечать. Если правило пока нельзя исправить, исключение делают узким и объясняют причину.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Задача | Инструмент |
| --- | --- |
| Единое форматирование | Prettier |
| Нарушение Rules of Hooks | Плагин ESLint для React Hooks |
| Несовместимый prop | Проверка типов TypeScript |
| Ошибка пользовательского сценария | Тест |
| Быстрая локальная проверка | lint-staged и pre-commit hook |
| Обязательная проверка PR | Задачи CI |

## Связанные темы

- [01 package.json scripts dependencies devDependencies](<./01 package.json scripts dependencies devDependencies.md>)
- [10 Babel transpilation polyfills browserslist](<./10 Babel transpilation polyfills browserslist.md>)
- [01 Стратегия тестирования frontend](<../Testing/01 Стратегия тестирования frontend.md>)
- [02 CI CD pipeline stages jobs artifacts cache](<../DevOps/02 CI CD pipeline stages jobs artifacts cache.md>)

## Источники

- [ESLint docs: Configuration Files](https://eslint.org/docs/latest/use/configure/configuration-files)
- [typescript-eslint: Typed Linting](https://typescript-eslint.io/getting-started/typed-linting/)
- [Prettier: Comparison with Linters](https://prettier.io/docs/comparison)
- [Prettier: Install](https://prettier.io/docs/install)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 11 npm Yarn pnpm workspaces и monorepo](<./11 npm Yarn pnpm workspaces и monorepo.md>) · [↑ Tooling](<./README.md>) · [⌂ Все разделы](<../../README.md>)
<!-- CARD-NAV-BOTTOM:END -->
