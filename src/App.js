import React from 'react';
import {MuiThemeProvider} from "@material-ui/core";
import {AxiosHandler} from 'src/Contexts/Axios'
import {BrowserRouter} from "react-router-dom";
import {renderRoutes, routes} from "src/routes";
import AuthView from "src/Views/Auth/AuthView";
import {Initialisation} from "src/Contexts/JWT";
import {theme} from "src/Theme/theme";
import 'src/normalize.css'

function App() {
    return (
        <MuiThemeProvider theme={theme}>
            <BrowserRouter>
                <AxiosHandler>
                    <Initialisation>
                        {renderRoutes(routes)}
                    </Initialisation>
                </AxiosHandler>
            </BrowserRouter>
        </MuiThemeProvider>
    );
}

export default App;
