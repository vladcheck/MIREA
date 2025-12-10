const express = require("express");
const router = express.Router();
const optionController = require("../controllers/optionController");

// GET /api/options - получить все варианты
router.get("/", optionController.getAllOptions);

// GET /api/options/:id - получить вариант по ID
router.get("/:id", optionController.getOptionById);

// POST /api/options - создать новый вариант
router.post("/", optionController.createOption);

// DELETE /api/options/:id - удалить вариант
router.delete("/:id", optionController.deleteOption);

module.exports = router;
