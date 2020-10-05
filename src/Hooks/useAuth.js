import {useContext} from 'react'
import {AuthProvider} from "src/Contexts/Guard";

export const useAuth = () => useContext(AuthProvider)
