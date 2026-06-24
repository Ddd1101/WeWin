package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class AccessoryDto(
    val material: String? = null,
    val size: Int? = null,
    val color: String? = null
)
