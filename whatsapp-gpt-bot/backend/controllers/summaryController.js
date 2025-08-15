const { summarizeText } = require('../utils/mistralSummary');
const { getFullConversation,cleanConversation } = require('../helpers/conversationFormat');
require('../config/db');
const Message = require('../models/message');
const Summary = require('../models/summary');

//const adminNumber = 918553635971;
exports.summarizeAllConversations = async(req, res) => {
  var adminNumber = req.body.admin_number;
    if (!adminNumber) {
        console.error("❌ Please provide an admin number.");
        process.exit(1);
    }
    try {
      const customers = await Message.distinct('cx_number', {
        admin_number: adminNumber,
        ignore_flag: { $ne: 1 }
      });

    if (!customers.length) {
      console.log("⚠️  No customers found for this admin number.");
      return;
    }

    const summaries = [];

    for (const customerNumber of customers) {
      let conversationText = await getFullConversation(adminNumber, customerNumber);

      if (!conversationText || typeof conversationText !== 'string') {
        conversationText = '';
      } else {
        conversationText = conversationText.trim();
      }

      if (conversationText.length < 10) {
        summaries.push({
          customerNumber,
          summary: null,
          message: "Conversation too short to summarize"
        });
        continue;
      }
      conversationText = cleanConversation(conversationText);
      console.log(conversationText);
      if(!conversationText){
        continue;
      }
      try {
        console.log('sahu');
        console.log(conversationText);
        const summary = await summarizeText(
          conversationText,
          "Summarize this WhatsApp conversation between a customer and an agent into 3 bullet points focusing on the main issue, important details, and actions taken."
        );
        const summaryDoc = {
            customer_number:customerNumber,
            conversation:conversationText,
            summary:summary
        };
        await Summary.create(summaryDoc);
      } catch (err) {
        console.log(err.message);
      }
    }
    console.log('All message saved to mongodb');
  } catch (err) {
    console.error("❌ Error summarizing all conversations:", err.message);
    process.exit(1);
  }
}
