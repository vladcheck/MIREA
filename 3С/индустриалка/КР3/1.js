// 3. Класс Square (Квадрат)
// Создайте класс Square с приватным свойством _side.
// Сеттер side запрещает отрицательные значения.
// Геттер area возвращает площадь квадрата: side².
// Геттер perimeter возвращает периметр: 4 * side.

class Square {
  _side;

  set side(s) {
    if (typeof s === "number" && s > 0) {
      this._side = s;
    } else {
      throw TypeError();
    }
  }

  get side() {
    return this._side;
  }

  get area() {
    return this._side * this._side;
  }

  get perimeter() {
    return this._side * 4;
  }
}
