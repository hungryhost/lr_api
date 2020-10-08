import React, {Fragment} from 'react'
import {Redirect} from "react-router";
import {useSelector} from "react-redux";


export const AuthGuard = ({ children }) => {
    const { isAuthenticated } = useSelector(state => state.auth);
    if (!isAuthenticated)
        return <Redirect to='/'/>
    return (
        <Fragment>
            {children}
        </Fragment>
    )
}
