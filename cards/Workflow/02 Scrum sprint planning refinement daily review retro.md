# 02 Scrum sprint planning refinement daily review retro

<!-- CARD-NAV-TOP:START -->
[← 01 Agile Scrum Kanban для frontend](<./01 Agile Scrum Kanban для frontend.md>) · [↑ Workflow](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Jira backlog issue story task acceptance criteria →](<./03 Jira backlog issue story task acceptance criteria.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

Какие основные события есть в Scrum и что на них важно для frontend-разработчика?

<details>
<summary><strong>Показать ответ</strong></summary>

В Scrum вся работа происходит внутри Sprint - цикла фиксированной длины не более месяца. Sprint включает четыре формальных события: Sprint Planning, Daily Scrum, Sprint Review и Sprint Retrospective. Они нужны для регулярной проверки результата и плана, а не просто для передачи статусов.

Sprint Planning отвечает на три вопроса: почему этот Sprint ценен, что команда может завершить и как будет выполнена выбранная работа. Результат - Sprint Goal и Sprint Backlog. Sprint Goal задаёт единую цель, а Sprint Backlog содержит выбранные элементы Product Backlog - упорядоченного списка продуктовой работы - и план их выполнения. Developers, то есть участники Scrum Team, создающие результат, формируют прогноз с учётом прошлой производительности, доступной мощности и Definition of Done.

Daily Scrum - ежедневное 15-минутное событие для Developers. Они проверяют прогресс к Sprint Goal и корректируют план ближайшей работы. Обязательной схемы «что сделал, что буду делать, какие блокеры» в Scrum Guide нет. Она допустима, пока помогает принять решения, а не превращает Daily в отчёт менеджеру.

Sprint Review - рабочая встреча Scrum Team и заинтересованных участников. Они проверяют результат спринта, изменения в продукте и окружении и решают, что делать дальше; Product Backlog может измениться. Это больше, чем демонстрация. Sprint Retrospective рассматривает качество и эффективность самой работы: взаимодействие, процесс, инструменты и Definition of Done. Итогом становятся конкретные улучшения.

Product Backlog refinement - постоянное уточнение будущей работы: элементы разбивают, описывают точнее, упорядочивают и оценивают. Это не отдельное обязательное событие Scrum и не обязано проходить одной встречей. Для frontend-разработчика здесь важно выяснить состояния интерфейса, контракт API, ошибки, адаптивность, доступность, аналитику, тестовые данные и зависимости до начала реализации.

</details>

## Встречные вопросы

<details>
<summary><strong>Вопрос:</strong> Что такое sprint?</summary>

Sprint - событие фиксированной длины не более месяца, внутри которого идеи превращаются в готовый Increment, то есть пригодное к использованию приращение продукта. Новый Sprint начинается сразу после предыдущего. Во время него качество не снижают и не вносят изменения, угрожающие Sprint Goal, но конкретный объём Sprint Backlog можно уточнять и согласовывать с Product Owner по мере появления новых знаний.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое sprint planning?</summary>

Sprint Planning начинает Sprint. Вся Scrum Team определяет ценность предстоящего Sprint и формулирует Sprint Goal. Developers выбирают посильный объём из Product Backlog и планируют, как создать соответствующий Definition of Done Increment. Вместе цель, выбранные элементы и план образуют Sprint Backlog. Для frontend это момент ещё раз проверить зависимости от макетов, API, окружения и тестовых данных.

</details>

<details>
<summary><strong>Вопрос:</strong> Можно ли менять объём работы во время Sprint и кто может его отменить?</summary>

Sprint Backlog не замораживается: по мере появления новых знаний Developers уточняют план и вместе с Product Owner могут пересогласовать конкретный объём. При этом изменения не должны угрожать Sprint Goal и снижать качество. Отменить Sprint может только Product Owner, если Sprint Goal потерял актуальность; обычная сложность задачи или ошибка оценки сами по себе не требуют отмены.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое refinement?</summary>

Product Backlog refinement - постоянная деятельность по разбиению и уточнению элементов Product Backlog. Элементы получают более точное описание, порядок, размер, критерии приёмки, зависимости и необходимые исследования. Product Owner отвечает за порядок, а Developers - за определение размера работы. В Scrum Guide refinement не является пятым событием и не имеет обязательного состава или timebox, то есть ограничения по времени; команда сама решает, когда и как его проводить.

</details>

<details>
<summary><strong>Вопрос:</strong> Что такое daily?</summary>

Daily Scrum - 15-минутное событие для Developers, чтобы проверить прогресс к Sprint Goal и адаптировать Sprint Backlog. Команда выбирает удобный формат самостоятельно. Подробное техническое обсуждение можно продолжить после Daily только с нужными участниками, чтобы короткая общая встреча не превратилась в решение одной частной проблемы.

</details>

<details>
<summary><strong>Вопрос:</strong> Чем review отличается от retrospective?</summary>

Sprint Review рассматривает результат и будущее продукта: что изменилось, какую ценность дал Increment и как адаптировать Product Backlog. В нём участвуют Scrum Team и заинтересованные люди. Sprint Retrospective рассматривает способ работы самой Scrum Team: качество, взаимодействие, процесс и инструменты. Review меняет продуктовый план, Retrospective - рабочий процесс.

</details>

<details>
<summary><strong>Вопрос:</strong> Нужно ли ждать Sprint Review, чтобы выпустить готовую функциональность?</summary>

Нет. Sprint Review не является воротами релиза. Как только Increment соответствует Definition of Done и процесс поставки это допускает, его можно выпустить до Review. На Review обсуждают уже созданный результат и дальнейшие изменения, а не дают формальное разрешение на публикацию.

</details>

<details>
<summary><strong>Вопрос:</strong> Сколько длятся события Scrum?</summary>

Для Sprint длиной в месяц Sprint Planning ограничен восемью часами, Sprint Review - четырьмя, Sprint Retrospective - тремя. Daily Scrum всегда ограничен 15 минутами. Для более короткого Sprint остальные события обычно короче. `Timebox`, то есть временное ограничение, задаёт верхнюю границу, а не требование обязательно занять всё время.

</details>

## Где это встречается во frontend

> [!NOTE]
> | Событие или деятельность | Пример результата |
> | --- | --- |
> | Refinement | Для формы уточнены валидация, ошибки и контракт API |
> | Sprint Planning | Работа разделена на интерфейс, интеграцию и тесты в рамках Sprint Goal |
> | Daily Scrum | Обнаружена зависимость от серверного контракта и назначен следующий шаг |
> | Sprint Review | Показан рабочий пользовательский сценарий и собрана обратная связь |
> | Sprint Retrospective | Команда договорилась раньше проверять доступность интерфейса |

## Связанные темы

- [01 Agile Scrum Kanban для frontend](<./01 Agile Scrum Kanban для frontend.md>)
- [03 Jira backlog issue story task acceptance criteria](<./03 Jira backlog issue story task acceptance criteria.md>)
- [05 Estimation blockers risks communication](<./05 Estimation blockers risks communication.md>)
- [02 Controlled uncontrolled и FormData](<../Forms/02 Controlled uncontrolled и FormData.md>)

## Источники

- [The Scrum Guide 2020](https://scrumguides.org/scrum-guide.html)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 01 Agile Scrum Kanban для frontend](<./01 Agile Scrum Kanban для frontend.md>) · [↑ Workflow](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [03 Jira backlog issue story task acceptance criteria →](<./03 Jira backlog issue story task acceptance criteria.md>)
<!-- CARD-NAV-BOTTOM:END -->
