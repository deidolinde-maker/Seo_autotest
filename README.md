# TASKDEV-3188 SEO monitor

Новый мониторинг строится отдельно от старого `seo_tests`.

## Режимы

- `Collector` запускается вручную и создаёт snapshot, после чего обновляет baseline.
- `Validator` запускается по расписанию, сам получает текущее состояние страниц и сравнивает его с baseline.
- `Validator` никогда не изменяет baseline автоматически.

## Файлы состояния

- `urls.txt` — единый ручной список URL, по одному URL в строке.
- `state/<site>/approved_baseline.json` — последний согласованный эталон сайта.
- `state/<site>/current_snapshot.json` — последний собранный снимок сайта.
- `state/<site>/validation_report.json` — последний результат проверки сайта.
- `allure-results/` — Allure result files, по одному тесту на URL.
- Параметр `--site` отбирает из общего списка только URL выбранного сайта.

## Jenkins

В репозитории находятся отдельные Jenkinsfile:

- `Jenkinsfile.101` — плановая проверка 101 в 07:00 по Москве;
- `Jenkinsfile.mol` — плановая проверка МОЛ в 07:15 по Москве;
- `Jenkinsfile.pol` — плановая проверка ПОЛ в 07:30 по Москве;
- `Jenkinsfile.collector` — ручной сбор snapshot и обновление baseline выбранного сайта.

Корневой `Jenkinsfile` оставлен как совместимый entry point для валидатора 101.
Для новых Jenkins job нужно явно указать соответствующий путь к Jenkinsfile.

Validator генерирует `allure-results`; Jenkinsfile публикует их через Allure Jenkins
Plugin. Если плагин не установлен, сам Validator и JSON-отчёт продолжают работать,
но Allure-вкладка в Jenkins не будет опубликована.

## Telegram

Jenkins Validator использует существующий proxy transport через Credentials:

- `telegram_proxy_url`;
- `telegram_proxy_auth_secret`;
- `tg_proxy_creds_survarius` (временно для текущего чата).

`collect` уведомления не отправляет. Если отправка Telegram не удалась в режиме
`validate`, pipeline завершается с кодом `2`.

URL, для которого Collector в baseline зафиксировал `redirect`, Validator не запрашивает
повторно и отображает как `пропущено`. После успешного ответа Collector URL автоматически
возвращается в обычную проверку.

На первом этапе `urls.txt` берётся из checkout. Перед production-запуском нужно
вынести `state/` на persistent Jenkins volume или во внешнее хранилище: очистка
workspace до этого момента отключена намеренно, иначе baseline будет потерян.

Позже `urls.txt` можно передавать через Jenkins Secret Text с тем же именем файла;
Python-код при этом менять не потребуется.

## QA-источники

Логика и тестовая стратегия подготовлены с учётом:

- `docs/qa-kb/workflows/analyze-task.md`
- `docs/qa-kb/core/test-design/techniques.md`
- `TASKDEV-3188_v17.md`
- `TASKDEV-3188_v17_QA_auto.md`
