import {useContext} from 'react'
import {AuthProvider} from "src/Components/AuthGuard";

export const useAuth = () => useContext(AuthProvider)
