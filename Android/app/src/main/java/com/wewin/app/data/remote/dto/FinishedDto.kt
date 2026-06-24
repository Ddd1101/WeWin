package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class FinishedDto(
    val labor_cost: Double = 0.0,
    val elastic_cost: Double = 0.0,
    val beads: List<FinishedBeadItemDto> = emptyList(),
    val accessories: List<FinishedAccessoryItemDto> = emptyList()
)
