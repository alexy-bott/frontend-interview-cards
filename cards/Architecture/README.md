# Architecture

<!-- SECTION-NAV:START -->
[⌂ Все разделы](<../../README.md>) · [Начать с первой карточки →](<./01 Что такое frontend architecture.md>)

Карточек в разделе: **11**
<!-- SECTION-NAV:END -->

Раздел для дружеского мок-собеса по frontend-архитектуре, FSD, API-слою, границам модулей и поддерживаемости проекта.

## Темы

1. [Что такое frontend-архитектура](<./01 Что такое frontend architecture.md>)
2. [FSD: слои, срезы, сегменты и правило импортов](<./02 FSD layers slices segments import rule.md>)
3. [FSD: public API и границы импортов](<./03 FSD public API import boundaries.md>)
4. [API-слой, контракт, DTO и преобразование данных](<./04 API слой contracts DTO mapping.md>)
5. [Где хранить состояние: компонент, server state, глобальный store или URL](<./05 Где хранить state local server global URL.md>)
6. [Feature flags: постепенный rollout и эксперименты](<./06 Feature flags rollout experiments.md>)
7. [Обработка ошибок и observability](<./07 Error handling observability logging monitoring.md>)
8. [Микрофронтенды: когда нужны и когда вредят](<./08 Microfrontends когда нужны и когда вредят.md>)
9. [Shared UI, дизайн-система и Radix UI](<./09 Shared UI design system Radix UI.md>)
10. [Архитектурные антипаттерны и циклические зависимости](<./10 Architecture anti-patterns utils dump circular dependencies.md>)
11. [Atomic Design, MVC, MVP и модульная архитектура](<./11 Atomic Design MVC MVP modular architecture.md>)

## Как пользоваться

Архитектурные вопросы стоит проверять через примеры: куда положить код, кто от кого может зависеть, где проходит граница фичи, как не превратить shared в свалку и как проверить, что структура реально помогает проекту.
