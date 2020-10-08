import {useContext} from 'react'
import {AuthProvider} from "Components/AuthGuard";

export const useAuth = () => useContext(AuthProvider)
