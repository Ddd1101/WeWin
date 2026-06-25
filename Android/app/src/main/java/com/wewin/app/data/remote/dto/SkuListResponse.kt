package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class SkuListResponse(
    val skus: List<SkuDto> = emptyList()
)
