import React, {Fragment} from 'react'
import axios from 'axios'
import {BASE_URL} from "src/config";
import {useHistory} from "react-router";

const  AxiosInstance = axios.create({
    baseURL: BASE_URL
})


export const AxiosHandler = ({ children }) => {
    const history = useHistory();
    AxiosInstance.interceptors.response.use(response => response, async request => {
        // todo: make error handler for requests
    })
    return (
        <Fragment>
            {children}
        </Fragment>
    )
}

export default AxiosInstance
