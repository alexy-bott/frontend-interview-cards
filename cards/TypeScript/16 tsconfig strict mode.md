# 16 tsconfig strict mode

<!-- CARD-NAV-TOP:START -->
[← 15 enum const enum и literal unions](<./15 enum const enum и literal unions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 import type isolatedModules declaration files →](<./17 import type isolatedModules declaration files.md>)
<!-- CARD-NAV-TOP:END -->

#### Вопрос

За что отвечает `tsconfig.json`? Что включает `strict` и какие настройки особенно важны во frontend-проекте?

#### Ответ

`tsconfig.json` описывает TypeScript-проект: какие файлы входят в программу, по каким правилам они проверяются, как разрешаются импорты и должен ли `tsc` генерировать JavaScript или только проверять типы.

У конфигурации есть три основные части:

```json
{
  "extends": "./tsconfig.base.json",
  "compilerOptions": {
    "strict": true,
    "noEmit": true
  },
  "include": ["src", "vite.config.ts"],
  "exclude": ["dist"]
}
```

`compilerOptions` задаёт поведение компилятора. `files` перечисляет точные входные файлы, `include` выбирает их по директориям и шаблонам, `exclude` убирает совпадения из результата `include`. При этом `exclude` не является запретом на импорт: если включённый файл импортирует исключённый, зависимость всё равно попадёт в программу.

`extends` позволяет вынести общие правила команды или монорепозитория (monorepo) в базовую конфигурацию. Относительные пути разрешаются от файла конфигурации, в котором они написаны. Для нескольких связанных TypeScript-проектов применяют `references` и режим сборки `tsc -b`, а не один общий `include` на весь репозиторий.

`strict: true` включает семейство строгих проверок. К наиболее заметным относятся:

- `strictNullChecks`: `null` и `undefined` нельзя использовать как обычное значение;
- `noImplicitAny`: компилятор не должен молча вывести `any` там, где тип не определён;
- `strictFunctionTypes`: параметры типов функций проверяются строже;
- `useUnknownInCatchVariables`: ошибка в `catch` рассматривается как `unknown`;
- `strictPropertyInitialization`: поля класса должны быть инициализированы;
- `strictBindCallApply`: `bind`, `call` и `apply` учитывают сигнатуру функции.

Конкретный набор `strict` зависит от версии TypeScript: новые версии могут включать в него дополнительные проверки. Поэтому компилятор обновляют отдельным контролируемым изменением и запускают полную проверку типов.

Полезные дополнительные флаги не обязательно входят в `strict`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

`noUncheckedIndexedAccess` добавляет `undefined` при чтении элемента, наличие которого не доказано. `exactOptionalPropertyTypes` различает отсутствующее свойство и явно записанное `undefined`. Оба флага выявляют реальные ошибки, но могут потребовать заметной миграции существующего проекта.

В Vite, esbuild, SWC и Babel преобразование TypeScript в JavaScript обычно выполняется без полной проверки типов. Поэтому отдельно запускают:

```bash
tsc --noEmit
```

Обычно в локальной разработке и CI для этого заводят команду `typecheck`. Сборка приложения и проверка типов решают разные задачи: успешное удаление типов из кода ещё не означает, что статические контракты соблюдены.

`skipLibCheck` пропускает полную проверку `.d.ts` зависимостей и может ускорить сборку или временно обойти конфликт библиотечных деклараций. Он не отключает проверку собственного кода, но способен скрыть несовместимость деклараций. Сначала лучше устранить дублирующиеся версии типов или обновить зависимости, а уже затем принимать этот компромисс осознанно.

#### Встречные вопросы

> [!followup]
> **Вопрос:** Почему `strictNullChecks` критичен во frontend?
>
> **Ответ:** Данные часто отсутствуют до загрузки, параметр URL может не существовать, ссылка `ref` сначала равна `null`, а поиск в массиве возвращает `undefined`. С выключенным флагом эти состояния незаметно совместимы с обычными значениями. С включённым код должен проверить отсутствие или выразить его в модели состояния.

> [!followup]
> **Вопрос:** Что делает `noImplicitAny`?
>
> **Ответ:** Он запрещает неявный `any`, когда TypeScript не смог вывести тип параметра или объявления. Явный `any` остаётся разрешённым, потому что иногда нужен на плохо типизированной границе. Польза флага в том, что каждая такая потеря проверки становится заметным решением разработчика.

> [!followup]
> **Вопрос:** Зачем нужен `noUncheckedIndexedAccess`?
>
> **Ответ:** Доступ `items[0]` или `dictionary[key]` не гарантирует, что значение существует во время выполнения программы. Флаг добавляет к типу результата `undefined`, если наличие элемента не доказано. После этого код должен проверить результат, задать значение по умолчанию или использовать структуру с конечным набором обязательных ключей.

> [!followup]
> **Вопрос:** Что меняет `exactOptionalPropertyTypes`?
>
> **Ответ:** Без него `value?: string` обычно разрешает и отсутствие свойства, и явное `value: undefined`. С флагом запись `undefined` разрешена только тогда, когда `undefined` явно входит в тип. Это важно для тела `PATCH`-запроса, перечисления свойств через `Object.keys`, копирования через spread-синтаксис и API, где «не передано» отличается от «передано пустое значение».

> [!followup]
> **Вопрос:** Зачем запускать `tsc --noEmit`, если Vite успешно собирает проект?
>
> **Ответ:** Vite обычно быстро удаляет типы через esbuild и передаёт модули дальше, но не строит полную TypeScript-программу для проверки всех связей. `tsc --noEmit` выполняет проверку типов и не создаёт выходные файлы. В CI нужны обе команды: сборка проверяет весь процесс создания приложения и обработку ресурсов, а `tsc` проверяет статические контракты.

> [!followup]
> **Вопрос:** Что выбрать для постепенного перевода JavaScript-проекта?
>
> **Ответ:** Можно включить `allowJs`, затем `checkJs` для выбранных файлов или использовать `// @ts-check`. Ошибки устраняют по директориям, новые модули пишут строго, а временные подавления оставляют локальными через `@ts-expect-error` с причиной. Глобальное ослабление `strict` закрепляет старые проблемы во всём проекте.

> [!followup]
> **Вопрос:** Чем `@ts-expect-error` лучше `@ts-ignore`?
>
> **Ответ:** `@ts-expect-error` сам станет ошибкой, когда следующая строка перестанет содержать ожидаемую проблему. Значит, временное подавление можно обнаружить и удалить после обновления типов. `@ts-ignore` продолжает молча скрывать строку даже тогда, когда исходная причина исчезла.

> [!followup]
> **Вопрос:** Когда нужны ссылки между TypeScript-проектами (`project references`)?
>
> **Ответ:** В monorepo или большой кодовой базе, где пакеты имеют отдельные `tsconfig`, явные зависимости и собственные артефакты. `references` вместе с `composite` позволяют `tsc -b` строить проекты в правильном порядке и переиспользовать результаты. Для одного небольшого приложения это обычно лишняя сложность.

#### Где это встречается во frontend

| Задача | Настройка или команда |
| --- | --- |
| Проверить отсутствие данных | `strictNullChecks` |
| Не допустить скрытый `any` | `noImplicitAny` |
| Учесть пустой массив или словарь | `noUncheckedIndexedAccess` |
| Различить отсутствие поля и `undefined` | `exactOptionalPropertyTypes` |
| Проверить типы отдельно от Vite | `tsc --noEmit` |
| Разделить пакеты monorepo | `references`, `composite`, `tsc -b` |
| Постепенно проверять JavaScript | `allowJs`, `checkJs` |

#### Связанные темы

- [03 any unknown never void](<./03 any unknown never void.md>)
- [12 Variance и совместимость функций](<./12 Variance и совместимость функций.md>)
- [17 import type isolatedModules declaration files](<./17 import type isolatedModules declaration files.md>)
- [26 tsconfig target lib moduleResolution paths jsx](<./26 tsconfig target lib moduleResolution paths jsx.md>)

#### Источники

- [TypeScript TSConfig Reference](https://www.typescriptlang.org/tsconfig/)
- [TypeScript TSConfig: strict](https://www.typescriptlang.org/tsconfig/strict.html)
- [TypeScript TSConfig: noUncheckedIndexedAccess](https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html)
- [TypeScript TSConfig: exactOptionalPropertyTypes](https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html)
- [TypeScript Handbook: Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 15 enum const enum и literal unions](<./15 enum const enum и literal unions.md>) · [↑ TypeScript](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [17 import type isolatedModules declaration files →](<./17 import type isolatedModules declaration files.md>)
<!-- CARD-NAV-BOTTOM:END -->
