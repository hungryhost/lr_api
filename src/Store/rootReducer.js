import {combineReducers} from '@reduxjs/toolkit'
import {reducer} from "../Slices/Auth";

export const rootReducer = combineReducers({
    auth: reducer
})
