import React, {Fragment} from 'react'
import {Box, Typography, TextField, Button, makeStyles, Divider, Link} from "@material-ui/core"
import {Formik} from "formik";
import * as Yup from 'yup';
import Axios from "src/Contexts/Axios";
import {parseName} from "../../../Utils/auth";
import {useDispatch} from "react-redux";
import {proceedAsAuthenticated} from "../../../Slices/Auth";

const useStyles = makeStyles(theme => ({
    haveMargin: {
        marginBottom: theme.spacing(4)
    }
}))


const Register = () => {
    const classes = useStyles();
    const dispatch = useDispatch();
    return (
        <Box>
            <Typography
                color='textPrimary'
                variant="h3"
            >
                Регистрация
            </Typography>
            <Typography
                color='textSecondary'
                gutterBottom
                variant='subtitle2'
                style={{marginBottom: 64}}
            >
                Зарегистрироваться и начать работать с помещениями
            </Typography>
            <Box display='flex' flexDirection='column'>
                <Formik
                    initialValues={{
                        email: "trigognight@gmail.com",
                        password: "test123",
                        passwordConfirm: "test123",
                        name: "Pavel Lapshin"
                    }}
                    onSubmit={async (values, {setErrors}) => {
                        const {first_name, last_name} = parseName(values.name);
                        if (values.password !== values.passwordConfirm)
                            setErrors({passwordConfirm: "Пароли не совпадают"})
                        else {
                            const response = await Axios.post('auth/register/', {
                                first_name,
                                last_name,
                                email: values.email,
                                password: values.password,
                                password2: values.passwordConfirm
                            })
                            dispatch(proceedAsAuthenticated())
                            console.log("Response object: ", response)
                        }
                    }}
                    validationSchema={Yup.object().shape({
                        email: Yup.string().email().max(255).required("Введите валидный email"),
                        password: Yup.string().min(6).max(32).required("Введите пароль"),
                        passwordConfirm: Yup.string().min(6).max(32).required("Введите пароль"),
                        name: Yup.string().max(256).required("Имя не должно быть пустым")
                    })}
                >
                    {({
                          values,
                          errors,
                          handleChange,
                          handleSubmit,
                          touched
                      }) => (
                        <Fragment>
                            <TextField
                                label='Имя и фамилия'
                                variant='outlined'
                                name='name'
                                error={Boolean(touched.name && errors.name)}
                                helperText={touched.name && errors.name}
                                className={classes.haveMargin}
                                value={values.name}
                                onChange={handleChange}
                                autoFocus
                            />
                            <TextField
                                label='Email'
                                variant='outlined'
                                type='email'
                                name='email'
                                error={Boolean(touched.email && errors.email)}
                                helperText={touched.email && errors.email}
                                className={classes.haveMargin}
                                value={values.email}
                                onChange={handleChange}
                            />
                            <TextField
                                label='Пароль'
                                variant='outlined'
                                type='password'
                                name='password'
                                error={Boolean(touched.password && errors.password)}
                                helperText={touched.password && errors.password}
                                className={classes.haveMargin}
                                value={values.password}
                                onChange={handleChange}
                            />
                            <TextField
                                label='Подтверждение пароля'
                                variant='outlined'
                                type='password'
                                name='passwordConfirm'
                                error={Boolean(touched.passwordConfirm && errors.passwordConfirm)}
                                helperText={touched.passwordConfirm && errors.passwordConfirm}
                                className={classes.haveMargin}
                                value={values.passwordConfirm}
                                onChange={handleChange}
                            />
                            <Button
                                variant='contained'
                                color='secondary'
                                className={classes.haveMargin}
                                fullWidth
                                size='large'
                                type="submit"
                                onClick={handleSubmit}
                            >
                                Зарегистрироваться
                            </Button>
                        </Fragment>
                    )}
                </Formik>
            </Box>
            <Divider/>
            <Box pt={2} display="flex" justifyContent='flex-end'>
                <Link color='textSecondary' href='/login'>
                    Войти
                </Link>
            </Box>
        </Box>
    )
}

export default Register
