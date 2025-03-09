const express = require("express");
const fs = require("fs");
const path = require("path");
const app = express();
const port = 3000;

// Serve static files
app.use(express.static(__dirname));

// API endpoint to scan log directories
app.get("/api/logs", (req, res) => {
    const logDir = path.join(__dirname, "log");
    
    // Check if log directory exists
    if (!fs.existsSync(logDir)) {
        return res.status(404).json({ error: "Log directory not found" });
    }
    
    try {
        const directories = fs.readdirSync(logDir, { withFileTypes: true })
            .filter(dirent => dirent.isDirectory())
            .map(dirent => dirent.name);
        
        // Get metadata for each log
        const logs = directories.map(dir => {
            const logFilePath = path.join(logDir, dir, `chat_${dir}.json`);
            
            if (fs.existsSync(logFilePath)) {
                try {
                    const fileData = JSON.parse(fs.readFileSync(logFilePath, "utf-8"));
                    return {
                        id: fileData.session_id,
                        path: `/log/${dir}/chat_${dir}.json`,
                        timestamp: fileData.timestamp,
                        participants: fileData.participants,
                        background: fileData.background?.substring(0, 100) + "...",
                        firstMessage: fileData.messages.length > 0 ? fileData.messages[0].content : "无消息"
                    };
                } catch (err) {
                    console.error(`Error parsing log file ${logFilePath}:`, err);
                    return null;
                }
            }
            return null;
        }).filter(Boolean);
        
        // Sort by timestamp, newest first
        logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        res.json(logs);
    } catch (err) {
        console.error("Error scanning log directories:", err);
        res.status(500).json({ error: "Failed to scan log directories" });
    }
});

// API endpoint to get a specific log file
app.get("/api/logs/:sessionId", (req, res) => {
    const { sessionId } = req.params;
    const logFilePath = path.join(__dirname, "log", sessionId, `chat_${sessionId}.json`);
    
    if (!fs.existsSync(logFilePath)) {
        return res.status(404).json({ error: "Log file not found" });
    }
    
    try {
        const fileData = fs.readFileSync(logFilePath, "utf-8");
        res.type("json").send(fileData);
    } catch (err) {
        console.error(`Error reading log file ${logFilePath}:`, err);
        res.status(500).json({ error: "Failed to read log file" });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});