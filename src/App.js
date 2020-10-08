import React from 'react';
import {MuiThemeProvider} from "@material-ui/core";
import {AxiosHandler} from 'Contexts/Axios'
import {BrowserRouter} from "react-router-dom";
import {renderRoutes, routes} from "./routes";
import AuthView from "Views/AuthView";
import {AuthProvider} from "Contexts/JWT";
import {theme} from "Theme/theme";
import './normalize.css'

function App() {
    return (
        <MuiThemeProvider theme={theme}>
            <BrowserRouter>
                <AxiosHandler>
                    <AuthProvider>
                        {renderRoutes(routes)}
                    </AuthProvider>
                </AxiosHandler>
            </BrowserRouter>
        </MuiThemeProvider>
    );
}

export default App;
