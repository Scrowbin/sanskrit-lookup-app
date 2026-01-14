import { useNavigate } from "react-router-dom";


export default function Home() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex flex-col bg-neutral-950 text-neutral-100">
        
        {/* Top section (1/3 height) */}
        <div className="h-[20vh] flex flex-row items-center justify-center gap-20 px-20">
            <button onClick={() => navigate("/LookUp")} className="h-[10vh] w-full max-w-md py-4 text-lg font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 transition">
                Look up declension
            </button>

            <button onClick={() => navigate("/MemorizeGame")} className="h-[10vh] w-full max-w-md py-4 text-lg font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-500 transition">
                Memorize With Game
            </button>
        </div>
        <hr className="w-full border-t border-neutral-700" />

        {/* Bottom section (info) */}
        <hr className=" w-full border-t border-neutral-700 mt-auto" />

        <div className="px-16 py-8 text-sm text-neutral-300 space-y-4">
            <p>
                This app helps students explore Sanskrit declensions, word forms,
                and grammar rules quickly and offline.
            </p>

            <p>
                Built with Electron, React, and Tailwind CSS.
            </p>

            <div className="space-y-1">
                <a
                    href="https://github.com/your-repo"
                    className="text-indigo-400 hover:underline"
                >
                    GitHub Repository
                </a>
                <p>Contact: your@email.com</p>
                <p className="text-neutral-500">
                    © 2026 Sanskrit Lookup. Educational use only.
                </p>
            </div>
        </div>

        </div>
    );
}
