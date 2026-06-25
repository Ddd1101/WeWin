package com.wewin.app.ui.navigation

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Main : Screen("main")
    object ProductList : Screen("products")
    object ProductDetail : Screen("product_detail/{productId}") {
        fun createRoute(productId: Int) = "product_detail/$productId"
    }
    object ProductEdit : Screen("product_edit?productId={productId}") {
        const val ARG_PRODUCT_ID = "productId"
        fun createRoute(productId: Int?) = if (productId != null) "product_edit?productId=$productId" else "product_edit"
    }
    object Profile : Screen("profile")
}
