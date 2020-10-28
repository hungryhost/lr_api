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
import {MainView} from "src/Views/Main/MainView";
import {Page as Title} from "src/Components/Page";

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
                const Page = route.title ? Title : Fragment
                return (
                    <Route
                        key={i}
                        path={route.path}
                        exact={route.exact}>
                            <Guard>
                                <Page title={route.title}>
                                    <Layout>
                                        {route.routes ? renderRoutes(route.routes) : <Component {...props}/>}
                                    </Layout>
                                </Page>
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
        guard: GuestGuard,
        title: "Авторизация"
    },
    {
        exact: true,
        path: '/register',
        component: lazy(() => import('src/Views/Auth/Components/Register')),
        layout: AuthView,
        guard: GuestGuard,
        title: "Регистрация"
    },
    {
        path: '/app',
        layout: MainView,
        component: Fragment,
        title: "Сервис аренды помещений"
    },
    // todo: for testing guards
    {
        path: "*",
        component: Redirect,
        guard: AuthGuard,
        props: {to: '/login'}
    }
];




