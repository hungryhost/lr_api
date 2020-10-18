import React from 'react'
import {Box, Typography, TextField, Button, makeStyles, Divider, Link} from "@material-ui/core"

const useStyles = makeStyles(theme => ({
    haveMargin: {
        marginBottom: theme.spacing(4)
    }
}))

const Login = () => {
    const classes = useStyles();
    return (
        <Box>
            <Typography
                color='textPrimary'
                variant="h3"
            >
                Вход
            </Typography>
            <Typography
                color='textSecondary'
                gutterBottom
                variant='subtitle2'
                style={{marginBottom: 64}}
            >
                Вход для управления своими помещениями
            </Typography>
            <Box display='flex' flexDirection='column'>
                <TextField
                    label='Email'
                    variant='outlined'
                    type='email'
                    className={classes.haveMargin}
                    autoFocus
                />
                <TextField
                    label='Пароль'
                    variant='outlined'
                    type='password'
                    className={classes.haveMargin}
                />
            </Box>
            <Button
                variant='contained'
                color='secondary'
                className={classes.haveMargin}
                fullWidth
                size='large'
            >
                Войти
            </Button>
            <Divider/>
            <Box pt={2} display="flex" justifyContent='flex-end'>
                <Link color='textSecondary' href='/register'>
                    Регистрация
                </Link>
            </Box>
        </Box>
    )
}

export default Login
