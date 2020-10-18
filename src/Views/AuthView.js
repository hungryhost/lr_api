import React, {useEffect} from 'react'
import {
    Container,
    makeStyles,
    Card,
    Box,
} from '@material-ui/core'
import {Page} from "src/Components/Page";

const useStyles = makeStyles(theme => ({
    container: {
        height: "90vh",
        maxHeight: '100vh',
        width: '100%',
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        paddingTop: '10vh',
        backgroundColor: theme.palette.background.primary,
    },
    content: {
        minWidth: 390,
        minHeight: 150,
        paddingTop: theme.spacing(3),
        paddingBottom: theme.spacing(3),
        paddingLeft: theme.spacing(8),
        paddingRight: theme.spacing(8),
        backgroundColor: theme.palette.background.secondary,
    },
}))


const AuthView = ({children}) => {
    const styles = useStyles()
    useEffect(() => {
        console.log("Child did mount...")
    })
    return (
        <Page title={"Авторизация"}>
            <Box className={styles.container}>
                <Card className={styles.content}>
                    {children}
                </Card>
            </Box>
        </Page>
    )
}

export default AuthView
