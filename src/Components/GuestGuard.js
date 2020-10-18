import React, {Fragment} from 'react'
import {Redirect} from "react-router";
import {useSelector} from "react-redux";

/**
 * This guard uses data from redux storage and makes decisions depending on
 * user auth status
 * */
export const GuestGuard = ({ children }) => {
    const { isAuthenticated } = useSelector(state => state.auth);
    if (isAuthenticated)
        return <Redirect to='/app'/>
    return (
        <Fragment>
            {children}
        </Fragment>
    )
}
