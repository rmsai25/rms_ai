const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema({
  message_id: { type: String, required: true },
  direction: { type: String, enum: ['incoming', 'outgoing'], required: true },
  admin_number: { type: String, required: true },
  cx_number: { type: String, required: true },
  content: { type: String },
  clean_content: { type: String },
  timestamp: { type: Date, default: Date.now },      // nullable
  media: { type: Boolean, default: false },
  device: { type: String },                         // e.g., "web", "android", "ios"
  issent: { type: Boolean, default: false },
  isread: { type: Boolean, default: false }
});

module.exports = mongoose.model('Message', messageSchema);
