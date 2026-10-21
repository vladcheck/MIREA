from gost_report import Report, TitleConfig, MIREA_PROFILE

r = Report(TitleConfig(
    work_type="Практическое занятие",
    work_number="№7",
    topic="Контейнеризация. Docker и Docker Compose",
    discipline="Инструменты девопс",
    student_name="Валекжанин В.С.",
    student_group="ЭФБО-04-24",
    year="2026",
), profile=MIREA_PROFILE)

r.toc_static([
    (1, "Введение", 4),
    (1, "1 Образ приложения", 5),
    (1, "2 Конфигурация приложения и СУБД", 9),
    (1, "3 Публикация через обратный прокси", 14),
    (1, "4 Ответы на контрольные вопросы", 19),
    (1, "Заключение", 21),
    (1, "Список использованных источников", 22),
])
r.bib.add("dockerfile", type="web", authors=["Docker"], title="Dockerfile reference",
          url="https://docs.docker.com/reference/dockerfile/", accessed="27.09.2026")
r.bib.add("cache", type="web", authors=["Docker"], title="Docker build cache",
          url="https://docs.docker.com/build/cache/", accessed="27.09.2026")
r.bib.add("compose", type="web", authors=["Docker"], title="Compose file reference",
          url="https://docs.docker.com/reference/compose-file/", accessed="27.09.2026")
r.bib.add("network", type="web", authors=["Docker"], title="Networking overview",
          url="https://docs.docker.com/engine/network/", accessed="27.09.2026")
r.bib.add("volumes", type="web", authors=["Docker"], title="Volumes",
          url="https://docs.docker.com/engine/storage/volumes/", accessed="27.09.2026")
r.bib.add("firewall", type="web", authors=["Docker"], title="Packet filtering and firewalls",
          url="https://docs.docker.com/engine/network/packet-filtering-firewalls/", accessed="27.09.2026")
r.bib.add("security", type="web", authors=["Docker"], title="Docker Engine security",
          url="https://docs.docker.com/engine/security/", accessed="27.09.2026")
r.bib.add("proxy", type="web", authors=["Nginx"], title="Модуль ngx_http_proxy_module",
          url="https://nginx.org/ru/docs/http/ngx_http_proxy_module.html", accessed="27.09.2026")
r.bib.add("install", type="web", authors=["Docker"], title="Install Docker Engine on Ubuntu",
          url="https://docs.docker.com/engine/install/ubuntu/", accessed="27.09.2026")
r.bib.add("postgres", type="web", authors=["Docker"], title="postgres. Docker Official Image",
          url="https://hub.docker.com/_/postgres", accessed="27.09.2026")

r.h1("Введение", center=True)
r.text(
    "Отчёт описывает занятие по упаковке веб приложения на Flask в контейнер "
    f"и запуску связки приложение плюс СУБД через Compose {r.bib.cite('compose')}. "
    f"Docker Engine ставится на сервер из официального репозитория {r.bib.cite('install')}."
)
r.text("Задачи работы:")
r.numbered([
    "Изучить понятия образа, контейнера и слоя, а также механизм кэширования при сборке.",
    "Разработать Dockerfile шаблонного приложения, запускаемого от имени непривилегированного пользователя.",
    "Описать конфигурацию приложение плюс СУБД в файле docker-compose.yml с изолированной сетью и именованным томом.",
    "Опубликовать приложение через Nginx из практической работы №6, исключив прямой доступ к порту контейнера из сети.",
])

r.h1("1 Образ приложения")
r.task("Задание 1. Образ приложения.")
r.text(
    "Работа начинается в ветке feature/docker. Каталог app хранится в репозитории "
    "и доставляется на сервер средством rsync, как в практической работе №6. "
    "Файл с секретом исключается из доставки, иначе флаг удаления сотрёт его на сервере."
)
l1 = r.listing(
    "flask==3.0.3\npsycopg2-binary==2.9.9\ngunicorn==22.0.0",
    "Зависимости приложения",
)
r.text(f"Зависимости приложения фиксируются {r.ref.on_listing(l1)}.")
l2 = r.listing(
    "import os\n"
    "import psycopg2\n"
    "from flask import Flask\n"
    "\n"
    "app = Flask(__name__)\n"
    "\n"
    "def get_connection():\n"
    "    return psycopg2.connect(\n"
    '        host=os.getenv("DB_HOST", "localhost"),\n'
    '        dbname=os.getenv("POSTGRES_DB", "app"),\n'
    '        user=os.getenv("POSTGRES_USER", "app"),\n'
    '        password=os.getenv("POSTGRES_PASSWORD", "app"),\n'
    "    )\n"
    "\n"
    '@app.route("/health")\n'
    "def health():\n"
    '    return "ok\\n"\n'
    "\n"
    '@app.route("/")\n'
    "def index():\n"
    "    conn = get_connection()\n"
    "    try:\n"
    "        with conn, conn.cursor() as cur:\n"
    '            cur.execute("CREATE TABLE IF NOT EXISTS visits ("\n'
    '                "id SERIAL PRIMARY KEY, visited_at TIMESTAMP DEFAULT now())")\n'
    '            cur.execute("INSERT INTO visits DEFAULT VALUES")\n'
    '            cur.execute("SELECT count(*) FROM visits")\n'
    "            count = cur.fetchone()[0]\n"
    "    finally:\n"
    "        conn.close()\n"
    '    return f"Hello from Docker! Visits: {count}\\n"',
    "Приложение app.py, сокращённо",
)
r.text(
    "Параметры соединения читаются из окружения, проверка /health отвечает строкой ok, "
    f"а корневой маршрут создаёт таблицу visits и наращивает счётчик {r.ref.on_listing(l2)}."
)
l3 = r.listing(
    "FROM python:3.12-slim\n"
    "RUN useradd --system --no-create-home app\n"
    "WORKDIR /app\n"
    "COPY requirements.txt .\n"
    "RUN pip install --no-cache-dir -r requirements.txt\n"
    "COPY app.py .\n"
    "USER app\n"
    "EXPOSE 5000\n"
    'CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "app:app"]',
    "Файл Dockerfile",
)
r.text(
    "Сборка описана "
    f"{r.ref.on_listing(l3)}: зависимости ставятся до копирования кода, поэтому правка кода "
    f"не делает недействительным слой установки пакетов {r.bib.cite('cache')}. "
    f"Процесс запускается от имени пользователя app {r.bib.cite('dockerfile')}."
)
l4 = r.listing(
    ".env\n__pycache__/\n*.pyc",
    "Файл .dockerignore",
)
r.text(
    "Контекст сборки ограничивается "
    f"{r.ref.on_listing(l4)}: секрет не должен попадать в слой образа, иначе его извлечёт "
    f"любой получивший образ {r.bib.cite('security')}."
)
r.text(
    "Образ собирается под тегом devops-app версии 1.0, перечень слоёв выводит команда history "
    f"{r.ref.on_figure(1)}."
)
f1 = r.figure("pr7/1.png", "Сборка образа devops-app и перечень слоёв")
r.text(
    "Контейнер запускается с публикацией порта только на адресе замыкания. Проверка /health "
    "возвращает код 200, а корневой маршрут возвращает код 500, в журнале видна ошибка соединения "
    f"с СУБД {r.ref.on_figure(f1 + 1)}."
)
f2 = r.figure("pr7/2.png", "Проверка контейнера без СУБД и пользователь app")
r.text(
    "Приложение обращается к адресу localhost, а внутри контейнера это имя указывает на сам контейнер, "
    "где СУБД нет, поэтому соединение невозможно даже при работающем PostgreSQL на сервере. "
    "Команда id подтверждает пользователя app, а не root."
)
r.text(
    "После замены приветствия повторная сборка помечает шаги словом CACHED "
    f"{r.ref.on_figure(f2 + 1)}: изменился только слой копирования кода и слои ниже него."
)
f3 = r.figure("pr7/3.png", "Повторная сборка после правки текста с кэшем слоёв")
r.text(
    "Инструкция CMD записана в exec форме, поэтому процесс приложения получает PID 1 "
    "и корректно принимает сигнал завершения при остановке контейнера. "
    "Замена двух инструкций COPY одной общей до установки зависимостей сделала бы кэш бесполезным: "
    "любая правка кода делала бы недействительным слой установки пакетов."
)

r.h1("2 Конфигурация приложения и СУБД")
r.task("Задание 2. Конфигурация «приложение плюс СУБД».")
l5 = r.listing(
    "POSTGRES_DB=app\nPOSTGRES_USER=app\nPOSTGRES_PASSWORD=change_me\nDB_HOST=db",
    "Шаблон переменных окружения",
)
r.text(
    f"Шаблон переменных окружения показан {r.ref.on_listing(l5)}, сам секрет в репозиторий не попадает. "
    "На сервере файл создаётся из шаблона, пароль заменяется случайным значением, "
    "права ограничиваются значением 600."
)
l6 = r.listing(
    "services:\n"
    "  db:\n"
    "    image: postgres:16-alpine\n"
    "    env_file: .env\n"
    "    volumes:\n"
    "      - db_data:/var/lib/postgresql/data\n"
    "    networks:\n"
    "      - backend\n"
    "    healthcheck:\n"
    '      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]\n'
    "      interval: 5s\n"
    "      timeout: 3s\n"
    "      retries: 5\n"
    "    restart: unless-stopped\n"
    "  app:\n"
    "    build: .\n"
    "    image: devops-app:1.0\n"
    "    env_file: .env\n"
    "    ports:\n"
    '      - "127.0.0.1:5000:5000"\n'
    "    depends_on:\n"
    "      db:\n"
    "        condition: service_healthy\n"
    "    networks:\n"
    "      - backend\n"
    "    restart: unless-stopped\n"
    "volumes:\n"
    "  db_data:\n"
    "networks:\n"
    "  backend:",
    "Файл docker-compose.yml",
)
r.text(
    "Конфигурация приведена "
    f"{r.ref.on_listing(l6)}: СУБД использует образ postgres версии 16, сведения хранятся "
    f"в именованном томе db_data, запуск приложения откладывается до готовности СУБД "
    f"{r.bib.cite('compose')} {r.bib.cite('postgres')}."
)
r.text(
    "Проверка готовности содержит удвоенный знак доллара, поэтому подстановка откладывается "
    "до оболочки внутри контейнера. Тег фиксирует основную версию СУБД, формат сведений "
    "несовместим между основными версиями."
)
r.text(
    "Проект запускается, сервис СУБД переходит в состояние healthy, три обращения наращивают "
    f"счётчик значениями 1, 2 и 3 {r.ref.on_figure(f3 + 1)}."
)
f4 = r.figure("pr7/4.png", "Состояние Healthy и рост счётчика Visits")
r.text(
    "Сеть проекта видна в перечне сетей, имя db разрешается во встроенном DNS, сокет слушает "
    f"только адрес замыкания, порт СУБД на сервере не слушается {r.ref.on_figure(f4 + 1)}."
)
f5 = r.figure("pr7/5.png", "Сеть проекта с разрешением имени db и портом 127.0.0.1:5000")
r.text(
    "Приложение находит СУБД по имени сервиса db через сеть backend "
    f"{r.bib.cite('network')}."
)
r.text(
    "Пересоздание без флага сохраняет том и продолжает отсчёт, пересоздание с флагом удаления томов "
    f"удаляет том и начинает отсчёт с единицы {r.ref.on_figure(f5 + 1)}."
)
f6 = r.figure("pr7/6.png", "Счётчик после down со значением 5 и после down с удалением томов со значением 1")
r.text(
    "На рабочем сервере флаг с удалением томов недопустим без осознанной необходимости "
    f"{r.bib.cite('volumes')}."
)
r.text(
    "Ветка фиксируется и отправляется, проверка подтверждает отсутствие секрета в репозитории, "
    f"затем создаётся снимок 05-docker-compose {r.ref.on_figure(f6 + 1)}."
)
f7 = r.figure("pr7/7.png", "Фиксация ветки feature/docker и отсутствие секрета в репозитории")

r.h1("3 Публикация через обратный прокси")
r.task("Задание 3. Публикация через обратный прокси-сервер.")
r.text(
    "Публикация тестового контейнера на всех адресах видна из сети при пустом выводе UFW: "
    "пакеты проходят через цепочки iptables раньше правил UFW "
    f"{r.ref.on_figure(f7 + 1)} {r.bib.cite('firewall')}."
)
f8 = r.figure("pr7/8.png", "Доступность порта из сети при отсутствии правила UFW")
r.text("Привязка порта приложения к адресу замыкания исключает такой доступ.")
l7 = r.listing(
    "location /app/ {\n"
    "    proxy_pass http://127.0.0.1:5000/;\n"
    "    proxy_set_header Host $host;\n"
    "    proxy_set_header X-Real-IP $remote_addr;\n"
    "    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
    "    proxy_set_header X-Forwarded-Proto $scheme;\n"
    "}",
    "Расположение приложения в конфигурации Nginx",
)
r.text(
    "Расположение показано "
    f"{r.ref.on_listing(l7)}: завершающий слэш в proxy_pass заменяет префикс app на корень, "
    f"исходные сведения о запросе передаются в заголовках {r.bib.cite('proxy')}."
)
r.text(
    f"Проверка конфигурации и перезагрузка Nginx проходят успешно {r.ref.on_figure(f8 + 1)}."
)
f9 = r.figure("pr7/9.png", "Добавление расположения app и проверка конфигурации Nginx")
r.text(
    "Оба обращения к приложению успешны, статический ресурс отвечает кодом 200 "
    f"{r.ref.on_figure(f9 + 1)}."
)
f10 = r.figure("pr7/10.png", "Успешные обращения к приложению через HTTPS и созданный ресурс")
r.text(
    "При остановленном сервисе прокси отвечает кодом 502 "
    f"{r.ref.on_figure(f10 + 1)}."
)
f11 = r.figure("pr7/11.png", "Ответ 502 при остановленном приложении")
r.text(
    "В журнале ошибок видна запись об отказе соединения с кодом 111 при обращении к апстриму "
    f"на адресе замыкания {r.ref.on_figure(f11 + 1)}: отказ произошёл на участке между Nginx "
    "и контейнером, сам прокси работает."
)
f12 = r.figure("pr7/12.png", "Остановка сервиса, запись журнала ошибок и запуск")
l8 = r.listing(
    "## 9. Контейнеризация\n"
    "Способ установки Docker Engine из официального репозитория и его версия; "
    "участники группы docker; расположение проекта на сервере в каталоге ~/app; "
    "расположение файла .env рядом с проектом и его права 600; публикуемые порты "
    "и адреса 127.0.0.1:5000, порт СУБД не публикуется; именованный том app_db_data; "
    "конфигурация обратного прокси с расположением /app/.",
    "Раздел 9 документа server-setup.md",
)
r.text(
    f"Раздел 9 документа server-setup.md описывает установку, группу docker, расположение "
    f"проекта и секрета, порты, тома и прокси {r.ref.on_listing(l8)}."
)
l9 = r.listing(
    'check "служба docker активна" systemctl is-active -q docker\n'
    'check "контейнер СУБД в healthy" test "$(docker inspect -f '
    "'{{.State.Health.Status}}' app-db-1)\" = \"healthy\"\n"
    'check "порты только на замыкании" test -z "$(ss -tln | awk '
    "'$4 ~ /:(5000|5432)$/ && $4 !~ /^127\\\\.0\\\\.0\\\\.1:/')\"\n"
    'check "права .env равны 600" test "$(stat -c %a ~/app/.env)" = "600"',
    "Проверки контейнеризации в audit.sh",
)
r.text(
    f"Четыре проверки раздела контейнеризации приведены {r.ref.on_listing(l9)}: активность службы, "
    "состояние healthy, отсутствие сокетов на внешних адресах, права секрета 600."
)
r.text(
    "Прогон без нарушений завершается кодом возврата 0 "
    f"{r.ref.on_figure(f12 + 1)}."
)
f13 = r.figure("pr7/13.png", "Прогон audit.sh без нарушений с кодом возврата 0")
r.text(
    "Прогон с публикацией порта на всех адресах завершается кодом возврата 1, "
    f"после чего конфигурация восстанавливается {r.ref.on_figure(f13 + 1)}."
)
f14 = r.figure("pr7/14.png", "Прогон audit.sh с нарушением публикации с кодом возврата 1")
r.text(
    "Ветка влита в main через запрос на слияние номер 4 "
    f"{r.ref.on_figure(f14 + 1)}."
)
f15 = r.figure("pr7/15.png", "Запрос на слияние feature/docker со статусом Merged")
r.link(
    "https://github.com/vladcheck/devops-course-2026/pull/4",
    "https://github.com/vladcheck/devops-course-2026/pull/4",
)

r.h1("4 Ответы на контрольные вопросы")
r.numbered([
    "Какие механизмы ядра Linux обеспечивают изоляцию контейнера. Почему контейнер запускается быстрее виртуальной машины. Ответ. Изоляцию дают пространства имён и контрольные группы: первые ограничивают видимость процессов, сети и файловой системы, вторые ограничивают потребление ресурсов. Контейнер делит ядро хоста и не грузит отдельную ОС, поэтому старт занимает секунды.",
    "Изменение app.py привело к пересборке за секунды, изменение requirements.txt привело к повторной установке всех зависимостей. Объясните по механизму кэширования слоёв. Что изменится, если обе инструкции COPY заменить одной общей перед RUN pip install. Ответ. Слой используется из кэша, пока неизменны инструкция и копируемые файлы, изменение слоя делает недействительными все слои ниже. Правка кода затрагивает только верхние слои, правка зависимостей перезапускает установку. Одна общая инструкция COPY до установки пакетов сделает любую правку кода поводом для переустановки всех пакетов.",
    "Приложение, запущенное командой docker run, получает отказ в соединении с СУБД по адресу localhost. Объясните причину. Каким образом приложение находит СУБД в конфигурации Compose. Ответ. Внутри контейнера имя localhost указывает на сам контейнер, где СУБД нет. В сети проекта Compose встроенный DNS разрешает имя сервиса db в адрес контейнера СУБД, приложение обращается по этому имени.",
    "Чем depends_on с условием service_healthy отличается от depends_on без условия. Какую ошибку предотвращает это условие. Ответ. Обычный depends_on ждёт только запуска контейнера, условие healthy ждёт успешной проверки pg_isready. Условие предотвращает гонку, при которой приложение стартует раньше готовности СУБД принимать соединения и падает с ошибкой соединения.",
    "Что происходит со сведениями СУБД после docker compose down и после docker compose down с флагом удаления томов. Почему для сервиса с томом тег postgres 16 alpine предпочтительнее latest. Ответ. Обычный down удаляет контейнеры и сеть, но сохраняет том, счётчик продолжается. Флаг удаления томов стирает и том, отсчёт начинается с единицы. Тег фиксирует основную версию, формат сведений несовместим между основными версиями, обновление latest сделает содержимое тома нечитаемым.",
    "Порт 5001 не разрешён правилами UFW, но доступен с хостовой системы. Объясните механизм и назовите способ, исключающий такой доступ. Ответ. Публикация реализуется правилами iptables в цепочках DOCKER, пакеты перенаправляются до обработки правилами UFW. Доступ исключается привязкой порта к адресу замыкания вместо всех адресов.",
    "Учётной записи без права sudo добавлена группа docker. Покажите, каким образом она может получить права root на сервере, и сопоставьте с моделью разграничения привилегий из практической работы №5. Ответ. Участник группы docker запускает контейнер с корневым каталогом хоста, смонтированным на запись, и правит любые файлы системы, фактически получая права root. Поэтому в группу docker нельзя включать учётные записи без права sudo, как требует модель из практической работы №5.",
    "Обращение к ресурсу приложения возвращает 502 Bad Gateway. Назовите две возможные причины и порядок диагностики. Ответ. Первая причина остановленное приложение, вторая неверный адрес апстрима. Порядок диагностики: повторить запрос, проверить журналы приложения и журнал ошибок Nginx, найти запись об отказе соединения, проверить состояние контейнеров и прослушиваемые сокеты.",
])

r.h1("Заключение", center=True)
r.numbered([
    "Образ приложения собран, процесс работает от имени непривилегированного пользователя app.",
    "Связка приложение плюс СУБД запускается через Compose, счётчик сохраняется при пересоздании контейнеров.",
    "Приложение опубликовано через Nginx по HTTPS, прямой доступ к порту контейнера из сети закрыт.",
    "Сценарий аудита содержит раздел контейнеризации и завершается с кодом возврата 0, ветка влита через запрос на слияние.",
])

r.bib.references()

r.save("ИД ПР №7.docx")
