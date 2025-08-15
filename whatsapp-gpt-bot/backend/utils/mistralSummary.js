const axios = require('axios');
require('dotenv').config();

// Use actual Hugging Face API key with proper permission
const HF_API_KEY = process.env.HF_API_KEY;
console.log('test');
console.log(HF_API_KEY);
const MODEL = "facebook/bart-large-cnn";

async function summarizeText(text, instruction) {
  console.log('pks');
  console.log(text);
  if (!HF_API_KEY) {
    throw new Error("Hugging Face API key is missing in environment variables");
  }

  if (!text || typeof text !== 'string') {
    throw new Error("Invalid input text for summarization");
  }

  try {
    const response = await axios.post(
      `https://api-inference.huggingface.co/models/${MODEL}`,
      { inputs: text },
      {
        headers: {
          Authorization: `Bearer ${HF_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    // ✅ For BART, Hugging Face returns: { summary_text: "..." }
    if (Array.isArray(response.data) && response.data[0]?.summary_text) {
        return response.data[0].summary_text.trim();
    }

    return '';
  } catch (err) {
    console.error("❌ Hugging Face API error:", err.response?.data || err.message);
    throw new Error("Failed to summarize text");
  }
}

module.exports = { summarizeText };
