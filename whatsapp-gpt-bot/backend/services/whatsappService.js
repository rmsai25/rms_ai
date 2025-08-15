const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const path = require('path');
const Message = require('../models/message');
const moment = require('moment-timezone');

// Store multiple clients (key = phone number)
const clients = {};
const trackedNumbers = new Set();
const ignoreList = new Set(); // numbers to ignore

/**
 * Start a WhatsApp client for a given number
 * @param {string} number - WhatsApp phone number (with country code)
 */
function startClientForNumber(number) {
  return new Promise((resolve, reject) => {
    if (clients[number]) {
      // If already started, return QR or ready status
      return resolve(getClientStatus(number));
    }
    
process.env.PUPPETEER_EXECUTABLE_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
    const authFolder = path.join(process.cwd(), '.wwebjs_auth');
    const client = new Client({
  authStrategy: new LocalAuth({
    dataPath: authFolder
  }),
  puppeteer: {
    headless: false,
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH,
    args: ['--no-sandbox']
  }
});

    clients[number] = { client, qr: null, ready: false };

    client.on('qr', async (qr) => {
      console.log(`📲 QR generated for ${number}`);
      const qrImage = await qrcode.toDataURL(qr); // Convert QR to Base64 image
      clients[number].qr = qrImage;
      resolve({ status: 'qr', qrImage });
    });

    client.on('ready', async () => {
        console.log(`✅ WhatsApp client ready for ${number}`);
        clients[number].ready = true;
        trackedNumbers.add(number);

        try {
            const chats = await client.getChats();

            for (const chat of chats) {
            // Skip group chats if you don’t want them
            if (chat.isGroup) continue;

            let cursor = null;
            let allMessagesFetched = false;

            while (!allMessagesFetched) {
                const messages = await chat.fetchMessages({
                limit: 100,
                before: cursor // fetch older messages
                });

                if (!messages || messages.length === 0) break;

                for (const msg of messages) {
                // Check if already exists in your database (based on msg.id._serialized)
                const messageId = msg.id._serialized;
                const exists = await Message.exists({ message_id: messageId });

                if (!exists) {
                    const isOutgoing = msg.fromMe;
                    await logMessage(number, msg, isOutgoing);
                }
                }

                // Set cursor to the last message in the current batch
                cursor = messages[messages.length - 1].id;

                // Stop if fewer than 100 messages returned (no more left)
                if (messages.length < 100) allMessagesFetched = true;
            }

            console.log(`📦 Fetched all messages for chat: ${chat.name || chat.id.user}`);
            }

            console.log(`✅ Completed full message sync for ${number}`);
        } catch (err) {
            console.error('❌ Error during message sync:', err.message);
        }
    });


    client.on('message', (msg) => logMessage(number, msg, false));
    client.on('message_create', (msg) => {
      if (msg.fromMe) logMessage(number, msg, true);
    });

    client.initialize();
  });
}

/**
 * Log a WhatsApp message into MongoDB
 */
exports.startTrackingNumber = (number) => {
  trackedNumbers.add(number);
  console.log(`📡 Started tracking: ${number}`);
  return { tracking: true };
};
exports.stopTrackingNumber = (number) => {
  trackedNumbers.delete(number);
  console.log(`🛑 Stopped tracking: ${number}`);
  return { tracking: false };
};

async function logMessage(number, message, isOutgoing) {
  try {
    const chat = await message.getChat();
    const fromNumber = message.from.split('@')[0].split('-')[0];
    const toNumber = (message.to || chat.id._serialized || '').split('@')[0];

    if (!trackedNumbers.has(fromNumber) && !trackedNumbers.has(toNumber)) return;

    // Check if other party is in ignore list
    const otherParty = trackedNumbers.has(fromNumber) ? toNumber : fromNumber;
    const ignoreFlag = ignoreList.size > 0 && ignoreList.has(otherParty) ? 1 : 0;

    const logEntry = {
      message_id: message.id.id,
      direction: isOutgoing ? 'outgoing' : 'incoming',
      admin_number: isOutgoing ? fromNumber : toNumber,
      cx_number: isOutgoing ? toNumber : fromNumber,
      content: message.body,
      clean_content:cleanMessageContent(message.body),
      timestamp: new Date(message.timestamp * 1000),
      media: message.hasMedia,
      device: message.deviceType,
      issent: message.ack >= 1,
      isread: message.ack === 3,
      ignore_flag: ignoreFlag
    };

    const exists = await Message.findOne({ message_id: logEntry.message_id });
    if (!exists) {
      await Message.create(logEntry);
      console.log(
        `📥 Message saved for ${number} (ignore_flag=${ignoreFlag}) at ${moment(logEntry.timestamp)
          .tz('Asia/Kolkata')
          .format('YYYY-MM-DD HH:mm:ss')} IST`
      );
    }
  } catch (err) {
    console.error('❌ Error logging message:', err.message);
  }
}

/**
 * Get current client status
 */
function getClientStatus(number) {
  if (!clients[number]) return { status: 'not_started' };
  if (clients[number].ready) return { status: 'ready' };
  return { status: 'qr', qrImage: clients[number].qr };
}

/**
 * Manage ignore list
 */
function addToIgnoreList(numbers) {
  numbers.forEach((n) => ignoreList.add(n));
  return Array.from(ignoreList);
}

function removeFromIgnoreList(numbers) {
  numbers.forEach((n) => ignoreList.delete(n));
  return Array.from(ignoreList);
}

function getIgnoreList() {
  return Array.from(ignoreList);
}

function cleanMessageContent(text) {
  if (!text || typeof text !== 'string') return '';

  return text
    // 1. Remove "media omitted" (case-insensitive)
    .replace(/\[?media omitted\]?/gi, '')

    // 2. Remove emojis & other pictographs (keep text & links)
    .replace(
      /([\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|\uD83E[\uDD00-\uDDFF])/g,
      ''
    )

    // 3. Remove control characters (non-printable)
    .replace(/[\x00-\x1F\x7F-\x9F]/g, '')

    // 4. Replace multiple spaces/newlines with single space
    .replace(/\s+/g, ' ')

    // 5. Trim spaces at start/end
    .trim();
}

module.exports = {
  startClientForNumber,
  getClientStatus,
  addToIgnoreList,
  removeFromIgnoreList,
  getIgnoreList
};
