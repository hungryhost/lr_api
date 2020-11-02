import React, {Fragment} from 'react'
import {Helmet} from 'react-helmet'


/**
* Component-container for changing title for children-view page
* */
export const Page = ({ title, children }) => (
    <Fragment>
        <Helmet>
            <title>{title}</title>
        </Helmet>
        { children }
    </Fragment>
)
