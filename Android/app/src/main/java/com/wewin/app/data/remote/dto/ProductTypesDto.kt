package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProductTypesDto(
    val product_types: List<ProductTypeOption> = emptyList()
) {
    @Serializable
    data class ProductTypeOption(
        val value: String,
        val label: String
    )
}
