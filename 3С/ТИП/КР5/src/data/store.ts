// Простое хранилище данных в памяти
// В реальном приложении здесь была бы база данных

class DataStore {
  constructor() {
    this.options = [
      { id: 1, text: "Вариант 1", votes: 0 },
      { id: 2, text: "Вариант 2", votes: 0 },
      { id: 3, text: "Вариант 3", votes: 0 },
    ];
    this.votes = [];
    this.nextOptionId = 4;
    this.nextVoteId = 1;
  }

  // Получить все варианты
  getOptions() {
    return [...this.options];
  }

  // Получить вариант по ID
  getOptionById(id) {
    return this.options.find((option) => option.id === parseInt(id));
  }

  // Создать новый вариант
  createOption(text) {
    const newOption = {
      id: this.nextOptionId++,
      text: text.trim(),
      votes: 0,
    };
    this.options.push(newOption);
    return newOption;
  }

  // Удалить вариант
  deleteOption(id) {
    const optionIndex = this.options.findIndex(
      (option) => option.id === parseInt(id)
    );
    if (optionIndex !== -1) {
      const deletedOption = this.options[optionIndex];
      this.options.splice(optionIndex, 1);
      // Удаляем все голоса за этот вариант
      this.votes = this.votes.filter((vote) => vote.optionId !== parseInt(id));
      return deletedOption;
    }
    return null;
  }

  // Получить все голоса
  getVotes() {
    return [...this.votes];
  }

  // Создать новый голос
  createVote(ip, optionId) {
    const option = this.getOptionById(optionId);
    if (!option) {
      throw new Error("Option not found");
    }

    // Проверяем, не голосовал ли уже этот IP за этот вариант
    const existingVote = this.votes.find(
      (vote) => vote.ip === ip && vote.optionId === parseInt(optionId)
    );

    if (existingVote) {
      throw new Error("IP already voted for this option");
    }

    const newVote = {
      id: this.nextVoteId++,
      ip: ip,
      optionId: parseInt(optionId),
      timestamp: new Date().toISOString(),
    };

    this.votes.push(newVote);

    // Увеличиваем счетчик голосов для варианта
    option.votes++;

    return newVote;
  }

  // Получить результаты голосования
  getResults() {
    return this.options
      .map((option) => ({
        id: option.id,
        text: option.text,
        votes: option.votes,
        percentage:
          this.options.reduce((total, opt) => total + opt.votes, 0) > 0
            ? (
                (option.votes /
                  this.options.reduce((total, opt) => total + opt.votes, 0)) *
                100
              ).toFixed(1)
            : "0.0",
      }))
      .sort((a, b) => b.votes - a.votes);
  }

  // Сбросить все голоса
  resetVotes() {
    this.votes = [];
    this.options.forEach((option) => {
      option.votes = 0;
    });
    this.nextVoteId = 1;
    return { success: true, message: "All votes have been reset" };
  }
}

// Экспортируем singleton экземпляр
module.exports = new DataStore();
