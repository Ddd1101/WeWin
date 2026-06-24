package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class MessageResponse(
    val message: String? = null
)
