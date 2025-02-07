// src/Home.js
import React from 'react';

function Home() {
    return (
        <div>
            <div style={{ height: "300px", background: "lightblue", display: "flex", justifyContent: "center", alignItems: "center", fontSize: "24px" }}>
                Welcome to Our Site!
            </div>
            <div style={{ display: "flex", margin: "20px" }}>
                <div style={{ flex: 1, marginRight: "10px" }}>
                    <img src="https://via.placeholder.com/400" alt="Example" style={{ width: "100%" }} />
                </div>
                <div style={{ flex: 2 }}>
                    <p>
                        This is an example paragraph. Here, you can describe something about your site or service.
                        This section can contain additional details and information that you want visitors to know about.
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Home;
