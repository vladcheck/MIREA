document.addEventListener("DOMContentLoaded", () => {
  // DOM элементы
  const optionsContainer = document.getElementById("options-container");
  const resultsContainer = document.getElementById("results-container");
  const chartContainer = document.getElementById("chart-container");
  const totalVotesElement = document.getElementById("total-votes");
  const resetButton = document.getElementById("reset-button");
  const newOptionInput = document.getElementById("new-option");
  const addOptionButton = document.getElementById("add-option");
  const adminOptionsList = document.getElementById("admin-options-list");

  // Загрузка данных при старте
  loadOptions();
  loadResults();

  // Обработчики событий
  resetButton.addEventListener("click", resetVotes);
  addOptionButton.addEventListener("click", addOption);
  newOptionInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") addOption();
  });

  // Функция для показа уведомления
  function showNotification(message, type = "success") {
    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.classList.add("show");
    }, 100);

    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }

  // Загрузка вариантов для голосования
  async function loadOptions() {
    try {
      const response = await fetch("/api/options");
      const data = await response.json();

      if (data.success) {
        optionsContainer.innerHTML = "";

        if (data.data.length === 0) {
          optionsContainer.innerHTML =
            '<p class="no-options">Нет доступных вариантов для голосования</p>';
          return;
        }

        data.data.forEach((option) => {
          const optionElement = document.createElement("div");
          optionElement.className = "option-card";
          optionElement.innerHTML = `
            <h3>Вариант ${option.id}</h3>
            <div class="option-text">${option.text}</div>
          `;

          optionElement.addEventListener("click", () =>
            voteForOption(option.id)
          );

          optionsContainer.appendChild(optionElement);
        });
      }
    } catch (error) {
      console.error("Error loading options:", error);
      showNotification("Ошибка загрузки вариантов", "error");
    }
  }

  // Голосование за вариант
  async function voteForOption(optionId) {
    try {
      const response = await fetch("/api/votes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ optionId }),
      });

      const data = await response.json();

      if (data.success) {
        showNotification("Ваш голос успешно учтен!");
        loadResults();

        // Визуальная обратная связь
        const selectedCard = document.querySelector(
          `.option-card:nth-child(${optionId})`
        );
        if (selectedCard) {
          selectedCard.classList.add("selected");
          setTimeout(() => {
            selectedCard.classList.remove("selected");
          }, 1000);
        }
      } else {
        throw new Error(data.message || "Ошибка голосования");
      }
    } catch (error) {
      console.error("Error voting:", error);
      showNotification(error.message, "error");
    }
  }

  // Загрузка результатов голосования
  async function loadResults() {
    try {
      const response = await fetch("/api/votes/results");
      const data = await response.json();

      if (data.success) {
        totalVotesElement.textContent = data.totalVotes;

        if (data.totalVotes === 0) {
          chartContainer.innerHTML =
            '<p class="no-results">Пока нет голосов</p>';
          return;
        }

        renderChart(data.results);
      }
    } catch (error) {
      console.error("Error loading results:", error);
      showNotification("Ошибка загрузки результатов", "error");
    }
  }

  // Рендеринг графика результатов
  function renderChart(results) {
    chartContainer.innerHTML = "";

    results.forEach((result) => {
      const percentage = parseFloat(result.percentage);

      const barElement = document.createElement("div");
      barElement.className = "result-bar";
      barElement.innerHTML = `
        <div class="label">Вариант ${result.id}</div>
        <div class="bar-container">
          <div class="bar-fill" style="width: ${percentage}%"></div>
        </div>
        <div class="bar-info">${result.votes} (${result.percentage}%)</div>
      `;

      chartContainer.appendChild(barElement);
    });
  }

  // Сброс голосов
  async function resetVotes() {
    if (
      !confirm(
        "Вы уверены, что хотите сбросить все голоса? Это действие нельзя отменить."
      )
    ) {
      return;
    }

    try {
      const response = await fetch("/api/votes/reset", {
        method: "POST",
      });

      const data = await response.json();

      if (data.success) {
        showNotification("Все голоса успешно сброшены");
        loadResults();
      } else {
        throw new Error(data.message || "Ошибка сброса голосов");
      }
    } catch (error) {
      console.error("Error resetting votes:", error);
      showNotification(error.message, "error");
    }
  }

  // Добавление нового варианта
  async function addOption() {
    const text = newOptionInput.value.trim();

    if (!text) {
      showNotification("Введите текст варианта", "error");
      return;
    }

    if (text.length > 100) {
      showNotification("Текст не может быть длиннее 100 символов", "error");
      return;
    }

    try {
      const response = await fetch("/api/options", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();

      if (data.success) {
        showNotification("Вариант успешно добавлен");
        newOptionInput.value = "";
        loadOptions();
        loadAdminOptions();
      } else {
        throw new Error(data.message || "Ошибка добавления варианта");
      }
    } catch (error) {
      console.error("Error adding option:", error);
      showNotification(error.message, "error");
    }
  }

  // Загрузка вариантов для администрирования
  async function loadAdminOptions() {
    try {
      const response = await fetch("/api/options");
      const data = await response.json();

      if (data.success) {
        adminOptionsList.innerHTML = "";

        if (data.data.length === 0) {
          adminOptionsList.innerHTML = "<p>Нет вариантов для управления</p>";
          return;
        }

        data.data.forEach((option) => {
          const optionElement = document.createElement("div");
          optionElement.className = "admin-option";
          optionElement.innerHTML = `
            <span>Вариант ${option.id}: ${option.text}</span>
            <button class="delete-option" data-id="${option.id}">×</button>
          `;

          adminOptionsList.appendChild(optionElement);
        });

        // Добавляем обработчики для кнопок удаления
        document.querySelectorAll(".delete-option").forEach((button) => {
          button.addEventListener("click", function () {
            const optionId = this.getAttribute("data-id");
            deleteOption(optionId);
          });
        });
      }
    } catch (error) {
      console.error("Error loading admin options:", error);
    }
  }

  // Удаление варианта
  async function deleteOption(optionId) {
    if (
      !confirm(
        `Вы уверены, что хотите удалить вариант ${optionId}? Все голоса за этот вариант будут удалены.`
      )
    ) {
      return;
    }

    try {
      const response = await fetch(`/api/options/${optionId}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (data.success) {
        showNotification("Вариант успешно удален");
        loadOptions();
        loadResults();
        loadAdminOptions();
      } else {
        throw new Error(data.message || "Ошибка удаления варианта");
      }
    } catch (error) {
      console.error("Error deleting option:", error);
      showNotification(error.message, "error");
    }
  }

  // Инициализация административного раздела
  loadAdminOptions();
});
