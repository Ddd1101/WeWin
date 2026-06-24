package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class ProductListResponse(
    val products: List<ProductDto> = emptyList(),
    val total_count: Int = 0,
    val page: Int = 1,
    val page_size: Int = 50
)
