const { contextBridge, ipcRenderer } = require("electron");

/**
 * Expose the Sanskrit engine API to the renderer process via
 * window.sanskritAPI.  All calls go through Electron IPC → main process
 * → Python HTTP API, keeping the renderer fully sandboxed.
 */
contextBridge.exposeInMainWorld("sanskritAPI", {
  /**
   * Conjugate a single verb form.
   * @param {Object} params
   * @param {string} params.root       - IAST root (e.g. "bhū")
   * @param {number} params.class_num  - Gaṇa 1-10
   * @param {string} params.person     - "1" | "2" | "3"
   * @param {string} params.number     - "sg" | "du" | "pl"
   * @param {string} params.voice      - "active" | "middle" | "passive"
   * @param {string} params.tense      - tense/mood name
   * @param {string|null} params.derivative
   * @returns {Promise<{forms: string[], error: string|null}>}
   */
  conjugate: (params) => ipcRenderer.invoke("sanskrit:conjugate", params),

  /**
   * Generate a full conjugation paradigm (all 9 person×number cells).
   * @param {Object} params
   * @param {string} params.root
   * @param {number} params.class_num
   * @param {string} params.voice
   * @param {string} params.tense
   * @param {string|null} params.derivative
   * @returns {Promise<{paradigm: Object, error: string|null}>}
   */
  conjugateFull: (params) => ipcRenderer.invoke("sanskrit:conjugate-full", params),

  /**
   * Generate ALL tense paradigms + kṛdantas for one derivative of a root.
   * @param {Object} params
   * @param {string} params.root
   * @param {number} params.class_num
   * @param {string|null} params.derivative - null | "causative" | "desiderative" | "intensive"
   * @returns {Promise<{result: {tenses: Object, krdantas: string}, error: string|null}>}
   */
  conjugateDerivative: (params) => ipcRenderer.invoke("sanskrit:conjugate-derivative", params),

  /**
   * Decline a nominal stem across all 24 case×number cells.
   * @param {Object} params
   * @param {string} params.stem     - IAST stem (e.g. "rāma")
   * @param {string} params.gender   - "m" | "f" | "n"
   * @param {string} [params.stem_type="auto"]
   * @param {string} [params.r_subtype="agt"]
   * @returns {Promise<{paradigm: Object, error: string|null}>}
   */
  declense: (params) => ipcRenderer.invoke("sanskrit:declense", params),

  /**
   * Check if the Python API server is alive.
   * @returns {Promise<{status: string, error?: string}>}
   */
  health: () => ipcRenderer.invoke("sanskrit:health"),
});
