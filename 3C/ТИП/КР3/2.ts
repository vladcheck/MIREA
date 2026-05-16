// 27. Двойная обработка
// Напишите функцию doubleProcess(a, b, cb1, cb2), которая сначала
// вызывает cb1(a, b), а потом результат передаёт в cb2.

function doubleProcess(a, b, cb1, cb2) {
  cb2(cb1(a, b));
}
