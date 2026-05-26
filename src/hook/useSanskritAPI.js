/**
 * useSanskritAPI — React hook for calling the Sanskrit conjugation/declension engines.
 *
 * Works in two modes:
 *   1. **Electron**: Uses window.sanskritAPI (exposed by preload.cjs via IPC)
 *   2. **Browser fallback**: Direct HTTP to http://127.0.0.1:5199 (for Vite dev)
 *
 * Usage:
 *   const { conjugateFull, declense, loading, error } = useSanskritAPI();
 *   const paradigm = await conjugateFull({ root: "bhū", class_num: 1, ... });
 */
import { useState, useCallback, useRef, useEffect } from "react";

const API_BASE = "http://127.0.0.1:5199";

/**
 * Check whether we are running inside Electron with the preload bridge available.
 */
function hasElectronBridge() {
  return typeof window !== "undefined" && window.sanskritAPI != null;
}

/**
 * Fallback: direct HTTP POST to the Python server (for browser/Vite dev mode).
 */
async function httpPost(endpoint, body) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    throw new Error(errBody.error || `HTTP ${res.status}`);
  }
  return res.json();
}

export default function useSanskritAPI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [serverReady, setServerReady] = useState(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  // Probe the server on mount
  useEffect(() => {
    let cancelled = false;
    async function probe() {
      try {
        if (hasElectronBridge()) {
          const res = await window.sanskritAPI.health();
          if (!cancelled && res.status === "ok") setServerReady(true);
        } else {
          const res = await fetch(`${API_BASE}/api/health`);
          const json = await res.json();
          if (!cancelled && json.status === "ok") setServerReady(true);
        }
      } catch {
        // Server not ready yet — that's fine, it may still be starting
        if (!cancelled) setServerReady(false);
      }
    }
    probe();
    return () => { cancelled = true; };
  }, []);

  /**
   * Conjugate a single verb form.
   */
  const conjugate = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    try {
      const result = hasElectronBridge()
        ? await window.sanskritAPI.conjugate(params)
        : await httpPost("/api/conjugate", params);
      if (result.error) throw new Error(result.error);
      return result.forms;
    } catch (err) {
      if (mountedRef.current) setError(err.message);
      return [];
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  /**
   * Generate a full conjugation paradigm (all person×number cells).
   */
  const conjugateFull = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    try {
      const result = hasElectronBridge()
        ? await window.sanskritAPI.conjugateFull(params)
        : await httpPost("/api/conjugate/full", params);
      if (result.error) throw new Error(result.error);
      return result.paradigm;
    } catch (err) {
      if (mountedRef.current) setError(err.message);
      return {};
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  /**
   * Decline a nominal stem across all 24 case×number cells.
   */
  const declense = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    try {
      const result = hasElectronBridge()
        ? await window.sanskritAPI.declense(params)
        : await httpPost("/api/declense", params);
      if (result.error) throw new Error(result.error);
      return result.paradigm;
    } catch (err) {
      if (mountedRef.current) setError(err.message);
      return {};
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  /**
   * Generate ALL tense paradigms + kṛdantas for one derivative of a root.
   */
  const conjugateDerivative = useCallback(async (params) => {
    setLoading(true);
    setError(null);
    try {
      const result = hasElectronBridge()
        ? await window.sanskritAPI.conjugateDerivative(params)
        : await httpPost("/api/conjugate/derivative", params);
      if (result.error) throw new Error(result.error);
      return result.result;
    } catch (err) {
      if (mountedRef.current) setError(err.message);
      return null;
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  return {
    conjugate,
    conjugateFull,
    conjugateDerivative,
    declense,
    loading,
    error,
    serverReady,
    clearError: () => setError(null),
  };
}
