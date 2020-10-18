import {createSlice} from "@reduxjs/toolkit";
import Axios from "src/Contexts/Axios";

const initialAuthState = {
    isAuthenticated: false,
    isInitialised: false,
    user: null
}

const slice = createSlice({
    name: "auth",
    initialState: initialAuthState,
    reducers: {
        login(state, action) {
            state.isAuthenticated = action.payload
        }
    }
})

export const {actions, reducer} = slice

export const proceedAsAuthenticated = () => dispatch => dispatch(actions.login(true))

export const login = (login, password) => async dispatch => {
    const response = await Axios.post('auth/token/', {
        username: login,
        password,
    });
    if (response.status === 200) {
        dispatch(actions.login(true));
        const {access, refresh} = response.data
        localStorage.setItem('accessToken', access);
        localStorage.setItem('refreshToken', refresh)
        Axios.defaults.headers.common.Authorization = `Bearer ${access}`;
    }
    console.log("Log for login: ", response)
}


