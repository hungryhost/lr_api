import {combineReducers} from '@reduxjs/toolkit'
import {reducer as auth} from "src/Slices/Auth";
import {reducer as layout} from 'src/Slices/Layout'


export const rootReducer = combineReducers({
    auth,
    layout
})
