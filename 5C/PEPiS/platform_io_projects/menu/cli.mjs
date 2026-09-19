#!/usr/bin/env node
/**
 * DIS_F407VG Lab Runner — интерактивное меню для сборки/прошивки лабораторных.
 *
 * Запуск:
 *   npm start                  — интерактивное меню
 *   node cli.mjs               — то же самое
 *   node cli.mjs LR1_GPIO_LED upload --mode 3   — без меню (для скриптов/алиасов)
 */
import { intro, outro, select, confirm, isCancel, cancel, note } from "@clack/prompts";
import gradient from "gradient-string";
import chalk from "chalk";
import { spawn } from "node:child_process";
import { readdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const projectsRoot = join(here, "..");

/* Градиент в стиле opencode: оранжевый -> красный -> пурпурный */
const brand = gradient(["#f97316", "#ef4444", "#d946ef"]);
const dim = chalk.gray;

const BANNER = brand.multiline(String.raw`
  ┌──────────────────────────────────────────────┐
  │          DIS_F407VG · LAB RUNNER             │
  │   STM32F407VGT6 · PlatformIO · stlink        │
  └──────────────────────────────────────────────┘`);

/* ── Обнаружение проектов (папки с platformio.ini рядом с menu/).
 *    Проект с файлом .labrunner-hide внутри скрыт из меню. ── */
const PROJECTS = readdirSync(projectsRoot, { withFileTypes: true })
  .filter((d) => d.isDirectory() && existsSync(join(projectsRoot, d.name, "platformio.ini")))
  .filter((d) => !existsSync(join(projectsRoot, d.name, ".labrunner-hide")))
  .map((d) => d.name)
  .sort();

if (PROJECTS.length === 0) {
  console.error(chalk.red("Не найдено ни одного проекта с platformio.ini рядом с menu/"));
  process.exit(1);
}

/* Варианты задач внутри проектов (подставляются через PLATFORMIO_BUILD_FLAGS) */
const VARIANTS = {
  LR1_GPIO_LED: {
    flag: "MODE",
    label: "Режим (MODE)",
    options: [
      { value: "1", label: "Мигание светодиодом (PA0)", hint: "базовый пример" },
      { value: "2", label: "Бегущий огонь PA0→PA7", hint: "базовый пример" },
      { value: "3", label: "Огонь назад PA7→PA0", hint: "задание 1" },
      { value: "4", label: "Двухсторонний огонь", hint: "задание 2" },
      { value: "5", label: "Мигание, регулировка скорости", hint: "задание 3" },
    ],
  },
  LR3_LogicGen: {
    flag: "TASK",
    label: "Задание (TASK)",
    options: [
      { value: "0", label: "LED от SW1 + код 0–15", hint: "основная программа" },
      { value: "1", label: "Переключатель-инвертор", hint: "задание 1" },
      { value: "2", label: "Режимы LED по SW1+SW2", hint: "задание 2" },
      { value: "3", label: "Счётчик нажатий 0–9", hint: "задание 3" },
      { value: "4", label: "Двоичный код на 4 разрядах", hint: "задание 4" },
    ],
  },
};

const ACTIONS = [
  { value: "upload", label: "Собрать и прошить", hint: "pio run --target upload" },
  { value: "build", label: "Только собрать", hint: "pio run" },
  { value: "clean", label: "Очистить сборку", hint: "pio run -t clean" },
  { value: "code", label: "Открыть в VS Code", hint: "code <проект>" },
];

/* ── Запуск внешней команды с потоковым выводом ── */
function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, {
      cwd: opts.cwd,
      env: { ...process.env, ...(opts.env ?? {}) },
      stdio: "inherit",
    });
    child.on("error", (err) => reject(err));
    child.on("close", (code) => resolve(code));
  });
}

async function pio(project, action, variant) {
  const cwd = join(projectsRoot, project);
  const cfg = VARIANTS[project];
  const env = variant && cfg ? { PLATFORMIO_BUILD_FLAGS: `-D${cfg.flag}=${variant}` } : {};
  const args =
    action === "upload"
      ? ["run", "--target", "upload"]
      : action === "clean"
        ? ["run", "-t", "clean"]
        : ["run"];

  if (variant && cfg) {
    note(`${cfg.label}=${variant}`, "Вариант сборки");
  }
  try {
    const code = await run("pio", args, { cwd, env });
    return code === 0;
  } catch (err) {
    if (err.code === "ENOENT") {
      cancel('команда "pio" не найдена — проверьте PATH (brew install platformio)');
    } else {
      cancel(String(err));
    }
    return false;
  }
}

/* ── Неинтерактивный режим: node cli.mjs <проект> <действие> [--mode|--task N] ── */
async function cliMode(argv) {
  const [project, action = "build", ...rest] = argv;
  if (!PROJECTS.includes(project)) {
    console.error(chalk.red(`Неизвестный проект: ${project}`));
    console.error("Доступные: " + PROJECTS.join(", "));
    process.exit(1);
  }
  if (!ACTIONS.some((a) => a.value === action)) {
    console.error(chalk.red(`Неизвестное действие: ${action} (upload|build|clean|code)`));
    process.exit(1);
  }

  /* Разбор и валидация флага варианта (--mode/--task N) */
  const cfg = VARIANTS[project];
  const flagIdx = rest.findIndex((a) => a === "--mode" || a === "--task");
  let variant;
  if (flagIdx !== -1) {
    const flag = rest[flagIdx];
    variant = rest[flagIdx + 1];
    const flagName = flag.slice(2); /* mode | task */
    if (!cfg) {
      console.error(chalk.red(`У проекта ${project} нет вариантов (флаг ${flag} недопустим)`));
      process.exit(1);
    }
    if (cfg.flag.toLowerCase() !== flagName) {
      console.error(
        chalk.red(`Для ${project} используйте --${cfg.flag.toLowerCase()}, а не ${flag}`),
      );
      process.exit(1);
    }
    if (variant === undefined || !cfg.options.some((o) => o.value === variant)) {
      console.error(chalk.red(`Недопустимое значение ${flag}: ${variant ?? "(пусто)"}`));
      console.error("Допустимые: " + cfg.options.map((o) => o.value).join(", "));
      process.exit(1);
    }
  }

  let ok;
  if (action === "code") {
    try {
      ok = (await run("code", [join(projectsRoot, project)])) === 0;
    } catch (err) {
      console.error(
        chalk.red(
          err.code === "ENOENT"
            ? 'команда "code" не найдена — установите Shell Command в VS Code'
            : String(err),
        ),
      );
      ok = false;
    }
  } else {
    ok = await pio(project, action, variant);
  }
  process.exit(ok ? 0 : 1);
}

/* ── Интерактивное меню ── */
async function menuMode() {
  console.log(BANNER);
  intro(brand("Выбор лабораторной"));

  const project = await select({
    message: "Проект",
    options: PROJECTS.map((p) => ({
      value: p,
      label: p,
      hint: dim(join("platform_io_projects", p)),
    })),
  });
  if (isCancel(project)) return cancel("Отменено");

  const variantCfg = VARIANTS[project];
  let variant;
  if (variantCfg) {
    const def = variantCfg.options[project === "LR1_GPIO_LED" ? 1 : 0];
    const v = await select({
      message: variantCfg.label,
      options: variantCfg.options.map((o) => ({ ...o, hint: o.hint ? dim(o.hint) : undefined })),
      initialValue: def.value,
    });
    if (isCancel(v)) return cancel("Отменено");
    variant = v;
  }

  const action = await select({
    message: "Действие",
    options: ACTIONS.map((a) => ({ ...a, hint: dim(a.hint) })),
    initialValue: "upload",
  });
  if (isCancel(action)) return cancel("Отменено");

  if (action === "code") {
    try {
      const code = await run("code", [join(projectsRoot, project)]);
      if (code === 0) {
        outro(brand("Открыто в VS Code"));
      } else {
        outro(chalk.red("VS Code завершился с ошибкой"));
        process.exitCode = 1;
      }
    } catch (err) {
      outro(
        chalk.red(
          err.code === "ENOENT"
            ? 'команда "code" не найдена — установите Shell Command в VS Code'
            : String(err),
        ),
      );
      process.exitCode = 1;
    }
    return;
  }

  const ok = await pio(project, action, variant);
  if (ok) {
    outro(brand(action === "upload" ? "Прошито на стенд ✔" : "Сборка успешна ✔"));
  } else {
    outro(chalk.red("Ошибка — см. лог выше"));
    process.exitCode = 1;
  }

  const again = await confirm({ message: "Выполнить ещё одно действие?", initialValue: true });
  if (!isCancel(again) && again) return menuMode();
}

const argv = process.argv.slice(2);
if (argv.length > 0) {
  await cliMode(argv);
} else {
  await menuMode();
}
