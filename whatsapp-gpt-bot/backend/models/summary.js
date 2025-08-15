// models/Summary.js
const mongoose = require('mongoose');

const SummarySchema = new mongoose.Schema({
  customer_number: { type: String },
  conversation:{ type: String },
  summary: { type: String },
  created_at: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Summary', SummarySchema);
