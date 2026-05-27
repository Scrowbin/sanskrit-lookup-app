const { spawn } = require("child_process");
const path = require("path");

function runBenchmark() {
  console.log("==================================================");
  console.log("          ELECTRON APP BOOTUP BENCHMARK           ");
  console.log("==================================================");
  console.log("\n[1] Starting Electron App in Development Mode...");

  const startTime = Date.now();
  let serverReadyTime = 0;
  let windowReadyTime = 0;

  // We run the raw electron command so we can intercept stdout
  // 'npm run electron:only' runs 'electron .'
  const electronProcess = spawn("npx", ["electron", "."], {
    cwd: path.resolve(__dirname, ".."),
    shell: process.platform === "win32", // required for npx on windows
    env: { ...process.env, ELECTRON_IS_PACKAGED: "1" }
  });

  electronProcess.stdout.on("data", (data) => {
    const text = data.toString();
    
    // We check for the API server ready message
    if (text.includes("[Electron] Python API server is ready.")) {
      serverReadyTime = Date.now() - startTime;
      console.log(` -> Backend (API & FSTs) Fully Loaded in: ${(serverReadyTime / 1000).toFixed(2)} seconds`);
      
      // Close the app gracefully after we get the metrics
      setTimeout(() => {
        console.log("\nClosing app to conclude benchmark...");
        electronProcess.kill();
      }, 1000);
    }
  });

  electronProcess.stderr.on("data", (data) => {
    // some electron warnings come through stderr, we ignore them
  });

  electronProcess.on("close", (code) => {
    console.log("==================================================");
    console.log("                   RESULTS                        ");
    console.log("==================================================");
    if (serverReadyTime > 0) {
      console.log(`Total Time to Fully Interactive: ${(serverReadyTime / 1000).toFixed(2)} seconds`);
      console.log("(This includes launching the Electron window + warming up the Pāṇinian FSTs in the background)");
    } else {
      console.log("Benchmark failed: App closed before API server was ready.");
    }
    console.log("==================================================\n");
  });
}

runBenchmark();
