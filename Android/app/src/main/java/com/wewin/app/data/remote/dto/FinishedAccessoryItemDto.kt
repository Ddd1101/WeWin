package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class FinishedAccessoryItemDto(
    val accessory_id: Int,
    val sku_id: Int? = null,
    val sku: SkuDto? = null,
    val accessory_code: String? = null,
    val accessory_name: String? = null,
    val accessory_cost_price: Double = 0.0,
    val accessory_image_url: String? = null,
    val quantity: Int = 0
)
