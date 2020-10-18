import {createSlice} from "@reduxjs/toolkit";

const initialState = {
    isNavBarOpen: true,
    isNavBarShort: localStorage.getItem('isNavBarShort'),
}

const slice = createSlice({
    name: "layout",
    initialState,
    reducers: {
        toggleNavBar(state, action) {
            state.isNavBarOpen = action.payload;
        },
        toggleShortNavBar(state, action) {
            state.isNavBarShort = action.payload;
        }
    }
})

export const {reducer, actions} = slice;

export const toggleNavBar = () => (dispatch, store) => {
    const state = store().layout
    dispatch(actions.toggleNavBar(!state.isNavBarOpen));
}
export const toggleShortNavBar = () => (dispatch, store) => {
    const state = store().layout
    dispatch(actions.toggleShortNavBar(!state.isNavBarShort));
}
