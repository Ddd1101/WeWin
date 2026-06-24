package com.wewin.app.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class ErrorResponse(
    val error: String? = null,
    val message: String? = null
)
