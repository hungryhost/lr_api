import React from 'react'
import {
    Container,
    makeStyles,
    Card,
    Box,
} from '@material-ui/core'
import {Page} from "Components/Page";

const useStyles = makeStyles(theme => ({
    container: {
        height: "100vh",
        maxHeight: '100vh',
        width: '100%',
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        paddingTop: '30vh'
    },
    content: {
        minWidth: 350,
        minHeight: 150,
        padding: theme.spacing(2),
        backgroundColor: theme.palette.background.default
    },
}))


const AuthView = ({children}) => {
    const styles = useStyles()
    return (
        <Page title={"Авторизация"}>
            <Container className={styles.container}>
                <Card className={styles.content}>
                    {children}
                </Card>
            </Container>
        </Page>
    )
}

export default AuthView
