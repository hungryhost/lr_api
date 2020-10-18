import React, {Fragment} from 'react'
import {Redirect} from "react-router";
import {useSelector} from "react-redux";

/**
* This guard uses data from redux storage and makes decisions depending on
 * user auth status
* */
export const AuthGuard = ({ children }) => {
    const { isAuthenticated } = useSelector(state => state.auth);
    if (!isAuthenticated)
        return <Redirect to='/login'/>
    return (
        <Fragment>
            {children}
        </Fragment>
    )
}
