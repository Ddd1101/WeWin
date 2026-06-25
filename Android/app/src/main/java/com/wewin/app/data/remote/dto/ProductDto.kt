package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProductDto(
    val id: Int,
    val code: String,
    val name: String,
    val product_type: String,
    val product_type_display: String? = null,
    val purchase_cost: Double,
    val cost_price: Double,
    val selling_price: Double,
    val location: String? = null,
    val supplier: String? = null,
    val company_id: Int? = null,
    val company_name: String? = null,
    val image_url: String? = null,
    val is_active: Boolean = true,
    val created_by_id: Int? = null,
    val created_by_name: String? = null,
    val created_at: String? = null,
    val updated_at: String? = null,
    val bead: BeadDto? = null,
    val accessory: AccessoryDto? = null,
    val finished: FinishedDto? = null,
    val skus: List<SkuDto> = emptyList()
)
