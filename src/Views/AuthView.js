import React from 'react'
import {
    Container,
    makeStyles,
    Card
} from '@material-ui/core'
import {Page} from "Components/Page";

const useStyles = makeStyles(theme => ({
    container: {
        height: "100vh",
        width: '100%',
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
    },
    content: {
        border: '1px solid red'
    }
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
