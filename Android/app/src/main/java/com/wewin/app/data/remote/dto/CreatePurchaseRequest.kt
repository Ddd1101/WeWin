package com.wewin.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class CreatePurchaseItemRequest(
    @SerialName("product_id") val productId: Int? = null,
    @SerialName("sku_id") val skuId: Int? = null,
    @SerialName("product_type") val productType: String,
    @SerialName("product_name") val productName: String = "",
    @SerialName("sku_code") val skuCode: String = "",
    val quantity: Double,
    val unit: String,
    @SerialName("unit_price") val unitPrice: Double,
    val supplier: String = "",
    val location: String = "",
    @SerialName("quality_level") val qualityLevel: Int? = null,
    val material: String = "",
    val size: Int? = null,
    val color: String = "",
    val remark: String = ""
)

@Serializable
data class CreatePurchaseListRequest(
    val title: String,
    @SerialName("assignee_id") val assigneeId: Int,
    @SerialName("planned_date") val plannedDate: String,
    val notes: String = "",
    val items: List<CreatePurchaseItemRequest>
)

@Serializable
data class UpdatePurchaseListRequest(
    val title: String? = null,
    @SerialName("assignee_id") val assigneeId: Int? = null,
    @SerialName("planned_date") val plannedDate: String? = null,
    val notes: String? = null
)

@Serializable
data class MarkPartialRequest(
    @SerialName("purchased_quantity") val purchasedQuantity: Double
)
