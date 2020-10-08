import React, {Fragment} from 'react'
import {Helmet} from 'react-helmet'

export const Page = ({ title, children }) => (
    <Fragment>
        <h1>hey from page</h1>
        <Helmet>
            <title>{title}</title>
        </Helmet>
        { children }
    </Fragment>
)
