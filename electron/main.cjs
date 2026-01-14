const { app, BrowserWindow } = require("electron");
const path = require("path");

let mainWindow;


function createWindow() {
  mainWindow = new BrowserWindow({    
    width: 1000,
    height: 800,
    show: false,

    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      devTools: !app.isPackaged, // 👈 dev only
      sandbox: false,
      spellcheck: false,
      backgroundThrottling: false,
    },
  });

  if (app.isPackaged) {
    // 🚀 FAST: load built files
    mainWindow.loadFile(path.join(__dirname, "dist/index.html"));
  } else {
    // DEV ONLY
    mainWindow.loadURL("http://localhost:5173");
  }

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });
}

app.whenReady().then(createWindow);
// macOS behavior
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});