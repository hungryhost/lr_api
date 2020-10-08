import React from 'react';
import {AxiosHandler} from 'Contexts/Axios'
import {BrowserRouter} from "react-router-dom";
import {renderRoutes, routes} from "./routes";
import AuthView from "Views/AuthView";
import {AuthProvider} from "./Contexts/JWT";


function App() {
    return (
        <BrowserRouter>
            <AxiosHandler>
                <AuthProvider>
                    {renderRoutes(routes)}
                </AuthProvider>
            </AxiosHandler>
        </BrowserRouter>
    );
}

export default App;
