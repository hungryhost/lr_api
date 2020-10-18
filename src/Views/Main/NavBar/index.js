import React from 'react'
import {
    Drawer,
    Box,
    Typography,
    List,
    ListSubheader,
    ListItem,
    ListItemText,
    ListItemSecondaryAction,
    makeStyles,
    Avatar
} from "@material-ui/core";
import {useDispatch, useSelector} from "react-redux";

const useStyles = makeStyles(theme => ({
    container: {
        width: 256,
        height: 'calc(100vh - 64px)',
        maxHeight: 'calc(100vh - 64px)',
        paddingTop: 64
    }
}))

export const NavBar = () => {
    const {isNavBarOpen} = useSelector(store => store.layout);
    const classes = useStyles();
    return (
        <Drawer
            anchor='left'
            variant='persistent'
            open={isNavBarOpen}
            className={classes.container}
        >

        </Drawer>
    )
}
