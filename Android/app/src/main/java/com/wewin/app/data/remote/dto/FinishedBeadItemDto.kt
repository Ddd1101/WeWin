package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class FinishedBeadItemDto(
    val bead_id: Int,
    val sku_id: Int? = null,
    val sku: SkuDto? = null,
    val bead_code: String? = null,
    val bead_name: String? = null,
    val bead_cost_price: Double = 0.0,
    val bead_purchase_cost: Double? = null,
    val bead_image_url: String? = null,
    val quantity: Int = 0,
    val bead_weight: Double = 0.0,
    val bead_quality_level: Int = 5,
    val bead_remark: String? = null,
    val bead_size: Int? = null
)
