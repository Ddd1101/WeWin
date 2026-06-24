package com.wewin.app.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.ShoppingBag
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.wewin.app.data.local.TokenStore
import com.wewin.app.ui.products.ProductListScreen
import com.wewin.app.ui.profile.ProfileScreen

@Composable
fun MainScaffold(
    onNavigateToProductDetail: (Int) -> Unit,
    onNavigateToProductEdit: (Int?) -> Unit,
    onLogout: () -> Unit
) {
    val navController = rememberNavController()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route
    val context = LocalContext.current
    val tokenStore = remember { TokenStore(context.applicationContext) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = currentRoute == Screen.ProductList.route,
                    onClick = {
                        navController.navigate(Screen.ProductList.route) {
                            popUpTo(navController.graph.findStartDestination().id) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    },
                    icon = {
                        Icon(
                            imageVector = Icons.Filled.ShoppingBag,
                            contentDescription = "商品"
                        )
                    },
                    label = { Text("商品") }
                )
                NavigationBarItem(
                    selected = currentRoute == Screen.Profile.route,
                    onClick = {
                        navController.navigate(Screen.Profile.route) {
                            popUpTo(navController.graph.findStartDestination().id) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    },
                    icon = {
                        Icon(
                            imageVector = Icons.Filled.Person,
                            contentDescription = "我的"
                        )
                    },
                    label = { Text("我的") }
                )
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = Screen.ProductList.route,
            modifier = Modifier.padding(padding)
        ) {
            composable(Screen.ProductList.route) {
                ProductListScreen(
                    onNavigateToProductDetail = onNavigateToProductDetail,
                    onNavigateToProductEdit = onNavigateToProductEdit
                )
            }
            composable(Screen.Profile.route) {
                ProfileScreen(
                    tokenStore = tokenStore,
                    onLogout = onLogout
                )
            }
        }
    }
}
