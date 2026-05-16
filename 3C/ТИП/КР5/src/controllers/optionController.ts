const store = require("../data/store");

// Получить все варианты
const getAllOptions = (req, res) => {
  try {
    const options = store.getOptions();
    res.json({
      success: true,
      data: options,
      count: options.length,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message,
    });
  }
};

// Получить вариант по ID
const getOptionById = (req, res) => {
  try {
    const { id } = req.params;
    const option = store.getOptionById(id);

    if (!option) {
      return res.status(404).json({
        success: false,
        message: "Option not found",
      });
    }

    res.json({
      success: true,
      data: option,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message,
    });
  }
};

// Создать новый вариант
const createOption = (req, res) => {
  try {
    const { text } = req.body;

    if (!text || text.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: "Text is required and cannot be empty",
      });
    }

    if (text.trim().length > 100) {
      return res.status(400).json({
        success: false,
        message: "Text cannot be longer than 100 characters",
      });
    }

    const option = store.createOption(text);

    res.status(201).json({
      success: true,
      data: option,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message,
    });
  }
};

// Удалить вариант
const deleteOption = (req, res) => {
  try {
    const { id } = req.params;
    const deletedOption = store.deleteOption(id);

    if (!deletedOption) {
      return res.status(404).json({
        success: false,
        message: "Option not found",
      });
    }

    res.json({
      success: true,
      message: "Option deleted successfully",
      data: deletedOption,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message,
    });
  }
};

module.exports = {
  getAllOptions,
  getOptionById,
  createOption,
  deleteOption,
};
