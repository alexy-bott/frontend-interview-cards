# Image Font Link Script и оптимизация

<!-- CARD-NAV-TOP:START -->
[← 12 Route Groups Parallel и Intercepting Routes](<./12 Route Groups Parallel и Intercepting Routes.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 Environment variables next config standalone и deployment →](<./14 Environment variables next config standalone и deployment.md>)
<!-- CARD-NAV-TOP:END -->

## Вопрос

<br>

 💬 **Как Next.js оптимизирует изображения, шрифты, навигацию и сторонние скрипты через `next/image`, `next/font`, `next/link` и `next/script`?**

<h2></h2>

<br>
<dl>
<dd>

Next.js предоставляет компоненты для часто встречающихся ресурсов, потому что их загрузка напрямую влияет на Core Web Vitals, объём JavaScript и скорость переходов. Эти компоненты не делают страницу быстрой автоматически: разработчик всё равно задаёт правильные размеры, форматы и момент загрузки.

`next/image` расширяет обычный `<img>`. Компонент может изменять размер изображения под устройство, отдавать подходящий формат, загружать невидимые изображения лениво и резервировать место до загрузки. Резервирование места предотвращает layout shift, то есть неожиданное смещение интерфейса.

При локальном import Next.js знает ширину и высоту файла. Для внешнего URL нужно указать `width` и `height` либо использовать `fill`, когда изображение заполняет родителя с заданной геометрией. При `fill` важен prop `sizes`: без него браузер может скачать изображение значительно шире фактического блока.

```tsx
<Image
  src={product.imageUrl}
  alt={product.name}
  fill
  sizes="(max-width: 768px) 100vw, 33vw"
  style={{ objectFit: "cover" }}
/>
```

Внешние источники разрешают через строгий `images.remotePatterns` в `next.config.js`. Это ограничение защищает серверный оптимизатор изображений от обработки произвольных URL. Изображение первого экрана, влияющее на LCP, можно загрузить приоритетно через `priority` в Next.js 14; применять этот prop ко всей галерее нельзя, иначе ресурсы начинают конкурировать.

`next/font` загружает Google или локальные шрифты во время сборки, размещает их вместе с приложением и создаёт нужный CSS. Браузер не обращается к Google при открытии страницы. Фреймворк также использует `size-adjust`, чтобы запасной шрифт занимал близкое место и меньше сдвигал текст. Шрифт обычно подключают в корневом layout через `className` или CSS variable.

`next/link` выполняет клиентскую навигацию без полной перезагрузки документа и может заранее загрузить данные целевого маршрута. Prefetch, то есть предварительная загрузка, работает в production, когда ссылка попадает в область просмотра. Для статического маршрута обычно загружается весь маршрут, а для динамического Next.js может предварительно загрузить общие сегменты до ближайшего `loading.tsx`.

`next/script` управляет моментом выполнения стороннего JavaScript:

| Стратегия | Когда применять |
| --- | --- |
| `beforeInteractive` | Критический скрипт, который нужен до гидратации всего приложения |
| `afterInteractive` | Обычный скрипт после начала гидратации, значение по умолчанию |
| `lazyOnload` | Низкоприоритетный скрипт после события `load` и освобождения главного потока |
| `worker` | Экспериментальный запуск через Web Worker, в Next.js 14 не поддерживается App Router |

`beforeInteractive` следует использовать редко и размещать в корневом layout. Аналитика, чат-виджет и скрипт A/B-теста не должны без причины блокировать главный поток. Для каждого стороннего скрипта нужно оценить сетевой вес, время работы CPU, влияние на приватность, Content Security Policy и необходимость на конкретных страницах.

</dd>
</dl>
<br>


## Дополнительные вопросы

<details>
<summary><strong>Зачем <code>Image</code> нужны <code>width</code> и <code>height</code>, если CSS всё равно меняет размер?</strong></summary>

<dl>
<dd>
<h2></h2>

Эти значения задают исходное соотношение сторон, чтобы браузер зарезервировал место до загрузки файла. CSS может сделать изображение отзывчивым, сохраняя это соотношение. Без известных размеров контент после загрузки способен сдвинуть соседние элементы и ухудшить CLS.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Когда использовать <code>fill</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Когда размер задаётся контейнером, например у обложки карточки или главного изображения первого экрана. Родитель должен иметь `position: relative` или другой содержащий блок и явную геометрию. `object-fit` определяет вписывание, а `sizes` сообщает браузеру реальную ширину изображения на разных размерах viewport.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Зачем ограничивать <code>remotePatterns</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Сервер Next.js получает внешний URL и тратит ресурсы на загрузку и преобразование изображения. Разрешение любого домена превратило бы endpoint оптимизации в открытый proxy-сервис. `remotePatterns` ограничивает `protocol`, `hostname`, `port` и `pathname` ожидаемыми источниками.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Почему нельзя ставить <code>priority</code> всем изображениям?</strong></summary>

<dl>
<dd>
<h2></h2>

Приоритет сообщает браузеру загружать ресурс раньше обычного. Если так пометить всю страницу, фоновые изображения начинают конкурировать с LCP-изображением, CSS, шрифтами и данными. Приоритет нужен только одному или нескольким действительно видимым критическим изображениям.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Чем <code>next/font</code> лучше обычной ссылки на Google Fonts?</strong></summary>

<dl>
<dd>
<h2></h2>

Шрифт загружается во время сборки и раздаётся с того же приложения, поэтому браузеру не нужен отдельный запрос к Google. Next.js генерирует CSS и уменьшает layout shift за счёт метрик шрифта. Это не отменяет выбора небольшого числа начертаний и subsets, то есть наборов символов.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Что именно prefetch делает для <code>Link</code>?</strong></summary>

<dl>
<dd>
<h2></h2>

Он заранее получает RSC Payload и необходимые chunks маршрута, то есть части JavaScript-бандла, чтобы переход не начинался с нуля. Результат помещается в Router Cache браузера. Prefetch не означает загрузку всех backend-данных навсегда и может быть отключён через `prefetch={false}`, если автоматическая загрузка создаёт лишний трафик.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Как выбрать стратегию для стороннего скрипта?</strong></summary>

<dl>
<dd>
<h2></h2>

Сначала проверяют, нужен ли скрипт вообще. Код, без которого страница не может работать до гидратации, относится к редкому `beforeInteractive`. Функциональный скрипт после взаимодействия использует `afterInteractive`, а необязательный виджет или аналитика без требования раннего события можно отложить через `lazyOnload`.

<h2></h2>
</dd>
</dl>

</details>

<details>
<summary><strong>Заменяет ли <code>next/script</code> Content Security Policy?</strong></summary>

<dl>
<dd>
<h2></h2>

Нет. Компонент управляет загрузкой и порядком выполнения, но не определяет, каким источникам браузер доверяет. CSP ограничивает скрипты по источнику, nonce или hash. Для строгой политики стороннему скрипту может потребоваться nonce, то есть одноразовое разрешение, и явное разрешение домена.

<h2></h2>
</dd>
</dl>

</details>

## Где это встречается во frontend

| Проблема | Что проверить |
| --- | --- |
| Высокий CLS у карточек | Размеры `Image` и стабильный контейнер |
| Мобильный браузер скачивает большое изображение | `sizes` и адаптивные breakpoints |
| LCP-изображение начинает грузиться поздно | `priority` только для первого экрана |
| Текст сдвигается после шрифта | `next/font`, subsets и число начертаний |
| Переход по ссылке долго ждёт | `Link`, prefetch и `loading.tsx` |
| Сторонний виджет блокирует главный поток | Стратегия `Script` и необходимость виджета |

## Связанные темы

- [02 App Router pages layouts loading error route handlers](<./02 App Router pages layouts loading error route handlers.md>)
- [02 Core Web Vitals LCP INP CLS](<../Performance/02 Core Web Vitals LCP INP CLS.md>)
- [05 Images fonts resource priority preload lazy loading](<../Performance/05 Images fonts resource priority preload lazy loading.md>)
- [07 Images media alt captions](<../Accessibility/07 Images media alt captions.md>)
- [06 CSP security headers clickjacking](<../Security/06 CSP security headers clickjacking.md>)

## Источники

- [Next.js 14 docs: Image Optimization](https://nextjs.org/docs/14/app/building-your-application/optimizing/images)
- [Next.js 14 docs: Font Optimization](https://nextjs.org/docs/14/app/building-your-application/optimizing/fonts)
- [Next.js 14 docs: Link](https://nextjs.org/docs/14/app/api-reference/components/link)
- [Next.js 14 docs: Script Optimization](https://nextjs.org/docs/14/app/building-your-application/optimizing/scripts)

---

<!-- CARD-NAV-BOTTOM:START -->
[← 12 Route Groups Parallel и Intercepting Routes](<./12 Route Groups Parallel и Intercepting Routes.md>) · [↑ Next.js](<./README.md>) · [⌂ Все разделы](<../../README.md>) · [14 Environment variables next config standalone и deployment →](<./14 Environment variables next config standalone и deployment.md>)
<!-- CARD-NAV-BOTTOM:END -->
