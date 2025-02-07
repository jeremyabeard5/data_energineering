// src/Dashboards.js
import React, { useEffect, useRef } from 'react';

function Dashboards() {
    const ref = useRef(null);
    const viz = useRef(null);  // Reference to store the Tableau visualization instance

    useEffect(() => {
        const initViz = () => {
            const vizUrl = "https://public.tableau.com/views/evses/EVSEDashboard?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link"; // Replace this with your actual Tableau dashboard URL
            const options = {
                device: "desktop",
                hideTabs: false,
                hideToolbar: false,
                onFirstInteractive: function() {
                    console.log("The dashboard is now interactive.");
                }
            };

            // Clean up any existing visualization before creating a new one
            if (viz.current) {
                viz.current.dispose();
            }

            viz.current = new window.tableau.Viz(ref.current, vizUrl, options);
        };

        if (window.tableau) {
            initViz();
        } else {
            // If the tableau API script isn't loaded yet, retry after 100ms
            setTimeout(initViz, 100);
        }

        // Cleanup function to dispose of the visualization when the component unmounts
        return () => {
            if (viz.current) {
                viz.current.dispose();
            }
        };
    }, []);  // Ensure this effect only runs once unless specific depen
    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', margin: "20px" }}>
            <h1 style={{ position: 'absolute', top: '20px', width: '100%', textAlign: 'center' }}>Tableau Dashboards</h1>
            <div ref={ref} style={{ width: '80%', height: '700px', margin: 'auto' }}></div>
        </div>
    );

}

export default Dashboards;