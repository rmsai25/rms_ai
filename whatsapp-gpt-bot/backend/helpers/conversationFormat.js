const Message = require('../models/message');

// Configurable labels
const ROLE_LABELS = {
  customer: "Customer",
  agent: "Agent"
};

const MAX_MESSAGES_PER_CHUNK = 1000;
async function getConversationChunks(adminNumber,customerNumber) {
  const messages = await Message.find({
    admin_number: adminNumber,
    cx_number:customerNumber,
    ignore_flag: { $ne: 1 }
  }).sort({ timestamp: 1 });

  if (!messages.length) return [];

  // Format messages
  const formattedMessages = messages.map(m =>
    m.direction === 'incoming'
      ? `${ROLE_LABELS.customer}: ${m.clean_content}`
      : `${ROLE_LABELS.agent}: ${m.clean_content}`
  );

  // Chunk the conversation
const MAX_CHUNK_CHAR_LENGTH = 1000; // Safe limit for BART
function chunkMessagesByLength(messages, maxChars = MAX_CHUNK_CHAR_LENGTH) {
  const chunks = [];
  let currentChunk = '';

  for (let msg of formattedMessages) {
    if ((currentChunk + msg + '\n').length > MAX_CHUNK_CHAR_LENGTH) {
      chunks.push(currentChunk.trim());
      currentChunk = msg + '\n';
    } else {
      currentChunk += msg + '\n';
    }
  }

// Push the last remaining chunk
  if (currentChunk.trim().length > 0) {
    chunks.push(currentChunk.trim());
  }
    return chunks;
  }

  const chunks = chunkMessagesByLength(formattedMessages);
  return chunks;
}

async function getFullConversation(adminNumber, customerNumber) {
  const chunks = await getConversationChunks(adminNumber, customerNumber);
  return chunks.join('\n'); // Merge chunks into one text
}

function cleanConversation(raw) {
  return raw
    .split('\n')
    .filter(line => line.trim() && !/^Customer:\s*$/i.test(line) && !/^Agent:\s*$/i.test(line))
    .map(line => line.trim())
    .filter((line, index, self) => self.indexOf(line) === index) // remove duplicates
    .join('\n');
}

module.exports = {
  getConversationChunks,
  getFullConversation,
  cleanConversation
};
