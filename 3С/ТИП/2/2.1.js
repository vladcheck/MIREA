const n = prompt("Число");
console.log(n < 0 ? "Отрицательное" : n > 0 ? "Положительное" : "Ноль");

const n1 = prompt("Число");
console.log(n % 2 === 0 ? "Четное" : "Нечетное");

const a = +prompt("a"),
  b = +prompt("b");
console.log(a % b === 0 ? "Делится" : "Не делится");

const sign = prompt("sign", "+");
const x = +prompt("x"),
  y = +prompt("y");
let res;
switch (sign) {
  case "+":
    res = x + y;
    break;
  case "-":
    res = x - y;
    break;
  case "*":
    res = x * y;
    break;
  case "/":
    res = x / y;
    break;
}
console.log(`${x}${sign}${y} = ${res}`);
