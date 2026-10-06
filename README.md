# TASKDEV-3188 SEO monitor

Новый мониторинг строится отдельно от старого `seo_tests`.

## Режимы

- `Collector` запускается вручную и создаёт snapshot, после чего обновляет baseline.
- `Validator` запускается по расписанию, сам получает текущее состояние страниц и сравнивает его с baseline.
- `Validator` никогда не изменяет baseline автоматически.

## Файлы состояния

- `urls.txt` — ручной список URL, по одному URL в строке.
- `state/approved_baseline.json` — последний согласованный эталон.
- `state/current_snapshot.json` — последний собранный снимок.
- `state/validation_report.json` — последний результат проверки.
- `allure-results/` — Allure result files, по одному тесту на URL.
- При смешанном списке URL сайт определяется автоматически по hostname; `--site`
  можно использовать для контролируемого запуска одного набора данных.

## Jenkins

`Jenkinsfile` поддерживает три режима:

- `validate` — плановая проверка;
- `collect` — ручной сбор snapshot и обновление baseline.

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
