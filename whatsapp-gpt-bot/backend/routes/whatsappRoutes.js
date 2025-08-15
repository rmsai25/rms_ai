const express = require('express');
const router = express.Router();
const whatsappController = require('../controllers/whatsappController');

router.get('/api/whatsapp/fetch/:number', whatsappController.fetchMessagesForNumber);
router.get('/api/whatsapp/stop/:number', whatsappController.stopTrackingForNumber);
router.get('/api/whatsapp/ignore', whatsappController.getIgnoreList);
router.post('/api/whatsapp/ignore/add', whatsappController.addIgnoreNumbers);
router.post('/api/whatsapp/ignore/remove', whatsappController.removeIgnoreNumbers);
router.get('/api/whatsapp/messages', whatsappController.getAllMessages);
router.post('/api/whatsapp/init', whatsappController.initClient);
router.get('/api/whatsapp/status/:number', whatsappController.checkClientStatus);

module.exports = router;
