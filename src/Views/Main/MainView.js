import React from 'react'
import {Box, Container, makeStyles} from "@material-ui/core";
import {TopBar} from "src/Components/TopBar";
import {NavBar} from "./NavBar";


const useStyles = makeStyles(theme => ({
    container: {
        display: "flex",
        paddingTop: 64,
        paddingLeft: 256
    },
    root: {
        display: 'flex',
        height: '100%',
        overflow: 'hidden',
        width: '100%',
    },
}))

export const MainView = ({ children }) => {
    const classes = useStyles()
    return (
        <Box className={classes.root}>
            <TopBar/>
            <NavBar/>
            <Box className={classes.container}>
                { children }
                Hello
            </Box>
        </Box>
    )
}
