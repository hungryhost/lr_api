import React, {
    Suspense,
    Fragment,
    lazy
} from 'react';
import {
    Switch,
    Route, Redirect
} from 'react-router-dom';
import {CircularProgress} from '@material-ui/core';
import AuthView from "src/Views/Auth/AuthView";
import {GuestGuard} from "src/Components/GuestGuard";
import {AuthGuard} from "src/Components/AuthGuard";
import {MainView} from "./Views/Main/MainView";

/**
* Рендерим роуты с нужными guards
* Рендер компонентов делаем через lazy-suspense
*/

export const renderRoutes = (routes = []) => (
    <Suspense fallback={<CircularProgress />}>
        <Switch>
            {routes.map((route, i) => {
                const Guard = route.guard || Fragment;
                const Layout = route.layout || Fragment;
                const Component = route.component;
                const props = route.props;
                return (
                    <Route
                        key={i}
                        path={route.path}
                        exact={route.exact}>
                            <Guard>
                                <Layout>
                                    {route.routes ? renderRoutes(route.routes) : <Component {...props}/>}
                                </Layout>
                            </Guard>
                    </Route>
                );
            })}
        </Switch>
    </Suspense>
);


export const routes = [
    {
        exact: true,
        path: '/login',
        component: lazy(() => import('src/Views/Auth/Components/Login')),
        layout: AuthView,
        guard: GuestGuard
    },
    {
        exact: true,
        path: '/register',
        component: lazy(() => import('src/Views/Auth/Components/Register')),
        layout: AuthView,
        guard: GuestGuard
    },
    {
        path: '/app',
        layout: MainView,
        component: Fragment
    },
    // todo: for testing guards
    {
        path: "*",
        component: Redirect,
        guard: AuthGuard,
        props: {to: '/login'}
    }
];




