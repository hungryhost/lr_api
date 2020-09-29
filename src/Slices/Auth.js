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

        }
    }
})

const {actions, reducer} = slice

export const login = (login, password) => async dispatch => {
    const response = await Axios.post('login');
}
