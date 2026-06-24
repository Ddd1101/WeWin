package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProductStatsDto(
    val product_stats: ProductStats = ProductStats()
) {
    @Serializable
    data class ProductStats(
        val total_count: Int = 0,
        val active_count: Int = 0,
        val bead_count: Int = 0,
        val accessory_count: Int = 0,
        val finished_count: Int = 0,
        val sku_count: Int = 0
    )
}
