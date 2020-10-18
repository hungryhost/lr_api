import React, {Fragment} from 'react'
import {Box, Typography, TextField, Button, makeStyles, Divider, Link} from "@material-ui/core"
import {Formik} from "formik";
import * as Yup from 'yup'
import Axios from "src/Contexts/Axios";
import {useDispatch} from "react-redux";
import {login} from "src/Slices/Auth";

const useStyles = makeStyles(theme => ({
    haveMargin: {
        marginBottom: theme.spacing(4)
    }
}))

const Login = () => {
    const classes = useStyles();
    const dispatch = useDispatch();
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
                <Formik
                    initialValues={{email: 'trigognight@gmail.com', password: 'test123'}}
                    validationSchema={Yup.object().shape({
                        email: Yup.string().email().max(255).required("Введите валидный email"),
                        password: Yup.string().min(6).max(32).required("Введите пароль"),
                    })}
                    onSubmit={async (values, {setErrors}) => {
                        /*const response = await Axios.post('auth/token/', {
                            username: values.email,
                            password: values.password,
                        })
                        console.log("Response for login: ", response)*/
                        dispatch(login(values.email, values.password));

                    }}>
                    {({
                          values,
                          errors,
                          handleChange,
                          handleSubmit,
                          touched
                      }) => (
                        <Fragment>
                            <TextField
                                label='Email'
                                variant='outlined'
                                type='email'
                                name='email'
                                className={classes.haveMargin}
                                autoFocus
                                value={values.email}
                                error={Boolean(touched.email && errors.email)}
                                helperText={touched.email && errors.email}
                                onChange={handleChange}
                            />
                            <TextField
                                label='Пароль'
                                variant='outlined'
                                type='password'
                                name='password'
                                className={classes.haveMargin}
                                value={values.password}
                                error={Boolean(touched.password && errors.password)}
                                helperText={touched.password && errors.password}
                                onChange={handleChange}
                            />
                            <Button
                                variant='contained'
                                color='secondary'
                                className={classes.haveMargin}
                                fullWidth
                                size='large'
                                onClick={handleSubmit}
                            >
                                Войти
                            </Button>
                        </Fragment>
                    )}
                </Formik>
            </Box>
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
