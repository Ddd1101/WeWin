package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class BeadDto(
    val material: String? = null,
    val size: Int? = null,
    val color: String? = null,
    val weight: Double = 0.0,
    val quality_level: Int = 5,
    val remark: String? = null
)
