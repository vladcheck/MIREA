const express = require("express");
const router = express.Router();
const voteController = require("../controllers/voteController");

// GET /api/votes - получить все голоса
router.get("/", voteController.getAllVotes);

// GET /api/votes/results - получить результаты голосования
router.get("/results", voteController.getResults);

// POST /api/votes - создать новый голос
router.post("/", voteController.createVote);

// POST /api/votes/reset - сбросить все голоса (только для тестирования)
router.post("/reset", voteController.resetVotes);

module.exports = router;
