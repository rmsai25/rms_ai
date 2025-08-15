const express = require('express');
const router = express.Router();
const { summarizeAllConversations } = require('../controllers/summaryController');

router.get('/api/whatsapp/summarizeAllConversations', summarizeAllConversations);
module.exports = router;
