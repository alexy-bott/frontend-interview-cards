# Карточки для frontend-собеседований

База из **320 карточек** по frontend-разработке. Материалы подходят для проведения мок-собеседований и самостоятельной подготовки.

## Как пользоваться

1. Выберите раздел в таблице ниже.
2. Откройте первую карточку или нужный вопрос из оглавления раздела.
3. Перемещайтесь кнопками **←**, **↑** и **→** в начале или конце карточки.
4. Для поиска по всей базе используйте поиск GitHub по репозиторию.

## Разделы

| Раздел | Карточки | Быстрый старт |
| --- | ---: | --- |
| [Accessibility](<./cards/Accessibility/README.md>) | 10 | [Открыть →](<./cards/Accessibility/01 Что такое accessibility WCAG POUR.md>) |
| [Algorithms](<./cards/Algorithms/README.md>) | 11 | [Открыть →](<./cards/Algorithms/01 Big O time space complexity.md>) |
| [Architecture](<./cards/Architecture/README.md>) | 11 | [Открыть →](<./cards/Architecture/01 Что такое frontend architecture.md>) |
| [Browser Internals](<./cards/Browser Internals/README.md>) | 7 | [Открыть →](<./cards/Browser Internals/01 Что происходит после ввода URL.md>) |
| [CSS](<./cards/CSS/README.md>) | 18 | [Открыть →](<./cards/CSS/01 Что такое CSS cascade inheritance specificity.md>) |
| [DevOps](<./cards/DevOps/README.md>) | 8 | [Открыть →](<./cards/DevOps/01 Что frontend должен понимать в DevOps.md>) |
| [Forms](<./cards/Forms/README.md>) | 8 | [Открыть →](<./cards/Forms/01 Формы во frontend.md>) |
| [Frontend System Design](<./cards/Frontend System Design/README.md>) | 9 | [Открыть →](<./cards/Frontend System Design/01 Как проектировать frontend фичу.md>) |
| [Git](<./cards/Git/README.md>) | 9 | [Открыть →](<./cards/Git/01 Что такое Git и зачем он frontend разработчику.md>) |
| [HTML](<./cards/HTML/README.md>) | 10 | [Открыть →](<./cards/HTML/01 Зачем нужен HTML во frontend.md>) |
| [JavaScript](<./cards/JavaScript/README.md>) | 55 | [Открыть →](<./cards/JavaScript/01 Типы данных.md>) |
| [Next.js](<./cards/Next.js/README.md>) | 14 | [Открыть →](<./cards/Next.js/01 Что такое Next.js и зачем он нужен.md>) |
| [Patterns](<./cards/Patterns/README.md>) | 8 | [Открыть →](<./cards/Patterns/01 Зачем нужны design patterns во frontend.md>) |
| [Performance](<./cards/Performance/README.md>) | 10 | [Открыть →](<./cards/Performance/01 Что такое web performance и как ее измерять.md>) |
| [Principles](<./cards/Principles/README.md>) | 8 | [Открыть →](<./cards/Principles/01 SOLID во frontend.md>) |
| [React](<./cards/React/README.md>) | 27 | [Открыть →](<./cards/React/01 Что такое React и зачем он нужен.md>) |
| [Security](<./cards/Security/README.md>) | 11 | [Открыть →](<./cards/Security/01 Frontend threat model.md>) |
| [State Management](<./cards/State Management/README.md>) | 10 | [Открыть →](<./cards/State Management/01 Виды состояния во frontend.md>) |
| [Testing](<./cards/Testing/README.md>) | 9 | [Открыть →](<./cards/Testing/01 Стратегия тестирования frontend.md>) |
| [Tooling](<./cards/Tooling/README.md>) | 12 | [Открыть →](<./cards/Tooling/01 package.json scripts dependencies devDependencies.md>) |
| [TypeScript](<./cards/TypeScript/README.md>) | 29 | [Открыть →](<./cards/TypeScript/01 Зачем нужен TypeScript.md>) |
| [Web API](<./cards/Web API/README.md>) | 12 | [Открыть →](<./cards/Web API/01 REST API и ресурсная модель.md>) |
| [Web Basics](<./cards/Web Basics/README.md>) | 9 | [Открыть →](<./cards/Web Basics/01 HTTP request response headers body.md>) |
| [Workflow](<./cards/Workflow/README.md>) | 5 | [Открыть →](<./cards/Workflow/01 Agile Scrum Kanban для frontend.md>) |

## Структура карточки

Каждая карточка содержит основной вопрос и эталонный ответ. В зависимости от темы также могут присутствовать встречные вопросы, мини-задача, практические сценарии, связанные темы и источники.

Навигация и оглавления генерируются командой:

```bash
python scripts/generate_navigation.py
```

Проверить ссылки и структуру без изменения файлов:

```bash
python scripts/generate_navigation.py --check
```

## Служебные материалы

- [Аудит покрытия базы вопросов](<./cards/00 Аудит покрытия Базовые вопросы 200.md>)
