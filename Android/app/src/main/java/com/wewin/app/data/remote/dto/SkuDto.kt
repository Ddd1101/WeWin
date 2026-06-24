package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class SkuDto(
    val id: Int,
    val sku_id: Int? = null,
    val sku_code: String? = null,
    val name: String? = null,
    val sku_name: String? = null,
    val material: String? = null,
    val size: Int? = null,
    val color: String? = null,
    val purchase_cost: Double = 0.0,
    val cost_price: Double = 0.0,
    val weight: Double = 0.0,
    val quality_level: Int = 5,
    val selling_price: Double = 0.0,
    val location: String? = null,
    val supplier: String? = null,
    val remark: String? = null,
    val is_default: Boolean = false,
    val is_active: Boolean = true
)
