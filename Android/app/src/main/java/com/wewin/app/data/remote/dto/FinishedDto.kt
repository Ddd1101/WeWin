package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class FinishedDto(
    val cost_mode: String = "auto",
    val manual_cost: Double = 0.0,
    val reference_cost: Double = 0.0,
    val adopted_cost: Double = 0.0,
    val labor_cost: Double = 0.0,
    val elastic_cost: Double = 0.0,
    val beads: List<FinishedBeadItemDto> = emptyList(),
    val accessories: List<FinishedAccessoryItemDto> = emptyList()
)
