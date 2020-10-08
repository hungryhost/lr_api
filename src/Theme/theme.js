import {createMuiTheme} from "@material-ui/core";
import {purple} from "@material-ui/core/colors";

export const theme = createMuiTheme({
    palette: {
        primary: {
            // Purple and green play nicely together.
            main: purple[500],
        },
        secondary: {
            // This is green.A700 as hex.
            main: '#11cb5f',
        },
        background: {
            default: "#673AB7",
        }
    },
});
