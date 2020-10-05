import React, {createContext, useEffect} from 'react'
import { Redirect, useHistory } from "react-router";
import Axios from "src/Contexts/Axios";
import jwtDecode from 'jwt-decode'
import {useDispatch, useSelector} from "react-redux";

const initialAuthState = {
    isAuthenticated: false,
    isInitialised: false,
    user: null
}

const AuthContext = createContext({
    ...initialAuthState
})

export const AuthProvider = ({children}) => {
    /*
    * todo: FILL value
    * */

    const login = (email, password) => {

    }

    const logout = () => {

    }

    const isTokenValid = () => {

    }


    useEffect(() => {

    })
    return (
        <AuthContext.Provider value={null}>
            {children}
        </AuthContext.Provider>
    )
}

