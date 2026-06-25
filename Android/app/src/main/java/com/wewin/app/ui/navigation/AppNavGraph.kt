package com.wewin.app.ui.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.wewin.app.data.local.AuthEventBus
import com.wewin.app.data.local.TokenStore
import com.wewin.app.ui.login.LoginScreen
import com.wewin.app.ui.products.ProductDetailScreen
import com.wewin.app.ui.products.ProductEditScreen
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

@Composable
fun AppNavGraph(tokenStore: TokenStore) {
    val navController = rememberNavController()
    val scope = rememberCoroutineScope()

    var startRoute by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        val token = tokenStore.tokenFlow.first()
        startRoute = if (token != null) Screen.Main.route else Screen.Login.route
    }

    LaunchedEffect(Unit) {
        AuthEventBus.events.collect {
            navController.navigate(Screen.Login.route) {
                popUpTo(0) { inclusive = true }
            }
        }
    }

    val currentStartRoute = startRoute
    if (currentStartRoute == null) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator()
        }
        return
    }

    NavHost(
        navController = navController,
        startDestination = currentStartRoute
    ) {
        composable(Screen.Login.route) {
            LoginScreen(
                tokenStore = tokenStore,
                onLoginSuccess = {
                    navController.navigate(Screen.Main.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        composable(Screen.Main.route) {
            MainScaffold(
                onNavigateToProductDetail = { productId ->
                    navController.navigate(Screen.ProductDetail.createRoute(productId))
                },
                onNavigateToProductEdit = { productId ->
                    navController.navigate(Screen.ProductEdit.createRoute(productId))
                },
                onLogout = {
                    scope.launch { tokenStore.clear() }
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
        composable(
            route = Screen.ProductDetail.route,
            arguments = listOf(
                navArgument("productId") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val productId = backStackEntry.arguments?.getInt("productId") ?: 0
            ProductDetailScreen(
                productId = productId,
                onBack = { navController.popBackStack() },
                onEdit = {
                    navController.navigate(Screen.ProductEdit.createRoute(productId))
                }
            )
        }
        composable(
            route = Screen.ProductEdit.route,
            arguments = listOf(
                navArgument(Screen.ProductEdit.ARG_PRODUCT_ID) {
                    type = NavType.IntType
                    defaultValue = -1
                }
            )
        ) { backStackEntry ->
            val rawId = backStackEntry.arguments?.getInt(Screen.ProductEdit.ARG_PRODUCT_ID) ?: -1
            val productId = if (rawId >= 0) rawId else null
            ProductEditScreen(
                productId = productId,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
