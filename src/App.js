import React from 'react';
import {AxiosHandler} from 'Contexts/Axios'
import {BrowserRouter} from "react-router-dom";


function App() {
    return (
        <div>
            <BrowserRouter>
                <AxiosHandler>

                </AxiosHandler>
            </BrowserRouter>
        </div>
    );
}

export default App;
