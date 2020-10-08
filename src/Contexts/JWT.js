import React, {createContext, useEffect} from 'react'
import Axios from "Contexts/Axios";
import jwtDecode from 'jwt-decode'
import {useDispatch} from "react-redux";

const initialAuthState = {
    isAuthenticated: false,
    isInitialised: false,
    user: null
}

const AuthContext = createContext({
    ...initialAuthState
})

const setSession = (accessToken, refreshToken) => {
    if (accessToken && refreshToken) {
        localStorage.setItem("accessToken", accessToken);
        localStorage.setItem("refreshToken", refreshToken);
        Axios.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
    }
    else {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        delete Axios.defaults.headers.common.Authorization
    }
}

const isValidToken = async () => {
    const token = localStorage.getItem("accessToken");
    if (!token)
        return false
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp > currentTime ? true : await refreshOutdatedToken();
}

// todo: complete this one
const refreshOutdatedToken = async () => {
    return true
}

export const AuthProvider = ({children}) => {
    const dispatch = useDispatch();

    useEffect(() => {
        (async function initialize() {
            try {
                console.log("Инициализируем приложение...")
                const accessToken = localStorage.getItem('accessToken');
                if (accessToken && await isValidToken(accessToken)) {
                    // Обновляем токены на случай, если у нас в isValidToken произошло их обновление
                    const newAccessToken = localStorage.getItem('accessToken');
                    const newRefreshToken = localStorage.getItem('refreshToken');
                    setSession(newAccessToken, newRefreshToken);
                    // todo: здесь диспатчим то, что мы авторизированы
                }
                else {
                    // todo: здесь диспатчим то, что мы неавторизированы
                }
            }
            catch (e) {
                console.log("Произошла ошибка при инициализации: ", e)
                // todo: здесь диспатчим то, что мы неавторизированы
            }
        })()
    })

    return (
        <AuthContext.Provider value={null}>
            {children}
        </AuthContext.Provider>
    )
}

