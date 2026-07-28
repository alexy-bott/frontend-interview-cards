# Branching strategy feature branch main trunk git flow

<!-- CARD-NAV-TOP:START -->
[← 02 Working tree index commit history remote HEAD branch](<./02 Working tree index commit history remote HEAD branch.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Merge vs rebase fast-forward squash →](<./04 Merge vs rebase fast-forward squash.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Какие стратегии ветвления используются в командах? Чем feature branches, trunk-based development и Git Flow отличаются друг от друга?**

<h2></h2>

<br>
<dl>
<dd>

Стратегия ветвления определяет, откуда разработчик начинает работу, как долго живёт ветка, куда попадает готовый код и из какой ветки выпускается релиз. Универсально лучшей стратегии нет: выбор зависит от частоты поставки, способа релизов, размера команды, качества CI и необходимости поддерживать несколько версий продукта.

В workflow с feature branches задача выполняется в отдельной короткоживущей ветке и интегрируется в основную через merge request. Это изолирует историю задачи и удобно для review, но долгоживущие ветки накапливают расхождения и повышают риск сложных конфликтов.

Trunk-based development строится вокруг одной основной ветки, trunk. Разработчики либо часто интегрируют небольшие commits прямо в неё, либо используют очень короткие ветки. Основная ветка должна оставаться готовой к поставке, поэтому нужны быстрый CI, небольшие изменения и feature flags. Feature flag, или флаг функции, позволяет доставить код выключенным и включить возможность отдельно от deployment, то есть развёртывания новой версии.

Git Flow использует несколько долгоживущих веток: обычно `main` для выпущенных версий, `develop` для следующего релиза, а также `feature`, `release` и `hotfix` branches. Он поддерживает отдельную подготовку релизов и исправления нескольких версий, но создаёт больше merges и процессов. Для продукта с частыми небольшими deployments такой workflow часто тяжелее trunk-based подхода.

| Подход | Основная идея | Подходит, когда |
|---|---|---|
| Feature branches | Каждая задача проходит отдельный MR | Нужны изолированный review и понятный контроль интеграции |
| Trunk-based development | Маленькие изменения часто попадают в trunk | Команда выпускает часто и имеет быстрый надёжный CI |
| Git Flow | Релизная работа разделена между долгоживущими ветками | Есть плановые релизы и параллельная поддержка версий |

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Почему feature branch должна жить недолго?</strong></summary>

<dl>
<dd>
<h2></h2>

Пока ветка живёт отдельно, основная ветка продолжает меняться. Чем больше расхождение, тем труднее review, разрешение конфликтов и проверка совместной работы изменений. Риск уменьшают небольшие задачи, ранний draft MR и регулярная синхронизация с основной веткой.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Означает ли trunk-based development работу без branches?</strong></summary>

<dl>
<dd>
<h2></h2>

Не обязательно. Возможны прямые небольшие commits в trunk или короткоживущие branches, которые интегрируются за часы или один-два дня. Определяющий признак - частая интеграция в одну основную линию, а не конкретное отсутствие branches.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как доставить незавершённую функцию в trunk?</strong></summary>

<dl>
<dd>
<h2></h2>

Код разбивают на обратно совместимые части и скрывают пользовательскую возможность за feature flag. Незавершённый путь не должен влиять на обычных пользователей, а CI проверяет и включённое, и выключенное состояние там, где это критично. Удаление устаревших flags также планируют, иначе они превращаются в постоянные развилки кода.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем release branch отличается от feature branch?</strong></summary>

<dl>
<dd>
<h2></h2>

Feature branch содержит работу над конкретным изменением. Release branch фиксирует состав версии на этапе стабилизации: туда обычно принимают только исправления, после чего итог интегрируют в основные линии и помечают tag. Такой подход нужен не всем командам.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое hotfix branch?</strong></summary>

<dl>
<dd>
<h2></h2>

Это ветка для срочного исправления выпущенной версии. В Git Flow её начинают от production-линии, выпускают исправление, а затем переносят результат во все ветки, где ошибка не должна появиться снова, например в `main` и `develop`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что такое Git tag и зачем он нужен при релизе?</strong></summary>

<dl>
<dd>
<h2></h2>

Tag, или тег, - именованная ссылка на конкретный commit. В отличие от ветки, тег по соглашению не передвигают после публикации, поэтому им удобно отмечать выпущенные версии, например `v2.4.0`. Lightweight tag является простой ссылкой, а annotated tag хранит отдельный объект с автором, датой, сообщением и может быть подписан. Теги отправляют на remote явно, например `git push origin v2.4.0`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как синхронизировать feature branch с <code>main</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Можно merge-нуть актуальную `main` в feature branch или rebase-нуть собственные commits на новую `main`. Merge сохраняет существующую историю. Rebase делает линейную историю, но создаёт новые commits и обычно требует `push --force-with-lease` для уже опубликованной feature branch. Выбор определяется правилами команды.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Защищает ли отдельная ветка от интеграционных ошибок?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Ветка отделяет изменения в истории, но не доказывает их совместимость с текущей основной веткой и другими задачами. Для этого нужны актуальная база, pipeline на предполагаемом результате merge, тесты и проверка среды, близкой к production.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>По каким признакам выбирать стратегию ветвления?</strong></summary>

<dl>
<dd>
<h2></h2>

Смотрят на частоту релизов, длительность задач, число поддерживаемых версий, требования к согласованию, скорость CI и возможность использовать feature flags. Если изменения поставляются ежедневно, короткие branches и trunk-based workflow уменьшают задержку. Если релизы проходят длительную стабилизацию и несколько версий поддерживаются параллельно, release branches могут быть оправданы.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Ситуация | Возможный workflow |
|---|---|
| Небольшой SaaS с частыми deployments | Короткие feature branches, trunk-based development и feature flags |
| Корпоративный продукт с релизным циклом | Release branches и отдельный этап стабилизации |
| Срочная production-ошибка | Hotfix от выпущенной версии с переносом исправления в текущую разработку |
| Большой UI-проект | Маленькие MR снижают риск конфликтов в общих компонентах и маршрутах |

## Связанные темы

- [04 Merge vs rebase fast-forward squash](<./04 Merge vs rebase fast-forward squash.md>)
- [07 Merge request GitLab protected branches approvals](<./07 Merge request GitLab protected branches approvals.md>)
- [01 Что frontend должен понимать в DevOps](<../DevOps/01 Что frontend должен понимать в DevOps.md>)
- [08 Deployment strategies health checks rollback](<../DevOps/08 Deployment strategies health checks rollback.md>)

## Источники

- [Git docs: Git workflows](https://git-scm.com/docs/gitworkflows)
- [Git docs: git-tag](https://git-scm.com/docs/git-tag)
- [GitLab Docs: Trunk-based development](https://docs.gitlab.com/topics/gitlab_flow/#trunk-based-development)
- [GitLab Docs: Feature flags](https://docs.gitlab.com/operations/feature_flags/)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 02 Working tree index commit history remote HEAD branch](<./02 Working tree index commit history remote HEAD branch.md>) · [↑ Git](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [04 Merge vs rebase fast-forward squash →](<./04 Merge vs rebase fast-forward squash.md>)
<!-- CARD-NAV-BOTTOM:END -->
