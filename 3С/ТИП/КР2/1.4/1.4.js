class User {
  constructor(username) {
    this.username = username;
  }
}

const usersTable = [new User("Анна"), new User("Борис"), new User("Виктор")];

function createUser(username, userList) {
  const newLi = document.createElement("li");
  newLi.classList.add("username");

  const user = new User(username);
  usersTable.push(user);
  newLi.textContent = user.username;

  userList.appendChild(newLi);
}

const h1 = document.createElement("h1");
h1.textContent = "Список пользователей";

const userList = document.createElement("ul");
userList.id = "userList";
usersTable.forEach((user) => {
  createUser(user.username, userList);
});

const addUserButton = document.createElement("button");
addUserButton.id = "addUserButton";
addUserButton.textContent = "Добавить нового пользователя";
addUserButton.addEventListener("click", () => {
  const username = prompt("Введите имя пользователя", "");
  createUser(username, userList);
});

document.body.appendChild(h1);
document.body.appendChild(userList);
document.body.appendChild(addUserButton);
