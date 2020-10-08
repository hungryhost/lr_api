import React, {Fragment} from 'react'
import {Helmet} from 'react-helmet'

export const Page = ({ title, children }) => (
    <Fragment>
        <Helmet>
            <title>{title}</title>
        </Helmet>
        { children }
    </Fragment>
)
