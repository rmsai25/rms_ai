const whatsappService = require('../services/whatsappService');
const Message = require('../models/message');

exports.fetchMessagesForNumber = async (req, res) => {
  const { number } = req.params;
  try {
    const result = await whatsappService.startClientForNumber(number);
    res.status(200).json({ success: true, ...result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
};

exports.stopTrackingForNumber = async (req, res) => {
  const { number } = req.params;
  try {
    const result = whatsappService.stopTrackingNumber(number);
    res.status(200).json({ success: true, ...result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
};

exports.getIgnoreList = (req, res) => {
  res.json({ ignoreList: whatsappService.getIgnoreList() });
};

exports.addIgnoreNumbers = (req, res) => {
  const numbers = Array.isArray(req.body.numbers) ? req.body.numbers : [];
  if (numbers.length === 0) {
    return res.json({ message: 'No numbers provided to add', ignoreList: whatsappService.getIgnoreList() });
  }
  const updatedList = whatsappService.addToIgnoreList(numbers);
  res.json({ ignoreList: updatedList });
};

exports.removeIgnoreNumbers = (req, res) => {
  const numbers = Array.isArray(req.body.numbers) ? req.body.numbers : [];
  if (numbers.length === 0) {
    return res.json({ message: 'No numbers provided to remove', ignoreList: whatsappService.getIgnoreList() });
  }
  const updatedList = whatsappService.removeFromIgnoreList(numbers);
  res.json({ ignoreList: updatedList });
};

exports.getAllMessages = async (req, res) => {
  try {
    const messages = await Message.find().sort({ timestamp: -1 }); // latest first
    res.status(200).json({ success: true, count: messages.length, data: messages });
  } catch (err) {
    console.error('❌ Error fetching messages:', err.message);
    res.status(500).json({ success: false, error: err.message });
  }
};

exports.initClient = async (req, res) => {
  const { number } = req.body;
  if (!number) return res.status(400).json({ error: 'Number is required' });

  try {
    const result = await whatsappService.startClientForNumber(number);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.checkClientStatus = (req, res) => {
  const { number } = req.params;
  res.json(whatsappService.getClientStatus(number));
};