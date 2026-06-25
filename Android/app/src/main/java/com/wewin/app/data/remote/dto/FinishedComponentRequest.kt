package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class BeadComponentRequest(
    val bead_id: Int,
    val sku_id: Int? = null,
    val quantity: Int
)

@Serializable
data class AccessoryComponentRequest(
    val accessory_id: Int,
    val sku_id: Int? = null,
    val quantity: Int
)
