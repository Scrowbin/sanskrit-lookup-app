import {Routes, Route} from "react-router-dom"
import Home from "./pages/Home"
import LookUp from "./pages/LookUp"
import MemorizeGame from "./pages/MemorizeGame"
import NavBar from "./components/NavBar"

export default function SanskritVibeApp() {
  return (
    <div>
        <NavBar />
        <main className=''>
            <Routes>
                <Route path='/' element = {<Home/>}/>
                <Route path='/LookUp' element = {<LookUp/>}/>
                <Route path='/MemorizeGame' element = {<MemorizeGame/>}/>
            </Routes>
        </main>
    </div>
      
    )
}

/*
Notes / next steps you can perform locally:
- Expand DATA with more nouns/verbs and full declension tables.
- Add transliteration normalization for user input (IAST vs. diacritics stripping).
- Add audio or stroke animations for script learning.
- To enable PWA installability, add a manifest.json and a small service worker that caches this bundle and assets.
*/