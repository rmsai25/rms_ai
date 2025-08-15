const express = require('express');
const connectDB = require('./config/db');
const routes = require('./routes'); // Auto-loads everything

const app = express();
app.use(express.json());

connectDB();
app.use(routes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
