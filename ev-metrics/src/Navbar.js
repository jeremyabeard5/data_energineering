// src/Navbar.js
import { Link } from 'react-router-dom';

function Navbar() {
    return (
        <nav>
            <ul style={{ listStyleType: "none", display: "flex", justifyContent: "space-around" }}>
                <li><Link to="/">Home</Link></li>
                <li><Link to="/about">About</Link></li>
                <li><Link to="/dashboards">Dashboards</Link></li>
            </ul>
        </nav>
    );
}

export default Navbar;
