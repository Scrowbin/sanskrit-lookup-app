import "../css/NavBar.css"
import { Link } from "react-router-dom"


function NavBar (){ 
    return <nav className="navbar">
        <div className="navbar-brand">
            <Link to ="/">Home</Link>
        </div>
        <div className="navbar-links">
            <Link to = "/LookUp" className = "nav-link">Look Up</Link>
            <Link to = "/MemorizeGame" className = "nav-link">Memorize With Game</Link>
            {/* <Link to = "/" className = "nav-link"></Link> */}
        </div>
    </nav>
}

export default NavBar