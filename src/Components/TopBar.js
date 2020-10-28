import React, {useState} from 'react'
import {Toolbar, AppBar, IconButton, makeStyles, Box, Avatar, Typography} from "@material-ui/core";
import {Menu as MenuIcon} from '@material-ui/icons'
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import {useDispatch} from "react-redux";
import {logout} from "../Slices/Auth";

const useStyles = makeStyles(theme => ({
    root: {
        display: "flex",
        backgroundColor: theme.palette.background.secondary,
        justifyContent: "space-between"
    },
    menuButton: {
        marginRight: theme.spacing(2),
    },
    title: {
        flexGrow: 1,
    },
}))


export const TopBar = () => {
    const classes = useStyles();
    const dispatch = useDispatch();
    const [isMenuOpen, toggleMenu] = useState(false);
    return (
        <AppBar position='fixed'>
            <Toolbar className={classes.root}>
                <IconButton edge="start" className={classes.menuButton} color="inherit" aria-label="menu">
                    <MenuIcon />
                </IconButton>
                <Box>
                    <Avatar onClick={() => toggleMenu(prevState => !prevState)}>
                        PL
                    </Avatar>
                    <Typography>
                        UserName template
                    </Typography>
                    <Menu
                        id="simple-menu"
                        keepMounted
                        open={isMenuOpen}
                        onClose={() => toggleMenu(false)}
                    >
                        <MenuItem>Профиль</MenuItem>
                        <MenuItem>Помещения</MenuItem>
                        <MenuItem onClick={() => dispatch(logout())}>Выйти</MenuItem>
                    </Menu>
                </Box>
            </Toolbar>
        </AppBar>
    )
}
