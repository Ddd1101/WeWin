package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class AccessoryListDto(
    val accessories: List<AccessoryListItem> = emptyList()
) {
    @Serializable
    data class AccessoryListItem(
        val id: Int,
        val code: String,
        val name: String,
        val cost_price: Double = 0.0,
        val location: String? = null,
        val supplier: String? = null,
        val material: String? = null,
        val size: Int? = null,
        val color: String? = null,
        val image_url: String? = null,
        val skus: List<SkuDto> = emptyList()
    )
}
