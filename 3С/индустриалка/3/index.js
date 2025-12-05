if (prompt && alert) {
  const print = console.log; // Для себя

  // 1
  let a = 2 * (3 - 1);
  let b = 6 - 2;
  print(a === b);

  // 2
  let n = prompt("(2) Число");

  if (n.match(/[0-9]+\.?[0-9]*/)) {
    n = parseFloat(n);
    if (n > 0) alert(1);
    else if (n < 0) alert(-1);
    else alert(0);
  }

  // 3
  let word = prompt("(3) Любое слово");
  if (word.length % 2 === 1) {
    print(word[Math.floor(word.length / 2)]);
  } else {
    print(word[word.length / 2], word[word.length / 2 + 1]);
  }

  // 4
  let [a1, b1] = [2, 5];
  let result;
  result = a1 + b1 < 4 ? "Мало" : "Много";

  // 5
  let login = prompt("(5) Логин").toLowerCase();
  let message =
    login === "сотрудник"
      ? "Привет"
      : login === "директор"
      ? "Здравствуйте"
      : login === ""
      ? "Нет логина"
      : "";
  print(message);

  // 6
  let login1 = prompt("(6) Логин");

  if (login1.toLowerCase() === "админ") {
    let password = prompt("Пароль");

    if (password === "Я главный") {
      print("Здравствуйте!");
    } else if (password.length) {
      print("Неверный пароль");
    } else {
      print("Ничего не введено");
    }
  } else if (!login1.length) {
    print("Ничего не введено");
  } else {
    print("Я вас не знаю");
  }

  // 7
  const n1 = parseInt("(7) Число?");
  if (
    (n1 % 2 === 0 && n <= 99 && n >= 10) ||
    (n1 % 2 === 1 && n >= 100 && n <= 999)
  ) {
    print("YES");
  } else {
    print("NO");
  }

  // 8
  const year = parseInt("(8) Год?");
  if (year % 4 === 0 || (year % 100 === 0 && year % 400 === 0)) {
    print("YES");
  } else {
    print("NO");
  }

  // 9
  for (let i = 1; i <= 100; i++) {
    print("(9)", i);
  }

  // 10
  for (let i = 3; i <= 100; i += 3) {
    print("(10)", i);
  }

  // 11
  const array = [];
  for (let i = 1; i <= 100; i++) {
    array.push(i);
  }
  print(array.reduce((n, acc) => n + acc, 0));

  // 12
  const str = prompt("(12) Строка?");
  for (let char of str) {
    print(char);
  }

  // 13
  const upper = prompt("(13) Слово?");
  print(upper.split("").join(" "));

  // 14
  const phrase = prompt("(14) Фраза?").toLowerCase();
  let isPantagram = true; // предположение

  for (let char of "qwertyuiopasdfghjklzxcvbnm") {
    if (!phrase.includes(char)) {
      isPantagram = false;
      break;
    }
  }
  print(isPantagram ? "yes" : "no");
}
