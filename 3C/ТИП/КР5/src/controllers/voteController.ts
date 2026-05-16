const store = require("../data/store");

// Получить все голоса
const getAllVotes = (req, res) => {
  try {
    const votes = store.getVotes();
    res.json({
      success: true,
      data: votes,
      count: votes.length,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message,
    });
  }
};

// Создать новый голос
const createVote = (req, res) => {
  try {
    const { optionId } = req.body;

    if (!optionId) {
      return res.status(400).json({
        success: false,
        message: "optionId is required",
      });
    }

    // Получаем IP адрес пользователя
    const ip = req.ip || req.connection.remoteAddress;

    const vote = store.createVote(ip, optionId);

    res.status(201).json({
      success: true,
      data: vote,
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message,
    });
  }
};

// Получить результаты голосования
const getResults = (req, res) => {
  try {
    const results = store.getResults();
    const totalVotes = results.reduce(
      (sum, result) => sum + parseInt(result.votes),
      0
    );

    res.json({
      success: true,
      totalVotes: totalVotes,
      results: results,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message,
    });
  }
};

// Сбросить все голоса
const resetVotes = (req, res) => {
  try {
    const result = store.resetVotes();
    res.json({
      success: true,
      ...result,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message,
    });
  }
};

module.exports = {
  getAllVotes,
  createVote,
  getResults,
  resetVotes,
};
