const { app, BrowserWindow, ipcMain, protocol, Menu } = require("electron");
const path = require("path");

protocol.registerSchemesAsPrivileged([
  { scheme: "app", privileges: { secure: true, standard: true, supportFetchAPI: true, corsEnabled: true } }
]);
const { spawn } = require("child_process");
const http = require("http");

let mainWindow;
let pythonServer = null;
const API_PORT = 5199;
const API_BASE = `http://127.0.0.1:${API_PORT}`;

// ── Python API Server Management ─────────────────────────────────────────────

/**
 * Resolve the command + args to start the API server.
 *
 * - **Packaged** (app.isPackaged):  Runs the frozen PyInstaller executable
 *   that was placed in extraResources during the electron-builder build.
 *   No Python installation is required on the end-user's machine.
 *
 * - **Development**:  Runs api_server.py with the conda env that has pynini.
 */
function getServerCommand() {
  if (app.isPackaged) {
    // PyInstaller output lives in resources/api_server/api_server.exe
    const exePath = path.join(process.resourcesPath, "api_server", "api_server.exe");
    return { cmd: exePath, args: ["--port", String(API_PORT)], cwd: path.dirname(exePath) };
  }

  // Dev mode — use the conda env that has pynini + flask
  const condaPython = path.join(
    process.env.USERPROFILE || "C:\\Users\\hjiis",
    "miniconda3", "envs", "sanskrit", "python.exe"
  );
  const serverScript = path.join(__dirname, "..", "logic_handler", "api_server.py");

  return {
    cmd: condaPython,
    args: [serverScript, "--port", String(API_PORT)],
    cwd: path.join(__dirname, "..", "logic_handler"),
  };
}

/**
 * Spawn the Python Flask API server as a child process.
 * The server wraps the conjugation and declension engines.
 */
function startPythonServer() {
  const { cmd, args, cwd } = getServerCommand();
  console.log(`[Python API] Spawning: ${cmd} ${args.join(" ")}`);

  pythonServer = spawn(cmd, args, {
    cwd,
    stdio: ["ignore", "pipe", "pipe"],
  });

  pythonServer.stdout.on("data", (data) => {
    console.log(`[Python API] ${data.toString().trim()}`);
  });

  pythonServer.stderr.on("data", (data) => {
    // Flask/Werkzeug writes normal access logs to stderr — not an error.
    console.log(`[Python API] ${data.toString().trim()}`);
  });

  pythonServer.on("close", (code) => {
    console.log(`[Python API] Process exited with code ${code}`);
    pythonServer = null;
  });

  pythonServer.on("error", (err) => {
    console.error(`[Python API] Failed to start: ${err.message}`);
    pythonServer = null;
  });
}

/**
 * Stop the Python server if it's running.
 */
function stopPythonServer() {
  if (pythonServer) {
    pythonServer.kill("SIGTERM");
    pythonServer = null;
  }
}

/**
 * Make an HTTP request to the Python API server.
 * Returns a Promise that resolves with the parsed JSON response.
 */
function apiRequest(endpoint, body) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify(body);
    const options = {
      hostname: "127.0.0.1",
      port: API_PORT,
      path: endpoint,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(postData),
      },
      timeout: 120000, // 2 min timeout (FST compilation can be slow on first call)
    };

    const req = http.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(new Error(`Invalid JSON from API: ${data}`));
        }
      });
    });

    req.on("error", (e) => reject(e));
    req.on("timeout", () => {
      req.destroy();
      reject(new Error("API request timed out"));
    });

    req.write(postData);
    req.end();
  });
}

/**
 * Health-check the Python API with retries (used during startup).
 */
function waitForServer(retries = 30, interval = 1000) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const check = () => {
      const req = http.get(`${API_BASE}/api/health`, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            const json = JSON.parse(data);
            if (json.status === "ok") return resolve(true);
          } catch { }
          retry();
        });
      });
      req.on("error", retry);
      req.setTimeout(2000, () => {
        req.destroy();
        retry();
      });
    };

    const retry = () => {
      attempts++;
      if (attempts >= retries) {
        return reject(new Error("Python API server did not start in time"));
      }
      setTimeout(check, interval);
    };

    check();
  });
}

// ── IPC Handlers ─────────────────────────────────────────────────────────────

// Conjugation: single cell
ipcMain.handle("sanskrit:conjugate", async (_event, params) => {
  try {
    return await apiRequest("/api/conjugate", params);
  } catch (err) {
    return { forms: [], error: err.message };
  }
});

// Conjugation: full paradigm
ipcMain.handle("sanskrit:conjugate-full", async (_event, params) => {
  try {
    return await apiRequest("/api/conjugate/full", params);
  } catch (err) {
    return { paradigm: {}, error: err.message };
  }
});

// Conjugation: all tenses for one derivative
ipcMain.handle("sanskrit:conjugate-derivative", async (_event, params) => {
  try {
    return await apiRequest("/api/conjugate/derivative", params);
  } catch (err) {
    return { result: { tenses: {}, krdantas: "" }, error: err.message };
  }
});

// Declension: full paradigm
ipcMain.handle("sanskrit:declense", async (_event, params) => {
  try {
    return await apiRequest("/api/declense", params);
  } catch (err) {
    return { paradigm: {}, error: err.message };
  }
});

// Health check
ipcMain.handle("sanskrit:health", async () => {
  try {
    return await new Promise((resolve, reject) => {
      const req = http.get(`${API_BASE}/api/health`, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch {
            reject(new Error("Bad health response"));
          }
        });
      });
      req.on("error", (e) => reject(e));
      req.setTimeout(5000, () => {
        req.destroy();
        reject(new Error("Health check timed out"));
      });
    });
  } catch (err) {
    return { status: "error", error: err.message };
  }
});

// ── Window Creation ──────────────────────────────────────────────────────────

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    show: false,

    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      devTools: !app.isPackaged,
      webSecurity: false,
      sandbox: false,
      spellcheck: false,
      backgroundThrottling: false,
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const isProd = app.isPackaged || process.env.ELECTRON_IS_PACKAGED;
  if (isProd) {
    // 🚀 FAST: load built files securely through custom app protocol
    mainWindow.loadURL("app://dist/index.html");
  } else {
    // DEV ONLY
    mainWindow.loadURL("http://localhost:5173");
  }

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });
}

// ── App Lifecycle ────────────────────────────────────────────────────────────

app.whenReady().then(async () => {
  // No File / Edit / View / Window menu in the packaged app.
  Menu.setApplicationMenu(null);

  protocol.registerFileProtocol("app", (request, callback) => {
    let url = request.url.substring(6); // strips 'app://'
    url = url.split("?")[0].split("#")[0]; // remove query strings and hashes
    callback({ path: path.normalize(`${app.getAppPath()}/${url}`) });
  });

  // 1. Start the Python API server
  startPythonServer();

  // 2. Wait for it to be ready (with retries)
  try {
    await waitForServer(30, 1000);
    console.log("[Electron] Python API server is ready.");
  } catch (err) {
    console.error("[Electron] WARNING:", err.message);
    console.error("[Electron] The app will start but API calls may fail.");
    console.error("[Electron] Make sure Python, Flask, flask-cors, and pynini are installed.");
  }

  // 3. Create the window
  createWindow();
});

// macOS behavior
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    stopPythonServer();
    app.quit();
  }
});

app.on("before-quit", () => {
  stopPythonServer();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});