import React from 'react'
import {Box, Typography} from "@material-ui/core"



const Login = () => {
    return (
        <Box>
            <Typography
                color='textPrimary'
                gutterBottom
                variant="h2"
            >
                Sign in
            </Typography>
            <Typography
                variant="body2"
                color="textSecondary"
            >
                Sign in on the internal platform
            </Typography>
        </Box>
    )
}

export default Login
