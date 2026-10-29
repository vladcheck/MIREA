from gost_report import Report, TitleConfig, MIREA_PROFILE

r = Report(TitleConfig(
    work_type="Контрольная работа",
    work_number="№2",
    topic="Публикация контейнеризированного приложения на защищённом сервере",
    discipline="Инструменты девопс",
    student_name="Валекжанин В.С.",
    student_group="ЭФБО-04-24",
    year="2026",
), profile=MIREA_PROFILE)

r.toc_static([
    (1, "Введение", 2),
    (1, "1 Ревизия и сборка образа", 2),
    (1, "2 Конфигурация приложение плюс Redis", 3),
    (1, "3 Публикация по HTTPS", 5),
    (1, "4 Контроль и фиксация результата", 6),
    (1, "5 Ответы на вопросы к защите", 7),
    (1, "Заключение", 9),
    (1, "Список использованных источников", 9),
])

r.bib.add("dockerfile", type="web", authors=[], title="Dockerfile reference // Docker Docs",
          url="https://docs.docker.com/reference/dockerfile/", accessed="17.10.2026")
r.bib.add("cache", type="web", authors=[], title="Docker build cache // Docker Docs",
          url="https://docs.docker.com/build/cache/", accessed="17.10.2026")
r.bib.add("compose", type="web", authors=[], title="Compose file reference // Docker Docs",
          url="https://docs.docker.com/reference/compose-file/", accessed="17.10.2026")
r.bib.add("interpolation", type="web", authors=[],
          title="Set, use, and manage variables in a Compose file with interpolation // Docker Docs",
          url="https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/",
          accessed="17.10.2026")
r.bib.add("firewall", type="web", authors=[], title="Packet filtering and firewalls // Docker Docs",
          url="https://docs.docker.com/engine/network/packet-filtering-firewalls/", accessed="17.10.2026")
r.bib.add("redis-image", type="web", authors=[], title="redis. Docker Official Image // Docker Hub",
          url="https://hub.docker.com/_/redis", accessed="17.10.2026")
r.bib.add("persistence", type="web", authors=[], title="Redis persistence // Redis Docs",
          url="https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/",
          accessed="17.10.2026")
r.bib.add("proxy", type="web", authors=[], title="Nginx. Модуль ngx_http_proxy_module",
          url="https://nginx.org/ru/docs/http/ngx_http_proxy_module.html", accessed="17.10.2026")
r.bib.add("https", type="web", authors=[], title="Nginx. Настройка HTTPS-серверов",
          url="https://nginx.org/ru/docs/http/configuring_https_servers.html", accessed="17.10.2026")
r.bib.add("secrets", type="web", authors=[],
          title="Удаление конфиденциальных данных из репозитория // GitHub Docs",
          url="https://docs.github.com/ru/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository",
          accessed="17.10.2026")
r.bib.add("port-publish", type="web", authors=[], title="Port publishing and mapping // Docker Docs",
          url="https://docs.docker.com/engine/network/port-publishing/", accessed="20.10.2026")

r.h1("Введение", center=True)
r.text(
    "Цель контрольной работы, проверяющей результаты практических занятий № 5-7, "
    "заключается в том, чтобы без методических указаний упаковать веб-приложение "
    "в контейнер, описать многоконтейнерную конфигурацию с Redis и опубликовать "
    "её через обратный прокси-сервер Nginx с TLS, сохранив защищённость сервера."
)
r.text(
    "Проверяемые результаты включают ревизию Dockerfile, корректную работу с секретами, "
    "конфигурацию приложение плюс хранилище, выпуск самоподписанного сертификата с полем SAN, "
    "настройку обратного прокси-сервера и сохранение защиты сервера сценарием аудита."
)
r.text(
    "Вариант 4 определяет доменное имя kv.devops.local и порт приложения 8004. "
    "Исполнитель: Валекжанин В.С., группа ЭФБО-04-24."
)

r.h1("1 Ревизия и сборка образа")
r.task("Задание 1. Ревизия и сборка образа.")
r.text(
    "Шаблон приложения получен из репозитория kr2-template. Перед сборкой проведена "
    "ревизия Dockerfile и состава репозитория. Найденные дефекты и их последствия "
    "приведены в таблице 1."
)

t1 = r.table([
    ["№", "Файл, строка", "Дефект", "Последствие", "Исправление"],
    ["1", "Dockerfile, CMD", "Команда запуска записана в shell-форме и выполняется от root",
     "Процесс обёрнут в /bin/sh, не получает сигналы напрямую, остановка контейнера занимает десять секунд",
     "Перейти к exec-форме CMD и добавить USER app"],
    ["2", "Dockerfile, COPY", "Копирование всего каталога проекта выполняется до установки зависимостей",
     "Любое изменение кода делает недействительным слой установки пакетов, сборка занимает больше времени",
     "Сначала копировать requirements.txt и запускать pip install, затем копировать код"],
    ["3", "Dockerfile, порт", "Инструкция EXPOSE указывает порт 5000 вместо 8004",
     "Документация образа и публикация по умолчанию не соответствуют варианту 4",
     "Изменить EXPOSE на 8004 и привязать gunicorn к 0.0.0.0:8004"],
    ["4", "Dockerfile, контекст", "Файл .env копируется в образ вместе с кодом",
     "Пароль Redis оказывается в слое образа, доступном любому, кто получит образ",
     "Добавить .env в .dockerignore"],
    ["5", "Dockerfile", "Отсутствует непривилегированный пользователь",
     "Приложение работает от root, компрометация контейнера даёт повышенные права",
     "Создать пользователя app и переключиться на него"],
    ["6", "Репозиторий", "Файл .env отслеживается Git",
     "Секрет попадает в историю репозитория и распространяется при клонировании",
     "Добавить .env в .gitignore и удалить из индекса"],
    ["7", "Dockerfile / Compose", "Отсутствует проверка готовности сервисов",
     "Compose считает контейнер запущенным сразу после старта, даже если приложение не готово принимать соединения",
     "Добавить healthcheck для Redis и depends_on с условием service_healthy"],
], caption="Дефекты шаблона и их устранение")

r.text(
    f"Ревизия показала, что основные проблемы шаблона связаны с привилегиями, кэшированием, "
    f"секретами и сетевыми параметрами {r.ref.in_table(t1)}."
)

l1 = r.listing(
    "FROM python:3.12-slim\n"
    "RUN useradd --system --no-create-home app\n"
    "WORKDIR /app\n"
    "COPY requirements.txt .\n"
    "RUN pip install --no-cache-dir -r requirements.txt\n"
    "COPY app.py .\n"
    "USER app\n"
    "EXPOSE 8004\n"
    'CMD ["gunicorn", "--bind", "0.0.0.0:8004", "--access-logfile", "-", "app:app"]',
    "Файл Dockerfile",
)
r.text(
    f"Итоговый Dockerfile приведён {r.ref.on_listing(l1)}: зависимости устанавливаются до копирования "
    f"кода, поэтому правка app.py не трогает слой установки пакетов {r.bib.cite('cache')}. "
    f"Процесс запускается от имени пользователя app и принимает соединения на порту 8004 "
    f"{r.bib.cite('dockerfile')}."
)

l2 = r.listing(
    ".env\n"
    "__pycache__/\n"
    "*.pyc",
    "Файл .dockerignore",
)
r.text(
    f"Контекст сборки ограничивается {r.ref.on_listing(l2)}: файл с секретом исключается из образа, "
    f"иначе пароль останется в слое и будет доступен при распространении образа."
)

l3 = r.listing(
    "REDIS_HOST=localhost\n"
    "REDIS_PASSWORD=change_me\n"
    "STUDENT=unknown",
    "Шаблон переменных окружения",
)
r.text(
    f"Шаблон переменных окружения показан {r.ref.on_listing(l3)}; на сервере файл .env создаётся "
    f"отдельно, пароль заменяется случайным значением длиной не менее 32 шестнадцатеричных символов, "
    f"права ограничиваются значением 600."
)

l4 = r.listing(
    "rsync -avz --delete --exclude=.env --exclude=.git --dry-run ./ devops:kr2/\n"
    "rsync -avz --delete --exclude=.env --exclude=.git ./ devops:kr2/",
    "Доставка проекта на сервер",
)
r.text(
    f"Проект доставляется на сервер командой rsync {r.ref.on_listing(l4)}: флаг исключения .env не даёт "
    f"перезаписать секрет на сервере, а --dry-run позволяет проверить изменения перед копированием."
)

f1 = r.figure("kr2/1.png", "Проверка образа kr2-app: пользователь app, exec-форма CMD, health и быстрая остановка")
r.text(
    f"Проверка образа подтверждает, что контейнер работает от имени пользователя app, команда запуска "
    f"является JSON-массивом без оболочки, проверка /health возвращает ok, а остановка занимает "
    f"0,6 с {r.ref.on_figure(f1)}."
)

f2 = r.figure("kr2/2.png", "Размер образа kr2-app составляет 87,5 МБ")
r.text(
    f"Размер собранного образа kr2-app:1.0 составляет 87,5 МБ {r.ref.on_figure(f2)}."
)

r.h1("2 Конфигурация приложение плюс Redis")
r.task("Задание 2. Конфигурация приложение плюс Redis.")

l5 = r.listing(
    "services:\n"
    "  app:\n"
    "    build: .\n"
    "    image: kr2-app:1.0\n"
    "    env_file: .env\n"
    "    ports:\n"
    '      - "127.0.0.1:8004:8004"\n'
    "    depends_on:\n"
    "      redis:\n"
    "        condition: service_healthy\n"
    "    networks:\n"
    "      - backend\n"
    "    restart: unless-stopped\n"
    "  redis:\n"
    "    image: redis:7-alpine\n"
    "    env_file: .env\n"
    '    command: ["redis-server", "--appendonly", "yes", "--requirepass",\n'
    '      "${REDIS_PASSWORD:?REDIS_PASSWORD is not set}"]\n'
    "    healthcheck:\n"
    '      test: ["CMD-SHELL", "redis-cli -a \"$$REDIS_PASSWORD\" --no-auth-warning ping | grep -q PONG"]\n'
    "      interval: 5s\n"
    "      timeout: 3s\n"
    "      retries: 5\n"
    "    volumes:\n"
    "      - redis_data:/data\n"
    "    networks:\n"
    "      - backend\n"
    "    restart: unless-stopped\n"
    "volumes:\n"
    "  redis_data:\n"
    "networks:\n"
    "  backend:",
    "Файл docker-compose.yml",
)
r.text(
    f"Конфигурация приведена {r.ref.on_listing(l5)}: Redis использует официальный образ версии 7 на базе "
    f"Alpine, данные хранятся в именованном томе redis_data, приложение запускается только после "
    f"перехода Redis в состояние healthy {r.bib.cite('compose')} {r.bib.cite('redis-image')}. "
    f"Порт приложения опубликован только на адресе замыкания, порт Redis наружу не выведен "
    f"{r.bib.cite('port-publish')}."
)
r.text(
    f"Проверка готовности Redis содержит удвоенный знак доллара, поэтому подстановка пароля откладывается "
    f"до оболочки внутри контейнера {r.bib.cite('interpolation')}. Параметр --appendonly yes включает "
    f"журнал AOF, поэтому счётчик сохраняется при пересоздании контейнеров {r.bib.cite('persistence')}."
)

f3 = r.figure("kr2/3.png", "Сервисы в состоянии Up и Healthy, порт приложения привязан к 127.0.0.1:8004")
r.text(
    f"После запуска проекта оба сервиса находятся в состоянии Up, Redis отмечен как healthy, порт приложения "
    f"привязан только к адресу замыкания {r.ref.on_figure(f3)}."
)

f4 = r.figure("kr2/4.png", "Три обращения к приложению наращивают счётчик hits до 3, контейнер bea4a6737dad")
r.text(
    f"Три последовательных запроса к корневому маршруту наращивают счётчик значениями 1, 2 и 3, "
    f"в ответе виден идентификатор контейнера bea4a6737dad {r.ref.on_figure(f4)}."
)

f5 = r.figure("kr2/5.png", "Проверка привилегий, сети, аутентификации Redis и публикации портов")
r.text(
    f"Проверки показывают, что процессы не работают от root, приложение разрешает имя redis во встроенном DNS, "
    f"обращение к Redis без пароля возвращает ошибку NOAUTH, а на сервере прослушивается только порт 8004 "
    f"на адресе замыкания {r.ref.on_figure(f5)}."
)

r.text(
    "Приложение обращается к Redis по имени сервиса redis через изолированную сеть backend. "
    "Команда docker compose down без флага -v удаляет контейнеры и сеть, но сохраняет том redis_data, "
    "поэтому счётчик продолжает отсчёт после повторного запуска."
)

r.h1("3 Публикация по HTTPS")
r.task("Задание 3. Публикация по HTTPS.")
r.text(
    "Для публикации приложения по HTTPS выпущен отдельный самоподписанный сертификат с полем SAN "
    "для домена kv.devops.local. Закрытый ключ защищён правами 600 и владельцем root."
)

l6 = r.listing(
    "sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\\n"
    "  -keyout /etc/ssl/private/kr2.key \\\n"
    "  -out /etc/ssl/certs/kr2.crt \\\n"
    '  -subj "/CN=kv.devops.local" \\\n'
    '  -addext "subjectAltName=DNS:kv.devops.local"\n'
    "sudo chmod 600 /etc/ssl/private/kr2.key\n"
    "sudo chown root:root /etc/ssl/private/kr2.key",
    "Выпуск самоподписанного сертификата",
)
r.text(
    f"Команда формирования сертификата приведена {r.ref.on_listing(l6)}: в полях CN и SAN указано имя "
    f"kv.devops.local, ключ хранится в /etc/ssl/private/kr2.key с правами 600."
)

l7 = r.listing(
    "server {\n"
    "    listen 80;\n"
    "    server_name kv.devops.local;\n"
    "    return 301 https://$server_name$request_uri;\n"
    "}\n"
    "\n"
    "server {\n"
    "    listen 443 ssl;\n"
    "    server_name kv.devops.local;\n"
    "\n"
    "    ssl_certificate /etc/ssl/certs/kr2.crt;\n"
    "    ssl_certificate_key /etc/ssl/private/kr2.key;\n"
    "\n"
    "    access_log /var/log/nginx/kr2.access.log;\n"
    "    error_log /var/log/nginx/kr2.error.log;\n"
    "\n"
    "    location / {\n"
    "        proxy_pass http://127.0.0.1:8004;\n"
    "        proxy_set_header Host $host;\n"
    "        proxy_set_header X-Real-IP $remote_addr;\n"
    "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
    "        proxy_set_header X-Forwarded-Proto $scheme;\n"
    "    }\n"
    "}",
    "Конфигурация Nginx /etc/nginx/sites-available/kr2",
)
r.text(
    f"Конфигурация ресурса приведена {r.ref.on_listing(l7)}: HTTP-запросы перенаправляются на HTTPS кодом 301, "
    f"HTTPS-запросы передаются приложению на 127.0.0.1:8004 с заголовками Host, X-Real-IP, "
    f"X-Forwarded-For и X-Forwarded-Proto {r.bib.cite('proxy')} {r.bib.cite('https')}. "
    f"Журналы ресурса записываются в отдельные файлы."
)

f6 = r.figure("kr2/6.png", "Выпуск сертификата kv.devops.local с полем SAN")
r.text(
    f"Выпуск сертификата и проверка его полей выполнены успешно {r.ref.on_figure(f6)}."
)

f7 = r.figure("kr2/7.png", "Проверка конфигурации Nginx, reload и curl через заголовок Host")
r.text(
    f"Команда nginx -t подтверждает корректность синтаксиса, reload применяет конфигурацию без прерывания "
    f"обслуживания других ресурсов, а запрос с явным заголовком Host разрешается в домен kv.devops.local "
    f"{r.ref.on_figure(f7)}."
)

f8 = r.figure("kr2/8.png", "Успешное обращение к ресурсу по HTTPS с хостовой системы")
r.text(
    f"С хостовой системы ресурс доступен по HTTPS с проверкой сертификата, в ответе /whoami строка client "
    f"содержит адрес хоста, переданный Nginx в заголовке X-Forwarded-For {r.ref.on_figure(f8)}. "
    f"Приложение не может получить этот адрес из TCP-соединения, потому что фактическое соединение "
    f"установлено с Nginx на адресе замыкания."
)

r.h1("4 Контроль и фиксация результата")
r.task("Задание 4. Контроль и фиксация результата.")
r.text(
    "Завершающий этап проверяет, что защита сервера сохранена, секрет не утёк в отслеживаемые файлы, "
    "а изменения зафиксированы в ветке репозитория."
)

l8 = r.listing(
    "(cd ~/devops-course-2026 && scripts/audit.sh); echo $?\n"
    "diff <(sudo ufw status numbered) ~/ufw-before-kr2.txt && echo \"правила UFW не изменены\"\n"
    "sudo ls -l /etc/ssl/private/kr2.key ~/kr2/.env",
    "Проверка защиты сервера",
)
r.text(
    f"Сценарий аудита завершается с кодом возврата 0, правила UFW совпадают с начальным состоянием, "
    f"права ключа и файла .env соответствуют требованиям {r.ref.on_listing(l8)}."
)

l9 = r.listing(
    "pw=$(sed -n 's/^REDIS_PASSWORD=//p' ~/kr2/.env)\n"
    "grep -rlF --exclude=.env -- \"$pw\" ~/kr2\n"
    "unset pw\n"
    "git ls-files | grep -E '(^|/)\\.env$'\n"
    "git grep -nI -E 'REDIS_PASSWORD|requirepass'",
    "Проверка отсутствия секрета в отслеживаемых файлах",
)
r.text(
    f"Поиск действующего пароля по файлам проекта не находит совпадений, кроме файла .env, а команда "
    f"git ls-files не возвращает .env, подтверждая, что секрет не отслеживается {r.ref.on_listing(l9)}. "
    f"Исторический пароль шаблона остаётся в ветке main, поэтому на сервере используется новый пароль; "
    f"при необходимости историю можно очистить инструментами, описанными в документации GitHub "
    f"{r.bib.cite('secrets')}."
)

f10 = r.figure("kr2/10.png", "Запрос на слияние add-kr2-valekzhanin со статусом Merged")
r.text(
    f"Изменения объединены с main через запрос на слияние номер 11 {r.ref.on_figure(f10)}."
)
r.link(
    "https://github.com/vladcheck/MIREA/pull/11",
    "https://github.com/vladcheck/MIREA/pull/11",
)

r.h1("5 Ответы на вопросы к защите")
r.numbered([
    "Приложение внутри контейнера должно слушать адрес 0.0.0.0:8004, а не 127.0.0.1:8004, потому что localhost внутри контейнера указывает на сам контейнер, и обращение с сервера не достигнет процесса. Адрес 0.0.0.0 внутри контейнера открывает сокет на всех интерфейсах контейнера, но не делает приложение доступным из сети, поскольку внешний доступ определяет публикацией порта Docker. В данном случае порт опубликован только на 127.0.0.1, поэтому из сети приложение недоступно.",
    "Файл .env удалён из репозитория отдельным коммитом, но пароль из шаблона остаётся в истории Git. Пароль нельзя считать секретным, потому что он уже раскрыт. На сервере нужно сгенерировать новый случайный пароль. Историю публичной ветки main переписать сложно, поэтому практичнее сменить пароль и больше не использовать старый; очистку истории можно выполнить утилитами filter-repo или BFG, после чего потребуется форс-пуш, о чём нужно предупредить коллег.",
    "Инструкция RUN rm .env в Dockerfile не удаляет секрет из образа, потому что слои образа неизменяемы. Файл остаётся в предыдущем слое и доступен для извлечения. При публикации образа в реестр это опасно тем, что любой, кто скачает образ, сможет прочитать содержимое удалённого слоя. Защита обеспечивается исключением .env из контекста сборки через .dockerignore, а не удалением внутри Dockerfile.",
    "CMD в exec-форме записывается как JSON-массив, поэтому процесс gunicorn запускается напрямую и получает PID 1. Shell-форма оборачивает команду в /bin/sh -c, и PID 1 получает оболочка, которая некорректно пересылает сигналы дочернему процессу. Проверить PID 1 можно командой docker exec ИМЯ_КОНТЕЙНЕРА ps aux или docker inspect -f '{{.State.Pid}}' ИМЯ_КОНТЕЙНЕРА на хосте.",
    "Значение ${REDIS_PASSWORD} подставляет сам Docker Compose на этапе разбора файла на хосте. Значение $$REDIS_PASSWORD превращается Compose в одиночный знак доллара $REDIS_PASSWORD и передаётся в оболочку внутри контейнера, где уже выполняется подстановка переменной окружения. Если в проверке готовности записать ${REDIS_PASSWORD}, пароль подставится в строку команды на хосте, попадёт в вывод docker compose config и docker inspect, что приведёт к утечке секрета.",
    "Команда сервиса redis начинается с redis-server, потому что точка входа официального образа распознаёт такой формат и выполняет понижение привилегий до пользователя redis. Запуск через sh -c обходит эту логику, и Redis работает от root. Проверить пользователя можно командой docker compose exec redis ps aux или docker compose exec redis id redis.",
    "Порт Redis не опубликован, но пароль всё равно нужен, потому что изоляция сети Docker не является полноценным барьером. К Redis могут обратиться другие контейнеры в той же сети, а при ошибочной публикации порта или компрометации контейнера доступ откроется и извне. Пароль защищает от несанкционированного подключения внутри инфраструктуры.",
    "Условие depends_on с service_healthy задерживает запуск зависимого сервиса до тех пор, пока проверка готовности Redis не вернёт успех. depends_on без условия ждёт только фактического старта контейнера, не проверяя готовность службы. Без условия healthy приложение может стартовать раньше Redis и упасть с ошибкой соединения; пользователь в первые секунды может увидеть отказ или частичную загрузку страницы.",
    "Команда docker compose down удаляет контейнеры и сеть, но сохраняет именованный том redis_data, поэтому счётчик продолжает расти. Команда docker compose down -v дополнительно удаляет том, и счётчик сбросится. Замена тега образа на redis:latest опасна, потому что major-версия может измениться, а формат данных несовместим между основными версиями, что приведёт к повреждению данных в томе.",
    "Для kv.devops.local выпущен отдельный сертификат, потому что сертификат для devops.local не содержит SAN kv.devops.local. Команда curl --cacert ~/devops.crt https://kv.devops.local завершится ошибкой проверки имени хоста. Nginx выбирает сертификат по SPNI при TLS-рукопожатии: клиент передаёт имя сервера, и Nginx использует ssl_certificate из блока server с совпадающим server_name. Если SNI не используется, выбирается первый блок server на порту 443.",
    "В строке client ответа /whoami выводится адрес хостовой системы, переданный Nginx в заголовке X-Forwarded-For. Приложение не может определить адрес клиента по TCP-соединению, потому что для него соединение установлено с Nginx на 127.0.0.1. Значению X-Forwarded-For, полученному напрямую от клиента, доверять нельзя, так как клиент может подставить произвольное значение; доверять можно только тому адресу, который добавил доверенный прокси-сервер.",
    "После sudo reboot операционная система перезагружается. Службы, включённые через systemctl enable, например ssh и nginx, запускаются автоматически. Docker daemon, если он включён, тоже стартует. Контейнеры с политикой restart: unless-stopped пересоздаются Compose или Docker автоматически. Сервисы без политики перезапуска или вручную остановленные до перезагрузки не поднимутся сами.",
    "Запись в файле hosts нужна на хостовой системе, потому что клиент должен разрешить имя kv.devops.local в IP-адрес сервера. На самом сервере запись не нужна для работы обратного прокси, потому что Nginx принимает соединение на всех интерфейсах, сопоставляет запрос с server_name из заголовка Host и перенаправляет его на 127.0.0.1:8004, не обращаясь к DNS.",
    f"Если порт приложения ошибочно опубликован как 8004:8004 без привязки к 127.0.0.1, Docker создаёт правила iptables в цепочках DOCKER и DOCKER-USER, которые обрабатываются до правил UFW, поэтому UFW не препятствует доступу из сети {r.bib.cite('firewall')}. Проверка раздела [5] сценария аудита из практической работы № 7 не обнаружит эту проблему, потому что она смотрит на вывод ufw, а не на публикацию портов Docker. Нужно добавить проверку, что docker compose port app 8004 возвращает только 127.0.0.1, либо просканировать прослушиваемые сокеты командой ss.",
])

r.h1("Заключение", center=True)
r.numbered([
    "Образ приложения kr2-app:1.0 собран на базе python:3.12-slim, процесс работает от имени непривилегированного пользователя app и принимает соединения на порту 8004.",
    "Конфигурация приложение плюс Redis запускается через Docker Compose, счётчик посещений сохраняется в именованном томе redis_data при пересоздании контейнеров.",
    "Приложение опубликовано по HTTPS на домене kv.devops.local через обратный прокси-сервер Nginx, прямой доступ к порту контейнера из сети исключён привязкой к 127.0.0.1.",
    "Сценарий аудита завершается с кодом возврата 0, правила UFW не изменены, секрет не попал в отслеживаемые файлы, изменения зафиксированы через запрос на слияние номер 11.",
])

r.bib.references()

r.save("ИД КР №2.docx")
