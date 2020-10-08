import {configureStore} from "@reduxjs/toolkit";
import { ENABLE_REDUX_DEV_TOOLS } from "../config";
import {rootReducer} from "./rootReducer";

export const store = configureStore({
    reducer: rootReducer,
    devTools: ENABLE_REDUX_DEV_TOOLS
})
